"""Shared test setup: headless matplotlib and a throwaway git repo fixture."""

import subprocess
from pathlib import Path

import matplotlib
import pytest

matplotlib.use("Agg")

REPO_ROOT = Path(__file__).resolve().parents[1]


def run_git(repo: Path, *args: str) -> str:
    """Run git in ``repo`` and return stdout."""
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True
    ).stdout


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Return an empty git repo with a committer identity configured."""
    repo = tmp_path / "repo"
    repo.mkdir()
    run_git(repo, "init", "-q", "-b", "main")
    run_git(repo, "config", "user.email", "test@example.com")
    run_git(repo, "config", "user.name", "Test")
    run_git(repo, "config", "core.autocrlf", "false")
    return repo
