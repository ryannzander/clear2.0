"""Put stations in cells and report government-site coverage per Toronto cell.

Spec: methodology/grid.md#assign-stations and #coverage-report.
"""

import pandas as pd

from clear.grid.cells import cell_id, cell_index

__all__ = ["STATION_CELL_COLUMNS", "assign_stations", "coverage", "coverage_metrics"]

STATION_CELL_COLUMNS = [
    "station_id",
    "site_id",
    "source",
    "is_in_toronto",
    "lat_deg",
    "lon_deg",
    "cell_id",
]


def _join_sorted(values: "pd.Series[str]") -> str:
    return ",".join(sorted({str(v) for v in values}))


def assign_stations(registry: pd.DataFrame, cells: pd.DataFrame, size_deg: float) -> pd.DataFrame:
    """Give each registry station the ``cell_id`` of the cell containing its point.

    Method: methodology/grid.md#assign-stations

    Parameters
    ----------
    registry : pandas.DataFrame
        Station registry (``station_id``, ``site_id``, ``source``, ``is_in_toronto``, ``lat_deg``,
        ``lon_deg``).
    cells : pandas.DataFrame
        Built cells (``cell_id``).
    size_deg : float
        Cell size used to build ``cells``.

    Returns
    -------
    pandas.DataFrame
        ``STATION_CELL_COLUMNS``; ``cell_id`` is null for stations outside the built cells.
    """
    rows = cell_index(registry["lat_deg"], size_deg)
    cols = cell_index(registry["lon_deg"], size_deg)
    ids = pd.Series(
        [cell_id(int(r), int(c), size_deg) for r, c in zip(rows, cols, strict=True)],
        index=registry.index,
    )
    out = registry.assign(cell_id=ids.where(ids.isin(cells["cell_id"])))
    return out[STATION_CELL_COLUMNS].reset_index(drop=True)


def coverage(
    cells: pd.DataFrame,
    station_cells: pd.DataFrame,
    registry: pd.DataFrame,
    *,
    active_since: pd.Timestamp,
) -> pd.DataFrame:
    """Count stations, sites and active sites per cell; classify 0 / 1 / >1 active sites.

    Method: methodology/grid.md#coverage-report

    Parameters
    ----------
    cells : pandas.DataFrame
        Cells with ``cell_id``.
    station_cells : pandas.DataFrame
        Output of :func:`assign_stations`.
    registry : pandas.DataFrame
        ``station_id`` and ``last_time_utc``.
    active_since : pandas.Timestamp
        A site is active if any member has data at or after this time (first training year).

    Returns
    -------
    pandas.DataFrame
        ``cells`` plus ``n_stations``, ``n_sites``, ``n_sites_active``, ``site_ids`` (sorted,
        comma-separated) and ``coverage_class`` (``"0"``, ``"1"``, ``">1"``).
    """
    sc = station_cells.dropna(subset=["cell_id"]).merge(
        registry[["station_id", "last_time_utc"]], on="station_id", how="left"
    )
    active_sites = set(sc.loc[sc["last_time_utc"] >= active_since, "site_id"])
    sc = sc.assign(_active=sc["site_id"].isin(active_sites))
    per_cell = sc.groupby("cell_id").agg(
        n_stations=("station_id", "nunique"),
        n_sites=("site_id", "nunique"),
        site_ids=("site_id", _join_sorted),
    )
    active = sc[sc["_active"]].groupby("cell_id")["site_id"].nunique().rename("n_sites_active")
    out = cells.merge(per_cell, left_on="cell_id", right_index=True, how="left")
    out = out.merge(active, left_on="cell_id", right_index=True, how="left")
    for col in ("n_stations", "n_sites", "n_sites_active"):
        out[col] = out[col].fillna(0).astype("int64")
    out["site_ids"] = out["site_ids"].fillna("").astype(str)
    out["coverage_class"] = out["n_sites_active"].map(
        lambda n: "0" if n == 0 else ("1" if n == 1 else ">1")
    )
    return out


def coverage_metrics(cells: pd.DataFrame, *, cell_size_deg: float) -> dict[str, object]:
    """Summarise :func:`coverage` for the Toronto cells (EXP-002).

    Method: methodology/grid.md#coverage-report

    Parameters
    ----------
    cells : pandas.DataFrame
        Output of :func:`coverage` with ``is_in_toronto``.
    cell_size_deg : float
        Cell size, reported with the counts.

    Returns
    -------
    dict
        Cells built, Toronto cells, and Toronto cells with 0 / 1 / >1 active sites and with
        any site ever.
    """
    toronto = cells[cells["is_in_toronto"]]
    counts = toronto["coverage_class"].value_counts()
    return {
        "cell_size_deg": cell_size_deg,
        "cells_built": len(cells),
        "toronto_cells": len(toronto),
        "toronto_cells_with_0_active_sites": int(counts.get("0", 0)),
        "toronto_cells_with_1_active_site": int(counts.get("1", 0)),
        "toronto_cells_with_2plus_active_sites": int(counts.get(">1", 0)),
        "toronto_cells_with_any_site_ever": int((toronto["n_sites"] > 0).sum()),
    }
