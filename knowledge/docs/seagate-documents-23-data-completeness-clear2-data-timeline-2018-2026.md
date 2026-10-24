---
source: archive/seagate/Documents/23. Data Completeness/CLEAR2_Data_Timeline_2018-2026.docx
aliases: [archive/seagate/Documents/23. Data Completeness/CLEAR2_Data_Timeline_2018-2026.pdf]
sha256: 3d821cc58547ae948146f1007e0d2b1f18f09169cd8258d2c40fe97e9e083067
converted: 2026-10-24
converter: markitdown
status: current
kind: mirror
---

**CLEAR 2.0 Data Timeline, 2018–2026**

**Which data we hold for each fire season, and which years are missing**

*Hugo Bui & Ryan Zander · University of Toronto Schools · October 2026*

|  |
| --- |
| **Answer in brief**   * **No missing years in the training period (2021–2024).** Every main dataset is held for all four training seasons. The only exception is CAMS, which is still downloading. Alberta’s provincial network (Air Data Warehouse, 129 stations) and Montréal’s city network (RSQA) are now held for 2018–2025. * **2025 (validation)** is complete except NAPS 2025, which ECCC releases after validation (about March 2027); the same instruments are already in the validated Ontario and Québec provincial data and in AirNow. * **2026 (test)** is the season with gaps: validated NAPS, Ontario and Québec data are not released yet; US EPA data is partly submitted; FireWork 2026 is requested from ECCC; CWFIS 2026 is not posted; PurpleAir 2026 covers only Ontario, Québec and the Prairies. AirNow covers every hour and province for 2026 and agrees with validated data at r = 0.99–1.00. * **2018–2020** (optional pre-training only): PurpleAir was not bought and several products (HRRR-Smoke, RAP-Smoke, BlueSky, ERA5-Land, humidity, CAMS) were not downloaded; ERA5 wind and FIRMS cover only a Great Lakes box. These years are not needed for training. |

# **1. The timeline**

![Data timeline](data:image/png;base64...)

*Figure 1. Share of each fire season (1 May – 30 September) held, by dataset and year. Hatched = preliminary (not yet validated); pink = not yet released, with the expected date; grey = not held, with the reason.*

**How it is measured:** for ground monitors, the share of the season’s hours reported by the monitors that exist that year (a typical, complete network is 90–98%; PurpleAir sensors have about 70–80% uptime); for gridded products, the share of fire-season days with a file (BlueSky: the four daily runs; ERA5 and satellite: months). Everything was checked on disk on 21 October 2026 (scripts/data\_timeline\_2018\_2026.py).

# **2. Missing years and what fills them**

| **Dataset** | **Missing** | **Why** | **What we use instead / when** |
| --- | --- | --- | --- |
| **NAPS (ECCC)** | 2025, 2026 | Validated data released about 15 months after the year | Ontario/Québec provincial (same instruments) and AirNow; NAPS 2025 about March 2027, 2026 about 2028 |
| **Ontario provincial** | 2026 | Not released yet | AirNow (all Ontario stations); expected about mid-2027 |
| **Québec provincial (RSQAQ)** | 2026 | Not released yet | AirNow; expected about June 2027 |
| **US EPA AQS** | Part of 2026 | States submit July–September by 31 December 2026 | AirNow for the unsubmitted months; re-download in January 2027 |
| **PurpleAir** | 2018–2020; US in 2026 | Must be bought; few sensors before 2021 | Not needed before 2021; PurpleAir request for 2026 US |
| **FireWork (ECCC)** | 2026 | Not in the archive we bought | Requested from ECCC |
| **CWFIS (NRCan)** | 2026 | Posted after the season | FIRMS (same satellites); CWFIS expected early 2027 |
| **CAMS (ECMWF)** | 2022–2026 (part) | Download in progress (tape archive, 13-day requests) | Finishing in about 1–1½ weeks |
| **BlueSky Canada** | 10% of 2026 runs | Not in UBC’s archive | The previous run covers the gap (51-hour forecasts) |
| **HRRR-Smoke, RAP-Smoke, BlueSky, ERA5-Land, humidity** | 2018–2020 | Not downloaded (not needed) | Pre-training would mask these inputs |

*Table 1. Missing years and how each gap is handled.*

# **3. Ground monitors each year**

![Monitors per year](data:image/png;base64...)

*Figure 2. Number of monitors reporting in each fire season in the main networks.*

| **Network** | **2018** | **2019** | **2020** | **2021** | **2022** | **2023** | **2024** | **2025** | **2026** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **NAPS (ECCC)** | 228 | 229 | 230 | 229 | 229 | 231 | 192 | 0 | 0 |
| **Ontario provincial** | 38 | 39 | 39 | 39 | 38 | 38 | 39 | 38 | 0 |
| **Québec provincial (RSQAQ)** | 35 | 36 | 37 | 39 | 38 | 39 | 40 | 40 | 0 |
| **Montréal (RSQA, island of Montréal)** | 10 | 10 | 11 | 11 | 11 | 11 | 11 | 11 | 0 |
| **Northwest Territories (GNWT)** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 4 |
| **British Columbia provincial** | 63 | 66 | 63 | 64 | 67 | 69 | 67 | 69 | 68 |
| **Alberta provincial** | 50 | 54 | 64 | 62 | 66 | 71 | 76 | 76 | 70 |
| **Saskatchewan provincial** | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |
| **New Brunswick provincial** | 10 | 10 | 8 | 10 | 10 | 10 | 10 | 10 | 10 |
| **US EPA AQS 88101 (reference)** | 581 | 631 | 650 | 722 | 763 | 838 | 903 | 929 | 905 |
| **US EPA AQS 88502 (continuous)** | 349 | 322 | 304 | 284 | 264 | 231 | 210 | 196 | 185 |
| **AirNow (US EPA; provinces and states)** | 1,036 | 1,054 | 1,194 | 1,188 | 1,218 | 1,303 | 1,375 | 1,364 | 1,420 |
| **PurpleAir (EPA-corrected)** | 0 | 0 | 0 | 404 | 623 | 1,083 | 1,438 | 1,983 | 864 |

*Table 2. Monitors reporting in each fire season (0 = not held). US EPA 2026: monitors that have submitted at least part of the season. PurpleAir 2026: Ontario, Québec and the Prairies only.*

Sources: Cleaned Data/analysis/data\_timeline/timeline.csv and ground\_by\_year.csv. Prepared with the Claude AI assistant, directed and checked by the team.
