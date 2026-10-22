"""scripts/storage.py: links from .env, status, unplugged drives, refusals."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "storage.py"
INVENTORY = SCRIPT.parent / "inventory.py"


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


def make_repo(tmp_path: Path) -> tuple[Path, Path]:
    """A repo whose .env points data/raw at a 'drive' folder holding one file."""
    repo, store = tmp_path / "repo", tmp_path / "drive" / "RAW Data"
    (store / "EPA").mkdir(parents=True)
    (store / "EPA" / "a.csv").write_text("x", encoding="utf-8")
    repo.mkdir()
    (repo / ".env").write_text(f"# this machine\nCLEAR_RAW_DIR={store}\n", encoding="utf-8")
    return repo, store


def test_link_then_status_online(tmp_path: Path) -> None:
    repo, store = make_repo(tmp_path)

    result = run(repo, "link")

    assert result.returncode == 0, result.stderr
    assert (repo / "data" / "raw" / "EPA" / "a.csv").read_text(encoding="utf-8") == "x"
    assert run(repo, "link").stdout.strip() == f"data/raw: ok -> {store}"  # idempotent
    status = run(repo)
    assert status.returncode == 0, status.stdout
    assert "data/raw    online" in status.stdout
    assert "data/prior  not configured" in status.stdout


def test_unplugged_drive_reads_offline(tmp_path: Path) -> None:
    repo, store = make_repo(tmp_path)
    assert run(repo, "link").returncode == 0

    shutil.rmtree(store)  # the drive goes away; the link stays
    status = run(repo)

    assert status.returncode == 1
    assert "OFFLINE" in status.stdout


def test_changed_target_needs_relink_and_leaves_old_data(tmp_path: Path) -> None:
    repo, store = make_repo(tmp_path)
    assert run(repo, "link").returncode == 0
    other = tmp_path / "other"
    other.mkdir()
    (other / "b.csv").write_text("y", encoding="utf-8")
    (repo / ".env").write_text(f"CLEAR_RAW_DIR={other}\n", encoding="utf-8")

    refused = run(repo, "link")
    relinked = run(repo, "link", "--relink")

    assert refused.returncode == 1
    assert "--relink" in refused.stderr
    assert relinked.returncode == 0, relinked.stderr
    assert (repo / "data" / "raw" / "b.csv").is_file()
    assert (store / "EPA" / "a.csv").is_file()  # removing the link never touches the data


def test_refuses_to_replace_a_real_folder_with_files(tmp_path: Path) -> None:
    repo, _ = make_repo(tmp_path)
    (repo / "data" / "raw").mkdir(parents=True)
    (repo / "data" / "raw" / "keep.csv").write_text("k", encoding="utf-8")

    result = run(repo, "link")

    assert result.returncode == 1
    assert "real folder" in result.stderr
    assert (repo / "data" / "raw" / "keep.csv").is_file()


def test_verify_compares_backup_hashes(tmp_path: Path) -> None:
    repo, raw_backup, archive_backup = tmp_path / "repo", tmp_path / "bk-raw", tmp_path / "bk-arc"
    for path, data in {
        repo / "data/raw/EPA/a.csv": "one",
        repo / "data/raw/EPA/b.csv": "two",
        repo / "archive/x.docx": "doc",
        raw_backup / "EPA/a.csv": "one",
        raw_backup / "EPA/b.csv": "TWO",
    }.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding="utf-8")
    archive_backup.mkdir()
    (repo / ".env").write_text(
        f"CLEAR_BACKUP_RAW_DIR={raw_backup}\nCLEAR_BACKUP_ARCHIVE_DIR={archive_backup}\n",
        encoding="utf-8",
    )
    subprocess.run([sys.executable, str(INVENTORY), "--root", str(repo)], check=True)

    everything = run(repo, "verify")
    one_file = run(repo, "verify", "--folder", "data/raw/EPA/a.csv")

    assert everything.returncode == 1
    assert "data/raw/EPA: ok 1, mismatched 1" in everything.stdout
    assert "archive: missing 1" in everything.stdout
    assert "total: ok 1, missing 1, mismatched 1, unhashed 0" in everything.stdout
    assert (raw_backup / "EPA/b.csv").read_text(encoding="utf-8") == "TWO"  # never overwritten
    assert one_file.returncode == 0, one_file.stdout


def test_missing_target_is_refused(tmp_path: Path) -> None:
    repo, store = make_repo(tmp_path)
    shutil.rmtree(store)

    result = run(repo, "link")

    assert result.returncode == 1
    assert "not found" in result.stderr
    assert not (repo / "data" / "raw").exists()
