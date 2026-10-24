---
source: archive/seagate/Documents/35. AirNow/CLEAR2_AirNow_Summary.docx
aliases: [archive/seagate/Documents/35. AirNow/CLEAR2_AirNow_Summary.pdf]
sha256: 3c4b1acfe720f61a6327a94d0fb15c650683632a00375bd0cb864e62c6959aac
converted: 2026-10-24
converter: markitdown
status: current
kind: mirror
---

**AirNow: What It Is and Whether CLEAR Can Use It**

**Real-time government PM2.5 data for Canada and the US, and its role in the 2025 validation and 2026 test seasons**

*Hugo Bui & Ryan Zander · University of Toronto Schools · October 2026*

|  |
| --- |
| **Answer in brief**   * **AirNow is a government system, not a private network.** It is run by the US EPA with NOAA, the National Park Service, NASA, the CDC and tribal, state and local agencies, and it receives Canada’s data from Environment and Climate Change Canada and the provinces. It does not own monitors: it collects the **real-time readings of the same government monitoring stations** whose validated data later appear in NAPS, the provincial archives and EPA AQS. * **Not validated, but almost identical to validated data.** AirNow values are preliminary (automatic checks only). Compared with the validated data for the same monitors and hours, they agree at r = 0.99–1.00, differ on average by less than 0.4 µg/m³, and 97.6–100% of hours ≥ 60 µg/m³ are the same (100% at Toronto’s four stations). * **Coverage:** every province with monitors and every US state. In the 2025 fire season, **212 monitors in Canada** (12 provinces and territories) and **1,152 in the US** (50 states and DC); in 2026, 205 and 1,215. * **Mostly duplicate data for training.** 93% of AirNow monitors (197 of 212 in Canada, 1,071 of 1,152 in the US in 2025) are the same instruments we already hold in validated form. Our AirNow files start in 2014; for 2000–2024 the validated networks already hold these monitors. So AirNow adds little to the **training** data (2021–2024). * **But it is exactly what we need for 2025 validation and 2026 testing.** It is the only source that covers every hour of the 2026 fire season in every province and state now, and it fills NAPS 2025 (expected March 2027). It is also what the **live CLEAR app** will receive in real time, so testing on AirNow tests CLEAR the way it will actually run. |

# **1. What AirNow is**

* **A real-time data system run by government agencies.** The US EPA launched AirNow in 1998 to publish real-time air quality (the Air Quality Index) for the public. Its partners are NOAA, the National Park Service, NASA, the CDC, and the tribal, state and local air agencies that operate monitors. Environment and Climate Change Canada and the provinces send Canada’s real-time data to it, so AirNow covers both countries in one feed.
* **It collects, it does not measure.** Each agency’s monitors send hourly readings to AirNow within about an hour. The same agencies later check (validate) the data and submit it to the official archives: NAPS (Canada), the provincial archives, and EPA’s Air Quality System (AQS) in the US.
* **Files we use:** hourly observation files from AirNow’s public file server (HourlyAQObs, 2019–2026; HourlyData, 2014–2019), with each monitor’s site number (AQSID), location, reporting agency and PM2.5 in µg/m³. We downloaded 2014 to 8 October 2026 (about 117 million rows).
* **Not PurpleAir:** AirNow’s public Fire and Smoke Map also shows corrected low-cost sensors (such as PurpleAir), but those are a separate layer and are **not** in the monitor files we use.

# **2. Which monitoring stations feed AirNow**

In the 2025 fire season, AirNow PM2.5 came from **14 reporting agencies in Canada** and **120 in the US**: provincial and federal agencies in Canada, and state, county, city and tribal agencies (plus a few federal ones) in the US. They use the same reference or equivalent instruments (BAM 1020, Teledyne T640, Thermo SHARP 5030, TEOM) as the validated networks.

