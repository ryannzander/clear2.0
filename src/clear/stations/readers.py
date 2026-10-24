"""Read NAPS, MECP and AirNow hourly PM2.5 into lossless long tables in UTC.

Spec: methodology/stations.md#read-sources. Every reader returns :class:`SourceTables`:
station metadata (one row per station) and raw station-hours with ``station_id``, ``source``,
``dataset`` (the data-card slug), ``time_utc`` (UTC, hour-beginning), ``pm25_raw_ugm3`` (the
value exactly as published: sentinels, negatives and repeats kept) and ``method_code``.
Empty cells carry no value and produce no row. Value QC is :mod:`clear.stations.qc`.
Parsing is strict: a non-numeric token or undecodable byte raises instead of being dropped.
"""

import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from clear.geo import Bounds
from clear.stations.settings import SourceConfig
from clear.timeutil import lst_zone, to_utc

__all__ = [
    "AQOBS_DATASET",
    "HOURLYDATA_DATASET",
    "RAW_COLUMNS",
    "STATION_COLUMNS",
    "SourceTables",
    "read_airnow",
    "read_mecp",
    "read_naps",
    "to_number",
    "wide_to_long",
]

RAW_COLUMNS = ["station_id", "source", "dataset", "time_utc", "pm25_raw_ugm3", "method_code"]
STATION_COLUMNS = ["station_id", "source", "station_name", "lat_deg", "lon_deg"]
AQOBS_DATASET = "airnow-hourlyaqobs"
HOURLYDATA_DATASET = "airnow-hourlydata-2014-2019"
_HOUR_COLUMNS = [f"H{h:02d}" for h in range(1, 25)]
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_MECP_NAME_ID_RE = re.compile(r"\s*\(\d+\)\s*$")


@dataclass(frozen=True)
class SourceTables:
    """What a reader returns: station metadata and raw station-hours.

    Method: methodology/stations.md#read-sources
    """

    stations: pd.DataFrame
    raw: pd.DataFrame


def _empty() -> SourceTables:
    return SourceTables(pd.DataFrame(columns=STATION_COLUMNS), pd.DataFrame(columns=RAW_COLUMNS))


def to_number(values: "pd.Series[str]") -> "pd.Series[float]":
    """Parse published values: empty = NaN, numbers = float, anything else raises.

    Method: docs/standards/code.md#error-handling-fail-loud-at-boundaries

    Parameters
    ----------
    values : pandas.Series
        Cells as read (strings or numbers).

    Returns
    -------
    pandas.Series of float
        Same index; NaN only where the cell was empty.

    Raises
    ------
    ValueError
        If a non-empty cell is not a number; the message counts them and shows examples.
    """
    text = values.astype("string").str.strip()
    empty = text.isna() | (text == "")
    parsed = pd.to_numeric(text.mask(empty), errors="coerce")  # checked just below
    bad = parsed.isna() & ~empty
    if bad.any():
        examples = sorted({str(v) for v in text[bad]})[:5]
        raise ValueError(f"{int(bad.sum())} non-numeric value cells, e.g. {examples}")
    return parsed.astype("float64")


def wide_to_long(
    frame: pd.DataFrame, *, source: str, dataset: str, config: SourceConfig
) -> pd.DataFrame:
    """Melt station-day rows with ``H01``..``H24`` into raw station-hours in UTC.

    Method: methodology/stations.md#read-sources

    The local naive time of hour ``Hnn`` is ``date + nn hours`` for an hour-ending source
    (``H24`` = 00:00 of the next day), else ``date + (nn - 1) hours``; :func:`to_utc` then
    shifts hour-ending labels back one hour (ADR 0005).

    Parameters
    ----------
    frame : pandas.DataFrame
        ``station_id``, ``date`` (``YYYY-MM-DD``), ``method_code`` and ``H01``..``H24``.
    source : str
        Source key written to ``source``.
    dataset : str
        Data-card slug written to ``dataset``.
    config : SourceConfig
        Clock and hour label of the source.

    Returns
    -------
    pandas.DataFrame
        ``RAW_COLUMNS``, one row per non-empty cell.
    """
    long = frame.melt(
        id_vars=["station_id", "date", "method_code"],
        value_vars=_HOUR_COLUMNS,
        var_name="hour",
        value_name="pm25_raw_ugm3",
    )
    long["pm25_raw_ugm3"] = to_number(long["pm25_raw_ugm3"])
    long = long.dropna(subset=["pm25_raw_ugm3"])
    hour_number = long["hour"].str.slice(1).astype("int64")
    offset_h = hour_number if config.hour_ending else hour_number - 1
    local = pd.to_datetime(long["date"], format="%Y-%m-%d") + pd.to_timedelta(offset_h, unit="h")
    long["time_utc"] = to_utc(
        local, source_tz=lst_zone(config.utc_offset_h), hour_ending=config.hour_ending
    )
    return long.assign(source=source, dataset=dataset)[RAW_COLUMNS].reset_index(drop=True)


