---
source: archive/seagate/Documents/23. Data Completeness/CLEAR2_Validation_and_Test_Data_2025-2026.docx
aliases: [archive/seagate/Documents/23. Data Completeness/CLEAR2_Validation_and_Test_Data_2025-2026.pdf]
sha256: 492d64a8e5f9a5c910d7ee33c988ee9add18cf82b28d7a86c20e2fba9cc4f72d
converted: 2026-10-24
converter: markitdown
status: current
kind: mirror
---

**Validation (2025) and Test (2026) Data**

**What we hold, what is still missing, and when it should be published**

*Hugo Bui & Ryan Zander · University of Toronto Schools · October 2026*

|  |
| --- |
| **Answer in brief**   * **2025 (validation): ready.** Validated data is already held for Ontario, Québec (including the island of Montréal), BC, Alberta, Saskatchewan, New Brunswick and the US (EPA AQS). Only NAPS 2025 is missing; ECCC expects to release it in **about March 2027**. AirNow covers every province, including Alberta. * **2026 (test): usable now with AirNow.** AirNow (real-time data from every province and state) covers all 3,672 fire-season hours and all of Toronto’s stations. In 2023–2025 it agreed with validated data at r = 0.99–1.00 (98–100% of hours ≥ 60 µg/m³ the same), and in 2026 with the US data submitted to EPA at r = 0.996. * **When the validated 2026 data should arrive (estimates):** US EPA July–September by **January 2027** (certified by **May 2027**); CWFIS **early 2027**; New Brunswick final by **June 2027**; Québec and Montréal about **June 2027**; Ontario about **mid-2027**; BC verified about **mid-2027**; NAPS 2026 about **March 2028**. FireWork 2026 depends on ECCC’s reply. |

![Status 2025 2026](data:image/png;base64...)

*Figure 1. Status of each source for 2025 and 2026 (left) and expected release dates of the missing data (right).*

# **1. Source by source**

| **Source** | **2025 (validation)** | **2026 (test)** | **Expected release of missing data** | **Basis for the estimate** |
| --- | --- | --- | --- | --- |
| **NAPS (ECCC)** | Not released | Not released | 2025: about March 2027; 2026: about March 2028 | NAPS releases validated data about 15 months after the year |
| **Ontario provincial (MECP)** | Validated (38 monitors) | Not released | About mid-2027 | 2025 was online by 1 August 2026 (our download); the online tool now ends at 2025 |
| **Québec provincial (RSQAQ)** | Validated (40 monitors) | Not released | About June 2027 | 2025 file posted 22 June 2026 (Données Québec) |
| **Montréal (RSQA)** | Validated (11 monitors; downloaded 21 Oct 2026) | Not released | About June 2027 | 2025 file posted 11 June 2026 |
| **British Columbia provincial** | Verified (69) | Preliminary (68) | 2026 verified about mid-2027 | 2018–2025 already verified |
| **Alberta provincial (Air Data Warehouse)** | Validated (76 monitors) | Held to 31 August, may still change (70 monitors; September via AirNow) | September as it is submitted; reviewed data about mid-2027 | Downloaded 21 Oct 2026 by the team (Data Management Platform) |
| **Saskatchewan provincial** | Validated | Validated to April, then preliminary | 2026 about mid-2027 | Hub validation to April 2026 |
| **New Brunswick provincial** | Final | Preliminary | Final by 1 June 2027 | NB: quality assurance completed by 1 June of the next year |
| **US EPA AQS** | Validated (929 reference monitors) | Partly submitted (June in every state; September in 15) | July–September by 31 Dec 2026 (download Jan 2027); certified by 1 May 2027 | AQS submission deadline 90 days after each quarter; annual certification by 1 May |
| **AirNow (all provinces and states)** | Held (preliminary) | Held (preliminary) | Already available; stays preliminary | Real-time feed |
| **FireWork (ECCC)** | Held | Not held | Requested from ECCC | Depends on ECCC |
| **CWFIS fires (NRCan)** | Held | Not posted | About early 2027 | Posted after each season |
| **PurpleAir** | Held | ON, QC and Prairies only | US part with the PurpleAir request | Bought data |