| **Reporting agency (2025)** | **Monitors** | **Country** |
| --- | --- | --- |
| **Alberta Environmental Monitoring and Reporting Agency (AEMERA)** | 40 | Canada |
| **Canada-Quebec1** | 39 | Canada |
| **Ontario Ministry of the Environment** | 35 | Canada |
| **British Columbia Ministry of Environment** | 34 | Canada |
| **Metro Vancouver** | 21 | Canada |
| **Canada-Quebec2** | 10 | Canada |
| **Canada-New Brunswick1** | 9 | Canada |
| **Canada-Nova Scotia1** | 7 | Canada |
| **Saskatchewan Environment** | 6 | Canada |
| **Canadian Air and Precipitation Monitoring Network** | 5 | Canada |
| **Oregon Dept. of Environmental Quality** | 68 | United States |
| **Washington Department of Ecology** | 67 | United States |
| **Texas Commission on Environmental Quality** | 50 | United States |
| **Ohio EPA-DAPC** | 42 | United States |
| **Pennsylvania Dept. of Environmental Protection** | 38 | United States |
| **Florida Dept. of Environmental Protection** | 35 | United States |
| **Illinois EPA** | 34 | United States |
| **Idaho Department of Environmental Quality** | 30 | United States |
| **Indiana Dept. of Environmental Management** | 28 | United States |
| **Colorado Department of Public Health and Environment** | 26 | United States |

*Table 1. The largest reporting agencies (Cleaned Data/analysis/airnow\_summary/agencies\_2025.csv). "Canada-Quebec1" is the Québec ministry; "AEMERA" is Alberta’s monitoring agency; "Canadian Air and Precipitation Monitoring Network" is ECCC’s rural network.*

# **3. How AirNow differs from NAPS, the provincial networks and EPA AQS**

|  | **AirNow** | **NAPS / Ontario and Québec provincial / EPA AQS** |
| --- | --- | --- |
| **What it is** | Real-time collection system for the agencies’ monitors | Official archives of the same monitors after validation |
| **Who runs it** | US EPA and partners; Canadian data from ECCC and the provinces | ECCC (NAPS), provincial ministries, US EPA (AQS) |
| **When available** | Within about an hour | AQS: about 3–6 months; provinces: about 6–8 months after the year; NAPS: about 15 months after the year |
| **Validation** | Preliminary: automatic range and spike checks only | Full quality assurance: calibrations, audits, flags, corrections |
| **Coverage** | Canada and the US in one feed | One network or country each |
| **History in our files** | 2014 – 8 October 2026 | NAPS 2000–2024; Ontario and Québec 2000–2025; EPA AQS 2008–2026 (partly 2026) |
| **Time label** | UTC, labelled by the start of the hour | EPA AQS: start of the hour (UTC); Canadian archives: end of the hour (local standard time) |
| **Station IDs** | AQSID (9 or 12 digits; 124… = Canada, 840… = US) | NAPS ID, provincial ID, AQS site number |

*Table 2. AirNow compared with the validated networks.*

# **4. Is AirNow data validated, and is it as good as government station data?**

AirNow data **is** government station data: the same instruments at the same sites. What differs is that it is reported before validation. To see how much validation changes it, we compared AirNow with the validated data for the same monitors and hours (May–September):

| **Validated data** | **Monitors** | **Hours compared** | **r** | **Bias (µg/m³)** | **Hours ≥ 60 same** |
| --- | --- | --- | --- | --- | --- |
| **Ontario provincial 2023–25** | 38 | 371,581 | 0.997 | +0.33 | 98.3% |
| **Québec provincial 2023–25** | 35 | 352,842 | 1.000 | 0.00 | 99.9% |
| **NAPS 2023–24** | 197 | 1,167,007 | 0.998 | +0.19 | 98.8% |
| **US EPA AQS 2023–25** | 883 | 7,962,671 | 0.991 | +0.05 | 97.6% |
| **US EPA AQS 2026 (submitted)** | 861 | 1,636,999 | 0.996 | −0.01 | 98.1% |
| **Montréal RSQA 2025 / Alberta warehouse 2025** | 10 / 36 | — | 1.000 | — | — |
| **Toronto (4 stations) 2023–25** | 4 | 37,183 | **0.999** | +0.17 | **100%** |

