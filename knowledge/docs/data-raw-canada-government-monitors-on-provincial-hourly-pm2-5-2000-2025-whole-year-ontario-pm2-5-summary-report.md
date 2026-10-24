---
source: data/raw/Canada Government Monitors/ON Provincial - Hourly PM2.5 - 2000-2025 (whole year)/Ontario_PM2.5_Summary_Report.docx
aliases: []
sha256: 8a296135584e99a7e3cd8bad375380585dfdb23c94b5d5e618acb13cd4f220d6
converted: 2026-10-24
converter: markitdown
status: current
kind: mirror
---

**Ontario Hourly PM2.5 Air Quality Monitoring Data**

Summary Report of the Combined Dataset (2000–2025)

*Prepared for the CLEAR 2.0 project – Data Cleaning Stage
Source: Air Quality Ontario (Government of Ontario)*

# 1. Overview and Coverage

This report summarizes the combined hourly fine particulate matter (PM2.5) concentration dataset for Ontario, built by merging 26 annual source files (2000–2025) published by Air Quality Ontario. All values are in micrograms per cubic metre (µg/m³).

|  |  |
| --- | --- |
| **Metric** | **Value** |
| Time period covered | 2003-01-01 to 2025-12-31 (23 years with data; 2000–2002 contained no data in the source files) |
| Monitoring locations (cities/towns) | 42 |
| Distinct station codes | 58 total (57 with at least one recorded value; 1 code never reported data) |
| Station-days recorded | 324,860 |
| Total hourly measurement cells | 7,796,640 (station-days × 24 hours) |
| Valid (non-missing) hourly measurements | 7,642,856 (98.03% of cells) |
| Missing / invalid hourly measurements | 153,784 (1.97% of cells) |

*Note: many towns/cities host more than one station code over the period because Ontario periodically relocated or replaced monitoring equipment at a location (e.g. Kingston has been monitored continuously since 2003 across three successive station codes: 52020, 52022, then 52023). Station counts and “coverage” figures above reflect the raw station codes present in the source files.*

# 2. Sample Measurements

Each source row represents one station-day with 24 hourly concentration readings (columns H01–H24). The table below shows a representative excerpt from the combined dataset (Barrie station, January 2003), including a run of the “9999” / “-999” missing-data codes documented by the source.

|  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Station** | **Date** | **H01** | **H02** | **H03** | **H04** | **H05** | **...** | **H21** | **H22** | **H23** | **H24** |
| Barrie (47045) | 2003-01-01 | 1 | 2 | 1 | 1 | 0 | ... | 0 | 0 | 1 | 1 |
| Barrie (47045) | 2003-01-02 | 2 | 1 | 0 | 0 | 1 | ... | 2 | 1 | 3 | 3 |
| Barrie (47045) | 2003-01-03 | 2 | 1 | 2 | 9999 | 9999 | ... | 2 | 2 | 2 | 2 |
| Barrie (47045) | 2003-01-04 | 2 | 2 | 3 | 2 | 3 | ... | 9 | 12 | 9 | 8 |

*The full combined spreadsheet retains this wide hourly layout (one row per station-day) for every station and year, plus a “Stations” reference sheet and missing-data summary sheets.*

# 3. Percentage of Missing Values by Year

