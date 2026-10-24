"""Value QC: sentinels and negatives become missing; repeats per station-hour are averaged.

Spec: methodology/stations.md#clean-values (ADR 0007). Runs on the lossless interim tables.
"""

from collections.abc import Sequence

import pandas as pd

from clear.stations.settings import StationsConfig

__all__ = ["HOURLY_COLUMNS", "apply_qc", "clean_values"]

HOURLY_COLUMNS = ["station_id", "source", "time_utc", "pm25_ugm3"]


def clean_values(
    values: "pd.Series[float]", *, sentinels: Sequence[float], negative_is_missing: bool
) -> "pd.Series[float]":
    """Turn sentinel codes (and negatives, if configured) into NaN.

    Method: methodology/stations.md#clean-values

    Parameters
    ----------
    values : pandas.Series of float
        Raw concentrations in µg/m³ (already numeric).
    sentinels : sequence of float
        Missing-value codes of the source (``config/stations.yaml``).
    negative_is_missing : bool
        If True, every value below zero becomes NaN (ADR 0007).

    Returns
    -------
    pandas.Series of float
        Same index; invalid values are NaN.
    """
    out = values.astype("float64")
    bad = out.isin(list(sentinels))
    if negative_is_missing:
        bad |= out < 0
    return out.mask(bad)


def apply_qc(raw: pd.DataFrame, config: StationsConfig) -> pd.DataFrame:
    """Apply ADR 0007 to raw station-hours: clean values, drop missing, average repeats.

    Method: methodology/stations.md#clean-values

    Parameters
    ----------
    raw : pandas.DataFrame
        Interim rows (``station_id``, ``source``, ``time_utc``, ``pm25_raw_ugm3``), possibly
        several per station-hour (NAPS method codes, MECP duplicate rows).
    config : StationsConfig
        Sentinels per source and ``negative_is_missing``.

    Returns
    -------
    pandas.DataFrame
        ``HOURLY_COLUMNS``, one row per station-hour with a valid value.
    """
    parts: list[pd.DataFrame] = []
    for source, group in raw.groupby("source", sort=True):
        cleaned = clean_values(
            group["pm25_raw_ugm3"],
            sentinels=config.source(str(source)).sentinels,
            negative_is_missing=config.negative_is_missing,
        )
        parts.append(group.assign(pm25_ugm3=cleaned).dropna(subset=["pm25_ugm3"]))
    if not parts:
        return pd.DataFrame(columns=HOURLY_COLUMNS)
    valid = pd.concat(parts, ignore_index=True)
    means = valid.groupby(["station_id", "source", "time_utc"], sort=True)["pm25_ugm3"].mean()
    return means.reset_index()[HOURLY_COLUMNS]
