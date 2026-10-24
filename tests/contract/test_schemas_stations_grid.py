from typing import Any

import pandas as pd
import pandera.errors as pe
import pytest

from clear.schemas.grid import CELLS, STATION_CELLS
from clear.schemas.stations import COMPLETENESS, HOURLY, INTERIM_RAW, MERGED, REGISTRY

T = pd.to_datetime(["2024-01-01 00:00", "2024-01-01 01:00"], utc=True)


def hourly(**overrides: Any) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "station_id": ["naps:060410"] * 2,
            "source": ["naps"] * 2,
            "time_utc": T,
            "pm25_ugm3": [1.0, 2.0],
        }
    )
    return frame.assign(**overrides)


def test_hourly_accepts_good_rows():
    HOURLY.validate(hourly())


@pytest.mark.parametrize(
    "bad",
    [
        {"pm25_ugm3": [-999.0, 2.0]},  # a sentinel survived
        {"station_id": ["060410"] * 2},  # no source prefix
        {"source": ["epa"] * 2},
        {"time_utc": pd.to_datetime(["2024-01-01 00:00", "2024-01-01 01:00"])},  # naive
        {"time_utc": [T[0], T[0]]},  # duplicate station-hour
    ],
)
def test_hourly_rejects(bad: dict[str, Any]):
    with pytest.raises((pe.SchemaError, pe.SchemaErrors)):
        HOURLY.validate(hourly(**bad), lazy=True)


def test_merged_requires_unique_site_hours():
    frame = pd.DataFrame(
        {
            "site_id": ["naps:1"] * 2,
            "time_utc": [T[0], T[0]],
            "pm25_ugm3": [1.0, 1.0],
            "source": ["naps"] * 2,
        }
    )
    with pytest.raises((pe.SchemaError, pe.SchemaErrors)):
        MERGED.validate(frame, lazy=True)


def test_station_cells_cell_id_format():
    frame = pd.DataFrame(
        {
            "station_id": ["naps:1"],
            "site_id": ["naps:1"],
            "source": ["naps"],
            "is_in_toronto": [True],
            "lat_deg": [43.7],
            "lon_deg": [-79.4],
            "cell_id": ["43.7,-79.4"],
        }
    )
    with pytest.raises((pe.SchemaError, pe.SchemaErrors)):
        STATION_CELLS.validate(frame, lazy=True)


# --- INTERIM_RAW -------------------------------------------------------------------------


def interim(**overrides: Any) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "station_id": ["naps:060410", "naps:060410"],
            "source": ["naps", "naps"],
            "dataset": ["naps-hourly-pm25"] * 2,
            "time_utc": [T[0], T[0]],  # repeats are allowed in interim (lossless)
            "pm25_raw_ugm3": [-999.0, -3.0],  # sentinels and negatives are allowed
            "method_code": pd.Series(["184", None], dtype="string"),
        }
    )
    return frame.assign(**overrides)


def test_interim_accepts_raw_values_repeats_and_null_method():
    INTERIM_RAW.validate(interim())


@pytest.mark.parametrize(
    "bad",
    [
        {
            "time_utc": pd.to_datetime(["2024-01-01 00:30", "2024-01-01 01:00"], utc=True)
        },  # off-hour
        {"time_utc": [T[0] + pd.Timedelta(milliseconds=500), T[1]]},  # sub-second
        {"time_utc": pd.to_datetime(["2024-01-01 00:00", "2024-01-01 01:00"])},  # naive
        {"source": ["epa", "epa"]},
        {"station_id": ["060410", "060410"]},
        {"extra": [1, 2]},  # strict
    ],
)
def test_interim_rejects(bad: dict[str, Any]):
    with pytest.raises((pe.SchemaError, pe.SchemaErrors)):
        INTERIM_RAW.validate(interim(**bad), lazy=True)


# --- REGISTRY ----------------------------------------------------------------------------


def registry(**overrides: Any) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "station_id": ["naps:060410"],
            "source": ["naps"],
            "station_name": ["Toronto"],
            "lat_deg": [43.75],
            "lon_deg": [-79.27],
            "first_time_utc": [T[0]],
            "last_time_utc": [T[1]],
            "present_h": [2],
            "is_in_toronto": [True],
            "site_id": ["naps:060410"],
        }
    )
    return frame.assign(**overrides)


def test_registry_accepts_good_row():
    REGISTRY.validate(registry())


@pytest.mark.parametrize(
    "bad",
    [{"lat_deg": [91.0]}, {"present_h": [-1]}, {"site_id": ["site-1"]}, {"extra": [0]}],
)
def test_registry_rejects(bad: dict[str, Any]):
    with pytest.raises((pe.SchemaError, pe.SchemaErrors)):
        REGISTRY.validate(registry(**bad), lazy=True)


def test_registry_requires_unique_station():
    with pytest.raises((pe.SchemaError, pe.SchemaErrors)):
        REGISTRY.validate(pd.concat([registry(), registry()], ignore_index=True), lazy=True)


# --- COMPLETENESS ------------------------------------------------------------------------


def completeness(**overrides: Any) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "unit_kind": ["station"],
            "unit_id": ["naps:060410"],
            "period": ["year"],
            "period_label": ["2024"],
            "period_start_utc": [T[0]],
            "period_end_utc": [T[1]],
            "expected_h": [10],
            "present_h": [8],
            "present_frac": [0.8],
            "longest_gap_h": [2],
            "is_complete": [True],
        }
    )
    return frame.assign(**overrides)


def test_completeness_accepts_good_row():
    COMPLETENESS.validate(completeness())


@pytest.mark.parametrize(
    "bad",
    [
        {"present_frac": [1.2]},
        {"period": ["week"]},
        {"unit_kind": ["sensor"]},
        {"longest_gap_h": [-1]},
    ],
)
def test_completeness_rejects(bad: dict[str, Any]):
    with pytest.raises((pe.SchemaError, pe.SchemaErrors)):
        COMPLETENESS.validate(completeness(**bad), lazy=True)


# --- CELLS -------------------------------------------------------------------------------


def cells(**overrides: Any) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "cell_id": ["N4360W07940"],
            "row": [436],
            "col": [-794],
            "lat_min_deg": [43.6],
            "lat_max_deg": [43.7],
            "lon_min_deg": [-79.4],
            "lon_max_deg": [-79.3],
            "lat_center_deg": [43.65],
            "lon_center_deg": [-79.35],
            "city_frac": [0.7],
            "is_in_toronto": [True],
            "n_stations": [2],
            "n_sites": [1],
            "n_sites_active": [1],
            "site_ids": ["naps:060445"],
            "coverage_class": ["1"],
        }
    )
    return frame.assign(**overrides)


def test_cells_accepts_good_row():
    CELLS.validate(cells())


@pytest.mark.parametrize(
    "bad",
    [
        {"coverage_class": ["2"]},
        {"city_frac": [1.5]},
        {"cell_id": ["43.6,-79.4"]},
        {"n_sites": [-1]},
        {"extra": [0]},
    ],
)
def test_cells_rejects(bad: dict[str, Any]):
    with pytest.raises((pe.SchemaError, pe.SchemaErrors)):
        CELLS.validate(cells(**bad), lazy=True)
