---
source: data/raw/AirNow/HourlyAQObs 2019-2026
aliases: []
sha256: null                      # folder card: per-file hashes in manifests/inventory.csv
converted: 2026-10-24
converter: manual
status: current
kind: data-card
dataset: airnow-hourlyaqobs
provider: US EPA AirNow program (data owned by the reporting agencies; Ontario sites from the Ontario Ministry of the Environment)
variables: [pm25_ugm3]
units: {pm25_ugm3: µg/m³}
time_coverage: 2019-05-29T00:00:00Z/2026-10-09T00:00:00Z   # last hour starts 2026-10-08T23:00Z
time_convention: UTC, hour-beginning (ValidTime 10:00 = 10:00-10:59 UTC); no DST; GMTOffset = hours to local standard time
spatial_coverage: US + Canada; 1,841 AQSIDs (282 Canadian); 4 Toronto sites in 2026
rows: 74493289                    # site-hours with a PM2.5 value
validation: unvalidated
validation_report: null
---

# airnow-hourlyaqobs

## What it is
AirNow `HourlyAQObs` files (one per UTC hour, all AirNow sites), reduced to PM2.5 columns and
stored as one parquet per month. Near-real-time, preliminary data. One row is one site-hour.
For 2026 it is the only government PM2.5 source in `data/raw` (NAPS ends 2024, MECP 2025).

## Origin
- Made by the legacy script `scripts/download_airnow.py` (now `inbox/seagate/legacy-code/scripts/`,
  to be filed under `archive/legacy-code/`) from
  `https://files.airnowtech.org/airnow/YYYY/YYYYMMDD/HourlyAQObs_YYYYMMDDHH.dat`.
- Kept: 16 of the source columns; rows with `PM25` not null and `CountryCode` in `US`, `CA`.
  Hours with no file go to `missing_files.log`. Download dates: `unknown`.
- Files: `airnow_pm25_2019_05.parquet` … `airnow_pm25_2026_09.parquet` (89),
  `airnow_pm25_2026_10_partial.parquet` (to 2026-10-08 23:00 UTC), `missing_files.log`
  (one line: `2025-04-01 22:00 missing`).

## Columns / variables
| Original name | Canonical name | Type | Unit | Meaning / notes |
|---|---|---|---|---|
| `AQSID` | `station_id` = `airnow:<AQSID>` | str | — | 9 or 12 digits. Canada: `000` + NAPS-style ID, or `124000` + ID (12-digit, country code 124) |
| `SiteName` | `station_name` `<verify>` | str | — | Can change over time for one AQSID |
| `Status` | — | str | — | `Active` / `Inactive` (94,005 rows Inactive) |
| `Latitude`, `Longitude` | `lat_deg`, `lon_deg` | float | ° | Per row; can change over time for one AQSID |
| `Elevation` | — | float | m | |
| `GMTOffset` | — | float | h | Hours to local standard time; DST not considered (fact sheet) |
| `CountryCode`, `StateName` | — | str | — | Canada: `CA`, `CC` |
| `ValidDate` | part of `time_utc` | str | — | `mm/dd/yy` to 2021-10, `mm/dd/yyyy` after; both occur in the 2020-09 and 2021-10 files |
| `ValidTime` | part of `time_utc` | str | — | `HH:MM`, UTC, start of hour; all on the hour |
| `DataSource` | — | str | — | Reporting agency |
| `PM25_AQI` | — | float | — | US NowCast AQI, not a concentration |
| `PM25_Measured` | — | int | — | 1 if the site measures PM2.5; 0 on 909 rows that still carry `PM25` |
| `PM25` | `pm25_ugm3` | float | µg/m³ | Hourly raw concentration |
| `PM25_Unit` | — | str | — | Always `UG/M3` |

## Coverage
- 2019-05-29 00:00 UTC to 2026-10-08 23:00 UTC. Every month complete except 2025-04 (719 of 720
  hours). AirNow's HourlyAQObs archive starts 2019-05-28 (fact sheet).
- Sites per month: ~1,000 (2019) to ~1,400 (2026). No duplicate (AQSID, ValidDate, ValidTime).
- Toronto (PM2.5 sites in a box around the City; inside-boundary test is Phase 1 build):

| AQSID | SiteName | Lat, lon | First–last hour (UTC) | Rows |
|---|---|---|---|---|
| 000060424 | Toronto Downtown | 43.6619, −79.3853 | 2019-05 – 2021-01 | 13,323 |
| 124000060445 | Toronto Downtown | 43.64545, −79.3891 | 2020-04 – 2026-10 | 55,312 |
| 000060410 | Toronto East / LAWRENCE & KENNEDY | 43.74792, −79.27406 (also 43.7453, −79.2703) | 2023-07 – 2026-10 | 28,081 |
| 124000060430 | Toronto West | 43.70944, −79.5435 | 2023-07 – 2026-10 | 27,962 |
| 124000060440 | Toronto North | 43.78047, −79.46737 | 2023-07 – 2026-10 | 27,836 |

- Before 2023-07 AirNow carries only the downtown Toronto site.
- Ontario: 39 AQSIDs (28 `000…`, 11 `124000…`) with `DataSource` "Ontario Ministry of the
  Environment"; most `124000…` IDs start in 2023-07.

## Time convention
- UTC, hour-beginning. Fact sheet (AirNow HourlyAQObs, updated 2023-03, last updated 2025-08):
  time "is reported in GMT and corresponds to the beginning of the measurement period"; a value
  stamped 10:00 is measured 10:00–10:59 UTC. Same statement for the file-name hour.
- Observed check (2026-10-24): AQSID 124000060445 equals NAPS 060445 (hour-ending LST, converted
  to UTC hour-beginning) at lag 0 in 99.6 % of 40,016 hours, 2020–2024; 000060410 vs MECP 33003
  best at lag 0 (77 % equal, r = 0.996; lag ±1 h ≤ 41 %).

## Known issues
- No missing code: AirNow reports only valid values, and the fetch kept only rows with `PM25`.
  A missing hour is an absent row.
- Negatives: fact sheet says valid raw values can be negative, "typically greater than −5".
  Observed: 1,442,108 rows in (−5, 0]; 12,328 in (−10, −5]; 279 in (−100, −10]; 8 at −189.8 to
  −252.3 (AQSID 400430860 Seiling, 2026-10-02/03); −4996 and −9999 (410350004 Klamath Falls,
  2020-06-03 15:00 and 16:00 UTC). Max 2,629.9.
- AQSID 000060424 "Toronto Downtown" embeds NAPS ID 060424, but its values match MECP 31103
  (Bay/Wellesley, NAPS 060433), not NAPS 060424 (ended 2002). IDs across networks do not map 1:1.
- Preliminary data: "not fully verified or validated … subject to change" (fact sheet, AirNow
  Data Exchange Guidelines). The guidelines ask that products using it say the data are
  preliminary and credit the agencies.

## Validation
`unvalidated` — no report yet (needs `methodology/stations.md`). 2026-10-24.
Evidence read: AirNow HourlyAQObs fact sheet (docs.airnowapi.org/docs/HourlyAQObsFactSheet.pdf),
Data Exchange Guidelines (docs.airnowapi.org/docs/DataUseGuidelines.pdf),
[airnow-summary mirror](../docs/seagate-documents-35-airnow-clear2-airnow-summary.md).
