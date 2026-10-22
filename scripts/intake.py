"""File new originals from inbox/ (and the legacy folders) into archive/ and data/raw/.

This is the ONLY sanctioned writer into the protected folders (AGENTS.md hard rule 1).

Two steps, with a human/agent edit in between::

    uv run python scripts/intake.py plan [--legacy]   # writes inbox/_plan.yaml
    # Librarian reviews/edits inbox/_plan.yaml (dest paths, skip, delete)
    uv run python scripts/intake.py apply inbox/_plan.yaml

``apply`` validates the whole plan before touching anything: sources must exist and live
in inbox/ or a legacy folder (no ``..``, no duplicates), destinations must be new paths
under archive/ or data/raw/ and online (data/raw is usually a junction to another drive),
and only junk files may be deleted. A move within one drive is a rename; across drives it
is copy -> verify sha256 -> delete source, so a bad copy never costs the original. Every
action is logged to ``manifests/intake-log.csv``; the inventory is rebuilt at the end.
"""

from __future__ import annotations

import argparse
import csv
import os
import posixpath
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    INBOX_IGNORED,
    INTAKE_LOG_CSV,
    LEGACY_DOCS,
    LEGACY_RAW,
    REPO_ROOT,
    FileEntry,
    area_of,
    classify_kind,
    is_offline,
    iter_originals,
    sha256_path,
    utc_now,
)
from inventory import write_inventory  # noqa: E402

PLAN_PATH = "inbox/_plan.yaml"
INTAKE_SOURCE_AREAS: frozenset[str] = frozenset({"inbox", "legacy"})
INTAKE_ROOTS: tuple[str, ...] = ("inbox", LEGACY_DOCS, LEGACY_RAW)
DEST_ROOTS: tuple[str, ...] = ("archive/", "data/raw/")
LOG_COLUMNS: tuple[str, ...] = ("time_utc", "action", "src", "dest", "sha256")

# Path words that mark competition / pitch material (fenced off per the scope decision).
COMPETITION_WORDS: tuple[str, ...] = (
    "cayia",
    "conrad",
    "pitch",
    "olympiad",
    "competition",
    "award",
    "gala",
)

PLAN_HEADER = """\
# Intake plan — review before applying.
# Edit `dest`, or set `action` to skip | delete (delete is allowed for junk only).
# Apply with: uv run python scripts/intake.py apply inbox/_plan.yaml
"""


@dataclass(frozen=True)
class PlanItem:
    """One proposed intake action."""

    src: str
    action: str  # move | delete | skip
    dest: str
    kind: str
    reason: str


class PlanError(Exception):
    """Raised on a rejected plan (nothing moved) or a failed copy (that source is kept).

    Items applied before a failed copy stay applied and are logged.
    """


# --------------------------------------------------------------------------- plan


def _source_root(rel: str) -> str:
    for base in ("inbox", LEGACY_DOCS, LEGACY_RAW):
        if rel.startswith(base + "/"):
            return base
    raise ValueError(f"not an intake source: {rel}")


def _is_competition(rel: str, kind: str) -> bool:
    low = rel.lower()
    return kind == "media" or any(word in low for word in COMPETITION_WORDS)


def propose(entry: FileEntry) -> PlanItem:
    """Apply the simple filing rules to one inbox/legacy file."""
    if entry.kind == "junk":
        return PlanItem(entry.path, "delete", "", entry.kind, "macOS/Office junk")
    base = _source_root(entry.path)
    inner = entry.path[len(base) + 1 :]
    if base == LEGACY_RAW:
        dest, reason = f"data/raw/{inner}", "from RAW Data"
    elif entry.kind == "data":
        dest, reason = f"data/raw/{inner}", "dataset"
    elif _is_competition(entry.path, entry.kind):
        dest, reason = f"archive/competitions/{inner}", "competition/pitch/video material"
    else:
        dest, reason = f"archive/{inner}", f"{entry.kind} document"
    return PlanItem(entry.path, "move", dest, entry.kind, reason)


