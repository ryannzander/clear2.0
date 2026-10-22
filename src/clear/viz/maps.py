"""Maps: the one CLEAR projection and the study-domain extent.

The projection is a design token (``tokens.yaml``); the domain is a methodology constant
(``config/grid.yaml``, PROVISIONAL until ``methodology/grid.md``). Figure scripts call
:func:`map_axes` and never build a projection or extent themselves.
Standard: ``docs/standards/figures.md#maps``. Drawing needs ``uv sync --group geo``.
"""

import importlib

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pydantic import Field

from clear.config import ConfigModel, load_config
from clear.viz.tokens import MapProjection, load_tokens

__all__ = ["MapDomain", "map_axes", "map_domain", "map_projection"]

_M_PER_KM = 1000.0


class MapDomain(ConfigModel):
    """Study domain used as the map extent: centre (degrees) and half-width (km).

    Method: docs/standards/figures.md#maps

    PROVISIONAL: values come from ``config/grid.yaml`` until ``methodology/grid.md`` exists.
    """

    provisional: bool
    center_lat_deg: float = Field(ge=-90.0, le=90.0)
    center_lon_deg: float = Field(ge=-180.0, le=180.0)
    half_width_km: float = Field(gt=0.0)


class _GridConfig(ConfigModel):
    domain: MapDomain


def map_projection() -> MapProjection:
    """Return the projection every CLEAR map uses (Lambert Conformal Conic).

    Method: docs/standards/figures.md#maps

    Returns
    -------
    MapProjection
        Central longitude/latitude and standard parallels, in degrees.
    """
    return load_tokens().maps.projection


def map_domain() -> MapDomain:
    """Return the study domain used as the map extent, from ``config/grid.yaml``.

    Method: docs/standards/figures.md#maps

    Returns
    -------
    MapDomain
        Centre (``center_lat_deg``, ``center_lon_deg``) and ``half_width_km``. PROVISIONAL.

    Raises
    ------
    FileNotFoundError
        If ``config/grid.yaml`` is missing.
    pydantic.ValidationError
        If the file has a missing, unknown or out-of-range value.
    """
    return load_config("grid", _GridConfig).domain


def map_axes(fig: Figure, nrows: int = 1, ncols: int = 1, index: int = 1) -> Axes:
    """Add a map panel in the CLEAR projection, zoomed to the study domain.

    Method: docs/standards/figures.md#maps

    The extent is a square, ``2 * half_width_km`` on a side in projected metres, centred
    on the domain centre. Draw lon/lat data with an explicit source transform, e.g.
    ``transform=cartopy.crs.PlateCarree()``.

    Parameters
    ----------
    fig : Figure
        Figure to add the panel to.
    nrows, ncols, index : int
        Subplot grid position, as in ``Figure.add_subplot``.

    Returns
    -------
    Axes
        A cartopy ``GeoAxes`` with x/y limits in projected metres.

    Raises
    ------
    ModuleNotFoundError
        If cartopy is not installed (``uv sync --group geo``).
    """
    # cartopy is optional (geo group, absent in CI) and ships no type information, so it
    # is imported at call time and used as a dynamically typed module.
    ccrs = importlib.import_module("cartopy.crs")
    proj = map_projection()
    crs = ccrs.LambertConformal(
        central_longitude=proj.central_longitude_deg,
        central_latitude=proj.central_latitude_deg,
        standard_parallels=proj.standard_parallels_deg,
    )
    domain = map_domain()
    x_m, y_m = crs.transform_point(domain.center_lon_deg, domain.center_lat_deg, ccrs.Geodetic())
    half_m = domain.half_width_km * _M_PER_KM
    ax: Axes = fig.add_subplot(nrows, ncols, index, projection=crs)
    # Limits in the map's own projected metres: same as GeoAxes.set_extent(..., crs=crs).
    ax.set_xlim(x_m - half_m, x_m + half_m)
    ax.set_ylim(y_m - half_m, y_m + half_m)
    return ax
