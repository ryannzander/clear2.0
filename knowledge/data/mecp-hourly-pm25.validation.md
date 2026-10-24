---
dataset: mecp-hourly-pm25
date: 2026-10-24
spec: methodology/stations.md#validation-criteria
result: partial
---

# mecp-hourly-pm25 — validation

Checks run by `notebooks/validate_phase1.py` on the Phase 1 build (`uv run clear stations build`).

| Check | Spec source | Result | n failing |
|---|---|---|---|
| interim schema (UTC, on the hour, ids) | stations.md#read-sources | pass | 0 |
| non-numeric cells | ADR 0007 / code.md | pass (reader raises) | 0 |
| sentinel cells found → missing | ADR 0007 | handled in QC | 42478 |
| other negative cells → missing | ADR 0007 | handled in QC | 1 |
| repeat station-hours → averaged | ADR 0007 | handled in QC | 10848 |
| processed hourly ≥ 0, unique station-hour | stations.md#validation-criteria | pass | 0 |
| Toronto stations and years vs card | card Coverage | pass | 0 |
| time convention: lag-0 best vs co-located | ADR 0005 | 12 co-located pairs, best r at lag 0 in all: True | 0 |

## Issues and handling

- 2,884,137 raw rows in the read scope (City bounds ± 0.5°).
- Sentinels, negatives and repeats stay in the interim table (lossless) and are removed or averaged in `processed/stations/hourly_pm25` (ADR 0007).
- Hour-ending label confirmed by observation only (provider undocumented); lag check above.
- Scope: the Phase 1 read box only (City bounds +/- the registry margin); stations elsewhere in the card's coverage are not checked yet, so the result is at most partial.