def _last_per_station(meta: pd.DataFrame) -> pd.DataFrame:
    return meta.drop_duplicates("station_id", keep="last").reset_index(drop=True)


# --- NAPS -----------------------------------------------------------------------------


def _naps_header_row(path: Path) -> int:
    with path.open(encoding="utf-8-sig") as fh:
        for i, line in enumerate(fh):
            if line.startswith("Pollutant//"):
                return i
            if i > 50:
                break
    raise ValueError(f"{path}: no 'Pollutant//' header line in the first 50 lines")


def read_naps(
    paths: Iterable[Path], *, dataset: str, bounds: Bounds, config: SourceConfig
) -> SourceTables:
    """Read NAPS yearly ``PM25_YYYY.csv`` files, keeping stations inside ``bounds``.

    Method: methodology/stations.md#read-sources

    Parameters
    ----------
    paths : iterable of Path
        The yearly CSVs (``knowledge/data/naps-hourly-pm25.md``).
    dataset : str
        Data-card slug of the files.
    bounds : Bounds
        Read scope; stations outside it are skipped.
    config : SourceConfig
        ``sources.naps`` of ``config/stations.yaml``.

    Returns
    -------
    SourceTables
        ``station_id`` = ``naps:<6-digit NAPS ID>``; ``method_code`` kept per row.

    Raises
    ------
    ValueError
        If a file has no header line or a non-numeric hourly value.
    """
    meta_parts: list[pd.DataFrame] = []
    raw_parts: list[pd.DataFrame] = []
    for path in sorted(paths):
        table = pd.read_csv(path, skiprows=_naps_header_row(path), encoding="utf-8-sig", dtype=str)
        table.columns = [str(c).split("//")[0].strip() for c in table.columns]
        lat, lon = table["Latitude"].astype(float), table["Longitude"].astype(float)
        table = table[bounds.contains(lat, lon)]
        if table.empty:
            continue
        table = table.assign(
            station_id="naps:" + table["NAPS ID"].str.strip(),
            date=table["Date"].str.strip(),
            method_code=table["Method Code"].str.strip(),
            station_name=table["City"],
            lat_deg=table["Latitude"].astype(float),
            lon_deg=table["Longitude"].astype(float),
            source="naps",
        )
        meta_parts.append(table.drop_duplicates("station_id")[STATION_COLUMNS])
        raw_parts.append(wide_to_long(table, source="naps", dataset=dataset, config=config))
    if not meta_parts:
        return _empty()
    return SourceTables(
        stations=_last_per_station(pd.concat(meta_parts, ignore_index=True)),
        raw=pd.concat(raw_parts, ignore_index=True),
    )


# --- MECP -----------------------------------------------------------------------------


def _parse_mecp_file(path: Path) -> tuple[list[dict[str, object]], list[list[str]]]:
    """Return (station blocks, data rows) of one Air Quality Ontario yearly file."""
    stations: list[dict[str, object]] = []
    rows: list[list[str]] = []
    current: dict[str, object] = {}
    with path.open(encoding="utf-8") as fh:  # strict: an undecodable byte raises
        for line in fh:
            parts = [p.strip() for p in line.rstrip("\r\n").split(",")]
            key = parts[0]
            if key == "Station" and len(parts) > 1:
                current = {"station_name": _MECP_NAME_ID_RE.sub("", ",".join(parts[1:]))}
                stations.append(current)
            elif key in ("Latitude", "Longitude") and len(parts) > 1 and current:
                current["lat_deg" if key == "Latitude" else "lon_deg"] = float(parts[1])
            elif key.isdigit() and len(parts) >= 3 and _DATE_RE.match(parts[2]):
                current.setdefault("code", key)
                hours = parts[3:27]
                hours += [""] * (24 - len(hours))  # truncated last rows (mecp card)
                rows.append([key, parts[2], *hours])
    return stations, rows


