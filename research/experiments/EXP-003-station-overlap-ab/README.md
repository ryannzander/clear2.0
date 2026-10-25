---
id: EXP-003
title: Station overlap A/B, merged vs separate series
issue: "#1"
spec: methodology/stations.md#combine-sources
status: done
headline: false
mlflow_experiment: EXP-003-station-overlap-ab
---

# EXP-003 — Station overlap A/B: merged vs separate series

## Hypothesis

Merging co-located NAPS/MECP/AirNow stations into one series per site (priority NAPS > MECP >
AirNow, ADR 0003) gives, for every site and split, a series at least as complete as the
site's best single station, with no double counting; and the sources agree closely enough
(bias, RMSE, r) to be used interchangeably.

## Setup

- **Data versions:** stations outputs of EXP-001
- **Validation:** naps-hourly-pm25, mecp-hourly-pm25, airnow-hourlyaqobs, airnow-hourlydata-2014-2019 `partial` (Phase 1 read box; MECP hour label observed; AirNow preliminary), toronto-city-boundary `validated` (`knowledge/data/*.validation.md`)
- **Config:** `config/stations.yaml` (`overlap_mode`, `source_priority`, `crosswalk_max_distance_m`, `merged_exclude_stations`; ADRs 0003, 0008, 0010, 0011)
- **Seed(s):** none (deterministic)
- **Rerun:** `uv run clear stations report --json out.json` (keys `separate`, `merged`, `merged_vs_best_member`, `agreement`).

## Result

| Metric | Separate (stations) | Merged (sites) |
|---|---|---|
| Series in Toronto | 24 | 11 |
| Meeting 75% — train / val / test | 11 / 8 / 4 | 5 / 4 / 4 |
| Merged hours by source | — | NAPS 1,087,622 · MECP 35,299 · AirNow 41,168 |

Per site, merged vs its best single station (fraction of hours present; `merged_vs_best_member`):

| Site | Train | Val | Test |
|---|---|---|---|
| East (naps:060410) | 0.993 vs 0.991 | 0.998 vs 0.996 | 0.982 vs 0.982 |
| West (naps:060430) | 0.991 vs 0.990 | 0.996 vs 0.993 | 0.985 vs 0.984 |
| North (naps:060440) | 0.988 vs 0.988 | 0.995 vs 0.992 | 0.984 vs 0.984 |
| Downtown John St. (naps:060445) | 0.995 vs 0.982 | 0.980 vs 0.971 | 0.961 vs 0.961 |

Source agreement at shared sites (`agreement`; bias = station_b − station_a, AirNow sorts first):

- NAPS vs MECP: bias ≈ 0, r 0.997–1.000. Same instruments.
- AirNow vs NAPS/MECP at East, West and North (AirNow from 2023-07): AirNow reads
  **0.3–0.5 µg/m³ higher**, r ≈ 0.99. Downtown John St. (124000060445): no offset (≤ 0.005).
- AirNow `000060424` = MECP 31103 exactly (r 1.000), confirming the ID anomaly (ADR 0008).
- NAPS 060438 vs 060430 (same site): +1.47 µg/m³, r 0.82 — a different instrument.
- Every pair correlates best at lag 0 (lag ±1 h: 0.77–0.97), confirming the time conventions,
  including MECP's undocumented hour-ending label.

## Conclusion

**Partly supported.** Completeness: supported — for every site and split the merged series
is at least as complete as the best single station (up to +1.2 points, from filling one
network's gaps with another's), with 11 series instead of 24 and no double counting.
Interchangeability: not supported — NAPS 060438 differs from 060430 at the West site (RMSE
4.39 µg/m³, r 0.82) and was averaged into it before ADR 0011, and AirNow reads 0.3–0.5 µg/m³ high at three
sites, so the merged series steps when AirNow takes over in 2026 (ADRs 0010, 0011). Keep `overlap_mode: merged` as the default; the
switch stays for later model experiments. Ryan decided both on 2026-10-24: AirNow stays as published with the offset noted (ADR 0010);
060438 is left out of the merged series (ADR 0011). The numbers above are after that change.

## Next

- Repeat the A/B inside the first model experiment (target series phase).
