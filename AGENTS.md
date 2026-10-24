# CLEAR 2.0 — Agent Guide

CLEAR 2.0 is a wildfire-smoke early-warning research system for Toronto. It forecasts
PM2.5 and AQHI-aligned alert levels from ground monitors (NAPS, Ontario, EPA), low-cost
sensors (PurpleAir), satellite fire/smoke products and ERA5 wind. This repo is the R&D
workspace: methodology, data, code, experiments, figures.

Owner: Ryan Zander (solo). Agents do the work; Ryan makes the methodology calls.

## Start of every session

1. Read `STATUS.md` — current phase, per-part status, next actions, open questions.
2. Find things through the maps, never by sweeping folders:
   this file → the folder's `INDEX.md` → the file. Or run `/where <question>`.
3. Read text, not binaries. Every doc in `archive/` has a mirror in `knowledge/docs/`;
   every dataset has a data card in `knowledge/data/`.
4. Before data work: `uv run python scripts/storage.py` (are `data/raw`, `data/prior` online?).

## Repo map

| Path | What lives there | Map |
|---|---|---|
| `inbox/` | The only drop zone for new files. Emptied by `/map-refresh`. | `inbox/README.md` |
| `archive/` | Original docs (docx/pdf/png/mp4), read-only, gitignored. | `knowledge/INDEX.md` |
| `data/raw/` | Original datasets, immutable, gitignored. Junction to the raw copy on E: (`scripts/storage.py`). | `knowledge/data/INDEX.md` |
| `data/prior/` | Old pipeline outputs: reference and golden numbers only, never a pipeline input. Junction to the Seagate (D:). | `knowledge/data/INDEX.md` |
| `data/{interim,processed,features}/` | Pipeline outputs (Parquet tables, Zarr grids), gitignored, local on C:. | `data/INDEX.md` |
| `data/sources.yaml` | Provenance of every raw dataset (URL, query, date, license). | — |
| `manifests/inventory-summary.csv` | Committed: one row per dataset folder (files, bytes, status counts). Read first. | — |
| `manifests/inventory.csv` | Generated, local only (gitignored, Grep-able): every original file with size + sha256 + mirror path. | — |
| `knowledge/` | Text mirrors of docs, data cards, `_sources.json` (source → mirror). | `knowledge/INDEX.md` |
| `methodology/` | One canonical spec per methodology part. Read these first. | `methodology/INDEX.md` |
| `decisions/` | ADRs, one file per decision, `NNNN-slug.md`. | `decisions/INDEX.md` |
| `research/experiments/` | `EXP-NNN-slug/` with `README.md` + `metrics.json`. | `research/INDEX.md` |
| `research/literature/` | Scout's cited notes, one file per topic. | `research/literature/INDEX.md` |
| `research/log/` | Append-only daily log, `YYYY-MM-DD.md`. | — |
| `src/clear/` | The Python package. One module per methodology part. | `src/clear/INDEX.md` |
| `config/` | Every methodological constant, YAML, each linked to its spec/ADR. | `config/INDEX.md` |
| `figures/` | `src/fig_<slug>.py` → `out/fig_<slug>.{png,svg,md}`. | `figures/INDEX.md` |
| `notebooks/` | Scratch only, jupytext `.py`. Never imported. | — |
| `tests/` | `unit/`, `contract/` (schemas), `golden/` (reproduce old numbers). | — |
| `scripts/` | Repo tooling: inventory, intake, storage links, map checks, commit guards. | `scripts/INDEX.md` |
| `docs/system/` | How this R&D system works (flowcharts). | `docs/system/00-overview.md` |
| `docs/standards/` | Code, naming/units/time, data, figures, git, writing. | see below |

The legacy folders `CLEAR 2.0 (misc docs)/` and `RAW Data/` are inbox sources until
intake files them into `archive/` and `data/raw/`; each phase files only what it reads.
Treat them exactly like `archive/`.

## Hard rules

1. **Originals are immutable.** Never write, move or delete in `archive/`, `data/raw/`,
   `data/prior/` or the legacy folders. Only `scripts/intake.py` (via `/map-refresh`) and
   `/ingest` write there. Hooks enforce this — if a hook blocks you, follow its message;
   never work around it.
2. **No sweeps.** Never Glob/Grep inside `archive/`, `data/raw/`, `data/prior/` or the
   legacy folders. Use `knowledge/`, the INDEX files and `manifests/inventory-summary.csv`;
   Grep `manifests/inventory.csv` for single files.
3. **No binaries when a mirror exists.** Read the `.md` mirror or data card instead.
4. **Methodology decisions belong to Ryan.** Conflicting sources, new choices, and changes
   to targets, thresholds, splits or metrics become an ADR with `status: proposed`; ask Ryan.
   Never resolve silently. Write the conflict as an open question in the spec meanwhile.
5. **Headline results need Ryan.** Any number or figure headed for a paper, pitch or
   competition submission is shown to Ryan before it is marked `headline: true`.