“Missing” hourly values are those flagged in the source data with the sentinel codes 9999 or -999 (9999 is documented by Air Quality Ontario as “invalid or missing data”; -999 is an undocumented but consistently used equivalent flag), or left blank. Percentages below are of the hourly cells that were actually recorded that year (they exclude entire station-years for which the source reported “No data available” — see Section 6).

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Year** | **Station-Days** | **Missing Hours** | **Total Hours** | **% Missing** |
| 2003 | 11,797 | 23,829 | 283,128 | 8.42% |
| 2004 | 13,361 | 6,163 | 320,664 | 1.92% |
| 2005 | 13,870 | 15,075 | 332,880 | 4.53% |
| 2006 | 13,799 | 4,573 | 331,176 | 1.38% |
| 2007 | 14,600 | 4,264 | 350,400 | 1.22% |
| 2008 | 14,640 | 5,244 | 351,360 | 1.49% |
| 2009 | 14,591 | 6,683 | 350,184 | 1.91% |
| 2010 | 14,596 | 7,214 | 350,304 | 2.06% |
| 2011 | 14,598 | 5,713 | 350,352 | 1.63% |
| 2012 | 14,640 | 8,324 | 351,360 | 2.37% |
| 2013 | 14,600 | 8,942 | 350,400 | 2.55% |
| 2014 | 14,600 | 5,526 | 350,400 | 1.58% |
| 2015 | 14,404 | 5,493 | 345,696 | 1.59% |
| 2016 | 14,189 | 5,685 | 340,536 | 1.67% |
| 2017 | 14,232 | 4,422 | 341,568 | 1.29% |
| 2018 | 13,886 | 4,969 | 333,264 | 1.49% |
| 2019 | 14,377 | 4,029 | 345,048 | 1.17% |
| 2020 | 14,272 | 5,117 | 342,528 | 1.49% |
| 2021 | 14,235 | 4,939 | 341,640 | 1.45% |
| 2022 | 13,928 | 4,506 | 334,272 | 1.35% |
| 2023 | 13,867 | 5,640 | 332,808 | 1.69% |
| 2024 | 13,908 | 3,996 | 333,792 | 1.20% |
| 2025 | 13,870 | 3,438 | 332,880 | 1.03% |

*Overall across all 23 years: 1.97% of hourly cells are missing/invalid. 2003 stands out with the highest missing rate (8.42%), consistent with the network still being built out in its first reporting year; missing rates settle to roughly 1–2.5% from 2006 onward.*

# 4. Percentage of Missing Values by Station

Missing-data rates vary widely by station. The table below lists the 15 stations with the highest missing-value percentages (of hours actually recorded); the complete list of all 57 stations is provided in the “Missing by Station” sheet of the combined spreadsheet.

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Station** | **Station-Days** | **Missing Hours** | **Total Hours** | **% Missing** |
| Sarnia (14110) | 13 | 312 | 312 | 100.00% |
| Kingston (52020) | 1,391 | 10,724 | 33,384 | 32.12% |
| Merlin (13021) | 731 | 3,988 | 17,544 | 22.73% |
| London (15025) | 3,653 | 3,965 | 87,672 | 4.52% |
| Tiverton (18007) | 8,401 | 8,665 | 201,624 | 4.30% |
| Mississauga (46110) | 495 | 466 | 11,880 | 3.92% |
| Grand Bend (15020) | 8,400 | 7,273 | 201,600 | 3.61% |
| Thunder Bay (63203) | 7,569 | 6,290 | 181,656 | 3.46% |
| Oshawa (45025) | 731 | 470 | 17,544 | 2.68% |
| Dorset (49010) | 8,401 | 5,077 | 201,624 | 2.52% |
| Cornwall (56051) | 8,399 | 4,883 | 201,576 | 2.42% |
| Toronto North (34020) | 5,114 | 2,912 | 122,736 | 2.37% |
| Hamilton West (29118) | 8,401 | 4,535 | 201,624 | 2.25% |
| Kitchener (26060) | 8,401 | 4,423 | 201,624 | 2.19% |
| Kingston (52022) | 2,545 | 1,280 | 61,080 | 2.10% |

*Sarnia (14110) shows 100% missing because its only 13 recorded station-days (in 2016, immediately before it was succeeded by station 14111) are entirely flagged invalid. Kingston (52020) and Merlin (13021) also stand out; both were retired mid-period (52020 in 2006, 13021 in 2004) and their final recorded days carry disproportionately high invalid-value counts.*

# 5. Stations and Cities Covered

The dataset covers 42 distinct Ontario monitoring locations (cities/towns) via 58 station codes over the 2003–2025 period, listed below with their active date range.

