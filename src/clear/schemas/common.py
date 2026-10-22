"""Reusable pandera pieces: the ``time_utc`` column and concentration columns.

Example::

    import pandera.pandas as pa
    from clear.schemas import concentration_column, time_utc_column

    station_hourly = pa.DataFrameSchema(
        {"time_utc": time_utc_column(), "station_id": pa.Column(str),
         "pm25_ugm3": concentration_column()},
        unique=["time_utc", "station_id"],
    )
"""

import pandas as pd
import pandera.pandas as pa

TIME_UTC = "time_utc"


def is_utc(series: "pd.Series[pd.Timestamp]") -> bool:
    """Return True if ``series`` is tz-aware with zone UTC.

    Method: docs/standards/naming-units-time.md#time-rules

    Parameters
    ----------
    series : pandas.Series of datetime64
        Timestamps to check. Shape ``(n,)``.

    Returns
    -------
    bool
        True for dtype ``datetime64[*, UTC]``; False for naive or other zones.
    """
    dtype = series.dtype
    return isinstance(dtype, pd.DatetimeTZDtype) and str(dtype.tz) == "UTC"


def time_utc_column(*, nullable: bool = False, unique: bool = False) -> pa.Column:
    """Return the canonical ``time_utc`` column: tz-aware UTC timestamps.

    Method: docs/standards/naming-units-time.md#time-rules

    Any datetime resolution is accepted; naive or non-UTC timestamps fail validation.

    Parameters
    ----------
    nullable : bool, default False
        Allow missing timestamps.
    unique : bool, default False
        Require every timestamp to be distinct.

    Returns
    -------
    pandera.Column
        Column spec to place under the key ``time_utc``.
    """
    return pa.Column(
        checks=pa.Check(is_utc, error=f"{TIME_UTC} must be tz-aware UTC"),
        nullable=nullable,
        unique=unique,
    )


def non_negative() -> pa.Check:
    """Return a check that values are >= 0 (concentrations, counts, distances).

    Method: docs/standards/code.md#contract-pandera

    Returns
    -------
    pandera.Check
        Element-wise ``>= 0`` check; NaN handling is left to the column's ``nullable``.
    """
    # pandera leaves the **kwargs of built-in checks untyped.
    return pa.Check.ge(0, error="value must be non-negative")  # pyright: ignore[reportUnknownMemberType]


def concentration_column(*, nullable: bool = True) -> pa.Column:
    """Return a float concentration column (e.g. ``pm25_ugm3``) that must be >= 0.

    Method: docs/standards/code.md#contract-pandera

    Missing hours are allowed by default (``nullable=True``) because monitors drop out;
    completeness rules belong to the methodology spec, not to the type.

    Parameters
    ----------
    nullable : bool, default True
        Allow NaN (missing) values.

    Returns
    -------
    pandera.Column
        Float column spec, unit given by the column name (e.g. µg/m³ for ``_ugm3``).
    """
    return pa.Column(float, checks=non_negative(), nullable=nullable)
