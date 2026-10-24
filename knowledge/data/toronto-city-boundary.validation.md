---
dataset: toronto-city-boundary
date: 2026-10-24
spec: methodology/grid.md#validation-criteria
result: validated
---

# toronto-city-boundary — validation

Checks run by `notebooks/validate_phase1.py` on the Phase 1 build (`uv run clear stations build`).

| Check | Spec source | Result | n failing |
|---|---|---|---|
| geometry valid, one polygon | card | pass | 0 |
| CRS: WGS 84 | stations.md#select-toronto-stations | pass | 0 |
| area (UTM 17N) 641.4 km2 vs City 641 km2 | card Coverage | pass | 0 |
| sum of city_frac x cell area 641.4 km2 vs 641.4 km2 | grid.md#validation-criteria | pass | 0 |
| Toronto stations in Toronto cells | grid.md#validation-criteria | pass | 0 |

## Issues and handling

- None.
