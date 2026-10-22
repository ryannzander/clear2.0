---
name: map-refresh
description: Use when files are in inbox/ or the legacy folders, after any intake, or when the maps look stale. Files originals, writes text mirrors and data cards, refreshes INDEX files and the inventory, then commits.
---

# /map-refresh

## When
New files in `inbox/`; first run on the legacy folders (`CLEAR 2.0 (misc docs)/`, `RAW Data/`); `check_maps.py` fails; the Lead asks for a refresh.

## Inputs
None. Optional: a file list when the Lead fans out a batch.

## Steps
0. Storage: `uv run python scripts/storage.py`. If `data/raw` or `data/prior` is OFFLINE, say so and stop data-card work for that area (mirrors and `archive/` work continue). An offline area keeps its old inventory rows. Then read `manifests/inventory-summary.csv` (one row per dataset folder: files, bytes, mapped/unmapped/stale/superseded/junk) before anything else; Grep `manifests/inventory.csv` only for specific files.
1. Inventory: `uv run python scripts/inventory.py`.
2. Plan: `uv run python scripts/intake.py plan` (first run: `uv run python scripts/intake.py plan --legacy`). Writes `inbox/_plan.yaml`. Do not list or open the legacy folders yourself, and do not sweep `inbox/` (a hook blocks it; there you may write only `inbox/_plan.yaml`); the plan does. `inbox/seagate/` holds the Seagate's Documents, Pitches, handout and old code, waiting for Phase 1 intake: `inbox/seagate/legacy-code/` goes to `archive/legacy-code/` (it is the code that produced the prior outputs); `node_modules` was skipped.
3. Edit the plan. Per entry, set `action`, `dest`, `kind`, `reason`:
   - docs go to `archive/...`; datasets (csv, xlsx, nc, grib, parquet, json) to `data/raw/...`; original names kept.
   - competition, pitch and video material to `archive/competitions/...`.
   - macOS junk (`._*`, `.DS_Store`) is `delete`.
   - unclear or duplicate-with-different-content entries are `skip` with a reason.
4. Apply: `uv run python scripts/intake.py apply inbox/_plan.yaml`. Across drives it copies, hashes the copy against the source and only then deletes the source (a mismatch keeps the source). It refuses overwrites, an offline destination drive, `..` segments and duplicate `src`; logs to `manifests/intake-log.csv`; reruns inventory.
5. Mirrors, one per logical doc (docx preferred over pdf; other formats go in `aliases`; older versions get `status: superseded` and no mirror unless they hold unique content):
   - `uv run markitdown "<archive file>" -o knowledge/docs/<slugified-path>.md`
   - If markitdown fails: `pandoc "<file>" -t gfm -o <same output>`; set `converter: pandoc`.
   - Slugify path and name: lowercase, hyphens.
   - Prepend frontmatter (`source`, `aliases`, `sha256` from `manifests/inventory.csv` via Grep, `converted`, `converter`, `status`, `kind: mirror`).
6. Data cards, one per dataset in `knowledge/data/<dataset-slug>.md`. A multi-file dataset gets one card with `source:` = its folder (covers all files below; no `sha256`). Never one card per file. Peek at a sample file without loading it whole (files can be GBs):

   ```bash
   # dtypes + head from 5 rows; row count by streaming
   uv run python -c "import sys, pandas as pd; p = sys.argv[1]; df = pd.read_csv(p, nrows=5); print(df.dtypes); print(df.head(3)); print(sum(1 for _ in open(p, 'rb')) - 1, 'rows')" "data/raw/<file>.csv"
   # time range: read only the time column, in chunks
   uv run python -c "import sys, pandas as pd; c = sys.argv[2]; r = [(d[c].min(), d[c].max()) for d in pd.read_csv(sys.argv[1], usecols=[c], parse_dates=[c], chunksize=500_000)]; print(min(a for a, _ in r), max(b for _, b in r))" "data/raw/<file>.csv" "<time column>"
   ```

   Other formats: read the schema or a slice only (`pyarrow.parquet.ParquetFile(p).schema_arrow` and `.metadata.num_rows`; `xarray.open_dataset(p)` is lazy; `read_excel(p, nrows=5)`). Fill the frontmatter fields from the writing standard, `validation: unvalidated`. Unknown units, time convention or coverage: write `unknown`, never guess.
   Prior outputs in `data/prior/` (old pipeline results, reference only) also get one folder card each: `source: data/prior/<folder>`, `validation: unvalidated`, and a body line naming the legacy script that made them (`archive/legacy-code/...`) or `<verify>`. Needs the Seagate online; unmapped prior folders fail `check_maps.py` like raw ones.
7. INDEX lines, format `- [name](path) — what it is · status · key fact`, in `knowledge/INDEX.md` or `knowledge/data/INDEX.md`. Competition folders: one line per folder. PNGs: one descriptive line. Split a folder's INDEX when it reaches 100 lines.
8. Refresh: `uv run python scripts/inventory.py` (updates `manifests/inventory.csv`, `manifests/inventory-summary.csv` and `knowledge/_sources.json`).
9. Check: `uv run python scripts/check_maps.py` — the FULL check (walks every original; pre-commit only runs `--ci`). It prints one line per (status, dataset folder), e.g. `unmapped original: data/raw/NOAA/x.grib2 (+143008 more in data/raw/NOAA) — run /map-refresh`: fix one folder (one card) per line. Rerun until it passes.
10. Commit `docs(knowledge): <what was filed>` and push. Commit `inventory-summary.csv`, not `inventory.csv` (local only, gitignored). Mechanical change: no `/review`. No AI attribution.

## Bulk
For more than about 10 new docs, the Lead fans out parallel `librarian` agents, ~10 files each. Workers run steps 5-6 only and return one line per file (`source -> mirror | status | note`). The Lead merges the INDEX lines (step 7) and runs steps 8-10 once.

## Outputs
Originals filed; mirrors in `knowledge/docs/`; cards in `knowledge/data/`; updated INDEX files, inventory summary, `_sources.json`, `intake-log.csv`; one commit.

## Done when
- [ ] `inbox/` holds only `README.md` (and skipped items listed with reasons).
- [ ] Every non-junk original (archive, raw, prior) has a mirror, card, or an INDEX line marking it superseded or media.
- [ ] `check_maps.py` passes.
- [ ] Committed and pushed.

## Standards to load
- `docs/standards/writing.md` (mirror and card frontmatter, INDEX line format).
- `docs/standards/data.md` only when writing data cards.
