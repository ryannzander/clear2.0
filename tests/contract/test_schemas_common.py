import numpy as np
import pandas as pd
import pandera.errors
import pandera.pandas as pa
import pytest

from clear.schemas import concentration_column, time_utc_column

SCHEMA = pa.DataFrameSchema(
    {"time_utc": time_utc_column(unique=True), "pm25_ugm3": concentration_column()}
)


def frame(times, values) -> pd.DataFrame:
    return pd.DataFrame({"time_utc": times, "pm25_ugm3": values})


def utc_hours(n: int) -> pd.DatetimeIndex:
    return pd.date_range("2024-01-01", periods=n, freq="h", tz="UTC")


def test_valid_frame_passes_and_missing_hours_are_allowed():
    SCHEMA.validate(frame(utc_hours(3), [1.0, np.nan, 3.5]))


def test_naive_timestamps_fail():
    with pytest.raises(pandera.errors.SchemaError):
        SCHEMA.validate(frame(pd.date_range("2024-01-01", periods=2, freq="h"), [1.0, 2.0]))


def test_non_utc_timezone_fails():
    toronto = pd.date_range("2024-01-01", periods=2, freq="h", tz="America/Toronto")
    with pytest.raises(pandera.errors.SchemaError):
        SCHEMA.validate(frame(toronto, [1.0, 2.0]))


def test_negative_concentration_fails():
    with pytest.raises(pandera.errors.SchemaError):
        SCHEMA.validate(frame(utc_hours(2), [1.0, -0.1]))


def test_duplicate_times_fail_when_unique():
    times = pd.DatetimeIndex([utc_hours(1)[0], utc_hours(1)[0]])
    with pytest.raises(pandera.errors.SchemaError):
        SCHEMA.validate(frame(times, [1.0, 2.0]))
