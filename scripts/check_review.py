"""Review gate: commits touching gated paths need a passing review of the exact staged diff.

Flow: stage -> /review -> ``check_review.py record --verdict pass ...`` -> commit.
The pre-commit hook runs ``check``. If the staged diff changes after the review (new
edits, a formatter), the hash no longer matches and the change must be reviewed again.
Ryan's own manual commits may bypass with ``CLEAR_SKIP_REVIEW=1``.
Standard: docs/system/04-review-and-commit.md.

Usage:
    uv run python scripts/check_review.py record --verdict pass \
        --reviewer "<provider/model>" --round 1 --notes "..."
    uv run python scripts/check_review.py check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Research code and specs, plus everything that enforces the rules (tooling, hooks, tests,
# CI, pre-commit): an unreviewed commit must not be able to switch the gate off.
GATED = (
    "src/",
    "config/",
    "methodology/",
    "decisions/",
    "research/experiments/",
    "figures/src/",
    "scripts/",
    "tests/",
    ".claude/hooks/",
    ".claude/settings.json",
    ".claude/skills/review/",
    ".claude/agents/reviewer.md",
    ".github/workflows/",
    ".pre-commit-config.yaml",
    ".gitignore",
    ".ignore",
    "pyproject.toml",
    "uv.lock",
)
UNGATED_NAMES = frozenset({"INDEX.md"})  # maps are mechanical
RECORD = Path(".review") / "last.json"


def git(root: Path, *args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, check=True).stdout


def staged_files(root: Path) -> list[str]:
    # --no-renames: a move out of a gated folder lists the old path too, so it stays gated.
    out = git(root, "diff", "--cached", "--name-only", "--no-renames", "-z")
    return [p for p in out.decode("utf-8").split("\0") if p]


def staged_diff_sha256(root: Path) -> str:
    return hashlib.sha256(git(root, "diff", "--cached", "--binary")).hexdigest()


def gated(files: list[str]) -> list[str]:
    return [f for f in files if f.startswith(GATED) and f.rsplit("/", 1)[-1] not in UNGATED_NAMES]


def record(root: Path, verdict: str, reviewer: str, round_no: int, notes: str) -> int:
    files = staged_files(root)
    if not files:
        print("check_review: nothing is staged — stage the change, then review it.")
        return 1
    entry = {
        "diff_sha256": staged_diff_sha256(root),
        "verdict": verdict,
        "reviewer": reviewer,
        "round": round_no,
        "notes": notes,
        "time_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),  # noqa: UP017 (py3.10)
        "files": files,
    }
    path = root / RECORD
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
    summary = f"{verdict} by {reviewer} (round {round_no}) for {len(files)} file(s)"
    print(f"check_review: recorded {summary}")
    return 0


def check(root: Path) -> int:
    if os.environ.get("CLEAR_SKIP_REVIEW") == "1":
        print("check_review: skipped (CLEAR_SKIP_REVIEW=1)")
        return 0
    needs_review = gated(staged_files(root))
    if not needs_review:
        return 0
    path = root / RECORD
    problem = None
    if not path.is_file():
        problem = "no review on record"
    else:
        entry = json.loads(path.read_text(encoding="utf-8"))
        if entry.get("diff_sha256") != staged_diff_sha256(root):
            problem = "the staged diff changed since the last review"
        elif entry.get("verdict") != "pass":
            problem = f"the last review verdict was {entry.get('verdict')!r}"
    if problem is None:
        return 0
    print(f"check_review: blocked — {problem}.", file=sys.stderr)
    print("Gated files staged:", file=sys.stderr)
    for f in needs_review:
        print(f"  {f}", file=sys.stderr)
    print(
        "Run /review on the staged diff; on pass it records the verdict "
        "(scripts/check_review.py record). Ryan can bypass with CLEAR_SKIP_REVIEW=1.",
        file=sys.stderr,
    )
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    sub = parser.add_subparsers(dest="command")
    rec = sub.add_parser("record", help="record a review verdict for the staged diff")
    rec.add_argument("--verdict", choices=["pass", "fail"], required=True)
    rec.add_argument("--reviewer", required=True, help='who reviewed, "<provider/model>"')
    rec.add_argument("--round", type=int, required=True, dest="round_no")
    rec.add_argument("--notes", default="")
    sub.add_parser("check", help="pre-commit: require a passing review for gated paths")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.command == "record":
        return record(root, args.verdict, args.reviewer, args.round_no, args.notes)
    return check(root)


if __name__ == "__main__":
    sys.exit(main())
