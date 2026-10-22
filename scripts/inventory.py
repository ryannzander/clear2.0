"""Inventory every original file and map it to its text mirror or data card.

Scans ``archive/``, ``data/raw/``, ``data/prior/``, ``inbox/`` and the two legacy folders,
then writes:

- ``manifests/inventory.csv`` — one row per original: path, area, bytes, sha256,
  modified_utc, kind, mirror, status (mapped | unmapped | stale | superseded | junk).
  Local only (gitignored): it has a row per file, far too many for git.
- ``manifests/inventory-summary.csv`` — one row per dataset folder (area folder + one
  level): file count, bytes, status counts. Committed; this is what agents read first.
- ``knowledge/_sources.json`` — source path (and every alias) -> mirror path + sha256,
  built from the frontmatter of every ``knowledge/**/*.md``.

Hashes are reused from the previous inventory when size and mtime are unchanged, so
re-runs only hash new or modified files. An area whose drive is unplugged (its junction
target is missing) keeps its rows from the previous inventory instead of losing them.

Usage::

    uv run python scripts/inventory.py            # rebuild all three files
    uv run python scripts/inventory.py --check    # write nothing; exit 1 if out of date
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    AREA_DIRS,
    INVENTORY_COLUMNS,
    INVENTORY_CSV,
    INVENTORY_SUMMARY_CSV,
    KNOWLEDGE_DIR,
    REPO_ROOT,
    SOURCES_JSON,
    FileEntry,
    iter_originals,
    iter_repo_markdown,
    offline_area_dirs,
    read_frontmatter,
    sha256_path,
    summary_folder,
    to_rel,
)

HashMode = Literal["all", "needed"]
STATUSES: tuple[str, ...] = ("mapped", "unmapped", "stale", "superseded", "junk")
SUMMARY_COLUMNS: tuple[str, ...] = ("folder", "area", "files", "bytes", *STATUSES)

LINK_RE = re.compile(r"\]\(\s*<([^>]+)>\s*\)|\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
CODE_RE = re.compile(r"`([^`]+)`")
ENTRY_RE = re.compile(r"^\s*[-*]\s+")
AREA_PREFIXES: tuple[str, ...] = tuple(d for dirs in AREA_DIRS.values() for d in dirs)


@dataclass(frozen=True)
class SourceEntry:
    """What a mirror or data card's frontmatter says about one original."""

    mirror: str
    sha256: str | None  # None for aliases: their hash was not recorded at conversion
    superseded: bool
    alias_of: str | None = None


def load_sources(root: Path) -> dict[str, SourceEntry]:
    """Read every knowledge/ markdown frontmatter into source/alias -> SourceEntry."""
    sources: dict[str, SourceEntry] = {}
    kdir = root / KNOWLEDGE_DIR
    if not kdir.is_dir():
        return sources
    for md in sorted(kdir.rglob("*.md")):
        if md.name == "INDEX.md" or md.name.startswith("_"):
            continue
        fm = read_frontmatter(md)
        if not fm or not isinstance(fm.get("source"), str):
            continue
        mirror = to_rel(md, root)
        source = str(fm["source"]).replace("\\", "/")
        superseded = str(fm.get("status", "current")).lower() == "superseded"
        sha = fm.get("sha256")
        sources[source] = SourceEntry(mirror, str(sha) if sha else None, superseded)
        for alias in fm.get("aliases") or []:
            alias_path = str(alias).replace("\\", "/")
            sources.setdefault(alias_path, SourceEntry(mirror, None, superseded, source))
    return sources


def _resolve_ref(raw: str, index_dir: str) -> str | None:
    ref = unquote(raw.strip()).split("#", 1)[0].replace("\\", "/").rstrip("/")
    if not ref or "://" in ref:
        return None
    if ref.startswith(AREA_PREFIXES):
        return ref
    parts: list[str] = []
    for seg in f"{index_dir}/{ref}".split("/"):
        if seg in ("", "."):
            continue
        if seg == "..":
            if parts:
                parts.pop()
            continue
        parts.append(seg)
    return "/".join(parts)


def _covers_whole_area(ref: str) -> bool:
    """Return True for an area root (``data/raw``) or any folder above one (``data``).

    INDEX files name these to describe the layout; such a link must not count as mapping
    every file below it.
    """
    return any(d == ref or d.startswith(ref + "/") or not ref for d in AREA_PREFIXES)


