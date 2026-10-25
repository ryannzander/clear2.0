---
dataset: airnow-hourlyaqobs
date: 2026-10-24
spec: methodology/stations.md#validation-criteria
result: partial
---

# airnow-hourlyaqobs — validation

Checks run by `notebooks/validate_phase1.py` on the Phase 1 build (`uv run clear stations build`).

| Check | Spec source | Result | n failing |
|---|---|---|---|
| interim schema (UTC, on the hour, ids) | stations.md#read-sources | pass | 0 |
| non-numeric cells | ADR 0007 / code.md | pass (reader raises) | 0 |
| sentinel cells found → missing | ADR 0007 | handled in QC | 0 |
| other negative cells → missing | ADR 0007 | handled in QC | 99 |
| repeat station-hours → averaged | ADR 0007 | handled in QC | 0 |
| processed hourly ≥ 0, unique station-hour | stations.md#validation-criteria | pass | 0 |
| Toronto stations and years vs card | card Coverage | pass | 0 |
| time convention: lag-0 best vs co-located | ADR 0005 | 11 co-located pairs, best r at lag 0 in all: True | 0 |

## Issues and handling

- 517,158 raw rows in the read scope (City bounds ± 0.5°).
- Sentinels, negatives and repeats stay in the interim table (lossless) and are removed or averaged in `processed/stations/hourly_pm25` (ADR 0007).
- Preliminary data (card); AirNow reads 0.3–0.5 µg/m³ above NAPS/MECP at East, West, North (EXP-003); used as published, offset noted (ADR 0010, decided 2026-10-24).
- `PM25_Measured = 0` rows are not filtered (stations.md open question 2).
- Scope: the Phase 1 read box only (City bounds +/- the registry margin); stations elsewhere in the card's coverage are not checked yet, so the result is at most partial.
