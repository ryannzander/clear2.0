import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "guard_commit.py"
# Built at runtime so this file never contains a secret-looking literal itself.
FAKE_UUID = "-".join(["0f8fad5b", "d9cb", "469f", "a165", "70867728950e"])


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, capture_output=True, check=True)


def add(repo: Path, rel: str, content: str | bytes) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")
    git(repo, "add", "--", rel)


def guard(repo: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *extra],
        capture_output=True,
        text=True,
    )


def test_clean_staging_passes(git_repo: Path):
    add(git_repo, "src/clear/x.py", "x = 1\n")
    add(git_repo, "inbox/README.md", "# inbox\n")
    add(git_repo, "data/sources.yaml", "datasets: []\n")
    add(git_repo, "figures/out/fig_a.png", b"\x89PNG\0binary")
    result = guard(git_repo)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "rel",
    [
        "archive/report.docx",
        "data/raw/naps.csv",
        "CLEAR 2.0 (misc docs)/a.pdf",
        "RAW Data/b.xlsx",
        "inbox/new.pdf",
        "data/processed/x.parquet",
        "notebooks/explore.ipynb",
    ],
)
def test_blocked_paths(git_repo: Path, rel: str):
    add(git_repo, rel, "content\n")
    result = guard(git_repo)
    assert result.returncode == 1
    assert rel in result.stderr


def test_large_file_blocked(git_repo: Path):
    add(git_repo, "figures/out/huge.png", b"\0" * (1024 * 1024 + 1))
    result = guard(git_repo)
    assert result.returncode == 1
    assert "1 MB" in result.stderr


@pytest.mark.parametrize(
    "line",
    [
        "-----BEGIN " + "RSA PRIVATE KEY-----",
        f"PURPLEAIR_READ_KEY = '{FAKE_UUID}'",
        f"key: 123456:{FAKE_UUID}",
        "api_key = '" + "A1b2C3d4E5f6G7h8I9j0K1l2" + "'",
    ],
)
def test_secrets_blocked(git_repo: Path, line: str):
    add(git_repo, "src/clear/settings.py", f"{line}\n")
    result = guard(git_repo)
    assert result.returncode == 1
    assert "looks like" in result.stderr


def test_placeholders_and_allow_marker_pass(git_repo: Path):
    add(
        git_repo,
        ".env.example",
        "api_key = '<your-purpleair-key-goes-here>'\n"
        f"read_key = '{FAKE_UUID}'  # guard: allow (documented test fixture)\n",
    )
    result = guard(git_repo)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    ("message", "blocked"),
    [
        ("feat: x\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n", True),
        ("fix: y\n\nGenerated with [Claude Code](https://claude.com/claude-code)\n", True),
        ("docs: z \U0001f916\n", True),
        ("feat: x\n\nCo-Authored-By: Ryan Zander <ryan@example.com>\n", False),
        ("chore: scaffold\n\n# Co-Authored-By: Claude (git drops comment lines)\n", False),
        ("docs: explain the Claude agents in AGENTS.md\n", False),
    ],
)
def test_commit_message_without_ai_attribution(tmp_path: Path, message: str, blocked: bool):
    msg = tmp_path / "COMMIT_EDITMSG"
    msg.write_text(message, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--commit-msg", str(msg)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert (result.returncode == 1) is blocked, result.stderr


def test_all_files_mode_checks_tracked_files(git_repo: Path):
    add(git_repo, "src/ok.py", "x = 1\n")
    git(git_repo, "commit", "-q", "-m", "init")
    assert guard(git_repo, "--all-files").returncode == 0
    add(git_repo, "data/raw/sneaky.csv", "a,b\n")
    git(git_repo, "commit", "-q", "-m", "oops")
    result = guard(git_repo, "--all-files")
    assert result.returncode == 1
    assert "data/raw/sneaky.csv" in result.stderr
