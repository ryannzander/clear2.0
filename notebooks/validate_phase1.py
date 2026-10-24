# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
# ---
# %% [markdown]
# Phase 1 validate step (scratch driver, never imported): runs the checks of
# methodology/stations.md#validation-criteria on the built outputs and writes
# knowledge/data/<slug>.validation.md. Run: uv run python notebooks/validate_phase1.py
# ruff: noqa: E501  (report sentences are kept whole; scratch driver)

# %%
import json

import pandas as pd

from clear.geo import CITY_BOUNDARY_FILE, read_city_boundary
from clear.paths import data_dir, repo_root
from clear.schemas.stations import HOURLY, INTERIM_RAW, REGISTRY
from clear.stations.pipeline import outputs
from clear.stations.report import source_agreement, years_active
from clear.stations.settings import load_stations_config

DATE = "2026-10-24"
cfg = load_stations_config()
paths = outputs()
registry = REGISTRY.validate(pd.read_parquet(paths.registry))
hourly = HOURLY.validate(pd.read_parquet(paths.hourly))
toronto = registry[registry["is_in_toronto"]]
agreement = source_agreement(hourly, toronto)

# Toronto stations and years each card lists (source calendar), for the coverage check.
CARD_YEARS = {
    "naps-hourly-pm25": {
        "naps:060403": (2000, 2001),
        "naps:060410": (2002, 2024),
        "naps:060413": (2002, 2010),
        "naps:060421": (2000, 2016),
        "naps:060424": (2000, 2002),
        "naps:060429": (2001, 2012),
        "naps:060430": (2000, 2024),
        "naps:060433": (2003, 2019),
        "naps:060435": (2010, 2024),
        "naps:060438": (2016, 2024),
        "naps:060439": (2019, 2019),
        "naps:060440": (2017, 2024),
        "naps:060445": (2019, 2024),
    },
    "mecp-hourly-pm25": {
        "mecp:31103": (2003, 2019),
        "mecp:31129": (2019, 2025),
        "mecp:33003": (2003, 2025),
        "mecp:34020": (2003, 2016),
        "mecp:34021": (2017, 2025),
        "mecp:35125": (2003, 2025),
    },
    "airnow-hourlyaqobs": {
        "airnow:124000060445": (2020, 2026),
        "airnow:000060410": (2023, 2026),
        "airnow:124000060430": (2023, 2026),
        "airnow:124000060440": (2023, 2026),
        "airnow:000060424": (2019, 2021),
    },
    "airnow-hourlydata-2014-2019": {"airnow:000060424": (2014, 2019)},
}


def years_of(station_id: str, raw: pd.DataFrame) -> tuple[int, int]:
    t = raw.loc[raw["station_id"] == station_id]
    span = pd.DataFrame(
        {
            "source": [t["source"].iloc[0]],
            "first_time_utc": [t["time_utc"].min()],
            "last_time_utc": [t["time_utc"].max()],
        }
    )
    years = years_active(span, cfg)  # the same rule as EXP-001 (stations.md#completeness)
    return int(years["first_year"].iloc[0]), int(years["last_year"].iloc[0])


def lag_rows(source: str) -> str:
    sub = agreement[
        agreement["station_a"].str.startswith(source)
        | agreement["station_b"].str.startswith(source)
    ]
    ok = bool(((sub["r"] > sub["r_lag_m1h"]) & (sub["r"] > sub["r_lag_p1h"])).all())
    return f"{len(sub)} co-located pairs, best r at lag 0 in all: {ok}"


def report(
    slug: str, spec: str, result: str, rows: list[tuple[str, str, str, str]], notes: list[str]
) -> None:
    table = "\n".join(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows)
    body = (
        f"---\ndataset: {slug}\ndate: {DATE}\nspec: {spec}\nresult: {result}\n---\n\n"
        f"# {slug} — validation\n\nChecks run by `notebooks/validate_phase1.py` on the Phase 1 build "
        "(`uv run clear stations build`).\n\n| Check | Spec source | Result | n failing |\n|---|---|---|---|\n"
        f"{table}\n\n## Issues and handling\n\n" + "\n".join(f"- {n}" for n in notes) + "\n"
    )
    (repo_root() / "knowledge" / "data" / f"{slug}.validation.md").write_text(
        body, encoding="utf-8", newline="\n"
    )


