"""``clear`` command-line entry point: ``uv run clear --help``.

Each methodology part adds its own sub-app here as it is built.
"""

import typer

from clear import __version__
from clear.grid.cli import app as grid_app
from clear.stations.cli import app as stations_app
from clear.viz.cli import app as figures_app

app = typer.Typer(name="clear", help="CLEAR 2.0 research CLI.", no_args_is_help=True)
app.add_typer(figures_app, name="figures")
app.add_typer(stations_app, name="stations")
app.add_typer(grid_app, name="grid")


@app.command()
def version() -> None:
    """Print the package version.

    Method: docs/standards/code.md#package-layout
    """
    typer.echo(__version__)


if __name__ == "__main__":
    app()