def read_mecp(
    paths: Iterable[Path], *, dataset: str, bounds: Bounds, config: SourceConfig
) -> SourceTables:
    """Read Air Quality Ontario yearly files (every station per file), inside ``bounds``.

    Method: methodology/stations.md#read-sources

    Parameters
    ----------
    paths : iterable of Path
        The yearly CSVs (``knowledge/data/mecp-hourly-pm25.md``).
    dataset : str
        Data-card slug of the files.
    bounds : Bounds
        Read scope.
    config : SourceConfig
        ``sources.mecp`` of ``config/stations.yaml``.

    Returns
    -------
    SourceTables
        ``station_id`` = ``mecp:<5-digit station ID>``; duplicate rows kept.

    Raises
    ------
    ValueError
        If a value cell is not a number.
    UnicodeDecodeError
        If a file is not valid UTF-8.
    """
    meta_records: list[dict[str, object]] = []
    rows: list[list[str]] = []
    for path in sorted(paths):
        stations, file_rows = _parse_mecp_file(path)
        meta_records += [s for s in stations if {"code", "lat_deg", "lon_deg"} <= s.keys()]
        rows += file_rows
    if not meta_records:
        return _empty()
    meta = pd.DataFrame.from_records(meta_records)
    meta = meta.assign(station_id="mecp:" + meta["code"].astype(str), source="mecp")
    meta = _last_per_station(meta[STATION_COLUMNS])
    meta = meta[bounds.contains(meta["lat_deg"], meta["lon_deg"])].reset_index(drop=True)
    wide = pd.DataFrame(rows, columns=["code", "date", *_HOUR_COLUMNS])
    wide = wide.assign(
        station_id="mecp:" + wide["code"],
        method_code=pd.Series(pd.NA, index=wide.index, dtype="string"),
    )
    wide = wide[wide["station_id"].isin(meta["station_id"])]
    return SourceTables(meta, wide_to_long(wide, source="mecp", dataset=dataset, config=config))


# --- AirNow ---------------------------------------------------------------------------

_AQOBS_COLUMNS = ["AQSID", "SiteName", "Latitude", "Longitude", "ValidDate", "ValidTime", "PM25"]
_HOURLYDATA_COLUMNS = ["AQSID", "ValidDate", "ValidTime", "Value"]
# monitoring_site_locations.dat fields (0-based; airnow-hourlydata-2014-2019 card).
_SITE_AQSID, _SITE_PARAMETER, _SITE_NAME, _SITE_LAT, _SITE_LON = 0, 1, 3, 8, 9


def _airnow_time_utc(
    valid_date: "pd.Series[str]", valid_time: "pd.Series[str]"
) -> "pd.Series[pd.Timestamp]":
    """Parse AirNow ``mm/dd/yy`` or ``mm/dd/yyyy`` + ``HH:MM`` (UTC, hour-beginning)."""
    date = valid_date.str.strip()
    stamp = date + " " + valid_time.str.strip()
    long_year = date.str.len() == 10
    out = pd.Series(pd.NaT, index=stamp.index, dtype="datetime64[us]")
    out[long_year] = pd.to_datetime(stamp[long_year], format="%m/%d/%Y %H:%M")
    out[~long_year] = pd.to_datetime(stamp[~long_year], format="%m/%d/%y %H:%M")
    return to_utc(out, source_tz="Etc/UTC", hour_ending=False)


def _airnow_site_locations(paths: Iterable[Path]) -> pd.DataFrame:
    """Latest PM2.5 site coordinates from the ``monitoring_site_locations_*.dat`` snapshots."""
    records: dict[str, tuple[str, float, float]] = {}
    for path in sorted(paths):  # names sort by snapshot date; later snapshots win
        # Some non-Canadian site names hold non-UTF-8 bytes. latin-1 maps every byte without
        # loss; ids, parameter and coordinates are ASCII, a non-UTF-8 name may read oddly.
        with path.open(encoding="latin-1") as fh:
            for line in fh:
                f = line.split("|")
                if len(f) <= _SITE_LON or f[_SITE_PARAMETER].strip() != "PM2.5":
                    continue  # other parameters, incl. the one corrupt RHUM line (card)
                lat, lon = float(f[_SITE_LAT]), float(f[_SITE_LON])
                records[f[_SITE_AQSID].strip()] = (f[_SITE_NAME].strip(), lat, lon)
    return pd.DataFrame(
        [(a, n, la, lo) for a, (n, la, lo) in records.items()],
        columns=["AQSID", "station_name", "lat_deg", "lon_deg"],
    )


