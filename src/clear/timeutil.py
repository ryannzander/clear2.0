"""Normalize source timestamps to tz-aware UTC.

Rule (docs/standards/naming-units-time.md#time-rules): every stored timestamp is tz-aware
UTC in a column named ``time_utc``. Hourly values are labelled by the START of their hour
(hour-beginning; decisions/0005-time-utc-hour-beginning.md). Sources differ: some report
local standard time all year, some local clock time with DST, some label hours by their END.
Each source's convention is verified and written in its data card
(``knowledge/data/<dataset>.md``, field ``time_convention``) before ingest code calls
:func:`to_utc` with the matching arguments. Never guess a convention here.
"""

from typing import Literal

import pandas as pd

__all__ = ["lst_zone", "to_utc"]

# An hour-ending label marks the end of a one-hour interval; the start is one hour earlier.
_ONE_HOUR = pd.Timedelta(hours=1)


def lst_zone(utc_offset_h: int) -> str:
    """Return the fixed-offset IANA zone for a local *standard* time (no DST).

    Method: docs/standards/naming-units-time.md#dst-pitfalls

    Parameters
    ----------
    utc_offset_h : int
        Offset from UTC in hours, e.g. ``-5`` for Eastern Standard Time.

    Returns
    -------
    str
        e.g. ``"Etc/GMT+5"`` for ``-5``. (IANA ``Etc/`` zones invert the sign.)
    """
    if utc_offset_h == 0:
        return "Etc/UTC"
    sign = "+" if utc_offset_h < 0 else "-"
    return f"Etc/GMT{sign}{abs(utc_offset_h)}"


def to_utc(
    local_naive: "pd.Series[pd.Timestamp]",
    *,
    source_tz: str,
    hour_ending: bool = False,
    ambiguous: Literal["raise", "infer", "NaT"] = "raise",
    nonexistent: Literal["raise", "NaT"] = "raise",
) -> "pd.Series[pd.Timestamp]":
    """Convert naive source timestamps to tz-aware UTC, hour-beginning.

    Method: docs/standards/naming-units-time.md#hour-labelling

    Hour-beginning output is the ``time_utc`` convention (ADR 0005).

    Parameters
    ----------
    local_naive : pandas.Series of datetime64 (naive)
        Timestamps exactly as the source reports them. Shape ``(n,)``.
    source_tz : str
        IANA zone the naive values are in: a DST zone such as ``"America/Toronto"`` for
        clock time, or a fixed offset such as ``lst_zone(-5)`` for local standard time.
    hour_ending : bool, default False
        True if the source labels each hourly value by the END of its hour; the result is
        shifted back one hour so labels mark the start.
    ambiguous : {"raise", "infer", "NaT"}, default "raise"
        Handling of repeated fall-back hours in DST zones. ``"infer"`` needs sorted input.
    nonexistent : {"raise", "NaT"}, default "raise"
        Handling of skipped spring-forward hours in DST zones.

    Returns
    -------
    pandas.Series of datetime64[UTC]
        Same index and shape as the input, tz-aware UTC, hour-beginning.

    Raises
    ------
    TypeError
        If the input is not datetime-like.
    ValueError
        If the input is already tz-aware (convert those with ``.dt.tz_convert("UTC")``);
        or, from pandas (>= 3), if a timestamp falls in a spring-forward gap with
        ``nonexistent="raise"`` or in a repeated fall-back hour with ``ambiguous="raise"``.
    """
    if not pd.api.types.is_datetime64_any_dtype(local_naive):
        raise TypeError(f"local_naive must be a datetime64 Series, got dtype {local_naive.dtype}")
    if isinstance(local_naive.dtype, pd.DatetimeTZDtype):
        raise ValueError(
            f"timestamps are already tz-aware ({local_naive.dtype}); use .dt.tz_convert('UTC')"
        )
    localized = local_naive.dt.tz_localize(source_tz, ambiguous=ambiguous, nonexistent=nonexistent)
    utc = localized.dt.tz_convert("UTC")
    return utc - _ONE_HOUR if hour_ending else utc
