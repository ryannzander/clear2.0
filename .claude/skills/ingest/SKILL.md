---
name: ingest
description: Use when a new raw dataset must be fetched or registered (ground monitors, PurpleAir, HMS/FIRMS, ERA5, files Ryan supplies) with full provenance.
---

# /ingest

## When
A dataset is needed that is not yet in `data/raw/`, or an existing one needs a refreshed pull.

## Inputs
Source name, what to fetch (stations, variables, time range, bounding box), the requesting issue or spec section.

## Steps
0. Run `uv run python scripts/storage.py` first. Ingest writes into `data/raw`, so it must be online (and linked); if not, stop and tell the Lead.
1. Check for an existing copy: `data/sources.yaml` and `knowledge/data/INDEX.md`. If one exists, stop and report it unless a refresh was requested.
2. Fetch code lives in `src/clear/ingest/<source>.py`: typed, tested, one module per source, query parameters as arguments. Credentials come from environment or `.env`, never from code or logs. Reuse the module if it exists.
3. Download into a fresh folder: `inbox/<dataset-slug>/`. Run the module (`uv run python -m clear.ingest.<source> --out inbox/<dataset-slug>`). Keep the provider's file names.
4. Add the entry to `data/sources.yaml` with the fields required by `docs/standards/data.md` (URL, query, retrieval date, license, fetch module). Record the license even if permissive.
5. File it: `uv run python scripts/intake.py plan`, check that the plan sends the files to `data/raw/<...>`, then `uv run python scripts/intake.py apply inbox/_plan.yaml`.
6. Write the data card `knowledge/data/<dataset-slug>.md`: peek with pandas (`uv run python -c "..."`: columns, dtypes, rows, time range) as in `/map-refresh` step 6. Record `time_convention` as documented by the provider (local standard time or UTC, hour-ending or hour-beginning). Set `validation: unvalidated`.
7. Add the line to `knowledge/data/INDEX.md`; run `uv run python scripts/inventory.py` and the FULL `uv run python scripts/check_maps.py` (a new original and card were added, which `--ci` does not look at; needs the data drives online).
8. Commit in two units:
   - fetch code, schemas, tests: `/review` first, then `feat: ingest <source> fetcher`.
   - provenance, card, INDEX, inventory: `data: register <dataset-slug>` (mechanical).
   Push after each. No AI attribution.
9. Hand off: tell the Lead the dataset is ready for `/validate-data` (needs a spec first).

## Outputs
Dataset in `data/raw/`; `data/sources.yaml` entry; data card; INDEX line; fetch module (reviewed); intake-log rows.

## Done when
- [ ] `data/sources.yaml` entry has URL, query, date, license.
- [ ] sha256 of the raw files is in `manifests/inventory.csv` (local; Grep it).
- [ ] Card exists with `validation: unvalidated` and a stated time convention (or `unknown`, flagged).
- [ ] No secrets in code, logs, card or commit.
- [ ] `inbox/<dataset-slug>/` is empty; `check_maps.py` passes.
- [ ] Both commits pushed.

## Standards to load
- `docs/standards/data.md` (stages, schemas, sources fields).
- `docs/standards/naming-units-time.md` when normalizing time at ingest.
