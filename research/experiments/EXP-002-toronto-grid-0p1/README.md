---
id: EXP-002
title: Toronto 0.1 degree grid and government sites per cell
issue: "#2"
spec: methodology/grid.md#coverage-report
status: done
headline: false
mlflow_experiment: EXP-002-toronto-grid-0p1
---

# EXP-002 — Toronto 0.1° grid and government sites per cell

## Hypothesis

Issue #2's rule: every 0.1° cell in Toronto holds one government monitoring station. Tested
on the cells that overlap the City (ADR 0006), counting sites with data since 2021.

## Setup

- **Data versions:** stations outputs of EXP-001; `toronto-city-boundary` sha256 `7c4b32f9…`
- **Validation:** naps-hourly-pm25, mecp-hourly-pm25, airnow-hourlyaqobs, airnow-hourlydata-2014-2019 `partial` (Phase 1 read box; MECP hour label observed; AirNow preliminary), toronto-city-boundary `validated` (`knowledge/data/*.validation.md`)
- **Config:** `config/grid.yaml: toronto_grid` (0.1°, any overlap), `config/splits.yaml`
- **Seed(s):** none (deterministic)
- **Rerun:** `uv run clear grid build --json out.json`; the `metrics` block of `metrics.json` is that JSON.

## Result

| Metric | Value |
|---|---|
| Cells built (City bounds snapped to 0.1°) | 24 (4 rows × 6 columns) |
| Toronto cells (overlap the City) | 17 |
| … with 0 active government sites | **12** |
| … with 1 active site | 4 |
| … with 2+ active sites | 1 (N4360W07940, downtown: John St. + Bay/Wellesley until 2021-01) |
| … with any site ever (2000–2026) | 6 (incl. `N4360W07970`, whose only site, NAPS 060432 / MECP 46109, lies just outside the City) |

Figure: [fig_toronto-stations-grid](../../../figures/out/fig_toronto-stations-grid.png).
A 0.1° cell is ~11.1 km N–S × 8.0 km E–W at 43.7°N; the City (641.7 km²) touches 17 cells,
several only as slivers.

## Conclusion

The one-station-per-cell rule **does not hold**: 12 of 17 Toronto cells have no active
government site. Six active sites cover 5 cells: East, West, North, NAPS 060435 (to 2024) one cell each, and
Downtown John St. plus Bay/Wellesley (active only through AirNow 000060424 to 2021-01-28)
share `N4360W07940`. Filling the empty cells needs other data (PurpleAir, models) or larger cells — issue #5.

## Next

- Phase 2: cell size (issue #5) and domain extent (issues #3–#4).
