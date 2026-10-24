import numpy as np
import pandas as pd
import pytest
from shapely.geometry import box

from clear.geo import Bounds
from clear.grid.assign import assign_stations, coverage
from clear.grid.cells import (
    build_cells,
    cell_id,
    cell_index,
    city_fraction,
    load_toronto_grid_config,
)


def test_cell_index_puts_edges_north_east():
    assert cell_index(np.array([43.7, 43.69999, -79.4, -79.40001]), 0.1).tolist() == [
        437,
        436,
        -794,
        -795,
    ]


def test_cell_id_is_south_west_corner():
    assert cell_id(436, -795, 0.1) == "N4360W07950"
    assert cell_id(-1, 2, 0.5) == "S0050E00100"


def test_build_cells_snaps_out_and_tiles():
    cells = build_cells(Bounds(-79.64, 43.58, -79.11, 43.86), 0.1)
    assert cells["lat_min_deg"].min() == pytest.approx(43.5)
    assert cells["lat_max_deg"].max() == pytest.approx(43.9)
    assert cells["lon_min_deg"].min() == pytest.approx(-79.7)
    assert cells["lon_max_deg"].max() == pytest.approx(-79.1)
    assert len(cells) == 4 * 6
    assert cells["cell_id"].is_unique
    area = (
        (cells["lat_max_deg"] - cells["lat_min_deg"])
        * (cells["lon_max_deg"] - cells["lon_min_deg"])
    ).sum()
    assert area == pytest.approx(0.4 * 0.6)


def test_city_fraction_partial_and_full():
    cells = build_cells(Bounds(-79.7, 43.5, -79.5, 43.6), 0.1)
    city = box(-79.65, 43.5, -79.5, 43.6)  # half of the west cell, all of the east cell
    frac = city_fraction(cells, city)
    assert frac.round(6).tolist() == [0.5, 1.0]


def test_assign_and_coverage():
    cells = build_cells(Bounds(-79.7, 43.5, -79.5, 43.6), 0.1)
    registry = pd.DataFrame(
        {
            "station_id": ["naps:1", "mecp:2", "naps:3", "naps:9"],
            "site_id": ["naps:1", "naps:1", "naps:3", "naps:9"],
            "source": ["naps", "mecp", "naps", "naps"],
            "is_in_toronto": [True, True, True, False],
            "lat_deg": [43.55, 43.55, 43.52, 45.0],
            "lon_deg": [-79.55, -79.55, -79.58, -79.0],
            "last_time_utc": pd.to_datetime(
                ["2025-01-01", "2025-01-01", "2010-01-01", "2025-01-01"], utc=True
            ),
        }
    )
    sc = assign_stations(registry, cells, 0.1)
    got = sc.set_index("station_id")["cell_id"]
    assert got[["naps:1", "mecp:2", "naps:3"]].tolist() == ["N4350W07960"] * 3
    assert pd.isna(got["naps:9"])  # outside the built cells
    cov = coverage(
        cells, sc, registry, active_since=pd.Timestamp("2021-01-01", tz="UTC")
    ).set_index("cell_id")
    east = cov[cov.index == "N4350W07960"]
    counts = [int(east[c].iloc[0]) for c in ("n_stations", "n_sites", "n_sites_active")]
    assert counts == [3, 2, 1]
    assert cov["coverage_class"].to_dict() == {"N4350W07970": "0", "N4350W07960": "1"}


def test_grid_config_loads_and_viz_still_reads_domain():
    from clear.viz.maps import map_domain

    assert load_toronto_grid_config().cell_size_deg == 0.1
    assert map_domain().half_width_km > 0


def test_city_fraction_area_sums_to_city_area():
    city = box(-79.63, 43.58, -79.12, 43.85)
    cells = build_cells(Bounds(-79.63, 43.58, -79.12, 43.85), 0.1)
    cell_area = (cells["lat_max_deg"] - cells["lat_min_deg"]) * (
        cells["lon_max_deg"] - cells["lon_min_deg"]
    )
    assert float((city_fraction(cells, city) * cell_area).sum()) == pytest.approx(
        city.area, rel=1e-9
    )


def test_coverage_metrics_counts_classes():
    from clear.grid.assign import coverage_metrics

    cells = pd.DataFrame(
        {
            "is_in_toronto": [True, True, True, False],
            "coverage_class": ["0", "1", ">1", "0"],
            "n_sites": [0, 1, 3, 0],
        }
    )
    m = coverage_metrics(cells, cell_size_deg=0.1)
    assert (
        m["toronto_cells"],
        m["toronto_cells_with_0_active_sites"],
        m["toronto_cells_with_any_site_ever"],
    ) == (3, 1, 2)


def test_map_axes_lonlat_box():
    pytest.importorskip("cartopy.crs")
    from clear import viz

    fig, first = viz.new_figure("paper-1col")
    first.remove()
    ax = viz.map_axes(fig, lonlat_box_deg=(-79.7, -79.1, 43.5, 43.9))
    x0, x1 = ax.get_xlim()
    assert x1 > x0
