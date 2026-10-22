# Git standard

Solo repo, private GitHub `clear2.0`. Rules in [AGENTS.md](../../AGENTS.md) (10, 9, 1);
flow diagram in [04-review-and-commit.md](../system/04-review-and-commit.md).

## Workflow

- Work directly on `main`. No branches, no PRs.
- Commit after each logical unit. Push immediately after the commit.
- One unit = one thing a reviewer can read in a minute: a spec, a module and its test, a
  dataset registration, a figure.
- Pull before starting; resolve conflicts, never force-push `main`.

## Commit messages

Format: `<type>: <imperative summary>`. Summary ≤ 72 characters, lowercase after the colon,
no trailing period. Add a body only when the why is not obvious.

| Type | Use for |
|---|---|
| `feat` | New pipeline code or capability in `src/clear/` |
| `fix` | Bug fix |
| `docs` | Specs, ADRs, standards, mirrors, INDEX, STATUS, log |
| `data` | `data/sources.yaml`, data cards, validation reports, manifests |
| `exp` | Experiment README, `metrics.json`, experiment code |
| `fig` | `figures/src/` scripts and their sidecars |
| `chore` | Tooling, config plumbing, dependencies, hooks, CI |
| `refactor` | Behaviour-preserving restructure |
| `test` | Tests only |

```
feat: add hourly mean aggregation for station readings
docs: add alert-levels spec draft and open ADR 0003
data: register ground-monitor download in sources.yaml
fig: add station coverage map with Toronto 1000 km extent
```

## No AI attribution

**Never** add `Co-Authored-By: ...`, "Generated with ...", or any AI footer to a commit
message, in any repository. If a tool or harness suggests a trailer, delete it before
committing. If one slips in, amend before pushing. Never rewrite history already on `main`.

## Pre-commit (local, every commit)

Install once: `uv run pre-commit install`.

| Hook | Does |
|---|---|
| `scripts/guard_commit.py` | Blocks staged protected paths, `inbox/` (except README), `data/` (except `sources.yaml`, `INDEX.md`), `*.ipynb`, files > 1 MB, secret-looking strings |
| `ruff format` | Formats Python |
| `ruff check` | Lints Python |
| `scripts/check_maps.py --ci` | Size budgets, broken ADR links, missing INDEX files, mirror frontmatter. Not unmapped, stale or junk originals: only the full `check_maps.py` (run by `/map-refresh`, needs the data drives online) finds those |
| `scripts/check_review.py check` | Gated paths need a passing review of the exact staged diff |
| `guard_commit.py --commit-msg` (commit-msg stage) | Rejects AI attribution: `Co-Authored-By` naming an AI, "Generated with ..." footers, the robot emoji (rule 10) |

- A failing hook means fix the cause. Never `--no-verify` (`-n`): Ryan only, and the guard
  hook blocks agents from using it.

## CI (GitHub Actions, on push to `main`)

Runs after `uv sync --group dev`. Protected folders and `data/` are absent in CI.

| Step | Command intent |
|---|---|
| Lint | `ruff format --check`, `ruff check` |
| Types | `pyright` (strict on `src/`) |
| Tests | `pytest` (golden tests needing data skip) |
| Guards | `guard_commit.py`, `check_maps.py --ci` |

- A red `main` is fixed forward in the next commit, before other work.

## Never committed

| What | Why |
|---|---|
| `archive/`, `data/raw/`, `data/prior/`, `CLEAR 2.0 (misc docs)/`, `RAW Data/` | Protected originals; backed up separately (`data/prior/` has no second copy) |
| `inbox/` contents (except `README.md`) | Drop zone, emptied by `/map-refresh` |
| `data/` (except `data/sources.yaml`, `data/INDEX.md`) | Derived and rebuildable; large |
| `manifests/inventory.csv` | One row per original (~175k rows); local only. Commit `manifests/inventory-summary.csv` instead |
| `*.ipynb` | Notebooks are jupytext `.py` |
| `.env`, API keys, tokens, `-----BEGIN ... KEY` blocks | Secrets. Commit `.env.example` only |
| Files > 1 MB | Guard blocks them. Shrink the artifact or store it outside git |
| `mlruns/`, `.review/` | Local run state |

If a secret is ever committed: revoke it at the provider first, then clean history.

## Review requirement

Changes under `src/`, `config/`, `methodology/`, `decisions/`, `research/experiments/`,
`figures/src/`, `scripts/`, `tests/`, `.claude/hooks/`, `.claude/skills/review/`,
`.github/workflows/` and the files `.claude/agents/reviewer.md`, `.claude/settings.json`,
`.pre-commit-config.yaml`, `.gitignore`, `.ignore`, `pyproject.toml`, `uv.lock` need a passing `/review`
of the staged diff (source of truth: `GATED` in `scripts/check_review.py`). Maps, mirrors, any `INDEX.md`, STATUS, log and docs skip review. Renames
count as delete + add, so moving gated code out of a gated folder is still reviewed.

1. Stage the change: `git add ...`, then `uv run pre-commit run` and re-stage until clean.
2. Run `/review` (the `reviewer` subagent, Opus 5.5).
3. Record it: `uv run python scripts/check_review.py record --verdict pass --reviewer "claude/opus-5.5" --round N`
4. Commit, then push.

- The record is tied to the hash of the staged diff. Any change after review invalidates it;
  review again.
- Maximum two fix rounds, then escalate to Ryan.
- `CLEAR_SKIP_REVIEW=1` bypasses the check. **Ryan only**; the guard hook blocks agents from
  setting it or committing with `--no-verify`. Unset it after the commit
  (PowerShell: `Remove-Item Env:CLEAR_SKIP_REVIEW`).

## Releases (later)

- Tag `vX.Y` on `main` for a paper submission, competition entry or public release.
- Tag message names what it froze (spec versions, ADR numbers, data card `sha256`s).
- **Before making the repo public**, in order:
  1. License: choose and add a `LICENSE`.
  2. Data redistribution: every `data/sources.yaml` entry has `redistribution_allowed`;
     `unknown` or `no` blocks publication of that dataset's derived files and mirrors.
  3. Secrets scan of the full history.
  4. Mirrors in `knowledge/` may contain third-party material; confirm each may be
     republished or remove it.
