"""``clear grid build``: the Toronto 0.1° grid and its government-station coverage."""

import json
from pathlib import Path
from typing import Annotated

import pandas as pd
import typer

from clear.grid.assign import coverage_metrics
from clear.grid.cells import load_toronto_grid_config
from clear.grid.pipeline import build_grid
from clear.schemas.stations import REGISTRY
from clear.stations.pipeline import outputs
from clear.stations.settings import load_splits_config

__all__ = ["app", "build"]

app = typer.Typer(name="grid", help="Toronto grid (methodology/grid.md).", no_args_is_help=True)


@app.command()
def build(
    json_out: Annotated[Path | None, typer.Option("--json", help="Write metrics here.")] = None,
) -> None:
    """Build cells, flag Toronto cells, assign stations; print the coverage metrics.

    Method: methodology/grid.md#method
    """
    config = load_toronto_grid_config()
    train = load_splits_config().splits["train"]
    active_since = pd.Timestamp(year=train.first_year, month=1, day=1, tz="UTC")
    registry = REGISTRY.validate(pd.read_parquet(outputs().registry))
    cells = build_grid(config, registry, active_since=active_since)
    metrics = coverage_metrics(cells, cell_size_deg=config.cell_size_deg)
    metrics["active_since_utc"] = active_since.isoformat()
    text = json.dumps(metrics, indent=2)
    typer.echo(text)
    if json_out is not None:
        json_out.write_text(text + "\n", encoding="utf-8")
