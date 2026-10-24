# 05 — Tooling

Toolchain: `uv` (Python 3.12), `ruff`, `pyright` (strict on `src/`), `pytest`, `pre-commit`,
`jupytext`. Everything runs through `uv run ...`. Code rules: [code.md](../standards/code.md).
Git rules: [git.md](../standards/git.md). Script list: `scripts/INDEX.md`.

## Setup

```bash
uv sync --all-groups              # local: everything available now
uv run pre-commit install         # once per clone
uv run pre-commit run --all-files # run every hook on the whole repo
```

CI uses the smaller set: `uv sync --group dev`.

## Dependency groups

Defined in `pyproject.toml`. Add a package to the group that matches its job.

| Group | Contents | Used by |
|---|---|---|
| core (`[project].dependencies`) | pandas, numpy, xarray, zarr, pyarrow, pandera, pydantic, pyyaml, typer, matplotlib, plotly | `src/clear/` |
| `dev` | ruff, pyright, pytest, pre-commit, jupytext | everyone, CI |
| `knowledge` | markitdown (docx, pdf, xlsx extras) | Librarian conversions |
| `geo` | cartopy, geopandas, netcdf4 | maps, grids, ERA5 and satellite reads |
| `ml` | torch (cu128), lightgbm, torch-geometric, mlflow | models phase — **not added yet** |

Add with `uv add --group <name> <package>`; core with `uv add <package>`. Commit `pyproject.toml`
and `uv.lock` together.

## Scripts

All in `scripts/`. Stdlib + pyyaml only, Python ≥ 3.10. Run as `uv run python scripts/<x>.py`.
Each takes `--root PATH` (default: repo root) so tests can run against a temp dir.

| Script | Does |
|---|---|
| `storage.py` | Status of `data/raw` and `data/prior` links and backup folders (online/OFFLINE, free GB; exit 1 if a store is offline or not linked). `link` creates missing links from `.env`; `link --relink` re-points a changed target. `verify [--folder X]` hashes the backup copies of inventory rows against `inventory.csv` (used by `/backup-check`; backup files missing from the inventory are not checked). Never moves or deletes data. |
| `inventory.py` | Scans originals → `manifests/inventory.csv` (local only, ~175k rows), `manifests/inventory-summary.csv` (committed, one row per dataset folder), `knowledge/_sources.json`. An offline link keeps its area's old rows and warns. `--check` writes nothing; exit 1 if it would change. |
| `intake.py` | `plan [--legacy]`, `apply inbox/_plan.yaml`. Only sanctioned writer into protected paths. Across drives: copy, hash the copy, compare, then delete the source (mismatch: delete the copy, keep the source). Refuses an offline destination, `..` segments and duplicate `src`. |
| `check_maps.py` | Full run: unmapped/stale/junk originals (one line per status and dataset folder; walks every original, data drives online; run by `/map-refresh`) plus size budgets, ADR links, INDEX files, mirror frontmatter. `--ci` (pre-commit, CI) checks only the latter four. |
| `guard_commit.py` | Blocks protected paths, big files, notebooks, secrets in a commit. |
| `check_review.py` | `record` and `check` for the review gate. See [04-review-and-commit.md](04-review-and-commit.md). |

## Pre-commit

Runs on every commit, locally:

1. `guard_commit.py` — data, secret and binary guards
2. `ruff format` + `ruff check` — lint and format
3. `check_maps.py --ci` — size budgets, ADR links, INDEX files, mirror frontmatter
4. `check_review.py check` — passing review of the staged diff, for gated paths

Hook failed? Fix the cause, re-stage, commit again. Never `--no-verify` (Ryan only; the guard
hook blocks agents). If the fix touches a gated path, the diff hash changed and it needs a
new review.

## CI

GitHub Actions on every push to `main` (no PRs):

| Job | Command |
|---|---|
| Lint | `ruff format --check`, `ruff check` |
| Types | `pyright` (strict on `src/`) |
| Tests | `pytest` |
| Guards | `guard_commit.py`, `check_maps.py --ci` |

CI cannot see `archive/`, `data/raw/`, `data/prior/` or `.review/`, so it skips mirror-hash and review checks.
Red CI on `main`: fix forward.

## Local MLflow

Arrives with the `ml` group in the models phase.

```bash
uv sync --group ml
uv run mlflow ui        # browse runs from ./mlruns
```

- `mlruns/` and `mlartifacts/` are gitignored. Runs are local to Ryan's machine.
- Each experiment's `README.md` + `metrics.json` is the committed record. Agents read those,
  never `mlruns/`.
- Experiment flow: [03-workflow.md](03-workflow.md).

## Secrets and config

- `.env` is gitignored: this machine's paths. Keys: `CLEAR_RAW_DIR`, `CLEAR_PRIOR_DIR`,
  `CLEAR_BACKUP_RAW_DIR`, `CLEAR_BACKUP_ARCHIVE_DIR`. `scripts/storage.py` reads them
  ([data.md](../standards/data.md#storage)). `.env.example` is the committed template.
- `.cdsapirc` is gitignored. `guard_commit.py` blocks PurpleAir and Copernicus CDS key patterns.
- Methodological constants never go in `.env`; they go in `config/*.yaml`.

## Common commands

| Task | Command |
|---|---|
| Install everything | `uv sync --all-groups` |
| Install git hooks | `uv run pre-commit install` |
| Run all hooks | `uv run pre-commit run --all-files` |
| Format | `uv run ruff format .` |
| Lint (autofix) | `uv run ruff check --fix .` |
| Type check | `uv run pyright` |
| All tests | `uv run pytest` |
| One test layer | `uv run pytest tests/unit` (also `tests/contract`, `tests/golden`) |
| CLI help | `uv run clear --help` |
| Rebuild all figures | `uv run clear figures build` |
| Rebuild one figure | `uv run clear figures build --only <slug>` |
| List figures | `uv run clear figures list` |
| Storage status (are the drives online?) | `uv run python scripts/storage.py` |
| Create or re-point data links | `uv run python scripts/storage.py link` (`--relink` if the target changed) |
| Is the backup identical? | `uv run python scripts/storage.py verify` (`--folder "data/raw/<dataset>"` for one) |
| Refresh inventory | `uv run python scripts/inventory.py` |
| Is inventory current? | `uv run python scripts/inventory.py --check` |
| Plan an intake | `uv run python scripts/intake.py plan` (`--legacy` for legacy folders) |
| Apply an intake | `uv run python scripts/intake.py apply inbox/_plan.yaml` |
| Check maps (full, drives online) | `uv run python scripts/check_maps.py` |
| Check maps (budgets and links only) | `uv run python scripts/check_maps.py --ci` |
| Record a review | `uv run python scripts/check_review.py record --verdict pass --reviewer "<provider/model>" --round N` |
| Check a review | `uv run python scripts/check_review.py check` |
| Convert a doc | `uv run markitdown <file> -o <out.md>` (normally via `/map-refresh`) |
| MLflow UI (models phase) | `uv run mlflow ui` |