def _airnow_raw(frame: pd.DataFrame, value_column: str, dataset: str) -> pd.DataFrame:
    out = pd.DataFrame(
        {
            "station_id": "airnow:" + frame["AQSID"].astype(str).str.strip(),
            "source": "airnow",
            "dataset": dataset,
            "time_utc": _airnow_time_utc(
                frame["ValidDate"].astype(str), frame["ValidTime"].astype(str)
            ),
            "pm25_raw_ugm3": to_number(frame[value_column]),
            "method_code": pd.NA,
        },
        index=frame.index,
    )
    return out.dropna(subset=["pm25_raw_ugm3"])[RAW_COLUMNS]


def _read_parquets(paths: Iterable[Path], columns: list[str], filters: object) -> pd.DataFrame:
    # pandas-stubs type `filters` narrower than the pyarrow filter lists pandas accepts.
    frames = [pd.read_parquet(p, columns=columns, filters=filters) for p in sorted(paths)]  # pyright: ignore[reportArgumentType]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=columns)


def read_airnow(
    aqobs_paths: Iterable[Path],
    hourlydata_paths: Iterable[Path],
    site_location_paths: Iterable[Path],
    *,
    bounds: Bounds,
) -> SourceTables:
    """Read AirNow HourlyAQObs (2019-05 on) and HourlyData (2014 to 2019-05) inside ``bounds``.

    Method: methodology/stations.md#read-sources

    Site coordinates come from HourlyAQObs rows (latest pair per AQSID), else from the
    HourlyData site-location snapshots. Both datasets are UTC hour-beginning (cards).

    Parameters
    ----------
    aqobs_paths, hourlydata_paths : iterable of Path
        Monthly parquet files of the two AirNow folders.
    site_location_paths : iterable of Path
        ``monitoring_site_locations_YYYYMMDD.dat`` snapshots.
    bounds : Bounds
        Read scope.

    Returns
    -------
    SourceTables
        ``station_id`` = ``airnow:<AQSID>``; ``dataset`` tells the two folders apart.

    Raises
    ------
    ValueError
        If a value cell is not a number, or a PM2.5 site line has unparsable coordinates.
    """
    box = [
        ("Latitude", ">=", bounds.lat_min_deg),
        ("Latitude", "<=", bounds.lat_max_deg),
        ("Longitude", ">=", bounds.lon_min_deg),
        ("Longitude", "<=", bounds.lon_max_deg),
    ]
    aqobs = _read_parquets(aqobs_paths, _AQOBS_COLUMNS, box)
    aqobs_raw = _airnow_raw(aqobs, "PM25", AQOBS_DATASET)
    # Coordinates from rows with a value only, latest first-to-last (spec: latest pair seen).
    meta = (
        aqobs.loc[aqobs_raw.index]
        .assign(time_utc=aqobs_raw["time_utc"])
        .sort_values("time_utc")
        .drop_duplicates("AQSID", keep="last")
        .rename(columns={"SiteName": "station_name", "Latitude": "lat_deg", "Longitude": "lon_deg"})
    )[["AQSID", "station_name", "lat_deg", "lon_deg"]]
    sites = _airnow_site_locations(site_location_paths)
    sites = sites[bounds.contains(sites["lat_deg"], sites["lon_deg"])]
    meta = pd.concat([meta, sites[~sites["AQSID"].isin(meta["AQSID"])]], ignore_index=True)
    wanted = meta["AQSID"].astype(str).tolist()
    hourlydata = _read_parquets(hourlydata_paths, _HOURLYDATA_COLUMNS, [("AQSID", "in", wanted)])
    raw = pd.concat(
        [aqobs_raw, _airnow_raw(hourlydata, "Value", HOURLYDATA_DATASET)], ignore_index=True
    )
    meta = meta.assign(
        station_id="airnow:" + meta["AQSID"].astype(str).str.strip(),
        source="airnow",
        lat_deg=meta["lat_deg"].astype("float64"),
        lon_deg=meta["lon_deg"].astype("float64"),
    )
    return SourceTables(stations=meta[STATION_COLUMNS].reset_index(drop=True), raw=raw)
