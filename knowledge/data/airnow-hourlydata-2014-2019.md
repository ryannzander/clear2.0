---
source: data/raw/AirNow/HourlyData 2014-2019
aliases: []
sha256: null                      # folder card: per-file hashes in manifests/inventory.csv
converted: 2026-10-24
converter: manual
status: current
kind: data-card
dataset: airnow-hourlydata-2014-2019
provider: US EPA AirNow program (data owned by the reporting agencies)
variables: [pm25_ugm3]
units: {pm25_ugm3: µg/m³}
time_coverage: 2014-01-01T00:00:00Z/2019-05-29T00:00:00Z   # last hour starts 2019-05-28T23:00Z
time_convention: UTC, hour-beginning (ValidTime 17:00 = 17:00-17:59 UTC); no DST
spatial_coverage: worldwide AirNow sites, 1,436 AQSIDs (144 Canadian-prefixed, 30 Ontario); 1 Toronto site
rows: 40419465                    # site-hour PM2.5 rows; plus 37 site-location snapshots (365,719 lines)
validation: partial
validation_report: knowledge/data/airnow-hourlydata-2014-2019.validation.md
---

# airnow-hourlydata-2014-2019

## What it is
AirNow `HourlyData` files (one per UTC hour, all parameters) reduced to PM2.5 rows and stored as
one parquet per month, plus monthly snapshots of AirNow's `monitoring_site_locations.dat`. The
hourly table has no coordinates; Phase 1 reads this folder mainly for site locations.

## Origin
- Made by the legacy script `scripts/download_airnow_hourlydata.py` (now
  `inbox/seagate/legacy-code/scripts/`, to be filed under `archive/legacy-code/`) from
  `https://files.airnowtech.org/airnow/YYYY/YYYYMMDD/HourlyData_YYYYMMDDHH.dat` and
  `.../monitoring_site_locations.dat`. Download dates: `unknown`.
- Kept: rows whose parameter is PM2.5, all countries, all columns as strings. The script read with
  `on_bad_lines="skip"`, so malformed source lines were dropped silently (count `unknown`).
- Files: `airnow_hourlydata_pm25_2014_01.parquet` … `_2019_05.parquet` (65; 2019-05 ends
  2019-05-28 23:00 UTC, where HourlyAQObs takes over); `missing_files.log` (empty: no hour
  missing); `site_locations/monitoring_site_locations_YYYYMMDD.dat` (37: 2016-06-21, then the
  1st of each month 2016-07 … 2019-06).

## Columns / variables
Hourly parquet (all `string` dtype):

| Original name | Canonical name | Type | Unit | Meaning / notes |
|---|---|---|---|---|
| `ValidDate` | part of `time_utc` | str | — | `mm/dd/yy`, UTC date |
| `ValidTime` | part of `time_utc` | str | — | `HH:MM`, UTC, start of hour |
| `AQSID` | `station_id` = `airnow:<AQSID>` | str | — | 9 digits; Canada `000` + NAPS-style ID |
| `SiteName` | `station_name` `<verify>` | str | — | |
| `GMTOffset` | — | str | h | Hours to local standard time; −10 to +8 present |
| `Parameter` | — | str | — | Always `PM2.5` |
| `Units` | — | str | — | Always `UG/M3` |
| `Value` | `pm25_ugm3` | str → float | µg/m³ | All values parse as numbers |
| `DataSource` | — | str | — | Reporting agency |

Site-location snapshots: pipe-delimited, no header, one line per site × parameter, 23 fields.
Fields used: 1 `AQSID`, 2 parameter, 4 site name, 5 status, 7 agency name, 9 latitude (°),
10 longitude (°), 11 elevation (m), 12 GMT offset (h), 13 country code. Fields 14–15 and 22–23
are not in the fact sheet's 19-field list (blank in the rows checked) `<verify>`.

## Coverage
- 2014-01-01 00:00 UTC to 2019-05-28 23:00 UTC; 65 months, no missing hourly file.
- 1,436 AQSIDs; 144 start with `000` (Canada); 30 Ontario (`00006…`), mostly Ontario Ministry of
  the Environment, plus 4 CAPMoN sites in 2014-07..11.
- Toronto: only AQSID `000060424` "Toronto Downtown", 46,603 rows (2014-01 … 2019-05). In all 37
  location snapshots it is `Active` at 43.661900, −79.385300 (Bay/Wellesley).
- Site snapshots cover only sites active from 2016-06; sites that closed earlier cannot be located
  from this folder.

## Time convention
- UTC, hour-beginning. HourlyData fact sheet (AirNow, last updated 2025-08): time "is reported in
  GMT and corresponds to the beginning of the measurement period"; a value with time 17:00 is
  measured 17:00–17:59 GMT. GMT offset converts to local standard time.
- Observed check (2026-10-24, 2014–2018): `000060424` equals MECP 31103 (hour-ending EST,
  converted to UTC hour-beginning) at lag 0 in 99.8 % of 42,953 hours (lag ±1 h: 37 %), and NAPS
  060433 in 87.0 % (r = 0.987).

## Known issues
- No missing code; only valid values are reported, so a missing hour is an absent row.
- 1,010,154 negative values (fact sheet: negative raw values kept, typically > −5). Max 3,854.
- AQSID `000060424` embeds NAPS ID 060424, but its values are MECP 31103 = NAPS 060433. Cross-network
  IDs do not map 1:1.
- `monitoring_site_locations_20161101.dat` line 6438 is corrupt (AQSID `080830101`, `RHUM`, then
  NUL bytes). Not a PM2.5 line.
- Preliminary data, same terms as [airnow-hourlyaqobs](airnow-hourlyaqobs.md).

## Validation
`partial` — [airnow-hourlydata-2014-2019.validation.md](airnow-hourlydata-2014-2019.validation.md), 2026-10-24.
Evidence read: AirNow HourlyData fact sheet (docs.airnowapi.org/docs/HourlyDataFactSheet.pdf),
Monitoring Site Locations fact sheet (docs.airnowapi.org/docs/MonitoringSiteFactSheet.pdf).