6. **No magic numbers.** Methodological constants live in `config/*.yaml` with a comment
   linking the spec section or ADR.
7. **One vocabulary.** Names come from `GLOSSARY.md`. Units go in names (`pm25_ugm3`,
   `wind_speed_ms`, `lag_h`). All timestamps are tz-aware UTC in a column named `time_utc`.
8. **Figures come from code.** Every figure is a script in `figures/src/` plus a sidecar.
   Colors only from `src/clear/viz/tokens.yaml`.
9. **Review before commit.** Changes to `src/`, `config/`, `methodology/`, `decisions/`,
   `research/experiments/`, `figures/src/`, `scripts/`, `tests/`, `.claude/hooks/`, the
   review skill and reviewer agent, `.claude/settings.json`, `.github/workflows/`,
   `.pre-commit-config.yaml`, `.gitignore`, `.ignore`, `pyproject.toml` or `uv.lock` (list: `GATED` in
   `scripts/check_review.py`) must pass `/review` first. `INDEX.md` files are never gated. The
   pre-commit hook checks for a passing review of the staged diff. Skipping it
   (`CLEAR_SKIP_REVIEW=1`, `git commit --no-verify`) is Ryan only; a hook blocks agents.
10. **Commit and push.** Work directly on `main`. Commit after each logical unit and push
    right away. Conventional messages (`feat|fix|docs|data|exp|fig|chore: ...`).
    **Never add AI attribution** — no `Co-Authored-By`, no "Generated with" footers.
11. **Size budgets.** AGENTS.md ≤ 150 lines, any INDEX.md ≤ 100 lines (split the folder
    if it grows past that), STATUS.md ≤ 60 lines, any docs file ≤ 200 lines.
12. **End of session.** Rewrite `STATUS.md`; append a few bullets to
    `research/log/YYYY-MM-DD.md` (decisions, outcomes, what's next).

## Roles

The main session is the **Lead**: it plans, delegates, keeps STATUS.md current, and is
the only role that talks to Ryan. Specialists live in `.claude/agents/`.

| Role | Model | Owns |
|---|---|---|
| Lead | Opus | Planning, delegation, STATUS.md, asking Ryan |
| Librarian | Sonnet | `/where`, `/map-refresh` — maps, mirrors, data cards, inbox |
| Data Steward | Opus | `/ingest`, `/validate-data`, `/backup-check` |
| Methodologist | Opus | `/spec`, `/adr`, `/method-check` |
| Experimenter | Opus | `/experiment` and pipeline code in `src/clear/` |
| Figure Maker | Sonnet | `/figure` |
| Scout | Sonnet | External literature → `research/literature/` (cited, or it doesn't exist) |
| Reviewer | Opus 5.5 (fresh context) | `/review` — the gate before every gated commit |

## Skills

| Skill | Use it to |
|---|---|
| `/where` | Answer "where is X / what do we know about X" from the maps only |
| `/map-refresh` | Process `inbox/`, refresh mirrors, data cards, INDEX files, inventory |
| `/ingest` | Fetch or register a raw dataset with full provenance |
| `/validate-data` | Validate a dataset against its spec; write the report + card status |
| `/backup-check` | Compare the Seagate backups of `data/raw/` and `archive/` with the inventory |
| `/spec` | Distill mirrors into a methodology spec from the template |
| `/adr` | Draft a decision record for Ryan |
| `/method-check` | Check that code matches its spec |
| `/experiment` | Run an experiment from its issue: scaffold, run, record |
| `/figure` | Make or update a figure that meets the figure standard |
| `/review` | Independent review of the staged diff (required for gated paths) |

## Phases

Each phase builds one stage of the forecasting system and runs the same loop inside it:
**catalogue** what it reads → **spec** (conflicts → ADRs for Ryan) → **validate** →
**build** → **answer** the Issues that opened it. Catalogue only what the stage reads.
0. **Scaffold** — this R&D system (done). 1. **Stations + grid** — Toronto government
monitors and the 0.1° grid (prompts 1–2). 2. **Domain** — smoke directions, warning
radius, cell size (prompts 3–5). Later: target series → features → models → alerts →
dashboard. Details and flowcharts: `docs/system/03-workflow.md`.

## Standards — load only the one you need

- Code shape, typing, docstrings, tests → `docs/standards/code.md`
- Names, units, time zones → `docs/standards/naming-units-time.md`
- Raw data, stages, schemas, sources → `docs/standards/data.md`
- Figures, colors, Mermaid diagrams → `docs/standards/figures.md`
- Git, commits, pre-commit, CI → `docs/standards/git.md`
- Mirrors, INDEX lines, data cards, glossary → `docs/standards/writing.md`
- Specs and ADRs → `methodology/_template.md`, `decisions/_template.md`

Toolchain: `uv` (Python 3.12), `ruff`, `pyright` (strict on `src/`), `pytest`, `pre-commit`.
Run things with `uv run ...`. Package CLI: `uv run clear --help`.
