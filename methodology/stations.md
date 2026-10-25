---
part: stations
status: accepted
owner: methodologist
sources:
  - knowledge/data/naps-hourly-pm25.md
  - knowledge/data/mecp-hourly-pm25.md
  - knowledge/data/airnow-hourlyaqobs.md
  - knowledge/data/airnow-hourlydata-2014-2019.md
  - knowledge/data/toronto-city-boundary.md
  - knowledge/docs/seagate-documents-04-toronto-stations-toronto-pm25-station-statistical-analysis.md
  - knowledge/docs/seagate-documents-23-data-completeness-clear2-data-completeness-continental.md
decisions:
  - decisions/0001-data-split.md
  - decisions/0002-toronto-city-boundary.md
  - decisions/0003-station-overlap-ab.md
  - decisions/0004-completeness-75pct.md
  - decisions/0005-time-utc-hour-beginning.md
  - decisions/0007-station-value-qc.md
  - decisions/0008-site-crosswalk-500m.md
  - decisions/0009-golden-station-years.md
  - decisions/0010-airnow-offset.md
  - decisions/0011-naps-060438-west-site.md
updated: 2026-10-24
---

# Stations — Toronto government PM2.5 monitors

## Purpose

Find every government PM2.5 monitor in the City of Toronto (NAPS, Ontario MECP, AirNow), give
each one hourly UTC series, link the same physical site across networks, and measure years
active and missing data (issue #1). The grid part places these stations in cells; the target
series part later builds on the hourly table.

## Inputs

| Name | Source dataset / data card | Units | Time convention |
|---|---|---|---|
| NAPS hourly PM2.5 | `knowledge/data/naps-hourly-pm25.md` | µg/m³ | local standard time UTC−5, hour-ending |
| MECP hourly PM2.5 | `knowledge/data/mecp-hourly-pm25.md` | µg/m³ | EST UTC−5, hour-ending (observed) |
| AirNow HourlyAQObs + HourlyData | `knowledge/data/airnow-hourlyaqobs.md`, `knowledge/data/airnow-hourlydata-2014-2019.md` | µg/m³ | UTC, hour-beginning |
| City boundary | `knowledge/data/toronto-city-boundary.md` | ° (WGS 84) | none |

## Outputs

| Name | Schema | Units |
|---|---|---|
| `data/interim/<dataset>/pm25_hourly_raw.parquet` (one per data card: `naps-hourly-pm25`, `mecp-hourly-pm25`, `airnow-hourlyaqobs`, `airnow-hourlydata-2014-2019`) | `clear.schemas.stations.INTERIM_RAW` | µg/m³ as published |
| `data/processed/stations/hourly_pm25.parquet` | `clear.schemas.stations.HOURLY` | µg/m³ |
| `data/processed/stations/registry.parquet` | `clear.schemas.stations.REGISTRY` | ° |
| `data/processed/stations/completeness.parquet` | `clear.schemas.stations.COMPLETENESS` | fraction, h |
| `data/processed/stations/series_merged.parquet` | `clear.schemas.stations.MERGED` | µg/m³ |

## Method

### Read sources

Read each dataset into a lossless long table (interim): `station_id`, `source`, `dataset`,
`time_utc`, `pm25_raw_ugm3` (the value as published: sentinels, negatives and repeats kept),
`method_code` (NAPS). Empty cells carry no value and give no row; any other non-numeric cell
stops the build.
`station_id` = `<source>:<provider id>` with leading zeros kept (`naps:060410`, `mecp:33003`,
`airnow:000060410`). Wide H01–H24 rows become one row per hour. NAPS and MECP are hour-ending
local standard time (UTC−5): `time_utc` = date + H hours, localized to UTC−5, minus 1 h
(hour-beginning, ADR 0005). AirNow `ValidDate` + `ValidTime` are UTC hour-beginning already.
Read scope: stations inside the registry box (City bounds ± `registry_margin_deg`); this
is a spatial scope of the read, values inside it are untouched. A configured dataset
folder with no files stops the build.

### Clean values

Apply ADR 0007 to the interim rows (processed `hourly_pm25`): each source's sentinel codes
and every negative value become missing; missing hours are dropped (absent row = missing
hour). Several values for one station-hour (MECP duplicate rows, NAPS method codes) are
averaged. AirNow rows with `PM25_Measured = 0` are kept as published (open question 2).

### Build the registry

One row per station: `station_id`, `source`, `station_name`, `lat_deg`, `lon_deg`, first and
last `time_utc` with data, `present_h`. Coordinates: NAPS and MECP publish one pair per ID;
AirNow uses the latest pair seen (HourlyAQObs, else the HourlyData site-location snapshots).

### Select Toronto stations

`is_in_toronto` = the station's point lies in or on the City boundary polygon (ADR 0002).

### Link sites

Stations within `crosswalk_max_distance_m` of each other (great-circle, single linkage) form
one site (ADR 0008). `site_id` = the `station_id` of the member from the highest-priority
source (`source_priority`), then the latest last hour, then the lowest id.

### Completeness

For each station and each site (unit), per calendar year, per month and per split (ADR 0001,
UTC calendar years): `expected_h` = hours in the period up to the end of the data
(`coverage_end_utc`, the last hour any source holds); `present_h`; `present_frac`;
`longest_gap_h` (longest run of missing hours inside the period); `is_complete` =
`present_frac >= completeness_min_frac` (ADR 0004). **Years active** = first to last
year with data in the source's own calendar (`utc_offset_h`: EST for NAPS and MECP, UTC for
AirNow), the calendar of the providers' yearly files, so a file's last evening is not
counted in the next UTC year (ADR 0009).

