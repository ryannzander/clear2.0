# STATUS

**Phase:** 1 — Stations + grid (from 2026-10-24) · **Next phase:** 2 — Domain
**Updated:** 2026-10-24

Each phase builds one stage of the system and runs: catalogue → spec → validate → build →
answer ([03-workflow.md](docs/system/03-workflow.md)). Dad's prompts are Issues #1–#5.

## Phase 1 parts

Stages: catalogued → spec'd → validated → built → answered.

| Part (spec slug) | Question | Stage |
|---|---|---|
| `stations` — Toronto government monitors (NAPS, MECP, AirNow): years active, missing data | #1 | — |
| `grid` — 0.1° grid over the City of Toronto, government stations per cell | #2 | — |

## Later phases

- **2 — Domain:** smoke directions (#3), warning radius for 12/24/48 h (#4), cell size
  from McGuire-2026 (#5). Parts: `grid` (domain extent), `lag-plume`, `era5-wind`.
- **Later:** target series (`target-pm25`, `alert-levels`, `bad-air-events`), features
  (`purpleair`, `satellite-fire-smoke`, `era5-wind`), `models`, alerts, `dashboard`.
  Part list is provisional (old folder names); folders 25, 26, 27 not placed yet.

## Storage

- `data/raw` → `E:\CLEAR 2.0\RAW Data` (886 GB, copy done 2026-10-21, 0 failed).
- `data/prior` → `D:\CLEAR 2.0\Cleaned Data` (Seagate, ~130 GB): reference/golden only.
- Inventory done 2026-10-22 (8631c34): 255,640 originals, 227,472 not filed yet.
- Check links: `uv run python scripts/storage.py`.

## Ryan's decisions (2026-10-24)

- Catalogue only what each phase reads; phases renamed so Phase 1 = stations + grid.
- Dad's prompts are Issues; the choices inside them become proposed ADRs.
- "Toronto" = the City of Toronto boundary.
- Missing data = % of hours present plus a 75% completeness flag.
- Station overlap is A/B tested: `merged` vs `separate`.
- The legacy duplicates on C: stay.

## Next 3 actions

1. Catalogue: data cards (NAPS, MECP, AirNow ×2, prior stations), scoped intake of doc
   folders 04, 15, 19, 23, 35 + NAPS/MECP summaries, `/ingest` the City boundary.
2. Spec: `methodology/stations.md`, `grid.md`, six proposed ADRs for Ryan.
3. Validate, build `clear.stations` + `clear.grid`, answer with EXP-001–003.

## Open questions for Ryan

- `time_utc`: hour-beginning (provisional) or hour-ending? ADR in the spec step.
- Data split 2021–24 train / 2025 val / 2026 test (dad's background): ADR in the spec step.
- `/backup-check` (E: vs Seagate by sha256) has not run yet.
- `data/prior` has one copy (Seagate only). Copy it to C: as a backup?
- E: will be ~93% full. Where do future large downloads go?
