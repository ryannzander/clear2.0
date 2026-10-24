"""`merged` and `separate` series for the station-overlap A/B test.

Spec: methodology/stations.md#combine-sources (ADR 0003).
"""

from collections.abc import Sequence

import pandas as pd

__all__ = ["MERGED_COLUMNS", "merged_series"]

MERGED_COLUMNS = ["site_id", "time_utc", "pm25_ugm3", "source"]


def merged_series(
    hourly: pd.DataFrame, registry: pd.DataFrame, *, source_priority: Sequence[str]
) -> pd.DataFrame:
    """One series per site: each hour takes the highest-priority source with a value.

    Method: methodology/stations.md#combine-sources

    Stations of the same source within one site are averaged for that hour. The
    ``separate`` mode is the hourly table itself (one series per ``station_id``).

    Parameters
    ----------
    hourly : pandas.DataFrame
        Valid station-hours (``station_id``, ``source``, ``time_utc``, ``pm25_ugm3``).
    registry : pandas.DataFrame
        ``station_id`` and ``site_id``.
    source_priority : sequence of str
        Source keys, best first (``config/stations.yaml``).

    Returns
    -------
    pandas.DataFrame
        ``MERGED_COLUMNS``, unique on (``site_id``, ``time_utc``).
    """
    rank = {s: k for k, s in enumerate(source_priority)}
    frame = hourly.merge(registry[["station_id", "site_id"]], on="station_id", how="inner")
    frame["_rank"] = frame["source"].map(lambda s: rank.get(str(s), len(rank)))
    best = frame.groupby(["site_id", "time_utc"])["_rank"].transform("min")
    frame = frame[frame["_rank"] == best]
    out = frame.groupby(["site_id", "time_utc", "source"])["pm25_ugm3"].mean().reset_index()
    return out[MERGED_COLUMNS].sort_values(["site_id", "time_utc"]).reset_index(drop=True)