### Combine sources

`overlap_mode` (ADR 0003) selects the series later parts use. `separate`: one series per
station, as read. `merged`: one series per site; each hour takes the value of the
highest-priority source that has one (same-source stations averaged) and records `source`.
Stations in `merged_exclude_stations` stay in the registry and in `separate` mode but are left
out of `merged` (ADR 0011: NAPS 060438). AirNow values are used as published (ADR 0010).
EXP-003 compares the two per site.

## Constants

| Name | Value | Config key | Justification / ADR |
|---|---|---|---|
| sentinels | NAPS −999; MECP 9999, −999; AirNow −9999, −4996 | `config/stations.yaml: sources.*.sentinels` | cards; ADR 0007 |
| negative values missing | true | `config/stations.yaml: negative_is_missing` | ADR 0007 |
| source priority | naps, mecp, airnow | `config/stations.yaml: source_priority` | ADR 0003 |
| overlap mode | merged | `config/stations.yaml: overlap_mode` | ADR 0003 |
| merged exclusions | naps:060438 | `config/stations.yaml: merged_exclude_stations` | ADR 0011 |
| crosswalk distance | 500 m | `config/stations.yaml: crosswalk_max_distance_m` | ADR 0008 |
| completeness threshold | 0.75 | `config/stations.yaml: completeness_min_frac` | ADR 0004 |
| registry margin | 0.5° | `config/stations.yaml: registry_margin_deg` | context for figures; Toronto itself uses the polygon |
| splits | 2021–24 / 2025 / 2026 | `config/splits.yaml: splits` | ADR 0001 |

## Decisions

- [0001-data-split](../decisions/0001-data-split.md) — train/val/test years
- [0002-toronto-city-boundary](../decisions/0002-toronto-city-boundary.md) — Toronto = City polygon
- [0003-station-overlap-ab](../decisions/0003-station-overlap-ab.md) — merged and separate, A/B
- [0004-completeness-75pct](../decisions/0004-completeness-75pct.md) — % hours + 75% flag
- [0005-time-utc-hour-beginning](../decisions/0005-time-utc-hour-beginning.md) — hour-beginning
- [0007-station-value-qc](../decisions/0007-station-value-qc.md) — what counts as missing
- [0008-site-crosswalk-500m](../decisions/0008-site-crosswalk-500m.md) — sites within 500 m
- [0009-golden-station-years](../decisions/0009-golden-station-years.md) — rebuild years stand over doc 04
- [0010-airnow-offset](../decisions/0010-airnow-offset.md) — AirNow used as published, offset noted
- [0011-naps-060438-west-site](../decisions/0011-naps-060438-west-site.md) — 060438 left out of merged West

## Open questions

1. MECP's hour-ending label is observed, not documented. The build re-checks it (co-located
   MECP vs NAPS agree best at lag 0, EXP-003); a failure needs a new ADR.
2. AirNow `PM25_Measured = 0` rows (909 in the whole archive, airnow card) are not filtered;
   whether any lie in the read scope is unchecked. → ADR?
3. Closed: AirNow's +0.3–0.5 µg/m³ offset at East, West and North is left as published and
   noted ([ADR 0010](../decisions/0010-airnow-offset.md)); revisit with the target series.
4. Closed: NAPS 060438 is left out of the merged West series
   ([ADR 0011](../decisions/0011-naps-060438-west-site.md)).

## Validation criteria

- Every `time_utc` is tz-aware UTC on the hour; (`station_id`, `time_utc`) is unique.
- `pm25_ugm3` ≥ 0 and no sentinel survives.
- Every Toronto station of the cards appears in the registry with its card's first/last year.
- Co-located NAPS/MECP/AirNow series agree at lag 0 better than at ±1 h.

## Golden numbers

| Number | Value (from old doc) | Source mirror path | Test name |
|---|---|---|---|
| First/last year per Toronto station (10 stations) and station count | per station; 10 | `knowledge/docs/seagate-documents-04-toronto-stations-toronto-pm25-station-statistical-analysis.md` (§2) | `tests/golden/test_stations_golden.py::test_reproduces_reported_number`, values in `tests/golden/expected/stations.yaml` (ADR 0009 for the 11 differences) |

## Sources

- `knowledge/data/naps-hourly-pm25.md`, `knowledge/data/mecp-hourly-pm25.md` — formats, codes, time
- `knowledge/data/airnow-hourlyaqobs.md`, `knowledge/data/airnow-hourlydata-2014-2019.md` — AirNow
- `knowledge/data/toronto-city-boundary.md` — the City polygon
- `knowledge/docs/seagate-documents-04-toronto-stations-toronto-pm25-station-statistical-analysis.md` — old station analysis
- `knowledge/docs/seagate-documents-23-data-completeness-clear2-data-completeness-continental.md` — old completeness counts
