"""Years active and missing data per station and per site.

Spec: methodology/stations.md#completeness (ADR 0001 splits, ADR 0004 threshold).
"""

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np
import pandas as pd

from clear.stations.settings import SplitYears

__all__ = ["COMPLETENESS_COLUMNS", "Period", "completeness", "hour_index", "periods_for"]

COMPLETENESS_COLUMNS = [
    "unit_kind",
    "unit_id",
    "period",
    "period_label",
    "period_start_utc",
    "period_end_utc",
    "expected_h",
    "present_h",
    "present_frac",
    "longest_gap_h",
    "is_complete",
]
_EPOCH = pd.Timestamp("1970-01-01", tz="UTC")
_HOUR = pd.Timedelta(hours=1)


@dataclass(frozen=True)
class Period:
    """A half-open UTC interval ``[start_utc, end_utc)`` with a kind and a label.

    Method: methodology/stations.md#completeness
    """

    period: str  # "year" | "month" | "split"
    label: str
    start_utc: pd.Timestamp
    end_utc: pd.Timestamp


def hour_index(time_utc: "pd.Series[pd.Timestamp]") -> np.ndarray:
    """Return whole hours since 1970-01-01 UTC as int64.

    Method: methodology/stations.md#completeness
    """
    return ((time_utc - _EPOCH) // _HOUR).to_numpy(dtype="int64")


def periods_for(
    first_utc: pd.Timestamp, last_utc: pd.Timestamp, splits: Mapping[str, SplitYears]
) -> list[Period]:
    """Return the calendar years and months spanning the data, plus the splits.

    Method: methodology/stations.md#completeness

    Parameters
    ----------
    first_utc, last_utc : pandas.Timestamp
        First and last hour (UTC) of the unit's data; whole years are covered.
    splits : mapping of str to SplitYears
        ``config/splits.yaml``.

    Returns
    -------
    list of Period
        Years, then months, then splits.
    """
    out: list[Period] = []
    for year in range(first_utc.year, last_utc.year + 1):
        start = pd.Timestamp(year=year, month=1, day=1, tz="UTC")
        out.append(Period("year", str(year), start, start + pd.DateOffset(years=1)))
        for month in range(1, 13):
            m_start = pd.Timestamp(year=year, month=month, day=1, tz="UTC")
            out.append(
                Period("month", f"{year}-{month:02d}", m_start, m_start + pd.DateOffset(months=1))
            )
    for name, years in splits.items():
        start = pd.Timestamp(year=years.first_year, month=1, day=1, tz="UTC")
        end = pd.Timestamp(year=years.last_year + 1, month=1, day=1, tz="UTC")
        out.append(Period("split", name, start, end))
    return out


def _period_stats(hours: np.ndarray, start_h: int, end_h: int) -> tuple[int, int]:
    """Return (hours present, longest run of missing hours) in ``[start_h, end_h)``."""
    lo, hi = np.searchsorted(hours, [start_h, end_h])
    present = hours[lo:hi]
    edges = np.concatenate(([start_h - 1], present, [end_h]))
    longest_gap = int((np.diff(edges) - 1).max())
    return int(present.size), longest_gap


def completeness(
    series: pd.DataFrame,
    *,
    unit_kind: str,
    unit_column: str,
    splits: Mapping[str, SplitYears],
    coverage_end_utc: pd.Timestamp,
    min_frac: float,
) -> pd.DataFrame:
    """Per unit and period: expected and present hours, fraction, longest gap, 75% flag.

    Method: methodology/stations.md#completeness

    Periods run from the unit's first data year to its last; splits are always reported.
    ``expected_h`` stops at ``coverage_end_utc`` (no source holds data after it), so the
    partial final year is not counted as missing.

    Parameters
    ----------
    series : pandas.DataFrame
        Valid hours: ``unit_column`` and ``time_utc`` (one row per unit-hour).
    unit_kind : str
        ``"station"`` or ``"site"``, written to ``unit_kind``.
    unit_column : str
        Column holding the unit id (``station_id`` or ``site_id``).
    splits : mapping of str to SplitYears
        ``config/splits.yaml``.
    coverage_end_utc : pandas.Timestamp
        Exclusive end of all data (last hour any source holds + 1 h).
    min_frac : float
        ``config/stations.yaml: completeness_min_frac`` (ADR 0004).

    Returns
    -------
    pandas.DataFrame
        ``COMPLETENESS_COLUMNS``; periods with no expected hours are left out.
    """
    end_h = int(hour_index(pd.Series([coverage_end_utc]))[0])
    rows: list[tuple[object, ...]] = []
    for unit_id, group in series.groupby(unit_column, sort=True):
        hours = np.unique(hour_index(group["time_utc"]))
        first = _EPOCH + pd.Timedelta(hours=int(hours[0]))
        last = _EPOCH + pd.Timedelta(hours=int(hours[-1]))
        for p in periods_for(first, last, splits):
            start_h = int(hour_index(pd.Series([p.start_utc]))[0])
            stop_h = min(int(hour_index(pd.Series([p.end_utc]))[0]), end_h)
            if stop_h <= start_h:
                continue
            present, gap = _period_stats(hours, start_h, stop_h)
            expected = stop_h - start_h
            frac = present / expected
            rows.append(
                (
                    unit_kind,
                    str(unit_id),
                    p.period,
                    p.label,
                    p.start_utc,
                    _EPOCH + pd.Timedelta(hours=stop_h),
                    expected,
                    present,
                    frac,
                    gap,
                    frac >= min_frac,
                )
            )
    out = pd.DataFrame(rows, columns=COMPLETENESS_COLUMNS)
    for col in ("period_start_utc", "period_end_utc"):
        out[col] = pd.to_datetime(out[col], utc=True)
    return out.astype(
        {
            "expected_h": "int64",
            "present_h": "int64",
            "longest_gap_h": "int64",
            "present_frac": "float64",
            "is_complete": "bool",
        }
    )
