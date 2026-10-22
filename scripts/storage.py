r"""Link the big data stores into the repo and report whether their drives are online.

Raw data and prior pipeline outputs do not fit on the repo drive, so ``data/raw`` and
``data/prior`` are junctions (Windows) or symlinks to folders on other drives. Every tool,
data card and hook keeps using the repo paths. Targets come from the repo-root ``.env``
(gitignored: they are one machine's paths)::

    CLEAR_RAW_DIR=E:\CLEAR 2.0\RAW Data             data/raw   -> working copy
    CLEAR_PRIOR_DIR=D:\CLEAR 2.0\Cleaned Data       data/prior -> read-only reference
    CLEAR_BACKUP_RAW_DIR=D:\CLEAR 2.0\RAW Data      backup of data/raw  (/backup-check)
    CLEAR_BACKUP_ARCHIVE_DIR=D:\CLEAR 2.0\archive   backup of archive/  (/backup-check)

Usage::

    uv run python scripts/storage.py                # status; exit 1 if a store is offline
    uv run python scripts/storage.py link           # create missing links from .env
    uv run python scripts/storage.py link --relink  # re-point links whose target changed
    uv run python scripts/storage.py verify         # hash every backup copy vs inventory.csv
    uv run python scripts/storage.py verify --folder "data/raw/NOAA"   # one dataset only
"""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    INVENTORY_CSV,
    REPO_ROOT,
    is_offline,
    sha256_path,
    summary_folder,
)

ENV_FILE = ".env"
# Repo folder -> .env key holding its link target.
LINKS: dict[str, str] = {"data/raw": "CLEAR_RAW_DIR", "data/prior": "CLEAR_PRIOR_DIR"}
# Repo folder -> .env key holding its backup folder (same layout below it).
BACKUPS: dict[str, str] = {
    "data/raw": "CLEAR_BACKUP_RAW_DIR",
    "archive": "CLEAR_BACKUP_ARCHIVE_DIR",
}
BYTES_PER_GB = 1024**3
BACKUP_STATES: tuple[str, ...] = ("ok", "missing", "mismatched", "unhashed")


def read_env(root: Path) -> dict[str, str]:
    """Parse ``KEY=VALUE`` lines of the repo-root .env (no escapes; quotes stripped)."""
    path = root / ENV_FILE
    if not path.is_file():
        return {}
    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip().strip("\"'")
    return env


def is_link(path: Path) -> bool:
    """Return True for a symlink or a Windows junction, dangling or not."""
    if path.is_symlink():
        return True
    isjunction = getattr(os.path, "isjunction", None)  # Python 3.12+
    if isjunction is not None:
        return bool(isjunction(path))
    expected = os.path.join(os.path.realpath(path.parent), path.name)
    return os.path.normcase(os.path.realpath(path)) != os.path.normcase(expected)


def make_link(link: Path, target: Path) -> None:
    """Create a directory link: a junction on Windows (no admin needed), else a symlink."""
    link.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            check=True,
            capture_output=True,
        )
    else:
        link.symlink_to(target, target_is_directory=True)


def remove_link(link: Path) -> None:
    """Remove the link itself, never what it points to."""
    if link.is_symlink():
        link.unlink()
    else:
        os.rmdir(link)  # on a junction this removes only the junction


def _same(a: str | Path, b: str | Path) -> bool:
    return os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


def link_one(root: Path, rel: str, target_raw: str, relink: bool) -> str:
    """Create or check one link. Returns a status line; raises SystemExit on refusal."""
    link, target = root / rel, Path(target_raw)
    if not target.is_dir():
        raise SystemExit(
            f"storage: {rel}: target {target} not found — drive unplugged or path wrong"
        )
    if is_link(link) or is_offline(link):
        current = os.path.realpath(link)
        if _same(current, target):
            return f"{rel}: ok -> {target}"
        if not relink:
            raise SystemExit(
                f"storage: {rel} points at {current}, .env says {target}. "
                "Rerun with --relink to re-point it."
            )
        remove_link(link)
    elif link.exists():
        if any(link.iterdir()):
            raise SystemExit(
                f"storage: {rel} is a real folder with files in it. Move them to {target} "
                "(or empty it) first; this script never moves or deletes data."
            )
        link.rmdir()
    make_link(link, target)
    return f"{rel}: linked -> {target}"


