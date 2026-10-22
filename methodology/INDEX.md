# methodology/ — one canonical spec per CLEAR part

Specs are the single source for methodology. Evidence (verbatim mirrors) lives in
`knowledge/docs/`; conflicts between sources become ADRs in `decisions/`.
Write new specs from [_template.md](_template.md) with `/spec`.

Line format: `- [slug](slug.md) — purpose · status · old folders`.
Status: `pending` → `draft` → `review` → `accepted`.

The list below is **provisional**, taken from the old `Documents/` folder names.
The Methodologist confirms the final list in Phase 2.

- [target-pm25](target-pm25.md) — Toronto hourly-mean PM2.5 target · status: pending · old folders 02, 04, 05 (not written)
- [alert-levels](alert-levels.md) — AQHI-aligned alert levels · status: pending · old folders 02, 03, 24 (not written)
- [stations](stations.md) — Toronto monitors + EPA monitor types · status: pending · old folders 04, 16 (not written)
- [bad-air-events](bad-air-events.md) — event definition + clustering · status: pending · old folder 05 (not written)
- [lag-plume](lag-plume.md) — lag time + smoke plume analysis · status: pending · old folder 06 (not written)
- [purpleair](purpleair.md) — low-cost sensors · status: pending · old folder 07 (not written)
- [satellite-fire-smoke](satellite-fire-smoke.md) — fire, smoke, AOD products · status: pending · old folder 08 (not written)
- [era5-wind](era5-wind.md) — wind fields · status: pending · old folder 12 (not written)
- [grid](grid.md) — 1000 km domain, grid + dynamic grid · status: pending · old folders 13, 15, 19 (not written)
- [models](models.md) — GBM + ST-GNN early warning · status: pending · old folders 09, 13, 14 (not written)
- [dashboard](dashboard.md) — dashboard · status: pending · old folder 10 (not written)
