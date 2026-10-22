"""scripts/intake.py: filing rules, safe apply, refusals."""

from __future__ import annotations

import csv
import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest
import yaml

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "intake.py"


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


def plan_items(root: Path) -> dict[str, dict[str, str]]:
    data = yaml.safe_load((root / "inbox" / "_plan.yaml").read_text(encoding="utf-8"))
    return {item["src"]: item for item in data}


def seed(root: Path) -> None:
    write(root / "inbox/README.md", b"readme")
    write(root / "inbox/notes.docx", b"doc")
    write(root / "inbox/pm25.csv", b"a,b\n")
    write(root / "inbox/._pm25.csv", b"junk")
    write(root / "inbox/CAYIA pitch deck.pdf", b"pitch")
    write(root / "inbox/demo.mp4", b"video")
    write(root / "RAW Data/era5/wind.nc", b"nc")
    write(root / "CLEAR 2.0 (misc docs)/Documents/04. Stations/stations.docx", b"st")


def test_plan_rules(tmp_path: Path) -> None:
    seed(tmp_path)
    assert run(tmp_path, "plan").returncode == 0
    items = plan_items(tmp_path)
    assert "inbox/README.md" not in items
    assert "RAW Data/era5/wind.nc" not in items  # legacy only with --legacy
    assert items["inbox/notes.docx"]["dest"] == "archive/notes.docx"
    assert items["inbox/pm25.csv"]["dest"] == "data/raw/pm25.csv"
    assert items["inbox/._pm25.csv"]["action"] == "delete"
    assert (
        items["inbox/CAYIA pitch deck.pdf"]["dest"] == "archive/competitions/CAYIA pitch deck.pdf"
    )
    assert items["inbox/demo.mp4"]["dest"] == "archive/competitions/demo.mp4"

    assert run(tmp_path, "plan", "--legacy").returncode == 0
    items = plan_items(tmp_path)
    assert items["RAW Data/era5/wind.nc"]["dest"] == "data/raw/era5/wind.nc"
    assert (
        items["CLEAR 2.0 (misc docs)/Documents/04. Stations/stations.docx"]["dest"]
        == "archive/Documents/04. Stations/stations.docx"
    )


def test_apply_moves_logs_and_prunes(tmp_path: Path) -> None:
    seed(tmp_path)
    assert run(tmp_path, "plan", "--legacy").returncode == 0
    result = run(tmp_path, "apply", "inbox/_plan.yaml")
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "archive/notes.docx").read_bytes() == b"doc"
    assert (tmp_path / "data/raw/pm25.csv").is_file()
    assert (tmp_path / "data/raw/era5/wind.nc").is_file()
    assert (tmp_path / "archive/Documents/04. Stations/stations.docx").is_file()
    assert not (tmp_path / "inbox/._pm25.csv").exists()
    assert not (tmp_path / "RAW Data").exists()  # emptied legacy folder pruned
    assert (tmp_path / "inbox/README.md").is_file()  # tooling files untouched
    with (tmp_path / "manifests/intake-log.csv").open(encoding="utf-8", newline="") as fh:
        log = list(csv.DictReader(fh))
    assert {r["action"] for r in log} == {"move", "delete"}
    assert all(len(r["sha256"]) == 64 for r in log)
    assert (tmp_path / "manifests/inventory.csv").is_file()


def write_plan(root: Path, items: list[dict[str, str]]) -> None:
    (root / "inbox").mkdir(parents=True, exist_ok=True)
    (root / "inbox/_plan.yaml").write_text(yaml.safe_dump(items), encoding="utf-8")


def test_refuses_overwrite(tmp_path: Path) -> None:
    write(tmp_path / "inbox/notes.docx", b"new")
    write(tmp_path / "archive/notes.docx", b"original")
    assert run(tmp_path, "plan").returncode == 0
    assert plan_items(tmp_path)["inbox/notes.docx"]["action"] == "skip"  # conflict flagged
    write_plan(
        tmp_path,
        [
            {
                "src": "inbox/notes.docx",
                "action": "move",
                "dest": "archive/notes.docx",
                "kind": "doc",
                "reason": "",
            }
        ],
    )
    result = run(tmp_path, "apply", "inbox/_plan.yaml")
    assert result.returncode == 1
    assert "refusing to overwrite" in result.stderr
    assert (tmp_path / "archive/notes.docx").read_bytes() == b"original"
    assert (tmp_path / "inbox/notes.docx").is_file()


def test_refuses_deleting_non_junk(tmp_path: Path) -> None:
    write(tmp_path / "inbox/notes.docx", b"doc")
    write(tmp_path / "inbox/data.csv", b"a")
    write_plan(
        tmp_path,
        [
            {
                "src": "inbox/data.csv",
                "action": "move",
                "dest": "data/raw/data.csv",
                "kind": "data",
                "reason": "",
            },
            {
                "src": "inbox/notes.docx",
                "action": "delete",
                "dest": "",
                "kind": "junk",
                "reason": "",
            },
        ],
    )
    result = run(tmp_path, "apply", "inbox/_plan.yaml")
    assert result.returncode == 1
    assert "non-junk" in result.stderr
    assert (tmp_path / "inbox/notes.docx").is_file()
    assert (tmp_path / "inbox/data.csv").is_file()  # whole plan rejected, nothing moved