def status_lines(root: Path, env: dict[str, str]) -> tuple[list[str], bool]:
    """One line per store and backup. Returns (lines, all configured stores online)."""
    lines: list[str] = []
    healthy = True
    for rel, key in LINKS.items():
        link = root / rel
        if key not in env:
            lines.append(f"{rel:<11} not configured ({key} missing from .env)")
        elif is_offline(link):
            healthy = False
            lines.append(f"{rel:<11} OFFLINE -> {env[key]} (plug in the drive)")
        elif not (is_link(link) or link.exists()):
            healthy = False
            lines.append(f"{rel:<11} not linked (run: uv run python scripts/storage.py link)")
        else:
            free = shutil.disk_usage(link).free / BYTES_PER_GB
            where = os.path.realpath(link) if is_link(link) else "in repo"
            lines.append(f"{rel:<11} online -> {where} ({free:,.0f} GB free)")
    for rel, key in BACKUPS.items():
        if key in env:
            backup = Path(env[key])
            if backup.is_dir():
                state = "online"
            elif Path(backup.anchor or ".").exists():
                state = "not created yet (first /backup-check copy creates it)"
            else:
                state = "offline"
            lines.append(f"backup of {rel}: {state} -> {backup}")
    return lines, healthy


def _online_backups(env: dict[str, str]) -> dict[str, Path] | None:
    """Repo folder -> backup folder, or None (with a message) if a backup drive is missing."""
    backups = {rel: Path(env[key]) for rel, key in BACKUPS.items() if key in env}
    offline = [str(b) for b in backups.values() if not Path(b.anchor or ".").exists()]
    if offline or not backups:
        missing = offline or list(BACKUPS.values())
        print(f"storage: backup drive offline or not configured: {missing}")
        return None
    return backups


def _backup_states(
    inventory: Path, backups: dict[str, Path], prefix: str
) -> Iterator[tuple[str, str]]:
    """Yield (path, ok|missing|mismatched|unhashed) per backed-up inventory row, in order."""
    with inventory.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):  # sorted by path, so each folder is contiguous
            path = row["path"]
            rel = next((r for r in backups if path.startswith(r + "/")), None)
            if rel is None or row["kind"] == "junk" or not path.startswith(prefix):
                continue
            copy = backups[rel] / path[len(rel) + 1 :]
            if not row["sha256"]:
                yield path, "unhashed"
            elif not copy.is_file() and not copy.is_dir():
                yield path, "missing"
            else:
                yield path, "ok" if sha256_path(copy) == row["sha256"] else "mismatched"


def _counts_line(label: str, counts: dict[str, int]) -> str:
    return f"{label}: " + ", ".join(f"{k} {v}" for k, v in counts.items() if v or label == "total")


def verify(root: Path, env: dict[str, str], prefix: str) -> int:
    """Hash each backed-up original's backup copy against its inventory sha256.

    Prints one line per dataset folder as it finishes, then the first problem paths.
    Read-only on both sides. Returns 1 if anything is missing or mismatched.
    """
    backups = _online_backups(env)
    inventory = root / INVENTORY_CSV
    if backups is None:
        return 1
    if not inventory.is_file():
        print("storage: no manifests/inventory.csv — run scripts/inventory.py first")
        return 1
    problems: dict[str, list[str]] = {"missing": [], "mismatched": []}
    totals: dict[str, int] = dict.fromkeys(BACKUP_STATES, 0)
    folder, counts = "", dict.fromkeys(totals, 0)
    for path, state in _backup_states(inventory, backups, prefix):
        if summary_folder(path) != folder:
            if folder:
                print(_counts_line(folder, counts), flush=True)
            folder, counts = summary_folder(path), dict.fromkeys(totals, 0)
        counts[state] += 1
        totals[state] += 1
        problems.get(state, []).append(path)
    if folder:
        print(_counts_line(folder, counts))
    print(_counts_line("total", totals))
    for state, paths in problems.items():
        if paths:
            print(f"{state} (first 20 of {len(paths)}):", *paths[:20], sep="\n  ")
    return 1 if totals["missing"] or totals["mismatched"] else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument(
        "command", nargs="?", choices=("status", "link", "verify"), default="status"
    )
    parser.add_argument("--relink", action="store_true", help="re-point links to the .env target")
    parser.add_argument("--folder", default="", help="verify: only paths starting with this")
    parser.add_argument(
        "--root", type=Path, default=REPO_ROOT, help="repo root (default: this repo)"
    )
    args = parser.parse_args(argv)
    root: Path = args.root.absolute()
    env = read_env(root)
    if args.command == "link":
        configured = {rel: env[key] for rel, key in LINKS.items() if key in env}
        if not configured:
            print(f"storage: no link targets in .env ({', '.join(LINKS.values())})")
            return 1
        for rel, target in configured.items():
            print(link_one(root, rel, target, args.relink))
        return 0
    if args.command == "verify":
        return verify(root, env, args.folder.replace("\\", "/"))
    lines, healthy = status_lines(root, env)
    print("\n".join(lines))
    return 0 if healthy else 1


if __name__ == "__main__":
    raise SystemExit(main())
