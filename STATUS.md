# STATUS

**Phase:** 1 — Stations + grid (answered 2026-10-24) · **Next phase:** 2 — Domain
**Updated:** 2026-10-24

Each phase builds one stage of the system and runs: catalogue → spec → validate → build →
answer ([03-workflow.md](docs/system/03-workflow.md)). Dad's prompts are Issues #1–#5.

## Phase 1 parts

Stages: catalogued → spec'd → validated → built → answered.

| Part (spec slug) | Question | Stage |
|---|---|---|
| `stations` — Toronto government monitors (NAPS, MECP, AirNow): years active, missing data | #1 | answered (EXP-001, EXP-003); inputs validated/partial |
| `grid` — 0.1° grid over the City of Toronto, government sites per cell | #2 | answered (EXP-002) |

Results: 24 stations = 11 sites in the City; 4 sites (East, West, North, Downtown John St.)
are ≥ 96% complete in train, val and test. 12 of 17 Toronto 0.1° cells have no active site.
Figures: `figures/out/fig_station-completeness`, `fig_toronto-stations-grid`. None headline.

## Later phases

- **2 — Domain:** smoke directions (#3), warning radius for 12/24/48 h (#4), cell size
  from McGuire-2026 (#5). Parts: `grid` (domain extent), `lag-plume`, `era5-wind`.
- **Later:** target series (`target-pm25`, `alert-levels`, `bad-air-events`), features
  (`purpleair`, `satellite-fire-smoke`, `era5-wind`), `models`, alerts, `dashboard`.

## Storage

- `data/raw` → `E:\CLEAR 2.0\RAW Data` (886 GB); `data/prior` → `D:\CLEAR 2.0\Cleaned Data`.
- Inventory 2026-10-22; Phase 1 intake 2026-10-24 (5 doc folders, City boundary).
- Validation: boundary `validated`; NAPS, MECP, AirNow ×2 `partial` (Phase 1 read box; reports in `knowledge/data/`).
- Rebuild Phase 1: `uv run clear stations build && uv run clear grid build` (~30 s).

## Decisions (ADRs 0001–0011, all accepted 2026-10-24)

Split 2021–24/2025/2026 · Toronto = City polygon · overlap A/B (merged default) · 75%
completeness flag · `time_utc` hour-beginning · 0.1° cells, edges on multiples, any overlap
counts · sentinels and negatives missing · sites = stations within 500 m · rebuild station
years stand over old doc 04 (old hour-ending UTC labels, 1 km merge) · AirNow as published
(offset noted) · NAPS 060438 out of merged West.

## Next 3 actions

1. Ryan: look at EXP-001–003 and the two figures; say if any is headline material.
2. Phase 2 catalogue: HMS smoke, ERA5 wind, McGuire-2026 paper (old folder 27).
3. Deferred review minors: `research/reviews/phase1-round3-minors.md`.

## Open questions for Ryan

- AirNow rows with `PM25_Measured = 0` are not filtered (stations.md open question 2). Filter them?
- `/backup-check` (E: vs Seagate by sha256) has not run yet.
- `data/prior` has one copy (Seagate only). Copy it to C: as a backup?
- E: is ~93% full. Where do future large downloads go?