def _entry_ref(line: str) -> str | None:
    """Return the path an INDEX entry line maps: its first link or code span.

    Only list items (``- [name](path) — ...``) are entries; paths named in prose map nothing.
    """
    if not ENTRY_RE.match(line):
        return None
    hits = [(m.start(), m.group(1) or m.group(2)) for m in LINK_RE.finditer(line)]
    hits += [(m.start(), m.group(1)) for m in CODE_RE.finditer(line)]
    return min(hits)[1] if hits else None


def load_index_refs(root: Path) -> dict[str, bool]:
    """Collect the path each INDEX.md entry maps -> True if that line says 'superseded'.

    References to an area root or above are ignored (see ``_covers_whole_area``).
    """
    refs: dict[str, bool] = {}
    for index in iter_repo_markdown(root, name="INDEX.md"):
        index_dir = to_rel(index.parent, root) if index.parent != root else ""
        for line in index.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            raw = _entry_ref(line)
            ref = _resolve_ref(raw, index_dir) if raw else None
            if ref and not _covers_whole_area(ref):
                refs[ref] = refs.get(ref, False) or "superseded" in line.lower()
    return refs


def _index_hit(path: str, refs: dict[str, bool]) -> bool | None:
    """Return superseded-flag if ``path`` (or a parent folder) is referenced, else None."""
    probe = path
    while probe:
        if probe in refs:
            return refs[probe]
        probe = probe.rsplit("/", 1)[0] if "/" in probe else ""
    return None


def load_previous(root: Path) -> dict[str, dict[str, str]]:
    """Rows of the previous inventory, by path."""
    csv_path = root / INVENTORY_CSV
    if not csv_path.is_file():
        return {}
    with csv_path.open(encoding="utf-8", newline="") as fh:
        return {r["path"]: r for r in csv.DictReader(fh)}


def _lookup(
    path: str, sources: dict[str, SourceEntry], lowered: dict[str, SourceEntry]
) -> SourceEntry | None:
    """Find the mirror/card for ``path``: exact match first, then the nearest parent folder.

    A data card whose ``source`` is a dataset folder covers every file below it (raw datasets
    can hold thousands of files). Folder matches carry no hash: per-file hashes live in the
    inventory, so a folder card is never "stale" because one file changed. ``lowered`` is
    ``sources`` keyed by lowercase path, for case-insensitive (Windows) matches.
    """
    probe = path
    while probe:
        hit = sources.get(probe) or lowered.get(probe.lower())
        if hit is not None:
            return hit if probe == path else replace(hit, sha256=None)
        probe = probe.rsplit("/", 1)[0] if "/" in probe else ""
    return None


def _hash(root: Path, entry: FileEntry, previous: dict[str, dict[str, str]]) -> str:
    old = previous.get(entry.path)
    if (
        old
        and old["sha256"]
        and old["bytes"] == str(entry.bytes)
        and old["modified_utc"] == entry.modified_utc
    ):
        return old["sha256"]
    return sha256_path(root / entry.path)


def _carried_over(
    previous: dict[str, dict[str, str]], offline: list[str]
) -> list[tuple[FileEntry, str]]:
    """Previous rows under offline area folders, as (entry, sha256), so they are not lost."""
    prefixes = tuple(d + "/" for d in offline)
    return [
        (
            FileEntry(r["path"], r["area"], int(r["bytes"]), r["modified_utc"], r["kind"]),
            r["sha256"],
        )
        for path, r in previous.items()
        if path.startswith(prefixes)
    ]


def classify_status(
    entry: FileEntry, sha: str, source: SourceEntry | None, index_hit: bool | None
) -> str:
    """Decide mapped | unmapped | stale | superseded | junk for one original."""
    if entry.kind == "junk":
        return "junk"
    if source is not None:
        if source.sha256 and sha and source.sha256 != sha:
            return "stale"
        return "superseded" if source.superseded else "mapped"
    if index_hit is not None:
        return "superseded" if index_hit else "mapped"
    return "unmapped"