|  |  |  |  |
| --- | --- | --- | --- |
| **City / Town** | **Station ID** | **Address** | **Active Years** |
| Barrie | 47045 | 83 Perry St. | 2003–2025 |
| Belleville | 54012 | 2 Sidney St., Water Treatment Plant | 2003–2025 |
| Brampton | 46089 | 525 Main St. N., Peel Manor | 2003–2016 |
| Brampton | 46090 | 109 Mclaughlin Rd. S. | 2017–2025 |
| Brantford | 21005 | 324 Grand River Ave. | 2004–2025 |
| Burlington | 44008 | North Shore Blvd. E./Lakeshore Rd. | 2003–2025 |
| Chatham | 13001 | 435 Grand Ave. W. | 2005–2025 |
| Cornwall | 56051 | Bedford St./3rd St. W. | 2003–2025 |
| Dorset | 49010 | 1026 Bellwood Acres Rd. | 2003–2025 |
| Grand Bend | 15020 | Point Blake Conservation Area | 2003–2025 |
| Guelph | 28028 | Exhibition St./Clark St. W. | 2003–2025 |
| Hamilton Downtown | 29000 | Elgin St./Kelly St. | 2003–2025 |
| Hamilton Mountain | 29114 | Vickers Rd./E. 18th St. | 2003–2018 |
| Hamilton Mountain | 29214 | 250 Fennell Ave. W. | 2018–2025 |
| Hamilton West | 29118 | Main St. W./Hwy 403 | 2003–2025 |
| Kingston | 52020 | 133 Dalton St. | 2003–2006 |
| Kingston | 52022 | 752 King St. W. | 2007–2013 |
| Kingston | 52023 | 23 Beechgrove Lane | 2014–2025 |
| Kitchener | 26060 | West Ave./Homewood Ave. | 2003–2025 |
| London | 15025 | 900 Highbury Ave. N. | 2003–2012 |
| London | 15026 | 42 St. Julien St. | 2013–2025 |
| Merlin | 13021 | Middle Rd., Moe Water Pump Stn. | 2003–2004 |
| Milton | 44029 | 1120 Main St. E. | 2018–2025 |
| Mississauga | 46108 | 3359 Mississauga Rd. N., U Of T Campus | 2008–2025 |
| Mississauga | 46109 | Frank Mckechnie Comm. Ctr | 2004–2007 |
| Mississauga | 46110 | Mississauga General Hospital | 2003–2004 |
| Morrisburg | 56010 | County Rd. 2, Morrisburg Water Tower | 2005–2015 |
| Newmarket | 48006 | Eagle St. W./Mccaffrey Rd. | 2003–2025 |
| North Bay | 75010 | Chippewa St. W., Dept. National Defence | 2003–2025 |
| Oakville | 44017 | Eighth Line/Glenashton Dr., Halton Res. | 2003–2025 |
| Oshawa | 45025 | Ritson Rd. Public School | 2003–2004 |
| Oshawa | 45026 | 2000 Simcoe St. N., Durham College | 2005–2018 |
| Oshawa | 45027 | Brittania Ave. W., EP Taylor Stables | 2018–2025 |
| Ottawa Central | 51002 | 960 Carling Ave. | 2007–2017 |
| Ottawa Downtown | 51001 | Rideau St./Wurtemburg St. | 2003–2025 |
| Parry Sound | 49005 | 7 Bay St. | 2003–2025 |
| Petawawa | 51010 | Petawawa Research Forest Facility | 2007–2022 |
| Peterborough | 59006 | 10 Hospital Dr. | 2003–2025 |
| Port Stanley | 16015 | 43665 Dexter Line, Elgin Water T. Plt | 2003–2025 |
| Sarnia | 14064 | Front St. N./Cn Tracks, Centennial Park | 2003–2015 |
| Sarnia | 14110 | 99 Seaway Rd., Point Lands | 2016–2016 |
| Sarnia | 14111 | 700 Christina St. N. | 2016–2025 |
| Sault Ste. Marie | 71068 | WM. Merrifield School | —–— |
| Sault Ste. Marie | 71078 | Sault College | 2004–2025 |
| St. Catharines | 27067 | Argyle Cres., Pump Stn. | 2003–2025 |
| Sudbury | 77219 | 1222 Ramsey Lake Rd. | 2004–2012 |
| Sudbury | 77233 | Applegrove St./Birch St. | 2013–2025 |
| Thunder Bay | 63200 | 615 James St. S., MTO | 2024–2025 |
| Thunder Bay | 63203 | 421 James St. S. | 2004–2024 |
| Tiverton | 18007 | 4th Concession/Bruce Rd. 23 | 2003–2025 |
| Toronto Downtown | 31103 | Bay St./Wellesley St. W. | 2003–2019 |
| Toronto Downtown | 31129 | 55 John St. | 2019–2025 |
| Toronto East | 33003 | Kennedy Rd./Lawrence Ave. E. | 2003–2025 |
| Toronto North | 34020 | Hendon Ave./Yonge St. | 2003–2016 |
| Toronto North | 34021 | 4905 Dufferin St., Eccc | 2017–2025 |
| Toronto West | 35125 | 125 Resources Rd. | 2003–2025 |
| Windsor Downtown | 12008 | 467 University Ave. W. | 2003–2025 |
| Windsor West | 12016 | College Ave./South St. | 2003–2025 |