*Table 3. AirNow vs validated data for the same monitors and hours (Cleaned Data/analysis/airnow\_vs\_validated/).*

* **Answer:** AirNow is not validated, but validation changes it very little. Ontario and Québec removed under 1% of hours during validation, and US agencies about 4.6%. For CLEAR’s purpose (detecting smoke hours and alert levels) AirNow gives essentially the same answer as validated data.
* **Lower confidence for AirNow-only monitors:** about 7% of AirNow monitors report only in real time and never appear in the validated archives we hold (section 6). Many are small-town state or tribal monitors (for example in Oregon, Washington and Idaho) and some may be non-regulatory instruments, so they should carry a lower weight or be checked before use.

# **5. Coverage in Canada and the US**

![AirNow map 2025](data:image/png;base64...)

*Figure 1. AirNow PM2.5 monitors in the 2025 fire season, coloured by whether we already hold the same monitor in validated form.*

| **Province or territory** | **2025** | **2026** | **Notes** |
| --- | --- | --- | --- |
| **Alberta** | 41 | 39 |  |
| **British Columbia** | 56 | 55 |  |
| **Manitoba** | 1 | 0 | Only one Manitoba station reports to AirNow |
| **New Brunswick** | 9 | 9 |  |
| **Newfoundland and Labrador** | 1 | 1 |  |
| **Nova Scotia** | 7 | 7 |  |
| **Northwest Territories** | 1 | 1 |  |
| **Ontario** | 38 | 38 |  |
| **Prince Edward Island** | 3 | 3 |  |
| **Québec** | 47 | 44 |  |
| **Saskatchewan** | 7 | 7 |  |
| **Yukon** | 1 | 1 |  |
| **Canada** | **212** | **205** |  |

*Table 4. AirNow PM2.5 monitors reporting in the fire season (May–September), Canada. Nunavut has no PM2.5 monitor in AirNow.*

| **State** | **2025** | **2026** | **State** | **2025** | **2026** |
| --- | --- | --- | --- | --- | --- |
| **AK** | 7 | 6 | MT | 24 | 19 |
| **AL** | 14 | 14 | NC | 24 | 24 |
| **AR** | 4 | 4 | ND | 9 | 9 |
| **AZ** | 23 | 23 | NE | 8 | 10 |
| **CA** | 140 | 143 | NH | 6 | 6 |
| **CO** | 28 | 28 | NJ | 19 | 20 |
| **CT** | 8 | 8 | NM | 14 | 15 |
| **DC** | 5 | 5 | NV | 20 | 21 |
| **DE** | 8 | 8 | NY | 23 | 23 |
| **FL** | 49 | 52 | OH | 43 | 42 |
| **GA** | 18 | 19 | OK | 14 | 13 |
| **IA** | 11 | 13 | OR | 77 | 77 |
| **ID** | 32 | 28 | PA | 51 | 54 |
| **IL** | 38 | 38 | RI | 6 | 6 |
| **IN** | 27 | 27 | SC | 11 | 11 |
| **KS** | 9 | 9 | SD | 9 | 9 |
| **KY** | 20 | 19 | TN | 19 | 20 |
| **LA** | 10 | 12 | TX | 55 | 59 |
| **MA** | 20 | 22 | UT | 24 | 27 |
| **MD** | 15 | 14 | VA | 16 | 18 |
| **ME** | 12 | 11 | VT | 3 | 4 |
| **MI** | 27 | 27 | WA | 69 | 114 |
| **MN** | 24 | 27 | WI | 18 | 18 |
| **MO** | 10 | 10 | WV | 5 | 4 |
| **MS** | 8 | 8 | WY | 18 | 17 |
| **US total** | **1,152** | **1,215** |  |  |  |

*Table 5. AirNow PM2.5 monitors reporting in the fire season, US states and DC (Hawaii and Puerto Rico are outside CLEAR’s area).*

# **6. A large network, or duplicate data?**

![AirNow by year](data:image/png;base64...)

