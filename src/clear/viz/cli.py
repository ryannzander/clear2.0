"""``clear figures`` — rebuild and list the figure scripts in ``figures/src/``."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer

from clear.paths import figures_src_dir, repo_root

app = typer.Typer(help="Build and list figures (figures/src/fig_<slug>.py).", no_args_is_help=True)

_PREFIX = "fig_"


def _scripts() -> list[Path]:
    return sorted(figures_src_dir().glob(f"{_PREFIX}*.py"))


def _slug(script: Path) -> str:
    return script.stem.removeprefix(_PREFIX)


@app.command("list")
def list_figures() -> None:
    """List every figure script by slug.

    Method: docs/standards/figures.md#provenance
    """
    for script in _scripts():
        typer.echo(_slug(script))


@app.command()
def build(
    only: Annotated[
        str | None, typer.Option("--only", help="Build just this slug, e.g. style-tokens.")
    ] = None,
) -> None:
    """Run figure scripts (each in its own process) to regenerate ``figures/out/``.

    Method: docs/standards/figures.md#provenance

    Parameters
    ----------
    only : str, optional
        Build just this slug; default builds every ``figures/src/fig_<slug>.py``.

    Raises
    ------
    typer.Exit
        Code 1 if no script matches or any script fails.
    """
    scripts = [s for s in _scripts() if only is None or _slug(s) == only]
    if not scripts:
        typer.echo(f"No figure script matches {only!r}." if only else "No figure scripts found.")
        raise typer.Exit(code=1)
    # Headless backend: figures are files, never windows.
    env = {**os.environ, "MPLBACKEND": "Agg"}
    failed: list[str] = []
    for script in scripts:
        result = subprocess.run([sys.executable, str(script)], cwd=repo_root(), env=env)
        status = "ok" if result.returncode == 0 else "FAILED"
        typer.echo(f"{status:>6}  {_slug(script)}")
        if result.returncode != 0:
            failed.append(_slug(script))
    if failed:
        typer.echo(f"{len(failed)} figure(s) failed: {', '.join(failed)}")
        raise typer.Exit(code=1)
