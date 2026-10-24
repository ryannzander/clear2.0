---
source: data/prior/stations
aliases: []
sha256: null                      # folder card: per-file hashes in manifests/inventory.csv
converted: 2026-10-24
converter: manual
status: current
kind: data-card
dataset: prior-stations
provider: CLEAR legacy pipeline (derived; not a provider dataset)
variables: [lat_deg, lon_deg]
units: {lat_deg: °, lon_deg: °}
time_coverage: null               # station metadata; registry first_ts/last_ts span 2008-01-01..2026-10-20 (naive)
time_convention: first_ts/last_ts are naive; NAPS/provincial tables label by hour END (UTC), AirNow/EPA by hour START (UTC) — mixed
spatial_coverage: Canada + US station lists; 26 tables
rows: 12044                       # sum over the 26 tables
validation: unvalidated
validation_report: null
---

# prior-stations

## What it is
Station lists and registries written by the old CLEAR cleaning scripts (`Cleaned Data/stations/`
on the Seagate). Reference and golden numbers only, never a pipeline input
([data.md](../../docs/standards/data.md#prior-outputs-dataprior)). One row is one station.

## Files and the scripts that made them
Legacy code is in `inbox/seagate/legacy-code/scripts/` (to be filed under `archive/legacy-code/scripts/`).

| Table (rows) | Columns | Made by |
|---|---|---|
| `naps_on_stations` (70), `naps_qc_stations` (61) | `station_id_raw` (int64), `station_name`, `lat`, `lon` | `clean_pipeline.py` (`load_naps`, from the derived NAPS ON/QC xlsx) |
| `on_provincial_stations` (58) | `station_name`, `station_id_raw` (int64), `Address`, `lat`, `lon`, `Elevation`, `Air intake height`, `Pollutant`, `Unit`, `First/Last Year w/ Data`, `Years w/ Data (count)`, `No-Data Years` | `clean_pipeline.py` (`load_on_provincial`, from the derived MECP xlsx "Stations" sheet) |
| `qc_provincial_stations` (245) | `station_id_raw`, `station_name`, `lat`, `lon` | `clean_pipeline.py` |
| `epa_{mi,ny,oh,pa,vt}_stations` (31, 19, 44, 57, 4) | `station_id_raw`, `lat`, `lon`, `station_name` (all null) | `clean_pipeline.py` |
| `purpleair_2021..2026_stations` (425, 669, 1144, 1606, 2073, 864) | `station_id_raw`, `station_name`, `lat`, `lon` | `clean_pipeline.py` |
| `naps_all_registry` (262) | `station_id` (`NAPS_<prov>_<6-digit id>`), `source`, `station_name`, `lat`, `lon`, `n_valid`, `first_ts`, `last_ts` | `clean_naps_all.py` (docstring) |
| `airnow_registry` (2,032) | `AQSID`, `station_name`, `lat`, `lon`, `region`, `country`, `station_id`, `kind` (2,018 permanent, 14 incident), `source`, `n_valid`, `first_ts`, `last_ts`, `data_source` | `clean_airnow.py`; `kind` corrected by `fix_airnow_registry_kind.py` (both docstrings) |
| `ab_dmp_registry` (129), `ab_provincial_registry` (66), `bc_provincial_registry` (88), `epa_all_states_registry` (1,206), `epa88502_all_states_registry` (858), `montreal_rsqa_registry` (12), `nb_provincial_registry` (10), `nt_territorial_registry` (5), `sk_provincial_registry` (6) | various: id, name, `lat`, `lon`, `n_valid`, `first_ts`, `last_ts`, distance-to-NAPS/AirNow flags | `<verify>` — likely the matching `clean_*.py` (not opened) |

Plus 26 macOS `._*` files (junk).

## Coverage
Rows relevant to Phase 1 (Toronto box, lat 43.55–43.90, lon −79.70 to −79.05):
- `naps_on_stations`: 15 IDs (13 "Toronto", 2 "Mississauga").
- `on_provincial_stations`: 8 (6 Toronto codes as in [mecp-hourly-pm25](mecp-hourly-pm25.md), 2 Mississauga).
- `airnow_registry`: 5 (as in [airnow-hourlyaqobs](airnow-hourlyaqobs.md); 000060424 first_ts 2014-01-01).
- `naps_all_registry`: 8 Toronto IDs, but this registry covers 2018-01 to 2024-12 only.

## Time convention
- `first_ts`, `last_ts`: naive timestamps meant as UTC.
- NAPS and Ontario tables come from `timestamp_local = date + H` plus 5 h, so they label the END
  of the hour (`clean_pipeline.py`, `clean_naps_all.py`). AirNow and EPA registries label the
  START of the hour (`clean_airnow.py` docstring says so and notes the mismatch).
- Do not compare `first_ts`/`last_ts` across tables without shifting one side by 1 h.

## Known issues
- Reference only: no pipeline input until a validate step and an ADR approve reuse.
- `naps_on_stations.station_id_raw` and `on_provincial_stations.station_id_raw` are int64: NAPS
  leading zeros are lost (`60410`, not `060410`).
- Built from derived xlsx, not from the provider CSVs (NAPS ON/QC, MECP).
- `epa_*_stations.station_name` is all null.

## Validation
`unvalidated` — no report yet. 2026-10-24.