*Figure 2. AirNow PM2.5 monitors each fire season in the files we hold (2014–2026).*

| **Fire season** | **AirNow monitors** | **Same monitor in a validated network we hold** | **Only in AirNow** | **Share duplicate** |
| --- | --- | --- | --- | --- |
| **2025 Canada** | 212 | 197 | 15 | 93% |
| **2025 US** | 1,152 | 1,071 | 81 | 93% |
| **2026 Canada** | 205 | 189 | 16 | 92% |
| **2026 US** | 1,215 | 1,093 | 122 | 90% |

*Table 6. Overlap with validated networks (Canada: a NAPS, provincial, Montréal or Alberta warehouse station within 0.5 km; US: the same AQS site number). Cleaned Data/analysis/airnow\_summary/overlap\_summary.csv.*

* **It is a large network (about 1,400 monitors), but mostly the same monitors we already have.** For the training seasons 2021–2024, the validated versions (NAPS, provincial, EPA AQS) are better, so AirNow adds little there. When both exist, the model should use the validated value and treat AirNow as the same station (monitors within 1 km count once), never as an extra station.
* **History:** our AirNow files start in 2014 (about 860 monitors then, about 1,400 now). AirNow cannot provide 2000–2013 in our data, but that does not matter: the same monitors are in NAPS (from 2000), the Ontario and Québec archives (from 2000) and EPA AQS.
* **What only AirNow adds:** (1) every hour that the validated archives have **not released yet** (2025 NAPS-only stations, all of 2026 in Canada, July–September 2026 in many US states, September 2026 in Alberta); (2) about 100 monitors that never reach the validated archives; and (3) the **real-time feed** the live CLEAR app will use.

# **7. Is AirNow good enough for 2025 validation and 2026 testing?**

|  |
| --- |
| **Yes**  NAPS 2025 will not be ready until about March 2027 and the provincial 2026 data until about mid-2027, but CLEAR does not need to wait. AirNow covers every hour of both seasons, in every province and state, and matches validated data almost exactly (Table 3).   * **2025 (validation):** use the validated provincial and EPA data already held (Ontario, Québec and Montréal, BC, Alberta, Saskatchewan, New Brunswick, EPA AQS); use AirNow only where NAPS 2025 is missing (NAPS-only stations) and for any gaps. * **2026 (test):** use AirNow for Canada (with the Alberta warehouse to 31 August, BC, Saskatchewan and New Brunswick preliminary data where available) and the EPA-submitted values in the US where states have sent them, with AirNow for the remaining months. * **Re-check later:** when NAPS 2025 (about March 2027) and the 2026 validated data (2027) are released, score the validation and test seasons again. Based on Table 3, the results should change very little. |

# **8. Cautions**

* **Preliminary values can change:** a small share of hours are removed or corrected in validation (under 1% in Ontario and Québec, about 4.6% in the US).
* **Time labels:** AirNow labels each hour by its start (UTC), the Canadian archives by its end. CLEAR moves the Canadian series back 1 hour before comparing (pending correction for all Canadian data).
* **Duplicates:** the same monitor appears in AirNow and in a validated network (and sometimes in AirNow under two IDs when its site number changed, as in 2020 and 2022). Monitors within 1 km are merged into one site.
* **AirNow-only monitors:** check them against nearby validated monitors before use.
* **A correction made while writing this document:** an earlier cleaning step labelled every AirNow site number starting with "840" as a temporary wildfire-smoke monitor. "840" is only the US country code; only 14 AirNow monitors (all US Forest Service) are wildfire-response monitors. The station list, the methodology and the logbook were corrected (scripts/fix\_airnow\_registry\_kind.py).

Sources: AirNow hourly files 2014 – 8 Oct 2026 (RAW Data/AirNow); analyses in Cleaned Data/analysis/airnow\_summary and airnow\_vs\_validated (scripts/analysis\_airnow\_summary.py, analysis\_airnow\_vs\_validated.py, clean\_aqs\_api\_2026.py). Prepared with the Claude AI assistant, directed and checked by the team, 21 October 2026.
