"""PostToolUse hook: format and lint every edited .py file with ruff.

Runs ``ruff format`` then ``ruff check --fix`` on the edited file. If lint errors remain,
exits 2 so the agent sees them and fixes them. Silently does nothing (exit 0) for
non-Python files, missing files, or when ruff/uv is not available yet.

Stdlib only. Reads the hook JSON from stdin.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RUFF_TIMEOUT_S = 60
RUFF_LINT_FAILED = 1  # ruff check exit code when violations remain


def ruff_command(root: Path) -> list[str] | None:
    """Prefer the project venv's ruff, then PATH, then `uv run --no-sync ruff`."""
    for candidate in (root / ".venv" / "Scripts" / "ruff.exe", root / ".venv" / "bin" / "ruff"):
        if candidate.is_file():
            return [str(candidate)]
    if found := shutil.which("ruff"):
        return [found]
    if uv := shutil.which("uv"):
        return [uv, "run", "--no-sync", "--quiet", "ruff"]
    return None


def run(cmd: list[str], root: Path) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            cmd,
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",  # ruff writes UTF-8; the system Python would assume cp1252
            errors="replace",
            timeout=RUFF_TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def main() -> int:
    if hasattr(sys.stderr, "reconfigure"):  # the system Python may default to cp1252
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    try:
        # Bytes + utf-8-sig: non-ASCII edits (e.g. "ug m⁻³") must not crash a cp1252 decode.
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8-sig") or "{}")
        raw = str((payload.get("tool_input") or {}).get("file_path") or "")
        root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd())
        path = Path(raw)
        if not raw.endswith(".py") or not path.is_file():
            return 0
        ruff = ruff_command(root)
        if ruff is None:
            return 0
        run([*ruff, "format", "--quiet", str(path)], root)
        result = run([*ruff, "check", "--fix", "--quiet", str(path)], root)
        if result is not None and result.returncode == RUFF_LINT_FAILED:
            print(f"ruff found issues it could not auto-fix in {raw}:", file=sys.stderr)
            print((result.stdout or result.stderr).strip(), file=sys.stderr)
            return 2
    except Exception:  # noqa: BLE001 — a hook bug must never wedge the session
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
