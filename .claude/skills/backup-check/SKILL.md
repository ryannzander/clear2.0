---
name: backup-check
description: Use when Ryan asks if the Seagate backup is current, after large intakes, or before a milestone. Compares backup sha256s against manifests/inventory.csv for data/raw and archive, and offers a safe copy of what is missing.
---

# /backup-check

## When
After `/map-refresh` or `/ingest` adds originals, before a milestone, or on request. Originals are gitignored, so the Seagate backup is their only second copy.

## Inputs
Two keys in the repo-root `.env` (gitignored; `.env.example` is the template):

| Key | Backs up | Mapping |
|---|---|---|
| `CLEAR_BACKUP_RAW_DIR` | `data/raw/` | `data/raw/<x>` ↔ `<backup>/<x>` |
| `CLEAR_BACKUP_ARCHIVE_DIR` | `archive/` | `archive/<x>` ↔ `<backup>/<x>` |

`data/prior/` has no second copy (known single-copy risk). It is not checked here; report it as "no backup".

## Steps
1. Storage status: `uv run python scripts/storage.py`. Both backup folders and `data/raw` must be online. If one is OFFLINE or a key is missing, stop and tell the Lead (Ryan plugs in the drive or fixes `.env`; `storage.py link --relink` after a drive-letter change).
2. Refresh the inventory: `uv run python scripts/inventory.py`.
3. Compare: `uv run python scripts/storage.py verify`. It hashes each backup copy of every `data/raw` and `archive` inventory row (junk skipped), prints one line per dataset folder as it goes, then the first 20 missing/mismatched paths; exit 1 if any. Read-only on both sides.
   - All of raw (~886 GB on USB) takes hours: run it in the background, or one dataset at a time with `--folder "data/raw/<dataset>"` (folders from `manifests/inventory-summary.csv`).
   - macOS `._*` junk on the Seagate is never copied and never counted.
4. Report per area: counts of ok, missing, mismatched; first 20 paths of each. `verify` only checks inventory rows against the backup: backup files that are not in the inventory (extras) are not checked or listed.
5. If files are missing, offer the copy with the interactive question tool (recommended: dry run first). The copy adds ONLY missing files and never overwrites. Run `robocopy` from PowerShell (Git Bash rewrites `/E`-style options). Dry run per area, `/L` lists without copying: `robocopy "<source>" "<backup>" /E /XC /XN /XO /R:1 /W:1 /XF ._* .DS_Store /L` with source `data\raw` ↔ `CLEAR_BACKUP_RAW_DIR` and `archive` ↔ `CLEAR_BACKUP_ARCHIVE_DIR`. Run without `/L` only after Ryan agrees. Never `/MIR` or `/PURGE`.
6. Mismatched files: `/XC /XN /XO` make robocopy skip them, so the copy never overwrites; they stay listed for Ryan. Ask Ryan which side is right.
7. Append a bullet to `research/log/YYYY-MM-DD.md` with the date, counts per area and action taken.

## Outputs
A report in the reply (counts + paths per area); optionally copied files; a log bullet.

## Done when
- [ ] Every raw and archive inventory row is classed ok, missing or mismatched.
- [ ] Nothing was deleted or overwritten on the backup (never use `/MIR` or `/PURGE`; mismatches are never overwritten).
- [ ] After any copy, step 3 is rerun and shows 0 missing.
- [ ] Mismatches are listed for Ryan.
- [ ] `data/prior/` reported as having no backup.

## Standards to load
- `docs/standards/data.md` (Storage, Backup, inventory fields).
