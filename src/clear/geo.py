"""Shared geography: lon/lat boxes and the City of Toronto boundary.

Infrastructure used by several parts (stations, grid). "Toronto" = the City of Toronto
polygon (decisions/0002-toronto-city-boundary.md). Reading the shapefile needs ``geopandas``
(``uv sync --group geo``); the geometry tests need only ``shapely``.
"""

import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import numpy as np
import pandas as pd
import shapely
from shapely.geometry.base import BaseGeometry

from clear.paths import data_dir

__all__ = ["CITY_BOUNDARY_FILE", "Bounds", "city_bounds", "in_city", "read_city_boundary"]

# Path under data/raw of the boundary (knowledge/data/toronto-city-boundary.md).
CITY_BOUNDARY_FILE = Path("City of Toronto boundary") / "toronto-boundary-wgs84.zip"


@dataclass(frozen=True)
class Bounds:
    """A lon/lat box in degrees (inclusive edges).

    Method: methodology/stations.md#read-sources
    """

    lon_min_deg: float
    lat_min_deg: float
    lon_max_deg: float
    lat_max_deg: float

    def expanded(self, margin_deg: float) -> "Bounds":
        """Return the box grown by ``margin_deg`` on every side.

        Method: methodology/stations.md#read-sources
        """
        return Bounds(
            self.lon_min_deg - margin_deg,
            self.lat_min_deg - margin_deg,
            self.lon_max_deg + margin_deg,
            self.lat_max_deg + margin_deg,
        )

    def contains(
        self, lat_deg: "pd.Series[float]", lon_deg: "pd.Series[float]"
    ) -> "pd.Series[bool]":
        """Return True where the point lies inside the box.

        Method: methodology/stations.md#read-sources

        Parameters
        ----------
        lat_deg, lon_deg : pandas.Series of float
            Point coordinates, same index.

        Returns
        -------
        pandas.Series of bool
            Same index as ``lat_deg``.
        """
        return lat_deg.between(self.lat_min_deg, self.lat_max_deg) & lon_deg.between(
            self.lon_min_deg, self.lon_max_deg
        )


def read_city_boundary(path: Path | None = None) -> BaseGeometry:
    """Return the City of Toronto polygon in WGS 84 lon/lat.

    Method: methodology/stations.md#select-toronto-stations

    Parameters
    ----------
    path : Path, optional
        The boundary zip; default ``data/raw/`` + :data:`CITY_BOUNDARY_FILE`.

    Returns
    -------
    shapely geometry
        Union of the file's features (one polygon), x = lon, y = lat.

    Raises
    ------
    ModuleNotFoundError
        If geopandas is not installed (``uv sync --group geo``).
    ValueError
        If the file holds no features, no CRS, or a CRS other than geographic WGS 84.
    """
    zip_path = path or data_dir() / "raw" / CITY_BOUNDARY_FILE
    # geopandas is optional (geo group, absent in CI) and only used to read the shapefile.
    gpd = importlib.import_module("geopandas")
    frame = gpd.read_file(f"zip://{zip_path.as_posix()}")
    crs = frame.crs
    # The .prj is geographic WGS 84 without an EPSG code (boundary card), so match by name.
    if crs is None or not (crs.is_geographic and crs.name == "WGS 84"):
        raise ValueError(f"{zip_path}: expected geographic WGS 84, got {crs}")
    if frame.empty:
        raise ValueError(f"{zip_path}: no features")
    return cast(BaseGeometry, frame.geometry.union_all())


def city_bounds(city: BaseGeometry) -> Bounds:
    """Return the lon/lat bounding box of ``city``.

    Method: methodology/stations.md#read-sources

    Parameters
    ----------
    city : shapely geometry
        The City polygon (lon/lat).

    Returns
    -------
    Bounds
        Its minimum and maximum lon and lat.
    """
    lon_min, lat_min, lon_max, lat_max = (float(v) for v in city.bounds)
    return Bounds(lon_min, lat_min, lon_max, lat_max)


def in_city(
    city: BaseGeometry, lat_deg: "pd.Series[float]", lon_deg: "pd.Series[float]"
) -> "pd.Series[bool]":
    """Return True where a point lies in or on the City polygon (ADR 0002).

    Method: methodology/stations.md#select-toronto-stations

    Parameters
    ----------
    city : shapely geometry
        The City polygon (lon/lat).
    lat_deg, lon_deg : pandas.Series of float
        Point coordinates, same index.

    Returns
    -------
    pandas.Series of bool
        Same index as ``lat_deg``.
    """
    inside = shapely.intersects_xy(
        city, lon_deg.to_numpy(dtype="float64"), lat_deg.to_numpy(dtype="float64")
    )
    return cast("pd.Series[bool]", pd.Series(np.asarray(inside, dtype=bool), index=lat_deg.index))
