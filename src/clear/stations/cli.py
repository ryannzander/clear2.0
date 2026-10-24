"""``clear stations build|report``: Toronto government stations, years active, missing data."""

import json
from pathlib import Path
from typing import Annotated

import pandas as pd
import typer

from clear.schemas.stations import COMPLETENESS, HOURLY, MERGED, REGISTRY
from clear.stations.pipeline import build_stations, outputs
from clear.stations.report import toronto_report
from clear.stations.settings import load_splits_config, load_stations_config

__all__ = ["app", "build", "report"]

app = typer.Typer(
    name="stations", help="Government stations (methodology/stations.md).", no_args_is_help=True
)


@app.command()
def build() -> None:
    """Read NAPS, MECP and AirNow; write hourly, registry, completeness and merged tables.

    Method: methodology/stations.md#method
    """
    counts = build_stations(load_stations_config(), load_splits_config())
    typer.echo(json.dumps(counts, indent=2))


@app.command()
def report(
    json_out: Annotated[Path | None, typer.Option("--json", help="Write the metrics here.")] = None,
) -> None:
    """Print the Toronto station list: site, source, years active, completeness per split.

    Method: methodology/stations.md#completeness
    """
    paths = outputs()
    table, metrics = toronto_report(
        REGISTRY.validate(pd.read_parquet(paths.registry)),
        COMPLETENESS.validate(pd.read_parquet(paths.completeness)),
        HOURLY.validate(pd.read_parquet(paths.hourly)),
        MERGED.validate(pd.read_parquet(paths.merged)),
        config=load_stations_config(),
    )
    typer.echo(table.to_string(index=False))
    typer.echo(json.dumps(metrics, indent=2))
    if json_out is not None:
        json_out.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
