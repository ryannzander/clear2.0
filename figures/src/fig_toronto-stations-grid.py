"""Toronto 0.1° grid: City boundary, Toronto cells and active government sites, stations.

Answers issue #2. Inputs: the grid and stations outputs (uv run clear stations build;
uv run clear grid build). Rebuild: uv run clear figures build --only toronto-stations-grid
"""

import importlib

import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Polygon

from clear import viz
from clear.geo import CITY_BOUNDARY_FILE, read_city_boundary
from clear.grid.cells import load_toronto_grid_config
from clear.grid.pipeline import grid_outputs
from clear.paths import data_dir
from clear.schemas.grid import CELLS
from clear.schemas.stations import REGISTRY
from clear.stations.pipeline import outputs

PRESET = "paper-2col"
HEIGHT_IN = 5.4
MARKERS = {"naps": "o", "mecp": "s", "airnow": "^"}
SCALE_BAR_M = 10_000  # length of the map scale bar


def main() -> None:
    viz.use_style(PRESET)
    ccrs = importlib.import_module("cartopy.crs")
    lonlat = ccrs.PlateCarree()
    size = load_toronto_grid_config().cell_size_deg
    cells_path = grid_outputs(size).cells
    registry_path = outputs().registry
    boundary_path = data_dir() / "raw" / CITY_BOUNDARY_FILE
    cells = CELLS.validate(pd.read_parquet(cells_path))
    registry = REGISTRY.validate(pd.read_parquet(registry_path))
    city = read_city_boundary(boundary_path)

    fig, first = viz.new_figure(PRESET, height_in=HEIGHT_IN)
    first.remove()
    box = (
        float(cells["lon_min_deg"].min()),
        float(cells["lon_max_deg"].max()),
        float(cells["lat_min_deg"].min()),
        float(cells["lat_max_deg"].max()),
    )
    ax = viz.map_axes(fig, lonlat_box_deg=box)

    ink, muted, grid = (
        viz.color("neutral.ink"),
        viz.color("neutral.muted"),
        viz.color("neutral.grid"),
    )
    for cell in cells.to_dict("records"):
        lon0, lon1 = float(cell["lon_min_deg"]), float(cell["lon_max_deg"])
        lat0, lat1 = float(cell["lat_min_deg"]), float(cell["lat_max_deg"])
        is_in_toronto = bool(cell["is_in_toronto"])
        no_site = is_in_toronto and int(cell["n_sites_active"]) == 0
        face = viz.color("neutral.missing") if no_site else viz.color("neutral.background")
        edge = ink if is_in_toronto else grid
        corners = [(lon0, lat0), (lon1, lat0), (lon1, lat1), (lon0, lat1)]
        ax.add_patch(
            Polygon(corners, closed=True, facecolor=face, edgecolor=edge, lw=0.6, transform=lonlat)
        )
        if is_in_toronto:
            ax.text(
                lon0 + 0.004,
                lat1 - 0.006,
                f"{cell['cell_id']}\n{int(cell['n_sites_active'])} active",
                fontsize="xx-small",
                va="top",
                color=muted,
                transform=lonlat,
            )
    for geom in getattr(city, "geoms", [city]):
        x, y = geom.exterior.xy
        ax.plot(list(x), list(y), color=ink, lw=1.2, transform=lonlat)

    toronto = registry[registry["is_in_toronto"]]
    labels = viz.load_tokens().source_labels
    for source, marker in MARKERS.items():
        sub = toronto[toronto["source"] == source]
        ax.scatter(
            sub["lon_deg"],
            sub["lat_deg"],
            marker=marker,
            s=28,
            facecolor=viz.color(f"source.{source}"),
            edgecolor=ink,
            lw=0.4,
            transform=lonlat,
            zorder=3,
        )
    handles = [
        Line2D(
            [],
            [],
            marker=m,
            ls="",
            markerfacecolor=viz.color(f"source.{s}"),
            markeredgecolor=ink,
            label=labels[s],
        )
        for s, m in MARKERS.items()
    ] + [
        Patch(
            facecolor=viz.color("neutral.missing"),
            edgecolor=ink,
            label="Toronto cell, no site active 2021+",
        ),
        Line2D([], [], color=ink, lw=1.2, label="City of Toronto boundary"),
    ]
    ax.legend(handles=handles, loc="lower right", frameon=True)
    # Scale bar: the map is Lambert conformal, so x/y are projected metres.
    (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
    bar_x, bar_y = x0 + 0.04 * (x1 - x0), y0 + 0.04 * (y1 - y0)
    ax.plot([bar_x, bar_x + SCALE_BAR_M], [bar_y, bar_y], color=ink, lw=2)
    ax.text(bar_x, bar_y + 0.012 * (y1 - y0), f"{SCALE_BAR_M / 1000:g} km", color=ink)
    ax.set_title(f"Toronto {size:g}° grid and government PM2.5 stations (all years)")

    viz.save_figure(
        fig,
        "toronto-stations-grid",
        caption=(
            f"{size:g}° cells over the City of Toronto (Lambert conformal, Canada-centred). "
            "Bold cells "
            "overlap the City; grey ones hold no government site with data since 2021. Markers are "
            "NAPS, Ontario MECP and AirNow stations inside the City, all years; co-located markers "
            "overlap (one site, several networks)."
        ),
        description=(
            "Map, lon -79.7 to -79.1, lat 43.5 to 43.9 (about 48 km x 44 km). Each Toronto cell is "
            "labelled with its cell_id and number of active government sites. Station markers by "
            "source: circle NAPS, square MECP, triangle AirNow."
        ),
        inputs=[cells_path, registry_path, boundary_path],
        preset=PRESET,
    )


if __name__ == "__main__":
    main()
