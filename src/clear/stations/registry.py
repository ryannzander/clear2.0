"""Station registry and the cross-network site crosswalk.

Spec: methodology/stations.md#build-the-registry and #link-sites (ADR 0008).
"""

from collections.abc import Sequence

import numpy as np
import pandas as pd

__all__ = ["build_registry", "haversine_m", "link_sites"]

# Mean Earth radius (IUGG), metres: converts great-circle angles to distances.
_EARTH_RADIUS_M = 6_371_008.8


def build_registry(stations: pd.DataFrame, hourly: pd.DataFrame) -> pd.DataFrame:
    """Add first/last hour with data and hours present to the station metadata.

    Method: methodology/stations.md#build-the-registry

    Parameters
    ----------
    stations : pandas.DataFrame
        ``station_id``, ``source``, ``station_name``, ``lat_deg``, ``lon_deg``.
    hourly : pandas.DataFrame
        Valid station-hours (``station_id``, ``time_utc``).

    Returns
    -------
    pandas.DataFrame
        One row per station that has at least one valid hour, plus ``first_time_utc``,
        ``last_time_utc`` and ``present_h``; sorted by ``station_id``.
    """
    span = hourly.groupby("station_id")["time_utc"].agg(["min", "max", "count"])
    span.columns = ["first_time_utc", "last_time_utc", "present_h"]
    registry = stations.drop_duplicates("station_id").merge(
        span, left_on="station_id", right_index=True, how="inner"
    )
    registry["present_h"] = registry["present_h"].astype("int64")
    return registry.sort_values("station_id").reset_index(drop=True)


def haversine_m(
    lat1_deg: np.ndarray, lon1_deg: np.ndarray, lat2_deg: np.ndarray, lon2_deg: np.ndarray
) -> np.ndarray:
    """Great-circle distance in metres (broadcasting).

    Method: decisions/0008-site-crosswalk-500m.md#decision

    Parameters
    ----------
    lat1_deg, lon1_deg, lat2_deg, lon2_deg : numpy.ndarray
        Coordinates of the two points, broadcastable shapes.

    Returns
    -------
    numpy.ndarray
        Distances in metres, broadcast shape.
    """
    lat1, lon1, lat2, lon2 = (np.radians(a) for a in (lat1_deg, lon1_deg, lat2_deg, lon2_deg))
    a = (
        np.sin((lat2 - lat1) / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    )
    return 2 * _EARTH_RADIUS_M * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def link_sites(
    registry: pd.DataFrame, *, max_distance_m: float, source_priority: Sequence[str]
) -> "pd.Series[str]":
    """Group stations within ``max_distance_m`` (single linkage) into sites.

    Method: methodology/stations.md#link-sites

    ``site_id`` is the ``station_id`` of the member from the highest-priority source, then
    the one with the latest last hour, then the lowest id (ADR 0008).

    Parameters
    ----------
    registry : pandas.DataFrame
        ``station_id``, ``source``, ``lat_deg``, ``lon_deg``, ``last_time_utc``.
    max_distance_m : float
        Linking distance (``config/stations.yaml: crosswalk_max_distance_m``).
    source_priority : sequence of str
        Source keys, best first.

    Returns
    -------
    pandas.Series of str
        ``site_id`` per row, same index as ``registry``.
    """
    n = len(registry)
    lat = registry["lat_deg"].to_numpy(dtype="float64")
    lon = registry["lon_deg"].to_numpy(dtype="float64")
    dist = haversine_m(lat[:, None], lon[:, None], lat[None, :], lon[None, :])
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, j in zip(*np.nonzero(np.triu(dist <= max_distance_m, k=1)), strict=True):
        parent[find(int(i))] = find(int(j))
    rank = {s: k for k, s in enumerate(source_priority)}
    order = registry.assign(
        _root=[find(i) for i in range(n)],
        _rank=registry["source"].map(lambda s: rank.get(str(s), len(rank))),
        _last=registry["last_time_utc"],
    ).sort_values(["_root", "_rank", "_last", "station_id"], ascending=[True, True, False, True])
    representative = order.drop_duplicates("_root").set_index("_root")["station_id"]
    roots = pd.Series([find(i) for i in range(n)], index=registry.index)
    return roots.map(representative).astype(str).rename("site_id")
