"""pandera schemas of the stations part's outputs.

Spec: methodology/stations.md#outputs.
"""

import pandas as pd
import pandera.pandas as pa

from clear.schemas.common import concentration_column, is_utc, non_negative, time_utc_column

__all__ = ["COMPLETENESS", "HOURLY", "INTERIM_RAW", "MERGED", "REGISTRY"]

# pyright ignores in this module: pandera leaves its built-in Check methods untyped.
_SOURCES = ["naps", "mecp", "airnow"]
_ID = r"^(naps|mecp|airnow):\d+$"


def _source() -> pa.Column:
    return pa.Column(str, pa.Check.isin(_SOURCES))  # pyright: ignore[reportUnknownMemberType]


def _station_id() -> pa.Column:
    return pa.Column(str, pa.Check.str_matches(_ID))  # pyright: ignore[reportUnknownMemberType]


def _frac() -> pa.Column:
    return pa.Column(float, pa.Check.in_range(0.0, 1.0))  # pyright: ignore[reportUnknownMemberType]


def _on_the_hour(series: "pd.Series[pd.Timestamp]") -> bool:
    return bool(series.dt.floor("h").eq(series).all())  # also rejects sub-second parts


def _hourly_time() -> pa.Column:
    """``time_utc`` of an hourly table: tz-aware UTC and on the hour (naming-units-time.md)."""
    return pa.Column(
        checks=[
            pa.Check(is_utc, error="time_utc must be tz-aware UTC"),
            pa.Check(_on_the_hour, error="time_utc must be on the hour"),
        ]
    )


INTERIM_RAW = pa.DataFrameSchema(
    {
        "station_id": _station_id(),
        "source": _source(),
        "dataset": pa.Column(str),
        "time_utc": _hourly_time(),
        "pm25_raw_ugm3": pa.Column(float),  # as published: sentinels, negatives, repeats kept
        "method_code": pa.Column(str, nullable=True),
    },
    strict=True,
)

HOURLY = pa.DataFrameSchema(
    {
        "station_id": _station_id(),
        "source": _source(),
        "time_utc": _hourly_time(),
        "pm25_ugm3": concentration_column(nullable=False),
    },
    unique=["station_id", "time_utc"],
    strict=True,
)

REGISTRY = pa.DataFrameSchema(
    {
        "station_id": _station_id(),
        "source": _source(),
        "station_name": pa.Column(str, nullable=True),
        "lat_deg": pa.Column(float, pa.Check.in_range(-90.0, 90.0)),  # pyright: ignore[reportUnknownMemberType]
        "lon_deg": pa.Column(float, pa.Check.in_range(-180.0, 180.0)),  # pyright: ignore[reportUnknownMemberType]
        "first_time_utc": time_utc_column(),
        "last_time_utc": time_utc_column(),
        "present_h": pa.Column(int, non_negative()),
        "is_in_toronto": pa.Column(bool),
        "site_id": _station_id(),
    },
    unique=["station_id"],
    strict=True,
)

COMPLETENESS = pa.DataFrameSchema(
    {
        "unit_kind": pa.Column(str, pa.Check.isin(["station", "site"])),  # pyright: ignore[reportUnknownMemberType]
        "unit_id": _station_id(),
        "period": pa.Column(str, pa.Check.isin(["year", "month", "split"])),  # pyright: ignore[reportUnknownMemberType]
        "period_label": pa.Column(str),
        "period_start_utc": time_utc_column(),
        "period_end_utc": time_utc_column(),
        "expected_h": pa.Column(int, non_negative()),
        "present_h": pa.Column(int, non_negative()),
        "present_frac": _frac(),
        "longest_gap_h": pa.Column(int, non_negative()),
        "is_complete": pa.Column(bool),
    },
    unique=["unit_kind", "unit_id", "period", "period_label"],
    strict=True,
)

MERGED = pa.DataFrameSchema(
    {
        "site_id": _station_id(),
        "time_utc": _hourly_time(),
        "pm25_ugm3": concentration_column(nullable=False),
        "source": _source(),
    },
    unique=["site_id", "time_utc"],
    strict=True,
)
