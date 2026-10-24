"""End-to-end build of the stations outputs from ``data/raw``.

Spec: methodology/stations.md#method. CLI: ``uv run clear stations build``.
"""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import pandera.pandas as pa

from clear.geo import CITY_BOUNDARY_FILE, Bounds, city_bounds, in_city, read_city_boundary
from clear.paths import data_dir
from clear.schemas.stations import COMPLETENESS, HOURLY, INTERIM_RAW, MERGED, REGISTRY
from clear.stations.combine import merged_series
from clear.stations.completeness import completeness
from clear.stations.qc import apply_qc
from clear.stations.readers import (
    AQOBS_DATASET,
    HOURLYDATA_DATASET,
    SourceTables,
    read_airnow,
    read_mecp,
    read_naps,
)
from clear.stations.registry import build_registry, link_sites
from clear.stations.settings import SourceConfig, SplitsConfig, StationsConfig

__all__ = ["StationsOutputs", "build_stations", "outputs", "source_files"]


@dataclass(frozen=True)
class StationsOutputs:
    """Where the stations build writes its tables.

    Method: methodology/stations.md#outputs
    """

    base: Path
    hourly: Path
    registry: Path
    completeness: Path
    merged: Path

    def interim(self, dataset: str) -> Path:
        """Return the lossless interim table of one dataset slug (``data/interim/<slug>/``).

        Method: methodology/stations.md#outputs
        """
        return self.base / "interim" / dataset / "pm25_hourly_raw.parquet"


def outputs(root: Path | None = None) -> StationsOutputs:
    """Return the output paths under ``root`` (default ``data/``).

    Method: methodology/stations.md#outputs

    Parameters
    ----------
    root : Path, optional
        Data folder; default ``data/``.

    Returns
    -------
    StationsOutputs
        Interim and processed paths.
    """
    base = root or data_dir()
    processed = base / "processed" / "stations"
    return StationsOutputs(
        base=base,
        hourly=processed / "hourly_pm25.parquet",
        registry=processed / "registry.parquet",
        completeness=processed / "completeness.parquet",
        merged=processed / "series_merged.parquet",
    )


def source_files(raw: Path, folder: str, pattern: str) -> list[Path]:
    """Return the files matching ``pattern`` in ``raw/folder``; fail if there are none.

    Method: docs/standards/code.md#error-handling-fail-loud-at-boundaries

    Parameters
    ----------
    raw : Path
        ``data/raw``.
    folder : str
        Dataset folder under ``raw`` (``config/stations.yaml``).
    pattern : str
        Glob pattern of the files.

    Returns
    -------
    list of Path
        Sorted matches.

    Raises
    ------
    FileNotFoundError
        If the folder is missing or holds no matching file (a whole network would vanish).
    """
    found = sorted((raw / folder).glob(pattern))
    if not found:
        raise FileNotFoundError(f"no {pattern} in {raw / folder} (config/stations.yaml)")
    return found


def _only_folder(source: SourceConfig) -> tuple[str, str]:
    if len(source.folders) != 1:
        raise ValueError(f"expected one dataset folder, got {list(source.folders)}")
    return next(iter(source.folders.items()))


def _read_all(config: StationsConfig, raw: Path, box: Bounds) -> list[SourceTables]:
    naps, mecp, airnow = (config.sources[s] for s in ("naps", "mecp", "airnow"))
    naps_slug, naps_dir = _only_folder(naps)
    mecp_slug, mecp_dir = _only_folder(mecp)
    aqobs_dir, hd_dir = airnow.folders[AQOBS_DATASET], airnow.folders[HOURLYDATA_DATASET]
    return [
        read_naps(
            source_files(raw, naps_dir, "PM25_*.csv"), dataset=naps_slug, bounds=box, config=naps
        ),
        read_mecp(source_files(raw, mecp_dir, "*.csv"), dataset=mecp_slug, bounds=box, config=mecp),
        read_airnow(
            source_files(raw, aqobs_dir, "airnow_pm25_*.parquet"),
            source_files(raw, hd_dir, "airnow_hourlydata_pm25_*.parquet"),
            source_files(raw, f"{hd_dir}/site_locations", "*.dat"),
            bounds=box,
        ),
    ]