def build_plan(root: Path, include_legacy: bool) -> list[PlanItem]:
    """Propose an action for every file waiting in inbox/ (and legacy folders)."""
    areas = {"inbox", "legacy"} if include_legacy else {"inbox"}
    items = [propose(e) for e in iter_originals(root) if e.area in areas]
    return _mark_conflicts(root, items)


def _mark_conflicts(root: Path, items: list[PlanItem]) -> list[PlanItem]:
    seen: set[str] = set()
    out: list[PlanItem] = []
    for item in items:
        key = item.dest.lower()
        if item.action == "move" and ((root / item.dest).exists() or key in seen):
            item = PlanItem(
                item.src, "skip", item.dest, item.kind, "CONFLICT: dest exists — pick a new dest"
            )
        seen.add(key)
        out.append(item)
    return out


def write_plan(root: Path, items: list[PlanItem]) -> Path:
    path = root / PLAN_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    body = yaml.safe_dump([vars(i) for i in items], sort_keys=False, allow_unicode=True, width=120)
    path.write_text(PLAN_HEADER + body, encoding="utf-8", newline="\n")
    return path


# -------------------------------------------------------------------------- apply


def load_plan(path: Path) -> list[PlanItem]:
    data: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "items" in data:
        data = data["items"]
    if not isinstance(data, list):
        raise PlanError(f"{path}: expected a list of items")
    items: list[PlanItem] = []
    for raw in data:
        if not isinstance(raw, dict):
            raise PlanError(f"{path}: every item must be a mapping")
        items.append(
            PlanItem(
                src=str(raw.get("src", "")).replace("\\", "/"),
                action=str(raw.get("action", "")),
                dest=str(raw.get("dest") or "").replace("\\", "/"),
                kind=str(raw.get("kind", "")),
                reason=str(raw.get("reason", "")),
            )
        )
    return items


def validate(root: Path, items: list[PlanItem]) -> list[str]:
    """Return every problem with the plan; an empty list means it is safe to apply."""
    problems: list[str] = []
    dests: set[str] = set()
    srcs: set[str] = set()
    for i in items:
        if i.action == "skip":
            continue
        if i.src.lower() in srcs:
            problems.append(f"{i.src}: listed twice")
            continue
        srcs.add(i.src.lower())
        problems.extend(_validate_item(root, i, dests))
    for d in DEST_ROOTS:
        if any(i.action == "move" and i.dest.startswith(d) for i in items) and is_offline(
            root / d.rstrip("/")
        ):
            problems.append(f"{d} is offline (drive unplugged?) — check scripts/storage.py")
    return problems


def _validate_item(root: Path, i: PlanItem, dests: set[str]) -> list[str]:
    if i.action not in ("move", "delete"):
        return [f"{i.src}: unknown action '{i.action}'"]
    if posixpath.normpath(i.src) != i.src or area_of(i.src) not in INTAKE_SOURCE_AREAS:
        return [f"{i.src}: source must be a plain path in inbox/ or a legacy folder (no '..')"]
    if i.src.lower() in {p.lower() for p in (*INTAKE_ROOTS, *INBOX_IGNORED)}:
        return [f"{i.src}: not an intake source (a source root or a tooling file)"]
    if not (root / i.src).exists():
        return [f"{i.src}: source not found"]
    if i.action == "delete":
        name = i.src.rsplit("/", 1)[-1]
        ok = classify_kind(name) == "junk"
        return [] if ok else [f"{i.src}: refusing to delete a non-junk file"]
    if not i.dest.startswith(DEST_ROOTS) or ".." in i.dest.split("/"):
        return [f"{i.src}: dest must be under archive/ or data/raw/ (got '{i.dest}')"]
    if (root / i.dest).exists():
        return [f"{i.src}: dest already exists, refusing to overwrite: {i.dest}"]
    if i.dest.lower() in dests:
        return [f"{i.src}: two items share dest {i.dest}"]
    dests.add(i.dest.lower())
    return []


