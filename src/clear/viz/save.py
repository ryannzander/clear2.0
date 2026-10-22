"""Provenance-tracked figure saving: png + svg + a sidecar naming inputs and commit.

Standard: ``docs/standards/figures.md#provenance``. Use it as ``clear.viz.save_figure``.
"""

import hashlib
import inspect
import os
import re
import subprocess
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

import matplotlib as mpl
import yaml
from matplotlib.figure import Figure
from pydantic import BaseModel, ConfigDict

from clear.paths import figures_out_dir, repo_root
from clear.viz.tokens import Preset
from clear.viz.tokens import preset as preset_by_name

__all__ = ["SavedFigure", "save_figure"]

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# Widths are compared in inches; anything closer than this is "the same width".
_WIDTH_TOLERANCE_IN = 0.01
# The clear package draws every figure, so its state is part of "the code that built it".
_PACKAGE_DIR = Path(__file__).resolve().parents[1]


class SavedFigure(BaseModel):
    """Paths written by :func:`save_figure`.

    Method: docs/standards/figures.md#provenance
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    png: Path
    svg: Path
    sidecar: Path


def save_figure(
    fig: Figure,
    slug: str,
    *,
    caption: str,
    inputs: Sequence[str | Path],
    preset: str,
    headline: bool = False,
    description: str = "",
    out_dir: Path | None = None,
    script: str | Path | None = None,
) -> SavedFigure:
    """Write ``fig_<slug>.png``, ``.svg`` and the provenance sidecar ``.md``.

    Method: docs/standards/figures.md#provenance

    Everything is checked before the first file is written, so a failure leaves no
    half-written figure behind. Files are saved at exactly the figure size (standard
    bbox), so the width checked here is the width on disk.

    Parameters
    ----------
    fig : Figure
        The figure; its width (in) must match the preset width.
    slug : str
        Lowercase-hyphenated name, e.g. ``"naps-hourly-2023"``.
    caption : str
        One-to-three sentence caption, as it would appear under the figure.
    inputs : sequence of str or Path
        Every data/config file the figure was drawn from (repo-relative or absolute).
        Each is hashed (sha256) into the sidecar.
    preset : str
        Size preset the figure was built for.
    headline : bool, default False
        True only after Ryan signs off on the figure for a paper/pitch/submission.
    description : str, optional
        What the figure shows (axes, encodings), for readers who cannot see it.
    out_dir : Path, optional
        Output directory; defaults to ``figures/out``.
    script : str or Path, optional
        Generating script (repo-relative or absolute); defaults to the calling file.

    Returns
    -------
    SavedFigure
        Paths of the three files written.

    Raises
    ------
    ValueError
        If ``slug`` is not lowercase-hyphenated, or the figure width differs from the preset.
    KeyError
        If ``preset`` is not defined in ``tokens.yaml``.
    FileNotFoundError
        If an input file does not exist.
    """
    p = _check_figure(fig, slug, preset)
    resolved = [_absolute(Path(i)) for i in inputs]
    missing = [str(path) for path in resolved if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"figure input(s) not found: {missing}")
    caller = _absolute(Path(script) if script else Path(inspect.stack()[1].filename))
    text = _sidecar_text(slug, caption, description, preset, headline, resolved, caller)
    target = out_dir or figures_out_dir()
    target.mkdir(parents=True, exist_ok=True)
    stem = target / f"fig_{slug}"
    paths = SavedFigure(
        png=stem.with_suffix(".png"), svg=stem.with_suffix(".svg"), sidecar=stem.with_suffix(".md")
    )
    # Never crop: a tight bbox would change the saved size away from the preset width.
    # matplotlib stubs type rc_context's unused fname as PathLike[Unknown].
    with mpl.rc_context({"savefig.bbox": "standard"}):  # pyright: ignore[reportUnknownMemberType]
        # matplotlib stubs leave savefig **kwargs untyped.
        fig.savefig(paths.png, dpi=p.dpi, metadata={"Software": None})  # pyright: ignore[reportUnknownMemberType]
        fig.savefig(paths.svg, metadata={"Date": None, "Creator": None})  # pyright: ignore[reportUnknownMemberType]
    paths.sidecar.write_text(text, encoding="utf-8")
    return paths


def _check_figure(fig: Figure, slug: str, preset_name: str) -> Preset:
    if not _SLUG_RE.match(slug):
        raise ValueError(f"slug {slug!r} must be lowercase letters/digits separated by hyphens")
    p = preset_by_name(preset_name)
    width_in = float(fig.get_size_inches()[0])
    if abs(width_in - p.width_in) > _WIDTH_TOLERANCE_IN:
        raise ValueError(
            f"figure width {width_in:.2f} in does not match preset {preset_name!r} "
            f"({p.width_in} in)"
        )
    return p


def _absolute(path: Path) -> Path:
    # Lexical, not resolve(): data/raw and data/prior are junctions to other drives, and
    # the sidecar should name the repo path, not the drive behind it.
    return Path(os.path.abspath(path if path.is_absolute() else repo_root() / path))


def _repo_relative(path: Path) -> str | None:
    try:
        return _absolute(path).relative_to(repo_root()).as_posix()
    except ValueError:
        return None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", *args], cwd=repo_root(), capture_output=True, text=True, check=True
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout


def _git_changed_paths() -> list[str] | None:
    # Whole-repo status, not a pathspec: a pathspec under a junction (data/raw) is an error.
    out = _git("status", "--porcelain=v1", "-z", "--untracked-files=all")
    if out is None:
        return None
    changed: list[str] = []
    fields = iter(out.split("\0"))
    for entry in fields:
        if not entry:
            continue
        changed.append(entry[3:])  # "XY path"
        if entry[0] in "RC":  # renames and copies carry the original path as the next field
            changed.append(next(fields, ""))
    return changed


def _git_commit(script: Path, inputs: Sequence[Path]) -> str:
    """Return the short HEAD sha, suffixed ``-dirty`` when HEAD does not hold the code used.

    Dirty: the script is outside the repo, git status fails, or the script, an input or the
    ``clear`` package has staged, unstaged or untracked changes. Gitignored inputs
    (``data/``) and inputs outside the repo are not in git; their sha256 pins them.
    """
    head = (_git("rev-parse", "--short", "HEAD") or "").strip()
    if not head:
        return "uncommitted"
    script_rel = _repo_relative(script)
    changed = _git_changed_paths()
    if script_rel is None or changed is None:
        return f"{head}-dirty"
    watched = [script_rel, *(r for r in map(_repo_relative, [*inputs, _PACKAGE_DIR]) if r)]
    if any(c == w or c.startswith(f"{w}/") for c in changed for w in watched):
        return f"{head}-dirty"
    return head


def _sidecar_text(
    slug: str,
    caption: str,
    description: str,
    preset_name: str,
    headline: bool,
    inputs: Sequence[Path],
    script: Path,
) -> str:
    meta = {
        "slug": slug,
        "caption": caption,
        "preset": preset_name,
        "headline": headline,
        "inputs": [
            {"path": _repo_relative(p) or p.as_posix(), "sha256": _sha256(p)} for p in inputs
        ],
        "script": _repo_relative(script) or script.as_posix(),
        "git_commit": _git_commit(script, inputs),
        "generated_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    front = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
    body = description or "<what the figure shows: axes, encodings, data period>"
    return f"---\n{front}\n---\n\n# fig_{slug}\n\n{caption}\n\n## What it shows\n\n{body}\n"
