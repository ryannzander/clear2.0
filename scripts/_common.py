"""Shared helpers for the repo tooling scripts (inventory, intake, check_maps).

Stdlib + pyyaml only so the scripts run before the project environment exists.
All paths handed around between functions are repo-relative POSIX strings.
"""

from __future__ import annotations

import hashlib
import os
import re
import unicodedata
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

LEGACY_DOCS = "CLEAR 2.0 (misc docs)"
LEGACY_RAW = "RAW Data"

# Area name -> top-level folder(s). Order matters: "data/raw" before anything shorter.
# data/raw and data/prior are usually junctions to other drives (scripts/storage.py).
AREA_DIRS: dict[str, tuple[str, ...]] = {
    "archive": ("archive",),
    "raw": ("data/raw",),
    "prior": ("data/prior",),
    "inbox": ("inbox",),
    "legacy": (LEGACY_DOCS, LEGACY_RAW),
}

# Folders whose originals are immutable (AGENTS.md hard rule 1).
PROTECTED_DIRS: tuple[str, ...] = ("archive", "data/raw", "data/prior", LEGACY_DOCS, LEGACY_RAW)

# Inbox files that belong to the tooling, not to the research record.
INBOX_IGNORED: frozenset[str] = frozenset({"inbox/README.md", "inbox/_plan.yaml"})

INVENTORY_CSV = "manifests/inventory.csv"  # one row per file; local only (too big for git)
INVENTORY_SUMMARY_CSV = "manifests/inventory-summary.csv"  # one row per dataset folder; committed
INTAKE_LOG_CSV = "manifests/intake-log.csv"
SOURCES_JSON = "knowledge/_sources.json"
KNOWLEDGE_DIR = "knowledge"

INVENTORY_COLUMNS: tuple[str, ...] = (
    "path",
    "area",
    "bytes",
    "sha256",
    "modified_utc",
    "kind",
    "mirror",
    "status",
)

# Read files in 1 MiB chunks so multi-GB grids hash without loading into memory.
HASH_CHUNK_BYTES = 1024 * 1024

ISO_UTC = "%Y-%m-%dT%H:%M:%SZ"

KIND_BY_EXTENSION: dict[str, str] = {
    **dict.fromkeys(("docx", "doc", "pdf", "pptx", "ppt", "md", "txt", "rtf", "odt"), "doc"),
    **dict.fromkeys(
        (
            "csv",
            "tsv",
            "xlsx",
            "xls",
            "nc",
            "grib",
            "grib2",
            "parquet",
            "json",
            "geojson",
            "zarr",
            "h5",
            "hdf",
            "hdf5",
            "tif",
            "tiff",
            "shp",
            "shx",
            "dbf",
            "prj",
            "kml",
            "kmz",
        ),
        "data",
    ),
    **dict.fromkeys(("png", "jpg", "jpeg", "gif", "svg", "webp", "bmp", "heic"), "image"),
    **dict.fromkeys(("mp4", "mov", "m4a", "mp3", "wav", "avi", "mkv", "webm"), "media"),
}

JUNK_NAMES: frozenset[str] = frozenset({".DS_Store", "Thumbs.db", "desktop.ini"})
JUNK_PREFIXES: tuple[str, ...] = ("._", "~$")  # macOS AppleDouble, Office lock files


@dataclass(frozen=True)
class FileEntry:
    """One original file (or one .zarr directory store) found on disk."""

    path: str
    area: str
    bytes: int
    modified_utc: str
    kind: str


def to_rel(path: Path, root: Path) -> str:
    """Return ``path`` relative to ``root`` as a POSIX string.

    Lexical on purpose: ``data/raw`` may be a junction to another drive, and resolving it
    would step outside the repo. Raises ValueError if ``path`` is not under ``root``.
    """
    rel = os.path.relpath(os.path.abspath(path), os.path.abspath(root))
    if rel == os.pardir or rel.startswith(os.pardir + os.sep):
        raise ValueError(f"{path} is not inside {root}")
    return Path(rel).as_posix()


def is_offline(path: Path) -> bool:
    """Return True if ``path`` is a link whose target is missing (e.g. an unplugged drive)."""
    return os.path.lexists(path) and not path.exists()


def offline_area_dirs(root: Path) -> list[str]:
    """Area folders whose link target is currently missing."""
    return [d for dirs in AREA_DIRS.values() for d in dirs if is_offline(root / d)]


def summary_folder(rel: str) -> str:
    """Return the dataset folder a path rolls up to: its area folder plus one level below.

    ``data/raw/NOAA/HRRR/x.grib2`` -> ``data/raw/NOAA``; ``data/raw/README.txt`` -> ``data/raw``.
    """
    for dirs in AREA_DIRS.values():
        for d in dirs:
            if rel.startswith(d + "/"):
                rest = rel[len(d) + 1 :]
                return f"{d}/{rest.split('/', 1)[0]}" if "/" in rest else d
    return rel.rsplit("/", 1)[0] if "/" in rel else ""


