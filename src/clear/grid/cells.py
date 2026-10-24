"""Build 0.1° cells over Toronto and measure how much of each lies in the City.

Spec: methodology/grid.md#build-cells and #select-toronto-cells (ADR 0006).
"""

import math
from pathlib import Path

import numpy as np
import pandas as pd
from pydantic import ConfigDict, Field
from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry

from clear.config import ConfigModel, load_config
from clear.geo import Bounds

__all__ = [
    "CELL_COLUMNS",
    "TorontoGridConfig",
    "build_cells",
    "cell_id",
    "cell_index",
    "city_fraction",
    "load_toronto_grid_config",
]

CELL_COLUMNS = [
    "cell_id",
    "row",
    "col",
    "lat_min_deg",
    "lat_max_deg",
    "lon_min_deg",
    "lon_max_deg",
    "lat_center_deg",
    "lon_center_deg",
]
# Cell edges are k * size; rounding to this many decimals removes float noise (k * 0.1).
_EDGE_DECIMALS = 9


class TorontoGridConfig(ConfigModel):
    """``toronto_grid`` block of ``config/grid.yaml``.

    Method: methodology/grid.md#constants
    """

    cell_size_deg: float = Field(gt=0.0, le=10.0)
    min_city_frac: float = Field(ge=0.0, lt=1.0)


class _GridFile(ConfigModel):
    # clear.viz.maps validates the `domain` block of the same file.
    model_config = ConfigDict(extra="ignore", frozen=True)

    toronto_grid: TorontoGridConfig


def load_toronto_grid_config(*, directory: Path | None = None) -> TorontoGridConfig:
    """Load the ``toronto_grid`` block of ``config/grid.yaml``.

    Method: methodology/grid.md#constants

    Parameters
    ----------
    directory : Path, optional
        Alternative config directory (tests).

    Returns
    -------
    TorontoGridConfig
        Cell size and Toronto-cell rule.
    """
    return load_config("grid", _GridFile, directory=directory).toronto_grid


def cell_index(value_deg: "pd.Series[float] | np.ndarray", size_deg: float) -> np.ndarray:
    """Return floor(value / size) as int64: the row (lat) or column (lon) of a cell.

    Method: methodology/grid.md#assign-stations

    A point on an edge belongs to the cell north/east of it. The small tolerance keeps a
    value that is an exact multiple (e.g. 43.7 / 0.1 = 436.99999...) on its own edge.

    Parameters
    ----------
    value_deg : pandas.Series or numpy.ndarray of float
        Latitudes (for rows) or longitudes (for columns), degrees.
    size_deg : float
        Cell size.

    Returns
    -------
    numpy.ndarray of int64
        Row or column index per value.
    """
    ratio = np.asarray(value_deg, dtype="float64") / size_deg
    return np.floor(np.round(ratio, _EDGE_DECIMALS)).astype("int64")


def cell_id(row: int, col: int, size_deg: float) -> str:
    """Name a cell by its south-west corner in hundredths of a degree (CSG-1 style).

    Method: methodology/grid.md#build-cells

    Examples
    --------
    >>> cell_id(436, -795, 0.1)
    'N4360W07950'
    """
    lat = round(row * size_deg * 100)
    lon = round(col * size_deg * 100)
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    return f"{ns}{abs(lat):04d}{ew}{abs(lon):05d}"


def build_cells(bounds: Bounds, size_deg: float) -> pd.DataFrame:
    """Cut cells with edges on multiples of ``size_deg`` covering ``bounds`` (snapped out).

    Method: methodology/grid.md#build-cells

    Parameters
    ----------
    bounds : Bounds
        Lon/lat box to cover (the City's bounds).
    size_deg : float
        Cell size (``config/grid.yaml: toronto_grid.cell_size_deg``).

    Returns
    -------
    pandas.DataFrame
        ``CELL_COLUMNS``, one row per cell, rows south to north then columns west to east.
    """
    row0, row1 = (
        cell_index(np.array([bounds.lat_min_deg]), size_deg)[0],
        math.ceil(round(bounds.lat_max_deg / size_deg, _EDGE_DECIMALS)),
    )
    col0, col1 = (
        cell_index(np.array([bounds.lon_min_deg]), size_deg)[0],
        math.ceil(round(bounds.lon_max_deg / size_deg, _EDGE_DECIMALS)),
    )
    records: list[tuple[object, ...]] = []
    for row in range(int(row0), int(row1)):
        for col in range(int(col0), int(col1)):
            lat0 = round(row * size_deg, _EDGE_DECIMALS)
            lon0 = round(col * size_deg, _EDGE_DECIMALS)
            lat1 = round((row + 1) * size_deg, _EDGE_DECIMALS)
            lon1 = round((col + 1) * size_deg, _EDGE_DECIMALS)
            records.append(
                (
                    cell_id(row, col, size_deg),
                    row,
                    col,
                    lat0,
                    lat1,
                    lon0,
                    lon1,
                    (lat0 + lat1) / 2,
                    (lon0 + lon1) / 2,
                )
            )
    return pd.DataFrame(records, columns=CELL_COLUMNS).astype({"row": "int64", "col": "int64"})


def city_fraction(cells: pd.DataFrame, city: BaseGeometry) -> "pd.Series[float]":
    """Return area(cell ∩ City) / area(cell) per cell, computed in lon/lat.

    Method: methodology/grid.md#select-toronto-cells

    Parameters
    ----------
    cells : pandas.DataFrame
        Output of :func:`build_cells`.
    city : shapely geometry
        The City polygon (lon/lat).

    Returns
    -------
    pandas.Series of float
        In [0, 1], same index as ``cells``.
    """
    fracs: list[float] = []
    edges = cells[["lon_min_deg", "lat_min_deg", "lon_max_deg", "lat_max_deg"]].to_numpy(
        dtype="float64"
    )
    for lon0, lat0, lon1, lat1 in edges.tolist():
        cell = Polygon([(lon0, lat0), (lon1, lat0), (lon1, lat1), (lon0, lat1)])
        fracs.append(min(1.0, max(0.0, float(city.intersection(cell).area) / float(cell.area))))
    return pd.Series(fracs, index=cells.index, name="city_frac", dtype="float64")
