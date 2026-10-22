"""Check that the repo maps are complete, fresh and within budget.

Fails (exit 1) when:

- an original in ``archive/``, ``data/raw/`` or ``data/prior/`` is unmapped (no mirror/data
  card and not listed in an INDEX.md), is stale (mirror sha256 differs from the source), or
  is junk — reported once per dataset folder;
- a markdown file is over its size budget (AGENTS.md rule 11);
- a ``decisions/NNNN-*.md`` link in ``methodology/`` points at a missing ADR;
- a map file named in AGENTS.md's repo map does not exist;
- a mirror or data card in ``knowledge/`` lacks the required frontmatter.

Files still waiting in ``inbox/`` or the legacy folders are reported, not failed: they
are pending intake by definition.

Usage::

    uv run python scripts/check_maps.py         # local / pre-commit (needs originals)
    uv run python scripts/check_maps.py --ci    # skip checks that need protected folders
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    KNOWLEDGE_DIR,
    REPO_ROOT,
    iter_repo_markdown,
    read_frontmatter,
    summary_folder,
    to_rel,
)
from inventory import build_rows  # noqa: E402

# Size budgets in lines — AGENTS.md hard rule 11.
AGENTS_MD_MAX_LINES = 150
INDEX_MD_MAX_LINES = 100
STATUS_MD_MAX_LINES = 60
DOCS_MD_MAX_LINES = 200

FAILING_AREAS: frozenset[str] = frozenset({"archive", "raw", "prior"})
PENDING_AREAS: frozenset[str] = frozenset({"inbox", "legacy"})
# One line per (status, dataset folder): a 100k-file dataset must not print 100k lines.
PROBLEM_LINES: dict[str, str] = {
    "unmapped": "unmapped original: {path}{more} — run /map-refresh",
    "stale": "stale mirror: {mirror} (source {path} changed){more}",
    "junk": "junk in originals: {path}{more} — should have been deleted at intake",
}
MIRROR_REQUIRED_KEYS: tuple[str, ...] = ("source", "sha256", "kind", "status")

ADR_LINK_RE = re.compile(r"decisions/(\d{4}-[A-Za-z0-9._-]+?\.md)")
CODE_RE = re.compile(r"`([^`]+)`")


def _line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8-sig", errors="replace").splitlines())


def check_originals(root: Path) -> tuple[list[str], int]:
    """Problems with filed originals (one line per dataset folder) + count pending intake."""
    groups: dict[tuple[str, str], list[dict[str, str]]] = {}
    pending = 0
    for row in build_rows(root, hash_mode="needed"):
        if row["area"] in PENDING_AREAS:
            pending += 1
            continue
        if row["area"] in FAILING_AREAS and row["status"] in PROBLEM_LINES:
            groups.setdefault((row["status"], summary_folder(row["path"])), []).append(row)
    problems: list[str] = []
    for (status, folder), rows in sorted(groups.items()):
        more = f" (+{len(rows) - 1} more in {folder})" if len(rows) > 1 else ""
        first = rows[0]
        problems.append(
            PROBLEM_LINES[status].format(path=first["path"], mirror=first["mirror"], more=more)
        )
    return problems, pending


def check_budgets(root: Path) -> list[str]:
    """Files over their line budget."""
    problems: list[str] = []
    fixed = {"AGENTS.md": AGENTS_MD_MAX_LINES, "STATUS.md": STATUS_MD_MAX_LINES}
    for name, limit in fixed.items():
        path = root / name
        if path.is_file() and (n := _line_count(path)) > limit:
            problems.append(f"{name}: {n} lines > budget {limit}")
    for index in iter_repo_markdown(root, name="INDEX.md"):
        if (n := _line_count(index)) > INDEX_MD_MAX_LINES:
            problems.append(
                f"{to_rel(index, root)}: {n} lines > budget {INDEX_MD_MAX_LINES} — split the folder"
            )
    docs = root / "docs"
    if docs.is_dir():
        for md in sorted(docs.rglob("*.md")):
            if (n := _line_count(md)) > DOCS_MD_MAX_LINES:
                problems.append(f"{to_rel(md, root)}: {n} lines > budget {DOCS_MD_MAX_LINES}")
    return problems


def check_adr_links(root: Path) -> list[str]:
    """Every decisions/NNNN-*.md referenced from methodology/ must exist."""
    problems: list[str] = []
    mdir = root / "methodology"
    if not mdir.is_dir():
        return problems
    for md in sorted(mdir.rglob("*.md")):
        text = md.read_text(encoding="utf-8-sig", errors="replace")
        for name in sorted(set(ADR_LINK_RE.findall(text))):
            if not (root / "decisions" / name).is_file():
                problems.append(f"{to_rel(md, root)}: links missing ADR decisions/{name}")
    return problems


def repo_map_targets(agents_md: Path) -> list[str]:
    """Map-column paths from the AGENTS.md repo-map table."""
    targets: list[str] = []
    in_map = False
    for line in agents_md.read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("## "):
            in_map = line.strip().lower() == "## repo map"
            continue
        if not in_map or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3:
            targets.extend(t for t in CODE_RE.findall(cells[2]) if t.endswith(".md"))
    return targets


def check_repo_map(root: Path) -> list[str]:
    agents_md = root / "AGENTS.md"
    if not agents_md.is_file():
        return ["AGENTS.md is missing"]
    return [
        f"AGENTS.md repo map names {t}, which does not exist"
        for t in repo_map_targets(agents_md)
        if not (root / t).is_file()
    ]


def check_frontmatter(root: Path) -> list[str]:
    """Mirrors and data cards must carry the provenance frontmatter."""
    problems: list[str] = []
    kdir = root / KNOWLEDGE_DIR
    for sub in ("docs", "data"):
        base = kdir / sub
        if not base.is_dir():
            continue
        for md in sorted(base.rglob("*.md")):
            if (
                md.name == "INDEX.md"
                or md.name.startswith("_")
                or md.name.endswith(".validation.md")
            ):
                continue
            fm = read_frontmatter(md) or {}
            missing = [k for k in MIRROR_REQUIRED_KEYS if k not in fm]
            if missing:
                problems.append(f"{to_rel(md, root)}: frontmatter missing {', '.join(missing)}")
    return problems


def run_checks(root: Path, ci: bool) -> tuple[list[str], int]:
    problems: list[str] = []
    pending = 0
    if not ci:
        original_problems, pending = check_originals(root)
        problems += original_problems
    problems += check_budgets(root)
    problems += check_adr_links(root)
    problems += check_repo_map(root)
    problems += check_frontmatter(root)
    return problems, pending


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument(
        "--root", type=Path, default=REPO_ROOT, help="repo root (default: this repo)"
    )
    parser.add_argument(
        "--ci", action="store_true", help="skip checks that need the protected folders"
    )
    args = parser.parse_args(argv)
    problems, pending = run_checks(args.root.resolve(), ci=args.ci)
    if pending:
        print(f"check_maps: {pending} file(s) pending intake in inbox/ or legacy folders")
    if problems:
        print("check_maps: FAILED", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print("check_maps: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
