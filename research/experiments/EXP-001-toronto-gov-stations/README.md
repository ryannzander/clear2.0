---
id: EXP-001
title: Toronto government stations, years active, missing data
issue: "#1"
spec: methodology/stations.md#completeness
status: done
headline: false
mlflow_experiment: EXP-001-toronto-gov-stations
---

# EXP-001 — Toronto government stations, years active, missing data

## Hypothesis

Not a test; a census. Issue #1 asks which NAPS, Ontario MECP and AirNow stations lie in the
City of Toronto, which years each was active, and how much data each is missing.

## Setup

- **Data versions:** `naps-hourly-pm25`, `mecp-hourly-pm25`, `airnow-hourlyaqobs`,
  `airnow-hourlydata-2014-2019`, `toronto-city-boundary` (sha256 in `data/sources.yaml`)
- **Validation:** naps-hourly-pm25, mecp-hourly-pm25, airnow-hourlyaqobs, airnow-hourlydata-2014-2019 `partial` (Phase 1 read box; MECP hour label observed; AirNow preliminary), toronto-city-boundary `validated` (`knowledge/data/*.validation.md`)
- **Config:** `config/stations.yaml`, `config/splits.yaml` (ADRs 0001–0005, 0007, 0008)
- **Seed(s):** none (deterministic)
- **Rerun:** `uv run clear stations build && uv run clear stations report --json out.json`; the `metrics` block of `metrics.json` is that JSON.

## Result

24 government stations have stood inside the City since 2000 (13 NAPS, 6 MECP, 5 AirNow).
Linked by location (< 500 m), they are **11 physical sites**. Full table:
`uv run clear stations report`; figure: [fig_station-completeness](../../../figures/out/fig_station-completeness.png).

| Site | Stations (years active) | Train 2021–24 | Val 2025 | Test 2026* |
|---|---|---|---|---|
| Toronto East (Kennedy/Lawrence) | NAPS 060410 (2002–24), MECP 33003 (2003–25), AirNow 000060410 (2023–26) | 0.99 | 1.00 | 0.98 |
| Toronto West (Resources Rd.) | NAPS 060430 (2000–24), 060438 (2016–24), MECP 35125 (2003–25), AirNow 124000060430 (2023–26) | 1.00 | 1.00 | 0.98 |
| Toronto North (Dufferin) | NAPS 060440 (2017–24), MECP 34021 (2017–25), AirNow 124000060440 (2023–26) | 0.99 | 0.99 | 0.98 |
| Toronto Downtown (55 John St.) | NAPS 060445 (2019–24), MECP 31129 (2019–25), AirNow 124000060445 (2020–26) | 0.99 | 0.98 | 0.96 |
| NAPS 060435 (43.611, −79.522) | NAPS 060435 (2010–24) | 0.90 | 0.00 | 0.00 |
| Downtown, Bay/Wellesley | NAPS 060424 (2000–02), 060433 (2003–19), MECP 31103 (2003–19), AirNow 000060424 (2014–21) | 0.02 | 0 | 0 |
| Toronto North (Hendon/Yonge) | NAPS 060421 (2000–16), MECP 34020 (2003–16) | 0 | 0 | 0 |
| Four short-lived NAPS sites | 060403 (2000–01), 060413 (2002–10), 060429 (2001–12), 060439 (2019) | 0 | 0 | 0 |

Values = fraction of hours present for the site (merged series). *2026 runs to 2026-10-08.

- Sites meeting the 75% flag: train 5, val 4, test 4. Stations: train 11, val 8, test 4.
- NAPS ends 2024, MECP 2025; for 2026 only AirNow reports, at the 4 active sites.

## Conclusion

Toronto has **4 government sites with near-complete data in every split** (East, West, North,
Downtown John St.); a fifth (060435) covers train only. Everything else closed before 2021.
The same physical site appears in two or three networks, so counting "stations" overstates
coverage (24 stations, 11 sites).

## Next

- EXP-003 compares merged vs separate series; EXP-002 places the sites in 0.1° cells.