# 6. Data Quality Notes

* **Empty source years.** Empty source years: The 2000–2002 annual files contain no station data at all (header only) — Ontario's hourly PM2.5 network reporting for this dataset effectively begins January 1, 2003.
* **Whole-year gaps.** 40 station-year combinations across the dataset are explicitly marked “No data available” in the source file for that year (e.g. Thunder Bay station 63200 reports no data for 21 of its 23 listed years, and Toronto Downtown station 31129 for 16 of its years) — these are excluded from the missing-value percentages above, but represent a further coverage gap and are listed in full on the “No-Data Station-Years” sheet.
* **Duplicate station-date rows.** 1,904 rows across 802 distinct station-date combinations are duplicated in the raw source files — typically two rows for the same station and date where each row supplies a different subset of the 24 hours (one half valid, the other flagged missing) rather than one complete row. These duplicates were preserved as-is in the combined spreadsheet to keep it a faithful merge of the raw files; they should be resolved (e.g. coalesced into a single row per station-date) during the next data-cleaning step.
* **Station code changes.** 12 of the 42 monitoring locations were tracked under more than one station code during 2003–2025 (e.g. Kingston, Toronto Downtown, Sarnia, Mississauga, Oshawa), reflecting site relocations or instrument replacements. Station codes generally hand off cleanly (one code's last year immediately precedes the successor's first year), so continuity by city is preserved even though the station ID changes.
* **Missing-value codes.** Missing/invalid readings are flagged with 9999 (documented) or -999 (undocumented, but used consistently) in the source files and were left unconverted in the combined spreadsheet. A small number of readings (3 cells) are small negative values (e.g. -3) distinct from the -999 flag — these are physically implausible for a concentration but are typical low-level instrument noise near zero and were not treated as missing.
* **Partial-year records.** Most stations have a small number of station-days that don't match the expected 365/366 for their year, generally because monitoring started or stopped partway through the year (station commissioning/decommissioning) rather than random data loss.

# 7. Combined Spreadsheet

All 26 annual source files were merged into a single workbook, “ON\_Hourly\_PM2.5\_2000-2025\_Combined.xlsx”, saved alongside this report. It contains:

* Combined Data – all 324,860 station-day rows (Year, Station ID, Station Name, Date, H01–H24), sorted by station and date.
* Stations – metadata (address, coordinates, elevation, air intake height, active years) for all 58 station codes.
* Missing by Year – the Section 3 table for all 23 years.
* Missing by Station – the Section 4 table for all 57 stations with data.
* No-Data Station-Years – the full list of 40 station-year combinations with zero reported data.
