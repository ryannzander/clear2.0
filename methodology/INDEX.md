# methodology/ — one canonical spec per CLEAR part

Specs are the single source for methodology. Evidence (verbatim mirrors) lives in
`knowledge/docs/`; conflicts between sources become ADRs in `decisions/`.
Write new specs from [_template.md](_template.md) with `/spec`.

Line format: `- [slug](slug.md) — purpose · status · old folders`.
Status: `pending` → `draft` → `review` → `accepted`.

Parts are built phase by phase (STATUS.md). Lines marked `pending` are provisional, taken
from the old `Documents/` folder names, and are confirmed when their phase starts.

- [target-pm25](target-pm25.md) — Toronto hourly-mean PM2.5 target · status: pending · old folders 02, 04, 05 (not written)
- [alert-levels](alert-levels.md) — AQHI-aligned alert levels · status: pending · old folders 02, 03, 24 (not written)
- [stations](stations.md) — Toronto government monitors: readers, registry, sites, completeness · status: accepted · old folders 04, 23, 35
- [bad-air-events](bad-air-events.md) — event definition + clustering · status: pending · old folder 05 (not written)
- [lag-plume](lag-plume.md) — lag time + smoke plume analysis · status: pending · old folder 06 (not written)
- [purpleair](purpleair.md) — low-cost sensors · status: pending · old folder 07 (not written)
- [satellite-fire-smoke](satellite-fire-smoke.md) — fire, smoke, AOD products · status: pending · old folder 08 (not written)
- [era5-wind](era5-wind.md) — wind fields · status: pending · old folder 12 (not written)
- [grid](grid.md) — 0.1° Toronto grid and station coverage (domain extent: Phase 2) · status: accepted · old folders 13, 15, 19
- [models](models.md) — GBM + ST-GNN early warning · status: pending · old folders 09, 13, 14 (not written)
- [dashboard](dashboard.md) — dashboard · status: pending · old folder 10 (not written)
