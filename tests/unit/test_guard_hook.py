""".claude/hooks/guard.py: drive the PreToolUse hook with JSON on stdin."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

HOOK = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "guard.py"
BLOCK = 2
ALLOW = 0


def hook_python() -> str:
    """Return the interpreter Claude Code runs hooks with: `python` on PATH outside this venv.

    The hook must keep working there (here: system Python 3.10), not just under the venv.
    """
    if override := os.environ.get("CLEAR_HOOK_PYTHON"):
        return override
    venv = Path(sys.prefix).resolve()
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not entry or Path(entry).resolve().is_relative_to(venv):
            continue
        if found := shutil.which("python", path=entry):
            return found
    return sys.executable


PYTHON = hook_python()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    sources = {
        "archive/Docs/a.docx": {"mirror": "knowledge/docs/docs/a.md", "sha256": "abc"},
        "archive/Docs/a.pdf": {
            "mirror": "knowledge/docs/docs/a.md",
            "sha256": None,
            "alias_of": "archive/Docs/a.docx",
        },
    }
    (tmp_path / "knowledge").mkdir()
    (tmp_path / "knowledge" / "_sources.json").write_text(json.dumps(sources), encoding="utf-8")
    return tmp_path


def call(
    repo: Path, tool: str, tool_input: dict[str, Any] | str, cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    payload = (
        tool_input
        if isinstance(tool_input, str)
        else json.dumps(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": tool,
                "tool_input": tool_input,
                "cwd": str(cwd or repo),
            }
        )
    )
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(repo)}
    return subprocess.run(
        [PYTHON, str(HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )


@pytest.mark.parametrize(
    ("tool", "tool_input", "expected"),
    [
        ("Write", {"file_path": "archive/x.docx", "content": "x"}, BLOCK),
        ("Edit", {"file_path": "RAW Data/x.csv", "old_string": "a", "new_string": "b"}, BLOCK),
        ("Write", {"file_path": "src/clear/x.py", "content": "x"}, ALLOW),
        ("Read", {"file_path": "knowledge/docs/docs/a.md"}, ALLOW),
        ("Read", {"file_path": "archive/Docs/unmapped.docx"}, ALLOW),
        ("Read", {"file_path": "archive/notes.md"}, ALLOW),
        ("Grep", {"pattern": "PM2.5", "path": "RAW Data"}, BLOCK),
        ("Grep", {"pattern": "PM2.5", "path": "CLEAR 2.0 (misc docs)/Documents"}, BLOCK),
        ("Grep", {"pattern": "PM2.5", "path": "src"}, ALLOW),
        ("Grep", {"pattern": "PM2.5", "glob": "archive/**/*.md"}, BLOCK),
        ("Glob", {"pattern": "archive/**/*.docx"}, BLOCK),
        ("Glob", {"pattern": "**/*.docx"}, BLOCK),
        # Claude Code's Glob ignores .gitignore, so root-anchored recursion is blocked.
        ("Glob", {"pattern": "**/*.py"}, BLOCK),
        ("Glob", {"pattern": "**/.DS_Store"}, BLOCK),
        ("Glob", {"pattern": "src/**/*.py"}, ALLOW),
        ("Glob", {"pattern": "**/*.py", "path": "src"}, ALLOW),
        ("Glob", {"pattern": "*.md"}, ALLOW),
        ("Glob", {"pattern": "*.png", "path": "figures/out"}, ALLOW),
        # data/ holds the raw and prior links, so recursion from it is blocked too.
        ("Glob", {"pattern": "**/*.parquet", "path": "data"}, BLOCK),
        ("Glob", {"pattern": "processed/**/*.parquet", "path": "data"}, ALLOW),
        ("Glob", {"pattern": "data/processed/**/*.parquet"}, ALLOW),
        ("Write", {"file_path": "data/prior/x.csv", "content": "x"}, BLOCK),
        ("Grep", {"pattern": "PM2.5", "path": "data/prior"}, BLOCK),
        # A glob's real start = path + the pattern's literal leading folders.
        ("Glob", {"pattern": "data/**/*.csv"}, BLOCK),
        ("Glob", {"pattern": "../data/**", "path": "knowledge"}, BLOCK),
        ("Glob", {"pattern": "**/*", "path": "inbox"}, BLOCK),
        ("Grep", {"pattern": "x", "path": "inbox"}, BLOCK),
        ("Grep", {"pattern": "x", "path": "inbox/README.md"}, ALLOW),
        # git global options before the subcommand.
        ("Bash", {"command": "git -C . clean -fdx"}, BLOCK),
        ("Bash", {"command": "git -c core.x=y clean -fdx"}, BLOCK),
        # Commands that never name a protected folder but still reach one.
        ("Bash", {"command": "cd data/raw && rm x.csv"}, BLOCK),
        ("Bash", {"command": "rm -rf data"}, BLOCK),
        ("Bash", {"command": "rm -rf .."}, BLOCK),
        ("PowerShell", {"command": "Remove-Item -Recurse -Force data"}, BLOCK),
        ("PowerShell", {"command": "cmd /c rmdir /s /q data"}, BLOCK),
        ("Bash", {"command": "bash -c 'rm -rf data'"}, BLOCK),
        ("Bash", {"command": 'echo x > "CLEAR 2.0 (misc docs)/x.txt"'}, BLOCK),
        ("Bash", {"command": "rm -rf archive/x # scripts/intake.py"}, BLOCK),
        ("Bash", {"command": "rm -rf data/interim/x"}, ALLOW),
        ("Bash", {"command": "uv run --no-project python scripts/intake.py plan --legacy"}, ALLOW),
        # Ryan-only bypasses.
        ("Bash", {"command": "CLEAR_SKIP_REVIEW=1 git commit -m x"}, BLOCK),
        ("PowerShell", {"command": '$env:CLEAR_SKIP_REVIEW = "1"; git commit -m x'}, BLOCK),
        ("Bash", {"command": "git commit --no-verify -m x"}, BLOCK),
        ("Bash", {"command": "git commit -n -m x"}, BLOCK),
        ("Bash", {"command": "git commit -m 'fix: x'"}, ALLOW),
        ("Bash", {"command": "grep CLEAR_SKIP_REVIEW docs/standards/git.md"}, ALLOW),
        # inbox/: nothing deleted or overwritten; the plan stays editable.
        ("Bash", {"command": "rm -rf inbox/seagate"}, BLOCK),
        ("Bash", {"command": "rm inbox/_plan.yaml"}, ALLOW),
        ("Write", {"file_path": "inbox/_plan.yaml", "content": "x"}, ALLOW),
        ("Write", {"file_path": "inbox/new.csv", "content": "x"}, ALLOW),
        # Wildcards are judged by their literal leading folders.
        ("Bash", {"command": "rm -rf data/*/*"}, BLOCK),
        ("PowerShell", {"command": "Remove-Item -Recurse -Force data/*/*"}, BLOCK),
        ("Bash", {"command": "rm -rf data/*"}, BLOCK),
        ("Bash", {"command": "rm -rf data/ra?/*"}, BLOCK),
        ("Bash", {"command": "rm data/interim/*.parquet"}, ALLOW),
        ("Bash", {"command": "rm *.tmp"}, ALLOW),
        # cd carries over to later segments; a lone & separates commands.
        ("Bash", {"command": "cd data && rm -rf raw/*"}, BLOCK),
        ("PowerShell", {"command": "Set-Location data; Remove-Item -Recurse -Force raw/*"}, BLOCK),
        ("Bash", {"command": "python scripts/intake.py & rm -rf data/raw/*"}, BLOCK),
        ("Bash", {"command": "true & rm -rf data/raw/*"}, BLOCK),
        ("PowerShell", {"command": 'cmd /c "echo hi & rmdir /s /q data"'}, BLOCK),
        ("Bash", {"command": "echo $(rm -rf data)"}, BLOCK),
        ("Bash", {"command": "uv run pytest -q 2>&1"}, ALLOW),
        # Other ways to switch the commit guards off.
        ("Bash", {"command": "SKIP=check-review git commit -m x"}, BLOCK),
        ("Bash", {"command": "git -c core.hooksPath=/dev/null commit -m x"}, BLOCK),
        ("PowerShell", {"command": "Set-Item Env:CLEAR_SKIP_REVIEW 1"}, BLOCK),
        ("Bash", {"command": "pre-commit uninstall"}, BLOCK),
        ("Bash", {"command": "echo x > .git/hooks/pre-commit"}, BLOCK),
        ("Write", {"file_path": ".git/hooks/pre-commit", "content": "x"}, BLOCK),
        ("Bash", {"command": "rm .git/index.lock"}, ALLOW),
        # Prefixes and wrappers.
        ("Bash", {"command": "env rm -rf data/raw/x"}, BLOCK),
        ("Bash", {"command": "(rm -rf data/raw/x)"}, BLOCK),
        ("Bash", {"command": "perl -pi -e 's/a/b/' data/raw/x.csv"}, BLOCK),
        # Sweeps that ignore .gitignore, from a folder holding originals.
        ("Bash", {"command": "find . -name '*.csv'"}, BLOCK),
        ("Bash", {"command": "find src -name '*.py'"}, ALLOW),
        ("Bash", {"command": "ls -R data"}, BLOCK),
        ("PowerShell", {"command": "Get-ChildItem data -Recurse"}, BLOCK),
        ("PowerShell", {"command": "Get-ChildItem src -Recurse -Filter *.py"}, ALLOW),
        ("Bash", {"command": "grep -rn foo ."}, BLOCK),
        ("Bash", {"command": "rg foo"}, ALLOW),
        ("Bash", {"command": "rg foo archive/"}, BLOCK),
        # A folder merely named like a protected one is fine.
        ("Bash", {"command": "mkdir -p research/archive"}, ALLOW),
        # Git Bash escaped spaces (what tab completion writes).
        ("Bash", {"command": "rm -rf RAW\\ Data/old"}, BLOCK),
        ("Bash", {"command": "mv RAW\\ Data/x.csv /tmp/"}, BLOCK),
        ("Bash", {"command": "echo x > RAW\\ Data/x.txt"}, BLOCK),
        ("Bash", {"command": "cd RAW\\ Data && rm -rf old"}, BLOCK),
        # Copy destination: robocopy's is the 2nd operand; deleting modes are refused.
        (
            "PowerShell",
            {"command": 'robocopy "D:/x" "data/raw" /E /XC /XN /XO /XF ._* .DS_Store'},
            BLOCK,
        ),
        ("PowerShell", {"command": "robocopy data/raw D:/bk /MIR"}, BLOCK),
        (
            "PowerShell",
            {"command": "robocopy data/raw D:/bk /E /XC /XN /XO /XF ._* .DS_Store"},
            ALLOW,
        ),
        # Extract, convert or download in place.
        ("Bash", {"command": "tar -xf a.tar -C data/raw/NOAA"}, BLOCK),
        ("Bash", {"command": "gunzip data/raw/x.csv.gz"}, BLOCK),
        ("Bash", {"command": "curl -o data/raw/x.csv https://example.com/x.csv"}, BLOCK),
        ("PowerShell", {"command": "Invoke-WebRequest https://x -OutFile data/raw/x.csv"}, BLOCK),
        ("Bash", {"command": "ruff check --fix archive/x.py"}, BLOCK),
        ("Bash", {"command": "rg -uu foo"}, BLOCK),
        ("Bash", {"command": "curl -s https://example.com"}, ALLOW),
        # False positives that must stay allowed.
        ("Bash", {"command": "ls -ltr"}, ALLOW),
        ("Bash", {"command": "grep -E 'a|find ' notes.txt"}, ALLOW),
        ("Bash", {"command": 'git commit -m "feat: x" -m "- add intake guard"'}, ALLOW),
        ("Bash", {"command": "git commit -m 'move notes > archive/x'"}, ALLOW),
        # PowerShell has no backslash escapes: a trailing backslash ends a folder path.
        ("PowerShell", {"command": 'robocopy data\\raw\\ "D:\\CLEAR 2.0\\RAW Data" /MIR'}, BLOCK),
        ("PowerShell", {"command": 'robocopy "D:\\bk\\" data\\raw\\ /E'}, BLOCK),
        ("PowerShell", {"command": "Copy-Item new.csv data\\raw\\ -Force"}, BLOCK),
        ("PowerShell", {"command": "Copy-Item x.csv archive\\ -Force"}, BLOCK),
        ("PowerShell", {"command": "Remove-Item data\\ -Recurse -Force"}, BLOCK),
        ("PowerShell", {"command": "Remove-Item ..\\ -Recurse"}, BLOCK),
        ("PowerShell", {"command": "cmd /c rd data\\ /s /q"}, BLOCK),
        ("PowerShell", {"command": "Get-ChildItem .\\ -Recurse"}, BLOCK),
        ("PowerShell", {"command": "Get-ChildItem data\\ -Recurse -Filter *.csv"}, BLOCK),
        (
            "PowerShell",
            {"command": 'Copy-Item a.csv "data\\interim\\"; Remove-Item -Recurse -Force data'},
            BLOCK,
        ),
        ("PowerShell", {"command": "ls -r *.csv"}, BLOCK),
        ("PowerShell", {"command": "Get-ChildItem -Depth 3 data"}, BLOCK),
        ("PowerShell", {"command": "Remove-Item -Path:data -Recurse"}, BLOCK),
        ("PowerShell", {"command": "Copy-Item a.csv data\\interim\\ -Force"}, ALLOW),
        # cmd-style /switches are not Git Bash drives.
        ("PowerShell", {"command": "tree /F"}, BLOCK),
        ("PowerShell", {"command": "cmd /c tree /f"}, BLOCK),
        ("Bash", {"command": "rsync -a --delete data/raw/ /mnt/backup/"}, BLOCK),
        ("Bash", {"command": "rm -rf data/raw/x"}, BLOCK),
        ("Bash", {"command": "uv run python scripts/intake.py apply inbox/_plan.yaml"}, ALLOW),
        ("Bash", {"command": "uv run python scripts/inventory.py --check"}, ALLOW),
        ("Bash", {"command": "ls src"}, ALLOW),
        ("Bash", {"command": "ls archive"}, ALLOW),
        ("Bash", {"command": "find archive -name '*.pdf'"}, BLOCK),
        ("Bash", {"command": "ls -R 'RAW Data'"}, BLOCK),
        ("Bash", {"command": "grep -rn PM25 archive/"}, BLOCK),
        ("Bash", {"command": "cp notes.txt archive/notes.txt"}, BLOCK),
        ("Bash", {"command": "cp archive/a.docx /tmp/a.docx"}, ALLOW),
        ("Bash", {"command": "echo hi > data/raw/x.txt"}, BLOCK),
        ("Bash", {"command": "sed -i 's/a/b/' archive/x.txt"}, BLOCK),
        ("Bash", {"command": "git clean -fdx"}, BLOCK),
        ("Bash", {"command": "git stash --all"}, BLOCK),
        ("Bash", {"command": "git status && uv run pytest -q"}, ALLOW),
        ("Bash", {"command": "rm -rf *"}, BLOCK),
        ("Bash", {"command": "mv src/a.py src/b.py"}, ALLOW),
        ("PowerShell", {"command": "Remove-Item -Recurse 'RAW Data\\x'"}, BLOCK),
        ("PowerShell", {"command": "Get-ChildItem -Recurse archive"}, BLOCK),
        ("PowerShell", {"command": "Get-ChildItem src"}, ALLOW),
    ],
)
def test_guard(repo: Path, tool: str, tool_input: dict[str, Any], expected: int) -> None:
    result = call(repo, tool, tool_input)
    assert result.returncode == expected, result.stderr


def test_read_of_mapped_binary_is_redirected(repo: Path) -> None:
    for path in (
        "archive/Docs/a.docx",
        "archive/Docs/a.pdf",
        str(repo / "archive" / "Docs" / "a.docx"),
    ):
        result = call(repo, "Read", {"file_path": path})
        assert result.returncode == BLOCK
        assert "knowledge/docs/docs/a.md" in result.stderr


def test_absolute_windows_style_paths(repo: Path) -> None:
    target = str(repo / "archive" / "x.docx").replace("/", "\\")
    assert call(repo, "Write", {"file_path": target, "content": "x"}).returncode == BLOCK
    assert call(repo, "Bash", {"command": f'rm "{target}"'}).returncode == BLOCK


def make_link(link: Path, target: Path) -> None:
    """Directory link like scripts/storage.py makes: a junction on Windows, else a symlink."""
    link.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)], check=True, capture_output=True
        )
    else:
        link.symlink_to(target, target_is_directory=True)


def test_link_target_paths_get_the_repo_folders_protection(
    repo: Path, tmp_path_factory: pytest.TempPathFactory
) -> None:
    drive = tmp_path_factory.mktemp("drive").resolve()
    (drive / "a.xlsx").write_bytes(b"x")
    make_link(repo / "data" / "raw", drive)
    sources_path = repo / "knowledge" / "_sources.json"
    sources = json.loads(sources_path.read_text(encoding="utf-8"))
    sources["data/raw/a.xlsx"] = {"mirror": "knowledge/data/a.md", "sha256": None}
    sources_path.write_text(json.dumps(sources), encoding="utf-8")
    new_file = str(drive / "new.csv")
    elsewhere = str(tmp_path_factory.mktemp("elsewhere") / "ok.txt")

    read = call(repo, "Read", {"file_path": str(drive / "a.xlsx")})

    assert call(repo, "Write", {"file_path": new_file, "content": "x"}).returncode == BLOCK
    assert call(repo, "Bash", {"command": f'rm "{new_file}"'}).returncode == BLOCK
    assert call(repo, "Glob", {"pattern": "*.csv", "path": str(drive)}).returncode == BLOCK
    assert read.returncode == BLOCK
    assert "knowledge/data/a.md" in read.stderr
    assert call(repo, "Write", {"file_path": elsewhere, "content": "x"}).returncode == ALLOW


def test_relative_paths_resolve_from_the_shell_cwd(repo: Path) -> None:
    (repo / "data").mkdir()
    result = call(repo, "Bash", {"command": "rm -rf raw"}, cwd=repo / "data")
    assert result.returncode == BLOCK


def test_existing_inbox_files_cannot_be_overwritten(repo: Path) -> None:
    (repo / "inbox").mkdir()
    (repo / "inbox" / "waiting.csv").write_text("x", encoding="utf-8")
    edit = {"file_path": "inbox/waiting.csv", "old_string": "x", "new_string": "y"}
    assert call(repo, "Edit", edit).returncode == BLOCK
    assert call(repo, "Bash", {"command": "cp new.csv inbox/waiting.csv"}).returncode == BLOCK
    assert call(repo, "Bash", {"command": "echo x > inbox/waiting.csv"}).returncode == BLOCK
    assert call(repo, "Bash", {"command": "echo x > inbox/new.txt"}).returncode == ALLOW
    assert call(repo, "Bash", {"command": "cp x.csv inbox/"}).returncode == ALLOW
    assert call(repo, "Bash", {"command": "cp new/waiting.csv inbox/"}).returncode == BLOCK
    assert call(repo, "Bash", {"command": "mv waiting.csv inbox"}).returncode == BLOCK


def test_backup_folders_cannot_be_deleted(
    repo: Path, tmp_path_factory: pytest.TempPathFactory
) -> None:
    backup = tmp_path_factory.mktemp("seagate").resolve() / "RAW Data"
    backup.mkdir()
    (repo / ".env").write_text(f"CLEAR_BACKUP_RAW_DIR={backup}\n", encoding="utf-8")
    for target in (backup, backup / "NOAA", backup.parent):
        command = {"command": f'rm -rf "{target.as_posix()}"'}
        assert call(repo, "Bash", command).returncode == BLOCK, target


@pytest.mark.skipif(os.name != "nt", reason="Git Bash drive paths exist only on Windows")
def test_git_bash_drive_paths_are_mapped(
    repo: Path, tmp_path_factory: pytest.TempPathFactory
) -> None:
    drive = tmp_path_factory.mktemp("drive").resolve()
    (drive / "RAW Data").mkdir()
    make_link(repo / "data" / "raw", drive / "RAW Data")
    posix = drive.as_posix()  # C:/Users/... -> /c/Users/...
    bash_form = f"/{posix[0].lower()}{posix[2:]}"
    escaped = bash_form.replace(" ", "\\ ")
    assert call(repo, "Bash", {"command": f"rm -rf {escaped}/RAW\\ Data/NOAA"}).returncode == BLOCK
    assert call(repo, "Bash", {"command": f"rm -rf {escaped}"}).returncode == BLOCK
    root_drive = f"/{posix[0].lower()}"  # e.g. /c: holds the repo itself
    for command in (f"rm -rf {root_drive}", f"rm -rf {root_drive}/", f"ls -R {root_drive}"):
        assert call(repo, "Bash", {"command": command}).returncode == BLOCK, command


def test_recursive_glob_from_above_the_repo_is_blocked(repo: Path) -> None:
    above = {"pattern": "**/*.pdf", "path": str(repo.parent)}
    absolute_pattern = {"pattern": f"{repo.as_posix()}/**/*.md"}
    assert call(repo, "Glob", above).returncode == BLOCK
    assert call(repo, "Glob", absolute_pattern).returncode == BLOCK


def test_payload_with_a_bom_is_still_checked(repo: Path) -> None:
    payload = json.dumps(
        {
            "tool_name": "Write",
            "tool_input": {"file_path": "archive/x.md", "content": "x"},
            "cwd": str(repo),
        }
    )
    assert call(repo, "Write", "﻿" + payload).returncode == BLOCK


def test_glob_above_a_link_target_is_blocked(
    repo: Path, tmp_path_factory: pytest.TempPathFactory
) -> None:
    drive = tmp_path_factory.mktemp("drive").resolve()
    (drive / "RAW Data").mkdir()
    make_link(repo / "data" / "raw", drive / "RAW Data")
    assert call(repo, "Glob", {"pattern": "**/*.csv", "path": str(drive)}).returncode == BLOCK
    rm = {"command": f'rm -rf "{drive}"'}
    assert call(repo, "Bash", rm).returncode == BLOCK


def test_bad_input_never_blocks(repo: Path) -> None:
    assert call(repo, "Bash", "not json").returncode == ALLOW
    assert call(repo, "Unknown", {"x": 1}).returncode == ALLOW
