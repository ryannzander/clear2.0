"""Build the Toronto 0.1° grid and its station coverage from the stations registry.

Spec: methodology/grid.md#method. CLI: ``uv run clear grid build``.
"""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from clear.geo import CITY_BOUNDARY_FILE, city_bounds, read_city_boundary
from clear.grid.assign import assign_stations, coverage
from clear.grid.cells import TorontoGridConfig, build_cells, city_fraction
from clear.paths import data_dir
from clear.schemas.grid import CELLS, STATION_CELLS

__all__ = ["GridOutputs", "build_grid", "grid_outputs"]


@dataclass(frozen=True)
class GridOutputs:
    """Where the grid build writes its tables.

    Method: methodology/grid.md#outputs
    """

    cells: Path
    station_cells: Path


def grid_outputs(cell_size_deg: float, root: Path | None = None) -> GridOutputs:
    """Return the output paths under ``root`` (default ``data/``); the cell size tags the files.

    Method: methodology/grid.md#outputs

    Parameters
    ----------
    cell_size_deg : float
        Cell size; ``0.1`` tags the files ``0p1``.
    root : Path, optional
        Data folder; default ``data/``.

    Returns
    -------
    GridOutputs
        Paths of the cells and station-cells tables.

    Examples
    --------
    >>> grid_outputs(0.1).cells.name
    'toronto_0p1.parquet'
    """
    base = (root or data_dir()) / "processed" / "grid"
    tag = f"{cell_size_deg:g}".replace(".", "p")
    return GridOutputs(
        cells=base / f"toronto_{tag}.parquet", station_cells=base / f"station_cells_{tag}.parquet"
    )


def build_grid(
    config: TorontoGridConfig,
    registry: pd.DataFrame,
    *,
    active_since: pd.Timestamp,
    raw: Path | None = None,
    out: GridOutputs | None = None,
) -> pd.DataFrame:
    """Build cells over the City, flag Toronto cells, assign stations, count coverage.

    Method: methodology/grid.md#method

    Parameters
    ----------
    config : TorontoGridConfig
        ``config/grid.yaml: toronto_grid``.
    registry : pandas.DataFrame
        ``data/processed/stations/registry.parquet``.
    active_since : pandas.Timestamp
        Start of the first training year (``config/splits.yaml``).
    raw : Path, optional
        Raw data folder; default ``data/raw``.
    out : GridOutputs, optional
        Output paths; default :func:`grid_outputs`.

    Returns
    -------
    pandas.DataFrame
        The cells table (also written to ``out.cells``).
    """
    raw_dir = raw or data_dir() / "raw"
    paths = out or grid_outputs(config.cell_size_deg)
    city = read_city_boundary(raw_dir / CITY_BOUNDARY_FILE)
    cells = build_cells(city_bounds(city), config.cell_size_deg)
    cells["city_frac"] = city_fraction(cells, city)
    cells["is_in_toronto"] = cells["city_frac"] > config.min_city_frac
    station_cells = assign_stations(registry, cells, config.cell_size_deg)
    table = coverage(cells, station_cells, registry, active_since=active_since)
    writes = ((table, CELLS, paths.cells), (station_cells, STATION_CELLS, paths.station_cells))
    for frame, schema, _ in writes:
        schema.validate(frame, lazy=True)
    for frame, _, path in writes:
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_parquet(path, index=False)
    return table