def _ns(frame: pd.DataFrame) -> pd.DataFrame:
    """Store UTC timestamps at nanosecond resolution (naming-units-time.md#time-rules)."""
    cols = [c for c in frame.columns if str(c).endswith("_utc")]
    return frame.astype({c: "datetime64[ns, UTC]" for c in cols}) if cols else frame


def build_stations(
    config: StationsConfig,
    splits: SplitsConfig,
    *,
    raw: Path | None = None,
    out: StationsOutputs | None = None,
) -> dict[str, int]:
    """Read every source, write lossless interim tables, then QC, registry, completeness.

    Method: methodology/stations.md#method

    Every table is validated against its schema before the first file is written, so a
    failure leaves no partial output.

    Parameters
    ----------
    config : StationsConfig
        ``config/stations.yaml``.
    splits : SplitsConfig
        ``config/splits.yaml``.
    raw : Path, optional
        Raw data folder; default ``data/raw``.
    out : StationsOutputs, optional
        Output paths; default :func:`outputs`.

    Returns
    -------
    dict of str to int
        Row counts per output and the number of Toronto stations and sites.

    Raises
    ------
    FileNotFoundError
        If a configured dataset folder holds no files.
    ValueError
        If a raw value cell is not a number.
    pandera.errors.SchemaErrors
        If an output breaks its schema (nothing is written then).
    """
    raw_dir = raw or data_dir() / "raw"
    paths = out or outputs()
    city = read_city_boundary(raw_dir / CITY_BOUNDARY_FILE)
    tables = _read_all(config, raw_dir, city_bounds(city).expanded(config.registry_margin_deg))
    raw_rows = pd.concat([t.raw for t in tables], ignore_index=True)
    stations = pd.concat([t.stations for t in tables], ignore_index=True)

    hourly = apply_qc(raw_rows, config)
    registry = build_registry(stations, hourly)
    registry["is_in_toronto"] = in_city(city, registry["lat_deg"], registry["lon_deg"])
    registry["site_id"] = link_sites(
        registry,
        max_distance_m=config.crosswalk_max_distance_m,
        source_priority=config.source_priority,
    )
    hourly = hourly[hourly["station_id"].isin(registry["station_id"])].reset_index(drop=True)
    merged = merged_series(hourly, registry, source_priority=config.source_priority)
    coverage_end = hourly["time_utc"].max() + pd.Timedelta(hours=1)
    complete = pd.concat(
        [
            completeness(
                series,
                unit_kind=kind,
                unit_column=column,
                splits=splits.splits,
                coverage_end_utc=coverage_end,
                min_frac=config.completeness_min_frac,
            )
            for series, kind, column in (
                (hourly, "station", "station_id"),
                (merged, "site", "site_id"),
            )
        ],
        ignore_index=True,
    )

    writes: list[tuple[pd.DataFrame, pa.DataFrameSchema, Path]] = [
        (group.reset_index(drop=True), INTERIM_RAW, paths.interim(str(dataset)))
        for dataset, group in raw_rows.groupby("dataset", sort=True)
    ]
    writes += [
        (hourly, HOURLY, paths.hourly),
        (registry, REGISTRY, paths.registry),
        (complete, COMPLETENESS, paths.completeness),
        (merged, MERGED, paths.merged),
    ]
    writes = [(_ns(frame), schema, path) for frame, schema, path in writes]
    for frame, schema, _ in writes:
        schema.validate(frame, lazy=True)
    for frame, _, path in writes:
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_parquet(path, index=False)

    toronto = registry[registry["is_in_toronto"]]
    return {
        "interim_raw_rows": len(raw_rows),
        "hourly_rows": len(hourly),
        "registry_stations": len(registry),
        "toronto_stations": len(toronto),
        "toronto_sites": int(toronto["site_id"].nunique()),
        "completeness_rows": len(complete),
        "merged_rows": len(merged),
    }