*Table 1. 2025 and 2026 data by source. Release dates are estimates from each publisher’s past releases and stated deadlines.*

# **2. AirNow coverage for 2025 and 2026**

| **Province or country** | **Stations 2025** | **Hours 2025** | **Stations 2026** | **Hours 2026** |
| --- | --- | --- | --- | --- |
| **AB** | 41 | 142,437 | 39 | 135,161 |
| **BC** | 56 | 199,615 | 55 | 192,561 |
| **MB** | 1 | 2,683 | 0 | 0 |
| **NB** | 9 | 26,032 | 9 | 31,042 |
| **NL** | 1 | 3,658 | 1 | 3,516 |
| **NS** | 7 | 25,582 | 7 | 25,425 |
| **NT** | 1 | 1,427 | 1 | 3,263 |
| **ON** | 38 | 138,001 | 38 | 135,989 |
| **PE** | 3 | 10,537 | 3 | 8,783 |
| **QC** | 47 | 165,104 | 44 | 158,899 |
| **SK** | 7 | 24,335 | 7 | 23,926 |
| **YT** | 1 | 3,305 | 1 | 3,607 |
| **United States (all)** | 1,152 | 3,982,755 | 1,215 | 4,069,439 |

*Table 2. AirNow stations and hourly readings, 1 May – 30 September (Cleaned Data/analysis/data\_timeline/airnow\_by\_region\_2025\_2026.csv).*

# **3. Why AirNow is good enough for now**

| **Validated data** | **Monitors** | **Hours compared** | **r** | **Bias (µg/m³)** | **Hours ≥ 60 same** |
| --- | --- | --- | --- | --- | --- |
| **Ontario provincial 2023–25** | 38 | 371,581 | 0.997 | +0.33 | 98.3% |
| **Québec provincial 2023–25** | 35 | 352,842 | 1.000 | 0.00 | 99.9% |
| **NAPS 2023–24** | 197 | 1,167,007 | 0.998 | +0.19 | 98.8% |
| **US EPA AQS 2023–25** | 883 | 7,962,671 | 0.991 | +0.05 | 97.6% |
| **US EPA AQS 2026 (submitted)** | 861 | 1,636,999 | 0.996 | −0.01 | 98.1% |
| **Toronto (4 stations) 2023–25** | 4 | 37,183 | **0.999** | +0.17 | **100%** |

*Table 3. AirNow compared with validated data for the same monitors and hours, May–September (scripts/analysis\_airnow\_vs\_validated.py, clean\_aqs\_api\_2026.py).*

# **4. What to do and when**

| **When** | **Action** |
| --- | --- |
| **Now** | Test on 2026 with AirNow (US: EPA-submitted values where available). Montréal RSQA 2025 (validated) downloaded and cleaned on 21 October 2026. |
| **January 2027** | Re-run the AQS Data API download for July–September 2026 (scripts/download\_aqs\_api\_2026.py); check CWFIS 2026. |
| **March 2027** | Download NAPS 2025 and re-score the validation season (NAPS-only stations such as South Etobicoke). |
| **May 2027** | US EPA 2026 data certified: download the final AQS files. |
| **June–August 2027** | Download Québec, Montréal, New Brunswick, BC and Ontario 2026; re-score the 2026 test with validated data and compare with the AirNow result. |
| **March 2028** | NAPS 2026 released: final check of the 2026 test. |

*Table 4. Calendar for collecting the validated data.*

Release dates are estimates based on when each publisher posted the previous year’s data (checked 21 October 2026) and on stated deadlines (US AQS submission and certification; New Brunswick’s QA schedule). The Ontario date is the least certain: the Ministry of the Environment, Conservation and Parks could be asked directly. Prepared with the Claude AI assistant, directed and checked by the team.
