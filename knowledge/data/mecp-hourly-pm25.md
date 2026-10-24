---
source: data/raw/Canada Government Monitors/ON Provincial - Hourly PM2.5 - 2000-2025 (whole year)
aliases: []
sha256: null                      # folder card: per-file hashes in manifests/inventory.csv
converted: 2026-10-24
converter: manual
status: current
kind: data-card
dataset: mecp-hourly-pm25
provider: Ontario Ministry of the Environment, Conservation and Parks (MECP), via Air Quality Ontario (airqualityontario.com)
variables: [pm25_ugm3]
units: {pm25_ugm3: µg/m³}
time_coverage: 2003-01-01T05:00:00Z/2026-01-01T05:00:00Z   # dates 2003-01-01..2025-12-31 EST; 2000-2002 files are empty
time_convention: EST (UTC-5) all year, no DST (file header); hour-ending H01-H24 by observed match with NAPS (not stated by the provider)
spatial_coverage: Ontario, 58 station codes (57 with data); 6 Toronto codes
rows: 324867                      # station-day rows: 324,860 complete + 7 truncated
validation: unvalidated
validation_report: null
---

# mecp-hourly-pm25

## What it is
Air Quality Ontario historical hourly PM2.5, one CSV per calendar year 2000–2025, every Ontario
station in each file. One row is one station-day with 24 hourly values.

## Files

| File(s) | What | Use |
|---|---|---|
| `Individual yearly spreadsheets/f44f4i8mr66g718tcn1icqnvah2_124_YYYY-01-01_YYYY-12-31.csv` (26) | Provider downloads, 2000–2025 | The dataset |
| `ON_Hourly_PM2.5_2000-2025_Combined.xlsx` | Derived merge (sheets: Combined Data 324,860 rows, Stations, Missing by Year, Missing by Station, No-Data Station-Years) | Not provider data; do not read |
| `Ontario_PM2.5_Summary_Report.docx` | Derived summary; mirror: [ontario-pm2-5-summary-report](../docs/data-raw-canada-government-monitors-on-provincial-hourly-pm2-5-2000-2025-whole-year-ontario-pm2-5-summary-report.md) | Context only |
| `Individual yearly spreadsheets/.claude/settings.local.json` | Stray tool settings | Not data |

**`_124_` is the pollutant, not a station.** `124` is Air Quality Ontario's pollutant ID for
PM2.5 (`s_pollutantId=124` on airqualityontario.com/history, checked 2026-10-24). Each yearly
file holds every station: 36–44 station blocks per year. The prefix `f44f4i8mr66g718tcn1icqnvah2`
is the same in all 26 names; its meaning is `unknown` (looks like a request token).

## Columns / variables
Each file: `From,January 1, YYYY EST` / `To,December 31, YYYY EST`, then one block per station,
then a footer (`Air Quality Ontario. Maintained by the Government of Ontario`, `Copyright King's
Printer for Ontario 2026`). Block = title line, key-value lines, header, rows. A station with no
data that year has `No data available` instead of rows (40 station-years).

| Original name | Canonical name | Type | Unit | Meaning / notes |
|---|---|---|---|---|
| block line `Station` | `station_name` `<verify>` | str | — | e.g. `Toronto East (33003)` |
| block lines `Address`, `Elevation`, `Air intake height` | — | str | — | Elevation and intake height carry the unit in the text (`226 metres`) |
| block line `Latitude` | `lat_deg` | float | ° | Decimal degrees; datum not stated (`unknown`). One value per station code |
| block line `Longitude` | `lon_deg` | float | ° | As above |
| block lines `Unit`, `Remarks` | — | str | — | `micrograms per cubic metre (&micro;g/m<sup>3</sup>)`; `9999 for invalid or missing data.` |
| `Station ID` | `station_id` = `mecp:<id>` | str | — | 5 digits, e.g. `33003` |
| `Pollutant` | — | str | — | `Fine Particulate Matter` |
| `Date` | — | str | — | `YYYY-MM-DD`, EST day |
| `H01` … `H24` | `pm25_ugm3` | int | µg/m³ | Hourly values; rows end with a trailing comma (28 fields) |

## Coverage
- 2000, 2001, 2002 files: 156 bytes, From/To lines and footer only, no stations. Data start
  2003-01-01; last date 2025-12-31.
- Stations with data per year: 33 (2003), 38 (2004–06), 40 (2007–16), 39–41 (2017–22), 38–39 (2023–25).
- 58 station codes; 71068 (Sault Ste. Marie) never has data.
- Toronto codes (station name contains "Toronto"; years with data):

| Station ID | Name | Address | Lat, lon | Years |
|---|---|---|---|---|
| 31103 | Toronto Downtown | Bay St./Wellesley St. W. | 43.662972, −79.388111 | 2003–2019 |
| 31129 | Toronto Downtown | 55 John St. | 43.645451, −79.3891 | 2019–2025 (2003–2018 blocks say "No data available") |
| 33003 | Toronto East | Kennedy Rd./Lawrence Ave. E. | 43.747917, −79.274056 | 2003–2025 |
| 34020 | Toronto North | Hendon Ave./Yonge St. | 43.781611, −79.417722 | 2003–2016 |
| 34021 | Toronto North | 4905 Dufferin St., Eccc | 43.78047, −79.467372 | 2017–2025 |
| 35125 | Toronto West | 125 Resources Rd. | 43.709444, −79.5435 | 2003–2025 |

## Time convention
- Zone: EST (UTC−5) all year, no DST. Evidence: the `From`/`To` lines of every file say `EST`.
- Label: hour-ending, **by observation only**. Air Quality Ontario's history and data-disclaimer
  pages do not state the hour label (checked 2026-10-24). Check (2026-10-24, 2014–2021): MECP
  35125 equals NAPS 060430 (same coordinates; NAPS documented hour-ending LST) at lag 0 in 99.9 %
  of 69,292 hours, and 33003 equals NAPS 060410 in 91.8 % (lag ±1 h: ≤ 48 %). Summer (May–Sep)
  matches the same, so there is no DST shift. AirNow 000060424 (UTC hour-beginning) matches MECP
  31103 at lag 0 in 99.8 % of 42,953 hours after the HE-EST → UTC conversion.
- Treat as hour-ending EST; confirm with MECP in the spec step (open question).

## Known issues
- Missing codes: `9999` (documented in each block's Remarks; 125,093 cells) and `-999` (not
  documented in the file; 28,690 cells). One blank hour cell.
- 7 truncated rows with fewer than 24 hour fields, each the last row of a block: 46110
  2004-05-10, 52020 2006-10-23, 52022 2009-12-24, 56010 2015-06-22, 14110 2016-04-20, 51010
  2022-02-28, 63203 2024-09-24.
- Duplicate station-dates: 1,102 extra rows on (Station ID, Date), 2003–2025 (217 in 2019). The
  derived summary says each pair splits the 24 hours between two rows `<verify>`.
- 3 cells of −3. Max 668 µg/m³ (75010 North Bay, 2023-06-25).
- Unit text contains HTML entities.
- Whether the historical download is final-verified data is `unknown`; the AQO data disclaimer
  covers the site's real-time pages.

## Validation
`unvalidated` — no report yet (needs `methodology/stations.md`). 2026-10-24.
