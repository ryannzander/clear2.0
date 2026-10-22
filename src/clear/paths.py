"""Repository paths used across the package.

The repo root is found from this file's location (the package is installed in editable
mode by ``uv sync``). Set ``CLEAR_ROOT`` to override, e.g. when running from a copy.
"""

import os
from pathlib import Path


def repo_root() -> Path:
    """Return the repository root directory.

    Method: AGENTS.md#repo-map

    Returns
    -------
    Path
        ``$CLEAR_ROOT`` if set, else the directory two levels above ``src/clear/``.
    """
    override = os.environ.get("CLEAR_ROOT")
    if override:
        return Path(override).resolve()
    return Path(__file__).resolve().parents[2]


def config_dir() -> Path:
    """Return ``<repo>/config``, where every methodological constant lives.

    Method: AGENTS.md#repo-map
    """
    return repo_root() / "config"


def figures_src_dir() -> Path:
    """Return ``<repo>/figures/src``, home of the ``fig_<slug>.py`` scripts.

    Method: AGENTS.md#repo-map
    """
    return repo_root() / "figures" / "src"


def figures_out_dir() -> Path:
    """Return ``<repo>/figures/out``, where built figures and sidecars are written.

    Method: AGENTS.md#repo-map
    """
    return repo_root() / "figures" / "out"
