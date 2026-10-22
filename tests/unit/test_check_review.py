import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_review.py"


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, capture_output=True, check=True)


def stage(repo: Path, rel: str, content: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    git(repo, "add", "--", rel)


def run(repo: Path, *args: str, skip: bool = False) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if k != "CLEAR_SKIP_REVIEW"}
    if skip:
        env["CLEAR_SKIP_REVIEW"] = "1"
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *args],
        capture_output=True,
        text=True,
        env=env,
    )


def record(repo: Path, verdict: str = "pass") -> subprocess.CompletedProcess[str]:
    return run(repo, "record", "--verdict", verdict, "--reviewer", "test/model", "--round", "1")


def test_ungated_changes_need_no_review(git_repo: Path):
    stage(git_repo, "STATUS.md", "# status\n")
    stage(git_repo, "knowledge/docs/a.md", "mirror\n")
    assert run(git_repo, "check").returncode == 0


def test_gated_change_blocked_until_reviewed(git_repo: Path):
    stage(git_repo, "src/clear/mod.py", "x = 1\n")
    blocked = run(git_repo, "check")
    assert blocked.returncode == 1
    assert "no review on record" in blocked.stderr

    assert record(git_repo).returncode == 0
    entry = json.loads((git_repo / ".review" / "last.json").read_text(encoding="utf-8"))
    assert entry["verdict"] == "pass"
    assert entry["files"] == ["src/clear/mod.py"]
    assert run(git_repo, "check").returncode == 0


def test_changing_the_staged_diff_invalidates_the_review(git_repo: Path):
    stage(git_repo, "methodology/alert-levels.md", "v1\n")
    record(git_repo)
    stage(git_repo, "methodology/alert-levels.md", "v2\n")
    result = run(git_repo, "check")
    assert result.returncode == 1
    assert "changed since the last review" in result.stderr


def test_failed_review_blocks(git_repo: Path):
    stage(git_repo, "config/alerts.yaml", "a: 1\n")
    record(git_repo, verdict="fail")
    result = run(git_repo, "check")
    assert result.returncode == 1
    assert "'fail'" in result.stderr


def test_skip_env_bypasses(git_repo: Path):
    stage(git_repo, "figures/src/fig_x.py", "x = 1\n")
    assert run(git_repo, "check", skip=True).returncode == 0


def test_record_with_nothing_staged_fails(git_repo: Path):
    assert record(git_repo).returncode == 1


def test_tooling_that_enforces_the_rules_is_gated(git_repo: Path):
    enforcing = (
        "scripts/check_review.py",
        ".pre-commit-config.yaml",
        "tests/unit/test_x.py",
        ".claude/skills/review/SKILL.md",
        ".claude/agents/reviewer.md",
        ".gitignore",
    )
    for rel in enforcing:
        stage(git_repo, rel, "x\n")
    result = run(git_repo, "check")
    assert result.returncode == 1
    for rel in enforcing:
        assert rel in result.stderr


def test_index_files_are_never_gated(git_repo: Path):
    stage(git_repo, "decisions/INDEX.md", "- [0001](0001-x.md) — accepted\n")
    stage(git_repo, "src/clear/INDEX.md", "# clear\n")
    assert run(git_repo, "check").returncode == 0


def test_moving_gated_code_out_still_needs_review(git_repo: Path):
    stage(git_repo, "src/clear/mod.py", "x = 1\n")
    git(git_repo, "commit", "-q", "-m", "seed")
    (git_repo / "notebooks").mkdir()
    git(git_repo, "mv", "src/clear/mod.py", "notebooks/mod.py")
    result = run(git_repo, "check")
    assert result.returncode == 1
    assert "src/clear/mod.py" in result.stderr


def test_help_is_ascii_safe(git_repo: Path):
    env = {**os.environ, "PYTHONIOENCODING": "cp1252"}
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True, env=env
    )
    assert result.returncode == 0, result.stderr