def build_rows(root: Path, hash_mode: HashMode = "all") -> list[dict[str, str]]:
    """Scan originals and return inventory rows (sorted by path).

    ``hash_mode="needed"`` only hashes files that have a recorded mirror hash to compare
    against (fast path for check_maps); other rows get an empty sha256. Rows under an
    offline area folder are carried over from the previous inventory.
    """
    sources = load_sources(root)
    lowered = {k.lower(): v for k, v in sources.items()}
    refs = load_index_refs(root)
    previous = load_previous(root)
    # (entry, known sha256); None means hash it below.
    entries: list[tuple[FileEntry, str | None]] = [(e, None) for e in iter_originals(root)]
    entries += _carried_over(previous, offline_area_dirs(root))
    rows: list[dict[str, str]] = []
    for entry, known_sha in entries:
        source = _lookup(entry.path, sources, lowered)
        needs_hash = hash_mode == "all" or bool(source and source.sha256)
        if known_sha is not None:
            sha = known_sha
        else:
            sha = _hash(root, entry, previous) if needs_hash else ""
        status = classify_status(entry, sha, source, _index_hit(entry.path, refs))
        rows.append(
            {
                "path": entry.path,
                "area": entry.area,
                "bytes": str(entry.bytes),
                "sha256": sha,
                "modified_utc": entry.modified_utc,
                "kind": entry.kind,
                "mirror": source.mirror if source else "",
                "status": status,
            }
        )
    return sorted(rows, key=lambda r: r["path"])


def render_csv(rows: list[dict[str, str]]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(INVENTORY_COLUMNS), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def render_summary(rows: list[dict[str, str]]) -> str:
    """One row per dataset folder: file count, bytes and status counts."""
    folders: dict[str, dict[str, int | str]] = {}
    for r in rows:
        key = summary_folder(r["path"])
        agg = folders.setdefault(
            key,
            {
                "folder": key,
                "area": r["area"],
                "files": 0,
                "bytes": 0,
                **dict.fromkeys(STATUSES, 0),
            },
        )
        agg["files"] = int(agg["files"]) + 1
        agg["bytes"] = int(agg["bytes"]) + int(r["bytes"])
        agg[r["status"]] = int(agg[r["status"]]) + 1
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(SUMMARY_COLUMNS), lineterminator="\n")
    writer.writeheader()
    writer.writerows(folders[k] for k in sorted(folders))
    return buf.getvalue()


def render_sources(root: Path) -> str:
    sources = load_sources(root)
    payload: dict[str, dict[str, str | None]] = {}
    for path in sorted(sources):
        s = sources[path]
        item: dict[str, str | None] = {"mirror": s.mirror, "sha256": s.sha256}
        if s.alias_of:
            item["alias_of"] = s.alias_of
        payload[path] = item
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def render_all(root: Path, rows: list[dict[str, str]]) -> dict[Path, str]:
    """Every generated file -> its content."""
    return {
        root / INVENTORY_CSV: render_csv(rows),
        root / INVENTORY_SUMMARY_CSV: render_summary(rows),
        root / SOURCES_JSON: render_sources(root),
    }


def write_inventory(root: Path) -> tuple[bool, list[dict[str, str]]]:
    """Rebuild the inventory, its summary and _sources.json. Returns (changed, rows)."""
    rows = build_rows(root)
    changed = False
    for path, content in render_all(root, rows).items():
        if _read(path) != content:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
            changed = True
    return changed, rows


def is_current(root: Path) -> bool:
    """Return True if every generated file matches the files on disk."""
    return all(
        _read(path) == content for path, content in render_all(root, build_rows(root)).items()
    )


def _summary(rows: list[dict[str, str]]) -> str:
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    detail = ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "no files"
    return f"{len(rows)} originals: {detail}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument(
        "--root", type=Path, default=REPO_ROOT, help="repo root (default: this repo)"
    )
    parser.add_argument("--check", action="store_true", help="write nothing; exit 1 if out of date")
    args = parser.parse_args(argv)
    root: Path = args.root.resolve()
    for folder in offline_area_dirs(root):
        print(
            f"inventory: {folder} is offline (link target missing — drive unplugged?); "
            "keeping its rows from the last inventory. Check: uv run python scripts/storage.py",
            file=sys.stderr,
        )
    if args.check:
        if is_current(root):
            print("inventory: up to date")
            return 0
        print("inventory: out of date — run `uv run python scripts/inventory.py`", file=sys.stderr)
        return 1
    changed, rows = write_inventory(root)
    print(f"inventory: {'updated' if changed else 'unchanged'} — {_summary(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
