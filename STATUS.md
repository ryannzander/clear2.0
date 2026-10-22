# STATUS

**Phase:** 0 — Scaffold (done) · **Next phase:** 1 — Map
**Updated:** 2026-10-21

## Per-part status

Parts are provisional (taken from the old `Documents/` folder names). The Methodologist
confirms the final list in Phase 2. Stages: mapped → spec'd → validated → built.

| Part (spec slug) | Old folders | Stage |
|---|---|---|
| `target-pm25` — Toronto hourly-mean PM2.5 target | 02, 04, 05 | — |
| `alert-levels` — AQHI-aligned alert levels | 02, 03, 24 | — |
| `stations` — Toronto monitors + EPA monitor types | 04, 16 | — |
| `bad-air-events` — event definition + clustering | 05 | — |
| `lag-plume` — lag time + smoke plume analysis | 06 | — |
| `purpleair` — low-cost sensors | 07, 22 | — |
| `satellite-fire-smoke` — fire, smoke, AOD products | 08 | — |
| `era5-wind` — wind fields | 12 | — |
| `grid` — 1000 km domain, grid + dynamic grid | 13, 15, 19, 21 | — |
| `models` — GBM + ST-GNN early warning | 09, 13, 14 | — |
| `dashboard` | 10 | — |

Not yet placed: folders 25 (Virginia), 26 (Research Papers), 27 (optimal PM2.5 spacing).

## Storage (2026-10-21)

- `data/raw` → `E:\CLEAR 2.0\RAW Data` (internal NVMe, 886.5 GB, ~155k files).
- `data/prior` → `D:\CLEAR 2.0\Cleaned Data` (Seagate, 130 GB): old pipeline outputs,
  reference only until validated + an ADR approves reuse.
- Seagate = backup of `data/raw` and `archive/`. Check: `uv run python scripts/storage.py`.

## Blockers

- Raw copy Seagate → E: running (log: `E:\CLEAR 2.0\_logs\`; done when `copy-done.txt`
  exists). Keep the PC awake; rerun `copy-from-seagate.cmd` to resume if interrupted.

## Next 3 actions

1. When the copy is done: `uv run python scripts/inventory.py` (hashes E:), then
   `/backup-check` to confirm E: matches the Seagate by sha256.
2. `/map-refresh` (Phase 1): legacy folders + `inbox/seagate/` → archive; data cards for
   every `data/raw` and `data/prior` dataset folder.
3. `/spec` per part (Phase 2); conflicts become ADRs for Ryan.

## Open questions for Ryan

- `time_utc`: hour-beginning (provisional) or hour-ending? Phase 2 ADR.
- "1000 km domain": ±1000 km around Toronto (provisional, `config/grid.yaml`) or 1000 km
  across? Square or radius? Settled by the `grid` spec.
- The repo's local `RAW Data/` and `CLEAR 2.0 (misc docs)/` look like older partial copies
  of the Seagate. After Phase 1 compares hashes, delete the local duplicates to free C:?
- `data/prior` has one copy (Seagate only). Copy it to C: (431 GB free) as a backup?
- E: will be ~93% full (~65 GB spare). Where do future large downloads go?
