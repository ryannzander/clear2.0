"""scripts/inventory.py: classification, mirror mapping, status logic, --check."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "inventory.py"


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def write(path: Path, data: bytes = b"x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def mirror(
    root: Path,
    rel: str,
    source: str,
    digest: str,
    *,
    status: str = "current",
    aliases: tuple[str, ...] = (),
) -> None:
    alias_list = ", ".join(aliases)
    text = (
        f"---\nsource: {source}\naliases: [{alias_list}]\nsha256: {digest}\n"
        f"converted: 2026-10-21\nconverter: markitdown\nstatus: {status}\n"
        "kind: mirror\n---\n\n# Mirror\n"
    )
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def rows(root: Path, name: str = "inventory.csv", key: str = "path") -> dict[str, dict[str, str]]:
    with (root / "manifests" / name).open(encoding="utf-8", newline="") as fh:
        return {r[key]: r for r in csv.DictReader(fh)}


def make_link(link: Path, target: Path) -> None:
    """Directory link like scripts/storage.py makes: a junction on Windows, else a symlink."""
    link.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)], check=True, capture_output=True
        )
    else:
        link.symlink_to(target, target_is_directory=True)


def build_fake_repo(root: Path) -> None:
    write(root / "archive/Docs/a.docx", b"aaa")
    write(root / "archive/Docs/a.pdf", b"pdf")
    mirror(
        root,
        "knowledge/docs/docs/a.md",
        "archive/Docs/a.docx",
        sha(b"aaa"),
        aliases=("archive/Docs/a.pdf",),
    )
    write(root / "archive/Docs/b.docx", b"bbb")
    write(root / "archive/Docs/c.docx", b"new")
    mirror(root, "knowledge/docs/docs/c.md", "archive/Docs/c.docx", sha(b"old"))
    write(root / "archive/Docs/._a.docx", b"junk")
    write(root / "archive/figs/map.png", b"png")
    write(root / "archive/Docs/old.docx", b"old")
    write(root / "archive/competitions/CAYIA/v.mp4", b"mp4")
    index = (
        "# knowledge\n"
        "- `archive/figs/map.png` — station map\n"
        "- `archive/Docs/old.docx` — superseded by a.docx\n"
        "- [CAYIA](../archive/competitions/CAYIA/) — competition material\n"
    )
    (root / "knowledge" / "INDEX.md").write_text(index, encoding="utf-8")
    write(root / "RAW Data/x.csv", b"a,b\n1,2\n")
    write(root / "inbox/README.md", b"readme")


def test_statuses_and_sources(tmp_path: Path) -> None:
    build_fake_repo(tmp_path)
    result = run(tmp_path)
    assert result.returncode == 0, result.stderr
    r = rows(tmp_path)
    assert r["archive/Docs/a.docx"]["status"] == "mapped"
    assert r["archive/Docs/a.docx"]["mirror"] == "knowledge/docs/docs/a.md"
    assert r["archive/Docs/a.docx"]["sha256"] == sha(b"aaa")
    assert r["archive/Docs/a.pdf"]["status"] == "mapped"
    assert r["archive/Docs/b.docx"]["status"] == "unmapped"
    assert r["archive/Docs/c.docx"]["status"] == "stale"
    assert r["archive/Docs/._a.docx"]["status"] == "junk"
    assert r["archive/figs/map.png"] == {
        **r["archive/figs/map.png"],
        "kind": "image",
        "status": "mapped",
    }
    assert r["archive/Docs/old.docx"]["status"] == "superseded"
    assert r["archive/competitions/CAYIA/v.mp4"]["status"] == "mapped"
    assert r["RAW Data/x.csv"]["area"] == "legacy"
    assert r["RAW Data/x.csv"]["kind"] == "data"
    assert "inbox/README.md" not in r
    sources = json.loads((tmp_path / "knowledge" / "_sources.json").read_text(encoding="utf-8"))
    assert sources["archive/Docs/a.docx"] == {
        "mirror": "knowledge/docs/docs/a.md",
        "sha256": sha(b"aaa"),
    }
    assert sources["archive/Docs/a.pdf"]["alias_of"] == "archive/Docs/a.docx"


def test_check_mode(tmp_path: Path) -> None:
    build_fake_repo(tmp_path)
    assert run(tmp_path, "--check").returncode == 1  # nothing written yet
    assert run(tmp_path).returncode == 0
    assert run(tmp_path, "--check").returncode == 0
    write(tmp_path / "archive/Docs/new.docx", b"n")
    assert run(tmp_path, "--check").returncode == 1


def test_hash_cache_is_reused(tmp_path: Path) -> None:
    write(tmp_path / "data/raw/big.csv", b"1,2,3\n")
    assert run(tmp_path).returncode == 0
    csv_path = tmp_path / "manifests" / "inventory.csv"
    real = sha(b"1,2,3\n")
    csv_path.write_text(
        csv_path.read_text(encoding="utf-8").replace(real, "cached"), encoding="utf-8"
    )
    assert run(tmp_path).returncode == 0
    assert rows(tmp_path)["data/raw/big.csv"]["sha256"] == "cached"  # unchanged file not re-hashed


def test_zarr_store_is_one_row(tmp_path: Path) -> None:
    write(tmp_path / "data/raw/era5.zarr/.zarray", b"{}")
    write(tmp_path / "data/raw/era5.zarr/0.0", b"chunk")
    assert run(tmp_path).returncode == 0
    r = rows(tmp_path)
    assert list(r) == ["data/raw/era5.zarr"]
    assert r["data/raw/era5.zarr"]["kind"] == "data"
    assert r["data/raw/era5.zarr"]["bytes"] == str(len(b"{}") + len(b"chunk"))


def test_folder_data_card_covers_every_file_below(tmp_path: Path) -> None:
    # Raw datasets can hold thousands of files; one card per dataset folder maps them all.
    write(tmp_path / "data/raw/EPA Hourly/2024/01.csv", b"one")
    write(tmp_path / "data/raw/EPA Hourly/2024/02.csv", b"two")
    write(tmp_path / "data/raw/Other/x.csv", b"other")
    mirror(tmp_path, "knowledge/data/epa-hourly.md", "data/raw/EPA Hourly", sha(b"unused"))

    result = run(tmp_path)

    assert result.returncode == 0, result.stderr
    got = rows(tmp_path)
    for path in ("data/raw/EPA Hourly/2024/01.csv", "data/raw/EPA Hourly/2024/02.csv"):
        assert got[path]["status"] == "mapped"
        assert got[path]["mirror"] == "knowledge/data/epa-hourly.md"
    assert got["data/raw/Other/x.csv"]["status"] == "unmapped"


def test_index_links_to_area_roots_map_nothing(tmp_path: Path) -> None:
    # The real INDEX files describe the layout by linking area roots; that must not count
    # as mapping every file below them.
    write(tmp_path / "data/raw/NOAA/HRRR/x.grib2", b"g")
    write(tmp_path / "data/prior/era5_cells/x.parquet", b"p")
    write(tmp_path / "archive/Docs/x.docx", b"d")
    write(
        tmp_path / "knowledge/INDEX.md",
        b"# knowledge\nOriginals live in `archive/`, `data/raw/` and `data/prior/`.\n",
    )
    write(tmp_path / "data/INDEX.md", b"# data\n- [raw/](raw/) - junction\n- [prior/](prior/)\n")
    write(tmp_path / "INDEX.md", b"- [data](data/) and [repo](./)\n")

    assert run(tmp_path).returncode == 0

    got = rows(tmp_path)
    for path in (
        "data/raw/NOAA/HRRR/x.grib2",
        "data/prior/era5_cells/x.parquet",
        "archive/Docs/x.docx",
    ):
        assert got[path]["status"] == "unmapped", path


def test_only_index_entries_map_not_prose(tmp_path: Path) -> None:
    write(tmp_path / "archive/competitions/CAYIA/v.mp4", b"v")
    write(tmp_path / "archive/competitions/Other/w.mp4", b"w")
    write(
        tmp_path / "knowledge/INDEX.md",
        b"# knowledge\nIt sits in `archive/competitions/` and is not mirrored.\n"
        b"- [CAYIA](../archive/competitions/CAYIA/) - pitch videos\n",
    )

    assert run(tmp_path).returncode == 0

    got = rows(tmp_path)
    assert got["archive/competitions/CAYIA/v.mp4"]["status"] == "mapped"
    assert got["archive/competitions/Other/w.mp4"]["status"] == "unmapped"


def test_linked_raw_store_uses_repo_paths(tmp_path: Path) -> None:
    repo, drive = tmp_path / "repo", tmp_path / "drive"
    write(drive / "EPA" / "a.csv", b"one")
    make_link(repo / "data" / "raw", drive)

    result = run(repo)

    assert result.returncode == 0, result.stderr
    assert rows(repo)["data/raw/EPA/a.csv"]["sha256"] == sha(b"one")


def test_unplugged_drive_keeps_previous_rows(tmp_path: Path) -> None:
    repo, drive = tmp_path / "repo", tmp_path / "drive"
    write(drive / "EPA" / "a.csv", b"one")
    make_link(repo / "data" / "raw", drive)
    write(repo / "archive" / "notes.docx", b"doc")
    assert run(repo).returncode == 0
    before = rows(repo)

    shutil.rmtree(drive)  # unplug: the junction stays, its target is gone
    result = run(repo)

    assert result.returncode == 0, result.stderr
    assert "data/raw is offline" in result.stderr
    assert rows(repo) == before
    assert run(repo, "--check").returncode == 0


def test_summary_rolls_up_by_dataset_folder(tmp_path: Path) -> None:
    write(tmp_path / "data/raw/NOAA/HRRR/2023/a.grib2", b"aa")
    write(tmp_path / "data/raw/NOAA/HRRR/2024/b.grib2", b"bbb")
    write(tmp_path / "data/raw/README_RAW_DATA.txt", b"r")
    write(tmp_path / "data/prior/era5_cells/x.parquet", b"p")

    assert run(tmp_path).returncode == 0

    summary = rows(tmp_path, "inventory-summary.csv", key="folder")
    assert summary["data/raw/NOAA"]["files"] == "2"
    assert summary["data/raw/NOAA"]["bytes"] == "5"
    assert summary["data/raw/NOAA"]["unmapped"] == "2"
    assert summary["data/raw"]["files"] == "1"
    assert summary["data/prior/era5_cells"]["area"] == "prior"
