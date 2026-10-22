"""Block commits that would put originals, data, notebooks, big files or secrets in git.

Runs as a pre-commit hook (checks the staged files) and in CI with ``--all-files``
(checks every tracked file). Standard: docs/standards/git.md.

Usage:
    uv run python scripts/guard_commit.py              # staged files (pre-commit)
    uv run python scripts/guard_commit.py --all-files  # tracked files (CI)
    uv run python scripts/guard_commit.py --commit-msg .git/COMMIT_EDITMSG  # commit-msg hook

The commit-msg mode rejects AI attribution (AGENTS.md rule 10): Co-Authored-By trailers
naming an AI, "Generated with ..." footers, the robot emoji.

Silence a false-positive secret match by ending that line with ``guard: allow``
(in a comment).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PROTECTED = ("archive/", "data/raw", "data/prior", "CLEAR 2.0 (misc docs)/", "RAW Data/")
INBOX_ALLOWED = {"inbox/README.md"}
DATA_ALLOWED = {"data/sources.yaml", "data/INDEX.md"}
MAX_BYTES = 1024 * 1024  # 1 MB: anything bigger is data or media, not source
ALLOW_MARK = "guard: allow"

_UUID = r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}"
SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("private key block", re.compile(r"-----BEGIN [A-Z0-9 ]*KEY-----")),
    (
        "PurpleAir API key",
        re.compile(rf"(?i)(purple\w*|x-api-key|read_key|write_key)[^\n]{{0,40}}?{_UUID}"),
    ),
    ("Copernicus CDS key", re.compile(rf"(?im)^\s*key\s*:\s*(\d+:)?{_UUID}")),
    ("Copernicus CDS key", re.compile(rf"(?i)(cdsapi|copernicus|\bcds\b)[^\n]{{0,40}}?{_UUID}")),
    (
        "credential assignment",
        re.compile(
            r"(?i)\b(api[_-]?key|token|secret|password|access[_-]?key)\b\s*[:=]\s*"
            r"['\"]?([A-Za-z0-9_\-./+=]{20,})"
        ),
    ),
]
_PLACEHOLDER = re.compile(r"(?i)(example|placeholder|your|xxxx|<|\$\{|environ|getenv)")
AI_ATTRIBUTION_RE = re.compile(
    r"(?i)^\s*co-authored-by:.*\b(claude|anthropic|openai|chatgpt|gpt|copilot|gemini|codex)\b"
    r"|generated (with|by) \[?(claude|chatgpt|copilot|codex|gemini)"
    r"|noreply@anthropic\.com|\U0001f916"
)


def git(root: Path, *args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, check=True).stdout


def list_files(root: Path, all_files: bool) -> list[str]:
    if all_files:
        out = git(root, "ls-files", "-z")
    else:
        out = git(root, "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z")
    return [p for p in out.decode("utf-8").split("\0") if p]


def read_blob(root: Path, path: str, all_files: bool) -> bytes:
    if all_files:
        return (root / path).read_bytes()
    return git(root, "show", f":{path}")


def path_problem(path: str) -> str | None:
    if path.startswith(PROTECTED):
        return "original/raw file (protected path) — originals never go in git"
    if path.startswith("inbox/") and path not in INBOX_ALLOWED:
        return "inbox file — run /map-refresh instead of committing it"
    if path.startswith("data/") and path not in DATA_ALLOWED:
        return "data file — data/ is gitignored except sources.yaml and INDEX.md"
    if path.endswith(".ipynb"):
        return "notebook — commit the jupytext .py pair, not the .ipynb"
    return None


def secret_problems(text: str) -> list[str]:
    found: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if ALLOW_MARK in line:
            continue
        for label, pattern in SECRET_PATTERNS:
            match = pattern.search(line)
            if match is None:
                continue
            if label == "credential assignment" and _PLACEHOLDER.search(match.group(2)):
                continue
            found.append(f"line {lineno}: looks like a {label}")
            break
    return found


def attribution_problems(message: str) -> list[str]:
    """Return commit-message lines that credit an AI tool (git drops '#' comment lines)."""
    return [
        f"commit message line {n}: AI attribution — {line.strip()}"
        for n, line in enumerate(message.splitlines(), start=1)
        if not line.startswith("#") and AI_ATTRIBUTION_RE.search(line)
    ]


def check(root: Path, all_files: bool) -> list[str]:
    problems: list[str] = []
    for path in list_files(root, all_files):
        reason = path_problem(path)
        if reason:
            problems.append(f"{path}: {reason}")
            continue
        try:
            blob = read_blob(root, path, all_files)
        except (OSError, subprocess.CalledProcessError):
            continue  # deleted in the working tree; nothing to scan
        if len(blob) > MAX_BYTES:
            problems.append(f"{path}: {len(blob) / 1e6:.1f} MB > 1 MB limit")
            continue
        if b"\0" in blob:
            continue  # binary (e.g. a figure PNG): size-checked only
        for issue in secret_problems(blob.decode("utf-8", errors="replace")):
            problems.append(f"{path}: {issue}")
    return problems


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stderr, "reconfigure"):  # messages hold em dashes; cp1252 would garble them
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--all-files", action="store_true", help="check tracked files (CI)")
    parser.add_argument("--commit-msg", type=Path, help="check this commit message file instead")
    args = parser.parse_args(argv)
    if args.commit_msg is not None:
        problems = attribution_problems(args.commit_msg.read_text(encoding="utf-8"))
    else:
        problems = check(args.root.resolve(), args.all_files)
    if problems:
        print("guard_commit: blocked —", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print("Fix or unstage these files (see docs/standards/git.md).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
