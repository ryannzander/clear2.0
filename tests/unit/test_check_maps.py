"""scripts/check_maps.py: unmapped originals, budgets, ADR links, repo map, frontmatter."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_maps.py"

AGENTS_MD = """# Guide

## Repo map

| Path | What | Map |
|---|---|---|
| `knowledge/` | mirrors | `knowledge/INDEX.md` |
| `methodology/` | specs | `methodology/INDEX.md` |
| `notebooks/` | scratch | — |

## Hard rules
"""


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def minimal_repo(root: Path) -> None:
    write(root / "AGENTS.md", AGENTS_MD)
    write(root / "STATUS.md", "# STATUS\n")
    write(root / "knowledge/INDEX.md", "# knowledge\n")
    write(root / "methodology/INDEX.md", "# methodology\n")


def test_clean_repo_passes(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    result = run(tmp_path)
    assert result.returncode == 0, result.stderr


def test_missing_repo_map_target(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    (tmp_path / "methodology/INDEX.md").unlink()
    result = run(tmp_path, "--ci")
    assert result.returncode == 1
    assert "methodology/INDEX.md" in result.stderr


def test_index_budget(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    write(tmp_path / "knowledge/INDEX.md", "- line\n" * 101)
    result = run(tmp_path, "--ci")
    assert result.returncode == 1
    assert "budget 100" in result.stderr


def test_docs_budget(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    write(tmp_path / "docs/system/long.md", "x\n" * 201)
    assert run(tmp_path, "--ci").returncode == 1


def test_adr_links(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    write(
        tmp_path / "methodology/alert-levels.md", "See [ADR](../decisions/0001-hourly-mean.md).\n"
    )
    result = run(tmp_path, "--ci")
    assert result.returncode == 1
    assert "0001-hourly-mean.md" in result.stderr
    write(tmp_path / "decisions/0001-hourly-mean.md", "# ADR\n")
    assert run(tmp_path, "--ci").returncode == 0


def test_unmapped_original_fails_locally_not_in_ci(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    write(tmp_path / "archive/Docs/b.docx", "bbb")
    result = run(tmp_path)
    assert result.returncode == 1
    assert "unmapped original: archive/Docs/b.docx" in result.stderr
    assert run(tmp_path, "--ci").returncode == 0


def test_big_unmapped_dataset_is_one_line(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    for i in range(50):
        write(tmp_path / f"data/raw/NOAA/HRRR/f{i:02d}.grib2", "g")
    write(tmp_path / "data/prior/era5_cells/x.parquet", "p")

    result = run(tmp_path)

    assert result.returncode == 1
    noaa = [line for line in result.stderr.splitlines() if "data/raw/NOAA" in line]
    assert len(noaa) == 1
    assert "unmapped original: data/raw/NOAA/HRRR/f00.grib2 (+49 more in data/raw/NOAA)" in noaa[0]
    assert "unmapped original: data/prior/era5_cells/x.parquet" in result.stderr


def test_stale_mirror_fails(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    write(tmp_path / "archive/a.docx", "changed")
    old = hashlib.sha256(b"original").hexdigest()
    write(
        tmp_path / "knowledge/docs/a.md",
        f"---\nsource: archive/a.docx\nsha256: {old}\nkind: mirror\nstatus: current\n---\n",
    )
    result = run(tmp_path)
    assert result.returncode == 1
    assert "stale mirror" in result.stderr


def test_pending_intake_is_reported_not_failed(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    write(tmp_path / "RAW Data/x.csv", "a,b\n")
    write(tmp_path / "inbox/new.docx", "n")
    result = run(tmp_path)
    assert result.returncode == 0, result.stderr
    assert "2 file(s) pending intake" in result.stdout


def test_mirror_frontmatter_required(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    write(tmp_path / "knowledge/docs/a.md", "# no frontmatter\n")
    result = run(tmp_path, "--ci")
    assert result.returncode == 1
    assert "frontmatter missing" in result.stderr