def area_of(rel: str) -> str | None:
    """Return the inventory area for a repo-relative path, or None if not scanned."""
    for area, dirs in AREA_DIRS.items():
        for d in dirs:
            if rel == d or rel.startswith(d + "/"):
                return area
    return None


def is_protected(rel: str) -> bool:
    """Return True if a repo-relative path lies inside an immutable originals folder."""
    low = rel.lower()
    return any(low == d.lower() or low.startswith(d.lower() + "/") for d in PROTECTED_DIRS)


def classify_kind(name: str) -> str:
    """Classify a file name as doc|data|image|media|junk|other by name/extension."""
    if name in JUNK_NAMES or name.startswith(JUNK_PREFIXES):
        return "junk"
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    return KIND_BY_EXTENSION.get(ext, "other")


def slugify(text: str) -> str:
    """Lowercase ASCII slug: non-alphanumerics become '-', repeats collapse."""
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")


def slugify_path(rel: str) -> str:
    """Slugify every segment of a path; the extension of the last segment is dropped."""
    parts = rel.split("/")
    stem = parts[-1].rsplit(".", 1)[0] if "." in parts[-1] else parts[-1]
    return "/".join([slugify(p) for p in parts[:-1]] + [slugify(stem)])


def sha256_file(path: Path) -> str:
    """Stream a file through sha256."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(HASH_CHUNK_BYTES):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_path(path: Path) -> str:
    """Hash a file, or a directory store (e.g. .zarr) as sorted (relpath, hash) pairs."""
    if path.is_file():
        return sha256_file(path)
    digest = hashlib.sha256()
    for child in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(sha256_file(child).encode())
    return digest.hexdigest()


def _utc_stamp(epoch: float) -> str:
    stamp = datetime.fromtimestamp(epoch, tz=timezone.utc)  # noqa: UP017 (py3.10)
    return stamp.strftime(ISO_UTC)


def utc_now() -> str:
    """Return the current time as an ISO-8601 UTC string (second precision)."""
    return datetime.now(tz=timezone.utc).strftime(ISO_UTC)  # noqa: UP017 (py3.10)


def _dir_store_stats(path: Path) -> tuple[int, float]:
    files = [p for p in path.rglob("*") if p.is_file()]
    size = sum(p.stat().st_size for p in files)
    mtime = max((p.stat().st_mtime for p in files), default=path.stat().st_mtime)
    return size, mtime


def iter_originals(root: Path) -> Iterator[FileEntry]:
    """Yield every original file under the scanned areas (inbox tooling files excluded)."""
    for area, dirs in AREA_DIRS.items():
        for d in dirs:
            base = root / d
            if base.is_dir():
                yield from _walk_area(root, base, area)


def _walk_area(root: Path, base: Path, area: str) -> Iterator[FileEntry]:
    for dirpath, dirnames, filenames in os.walk(base):
        current = Path(dirpath)
        stores = [d for d in dirnames if d.lower().endswith(".zarr")]
        dirnames[:] = sorted(d for d in dirnames if d not in stores)
        for store in stores:
            size, mtime = _dir_store_stats(current / store)
            rel = to_rel(current / store, root)
            yield FileEntry(rel, area, size, _utc_stamp(mtime), "data")
        for name in sorted(filenames):
            full = current / name
            rel = to_rel(full, root)
            if rel in INBOX_IGNORED:
                continue
            st = full.stat()
            yield FileEntry(rel, area, st.st_size, _utc_stamp(st.st_mtime), classify_kind(name))


def read_frontmatter(md_path: Path) -> dict[str, Any] | None:
    """Parse the leading YAML frontmatter block of a markdown file, if any."""
    try:
        text = md_path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return None
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


# Directories never walked when looking for INDEX.md / markdown files in the repo.
SKIP_WALK_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".venv",
        "node_modules",
        "mlruns",
        "mlartifacts",
        ".ruff_cache",
        ".pytest_cache",
        "__pycache__",
        ".review",
    }
)


def iter_repo_markdown(root: Path, name: str | None = None) -> Iterator[Path]:
    """Yield markdown files in the repo, skipping originals, inbox and tool caches."""
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        rel_dir = "" if current == root else to_rel(current, root)
        dirnames[:] = [
            d
            for d in dirnames
            if d not in SKIP_WALK_DIRS and area_of(f"{rel_dir}/{d}".lstrip("/")) is None
        ]
        for fname in filenames:
            if fname.endswith(".md") and (name is None or fname == name):
                yield current / fname