def _same_drive(src: Path, dest_dir: Path) -> bool:
    """Return True if a rename can move ``src`` into ``dest_dir`` (junctions followed)."""
    return os.stat(src).st_dev == os.stat(dest_dir).st_dev


def _remove(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def _move(root: Path, item: PlanItem) -> str:
    """Move one original, hash-verified; the source is deleted only after a good copy."""
    src, dest = root / item.src, root / item.dest
    before = sha256_path(src)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if _same_drive(src, dest.parent):
        os.rename(src, dest)
        after = sha256_path(dest)
    else:
        try:  # a failed or partial copy (disk full, unplugged) must not stay as an "original"
            if src.is_dir():
                shutil.copytree(src, dest)
            else:
                shutil.copy2(src, dest)
            after = sha256_path(dest)
        except BaseException:
            if dest.exists():
                _remove(dest)
            raise
    if after != before:
        if src.exists():  # cross-drive copy: drop the bad copy, keep the original
            _remove(dest)
        raise PlanError(f"sha256 mismatch moving {item.src} -> {item.dest}; source kept")
    if src.exists():
        _remove(src)
    return after


def _delete(root: Path, item: PlanItem) -> str:
    path = root / item.src
    digest = sha256_path(path)
    _remove(path)
    return digest


def _prune_empty_parents(root: Path, rel: str) -> None:
    """Remove now-empty source folders, never inbox/ itself."""
    current = (root / rel).parent
    stop = {root.resolve(), (root / "inbox").resolve()}
    while current.resolve() not in stop and current.is_dir() and not any(current.iterdir()):
        current.rmdir()
        current = current.parent


def _log(root: Path, rows: list[dict[str, str]]) -> None:
    path = root / INTAKE_LOG_CSV
    new = not path.is_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(LOG_COLUMNS), lineterminator="\n")
        if new:
            writer.writeheader()
        writer.writerows(rows)


def apply_plan(root: Path, items: list[PlanItem]) -> list[dict[str, str]]:
    """Validate, then execute every move/delete. Returns the log rows written."""
    problems = validate(root, items)
    if problems:
        raise PlanError("plan rejected, nothing moved:\n  " + "\n  ".join(problems))
    rows: list[dict[str, str]] = []
    try:
        for item in items:
            if item.action == "skip":
                continue
            digest = _move(root, item) if item.action == "move" else _delete(root, item)
            rows.append(
                {
                    "time_utc": utc_now(),
                    "action": item.action,
                    "src": item.src,
                    "dest": item.dest if item.action == "move" else "",
                    "sha256": digest,
                }
            )
            _prune_empty_parents(root, item.src)
    finally:
        if rows:
            _log(root, rows)
            write_inventory(root)
    return rows


# --------------------------------------------------------------------------- CLI


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument(
        "--root", type=Path, default=REPO_ROOT, help="repo root (default: this repo)"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    p_plan = sub.add_parser("plan", help=f"propose actions, write {PLAN_PATH}")
    p_plan.add_argument("--legacy", action="store_true", help="also plan the two legacy folders")
    p_apply = sub.add_parser("apply", help="validate and execute a plan file")
    p_apply.add_argument("plan", type=Path, help=f"plan file (usually {PLAN_PATH})")
    args = parser.parse_args(argv)
    root: Path = args.root.resolve()

    if args.command == "plan":
        items = build_plan(root, include_legacy=args.legacy)
        path = write_plan(root, items)
        conflicts = sum(1 for i in items if i.reason.startswith("CONFLICT"))
        print(f"intake: {len(items)} items planned ({conflicts} conflicts) -> {path}")
        return 0

    plan_path = args.plan if args.plan.is_absolute() else root / args.plan
    try:
        rows = apply_plan(root, load_plan(plan_path))
    except PlanError as exc:
        print(f"intake: {exc}", file=sys.stderr)
        return 1
    moved = sum(1 for r in rows if r["action"] == "move")
    print(f"intake: moved {moved}, deleted {len(rows) - moved}; inventory rebuilt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