def test_refuses_dest_outside_originals(tmp_path: Path) -> None:
    write(tmp_path / "inbox/x.py", b"print()")
    write_plan(
        tmp_path,
        [
            {
                "src": "inbox/x.py",
                "action": "move",
                "dest": "src/x.py",
                "kind": "other",
                "reason": "",
            }
        ],
    )
    result = run(tmp_path, "apply", "inbox/_plan.yaml")
    assert result.returncode == 1
    assert "dest must be under" in result.stderr


def move_item(src: str, dest: str) -> dict[str, str]:
    return {"src": src, "action": "move", "dest": dest, "kind": "data", "reason": ""}


def test_refuses_dotdot_and_duplicate_sources(tmp_path: Path) -> None:
    write(tmp_path / "archive/Docs/a.docx", b"already filed")
    write(tmp_path / "inbox/b.csv", b"b")
    write_plan(
        tmp_path,
        [
            move_item("inbox/../archive/Docs/a.docx", "archive/a.docx"),
            move_item("inbox/b.csv", "data/raw/b1.csv"),
            move_item("inbox/b.csv", "data/raw/b2.csv"),
        ],
    )
    result = run(tmp_path, "apply", "inbox/_plan.yaml")
    assert result.returncode == 1
    assert "no '..'" in result.stderr
    assert "listed twice" in result.stderr
    assert (tmp_path / "archive/Docs/a.docx").is_file()
    assert (tmp_path / "inbox/b.csv").is_file()


def test_refuses_offline_destination(tmp_path: Path) -> None:
    drive = tmp_path / "drive"
    drive.mkdir()
    repo = tmp_path / "repo"
    write(repo / "inbox/b.csv", b"b")
    link = repo / "data" / "raw"
    link.parent.mkdir(parents=True)
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(drive)], check=True)
    else:
        link.symlink_to(drive, target_is_directory=True)
    drive.rmdir()  # unplugged
    write_plan(repo, [move_item("inbox/b.csv", "data/raw/b.csv")])
    result = run(repo, "apply", "inbox/_plan.yaml")
    assert result.returncode == 1
    assert "offline" in result.stderr
    assert (repo / "inbox/b.csv").is_file()


def load_intake() -> ModuleType:
    spec = importlib.util.spec_from_file_location("intake_under_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses look the module up while it executes
    spec.loader.exec_module(module)
    return module


def test_cross_drive_move_copies_verifies_then_deletes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    intake = load_intake()
    monkeypatch.setattr(intake, "_same_drive", lambda src, dest: False)
    write(tmp_path / "inbox/b.csv", b"b")
    item = intake.PlanItem("inbox/b.csv", "move", "data/raw/b.csv", "data", "")

    rows = intake.apply_plan(tmp_path, [item])

    assert (tmp_path / "data/raw/b.csv").read_bytes() == b"b"
    assert not (tmp_path / "inbox/b.csv").exists()
    assert rows[0]["dest"] == "data/raw/b.csv"


def test_failed_cross_drive_copy_leaves_no_partial_original(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    intake = load_intake()
    monkeypatch.setattr(intake, "_same_drive", lambda src, dest: False)

    def half_then_fail(src: Path, dest: Path) -> None:
        Path(dest).write_bytes(b"ha")
        raise OSError("disk full")

    monkeypatch.setattr(intake.shutil, "copy2", half_then_fail)
    write(tmp_path / "inbox/b.csv", b"half")
    item = intake.PlanItem("inbox/b.csv", "move", "data/raw/b.csv", "data", "")

    with pytest.raises(OSError, match="disk full"):
        intake.apply_plan(tmp_path, [item])

    assert (tmp_path / "inbox/b.csv").read_bytes() == b"half"
    assert not (tmp_path / "data/raw/b.csv").exists()


def test_refuses_source_roots_and_tooling_files(tmp_path: Path) -> None:
    write(tmp_path / "inbox/_plan.yaml", b"[]")
    write(tmp_path / "inbox/README.md", b"readme")
    write_plan(
        tmp_path,
        [
            move_item("inbox", "archive/inbox"),
            move_item("inbox/README.md", "archive/r.md"),
            move_item("inbox/readme.md", "archive/r2.md"),
            move_item("inbox/.", "archive/inbox2"),
        ],
    )
    result = run(tmp_path, "apply", "inbox/_plan.yaml")
    assert result.returncode == 1
    assert "inbox: not an intake source" in result.stderr
    assert "inbox/README.md: not an intake source" in result.stderr
    assert "inbox/readme.md:" in result.stderr  # case-insensitive: rejected too
    assert "inbox/.: source must be a plain path" in result.stderr
    assert (tmp_path / "inbox/README.md").is_file()


def test_bad_cross_drive_copy_keeps_the_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    intake = load_intake()
    monkeypatch.setattr(intake, "_same_drive", lambda src, dest: False)
    monkeypatch.setattr(
        intake.shutil, "copy2", lambda src, dest: Path(dest).write_bytes(b"corrupt")
    )
    write(tmp_path / "inbox/b.csv", b"b")
    item = intake.PlanItem("inbox/b.csv", "move", "data/raw/b.csv", "data", "")

    with pytest.raises(intake.PlanError, match="source kept"):
        intake.apply_plan(tmp_path, [item])

    assert (tmp_path / "inbox/b.csv").read_bytes() == b"b"
    assert not (tmp_path / "data/raw/b.csv").exists()
