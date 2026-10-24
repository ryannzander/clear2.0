---
dataset: naps-hourly-pm25
date: 2026-10-24
spec: methodology/stations.md#validation-criteria
result: partial
---

# naps-hourly-pm25 — validation

Checks run by `notebooks/validate_phase1.py` on the Phase 1 build (`uv run clear stations build`).

| Check | Spec source | Result | n failing |
|---|---|---|---|
| interim schema (UTC, on the hour, ids) | stations.md#read-sources | pass | 0 |
| non-numeric cells | ADR 0007 / code.md | pass (reader raises) | 0 |
| sentinel cells found → missing | ADR 0007 | handled in QC | 306929 |
| other negative cells → missing | ADR 0007 | handled in QC | 1366 |
| repeat station-hours → averaged | ADR 0007 | handled in QC | 131424 |
| processed hourly ≥ 0, unique station-hour | stations.md#validation-criteria | pass | 0 |
| Toronto stations and years vs card | card Coverage | pass | 0 |
| time convention: lag-0 best vs co-located | ADR 0005 | 14 co-located pairs, best r at lag 0 in all: True | 0 |

## Issues and handling

- 3,489,048 raw rows in the read scope (City bounds ± 0.5°).
- Sentinels, negatives and repeats stay in the interim table (lossless) and are removed or averaged in `processed/stations/hourly_pm25` (ADR 0007).
- Scope: the Phase 1 read box only (City bounds +/- the registry margin); stations elsewhere in the card's coverage are not checked yet, so the result is at most partial.