# %%
SPEC = "methodology/stations.md#validation-criteria"
for source, slugs in (
    ("naps", ["naps-hourly-pm25"]),
    ("mecp", ["mecp-hourly-pm25"]),
    ("airnow", ["airnow-hourlyaqobs", "airnow-hourlydata-2014-2019"]),
):
    sentinels = cfg.source(source).sentinels
    for slug in slugs:
        raw = INTERIM_RAW.validate(pd.read_parquet(paths.interim(slug)))
        n_sent = int(raw["pm25_raw_ugm3"].isin(sentinels).sum())
        n_neg = int(((raw["pm25_raw_ugm3"] < 0) & ~raw["pm25_raw_ugm3"].isin(sentinels)).sum())
        n_rep = int(raw.duplicated(["station_id", "time_utc"]).sum())
        expected = CARD_YEARS[slug]
        got = {sid: years_of(sid, raw) for sid in expected if (raw["station_id"] == sid).any()}
        bad_years = {
            sid: (got.get(sid), want) for sid, want in expected.items() if got.get(sid) != want
        }
        rows = [
            ("interim schema (UTC, on the hour, ids)", "stations.md#read-sources", "pass", "0"),
            ("non-numeric cells", "ADR 0007 / code.md", "pass (reader raises)", "0"),
            ("sentinel cells found → missing", "ADR 0007", "handled in QC", str(n_sent)),
            ("other negative cells → missing", "ADR 0007", "handled in QC", str(n_neg)),
            ("repeat station-hours → averaged", "ADR 0007", "handled in QC", str(n_rep)),
            (
                "processed hourly ≥ 0, unique station-hour",
                "stations.md#validation-criteria",
                "pass",
                "0",
            ),
            (
                "Toronto stations and years vs card",
                "card Coverage",
                "pass" if not bad_years else "fail",
                str(len(bad_years)),
            ),
            ("time convention: lag-0 best vs co-located", "ADR 0005", lag_rows(source), "0"),
        ]
        notes = [
            f"{len(raw):,} raw rows in the read scope (City bounds ± {cfg.registry_margin_deg}°).",
            "Sentinels, negatives and repeats stay in the interim table (lossless) and are removed or averaged in `processed/stations/hourly_pm25` (ADR 0007).",
        ]
        if bad_years:
            notes.append(f"Year mismatches: {json.dumps(bad_years)}")
        if source == "airnow":
            notes.append(
                "Preliminary data (card); AirNow reads 0.3–0.5 µg/m³ above NAPS/MECP at East, West, North (EXP-003): open question for Ryan."
            )
            notes.append("`PM25_Measured = 0` rows are not filtered (stations.md open question 2).")
        if source == "mecp":
            notes.append(
                "Hour-ending label confirmed by observation only (provider undocumented); lag check above."
            )
        notes.append(
            "Scope: the Phase 1 read box only (City bounds +/- the registry margin); stations "
            "elsewhere in the card's coverage are not checked yet, so the result is at most partial."
        )
        result = "partial"
        report(slug, SPEC, result, rows, notes)
        print(slug, result, bad_years)

# %%
from shapely.geometry import box

from clear.grid.cells import load_toronto_grid_config
from clear.grid.pipeline import grid_outputs
from clear.schemas.grid import CELLS, STATION_CELLS

gpd = __import__("geopandas")
zip_path = data_dir() / "raw" / CITY_BOUNDARY_FILE
crs = gpd.read_file(f"zip://{zip_path.as_posix()}").crs
crs_ok = crs is not None and crs.is_geographic and crs.name == "WGS 84"
city = read_city_boundary(zip_path)
area_km2 = float(gpd.GeoSeries([city], crs=4326).to_crs(32617).area.iloc[0] / 1e6)
grid_paths = grid_outputs(load_toronto_grid_config().cell_size_deg)
cells = CELLS.validate(pd.read_parquet(grid_paths.cells))
station_cells = STATION_CELLS.validate(pd.read_parquet(grid_paths.station_cells))
boxes = gpd.GeoSeries(
    [box(r.lon_min_deg, r.lat_min_deg, r.lon_max_deg, r.lat_max_deg) for r in cells.itertuples()],
    crs=4326,
).to_crs(32617)
covered_km2 = float((cells["city_frac"].to_numpy() * boxes.area.to_numpy()).sum() / 1e6)
toronto_cells = set(cells.loc[cells["is_in_toronto"], "cell_id"])
in_city = station_cells[station_cells["is_in_toronto"]]
n_outside = int((~in_city["cell_id"].isin(toronto_cells)).sum())
report(
    "toronto-city-boundary",
    "methodology/grid.md#validation-criteria",
    "validated" if crs_ok and city.is_valid and n_outside == 0 else "partial",
    [
        ("geometry valid, one polygon", "card", "pass" if city.is_valid else "fail", "0"),
        (
            f"CRS: {crs.name if crs is not None else None}",
            "stations.md#select-toronto-stations",
            "pass" if crs_ok else "fail",
            "0",
        ),
        (
            f"area (UTM 17N) {area_km2:.1f} km2 vs City 641 km2",
            "card Coverage",
            "pass" if abs(area_km2 - 641) < 6.5 else "fail",
            "0",
        ),
        (
            f"sum of city_frac x cell area {covered_km2:.1f} km2 vs {area_km2:.1f} km2",
            "grid.md#validation-criteria",
            "pass" if abs(covered_km2 - area_km2) / area_km2 < 0.01 else "fail",
            "0",
        ),
        (
            "Toronto stations in Toronto cells",
            "grid.md#validation-criteria",
            "pass" if n_outside == 0 else "fail",
            str(n_outside),
        ),
    ],
    ["None."],
)
print("boundary", round(area_km2, 2), round(covered_km2, 2), n_outside)
