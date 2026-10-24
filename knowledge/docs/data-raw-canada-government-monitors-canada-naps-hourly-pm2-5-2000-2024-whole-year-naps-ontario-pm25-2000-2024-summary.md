---
source: data/raw/Canada Government Monitors/Canada NAPS Hourly PM2.5 2000-2024 (whole year)/NAPS_Ontario_PM25_2000-2024_Summary.docx
aliases: []
sha256: 8783daa36ee4c862bb0b70f41d6c9b94641877a01f54492c657e08d9da49bb58
converted: 2026-10-24
converter: markitdown
status: current
kind: mirror
---

**Ontario Hourly PM2.5 Data Summary**

*National Air Pollution Surveillance (NAPS) Program — 2000–2024*

# 1. Overview

This document summarizes the Ontario-only subset extracted from Environment and Climate Change Canada's National Air Pollution Surveillance (NAPS) hourly PM2.5 dataset covering 2000-2024. The subset was filtered from 25 annual source files (PM25\_2000.csv through PM25\_2024.csv) by selecting all rows where Province/Territory = "ON" (Ontario), and was exported to NAPS\_Ontario\_PM25\_2000-2024.xlsx.

# 2. Time Period

* Start date: 2000-01-01
* End date: 2024-12-31

Coverage spans 25 consecutive calendar years. Not every station was active for the full period - individual station start/end dates are listed in Section 8.

# 3. Coverage — Stations and Cities

* Total number of distinct monitoring stations (unique NAPS ID): 70
* Total number of distinct cities/municipalities: 37

Toronto has the densest coverage with 13 station locations recorded over the period (reflecting station relocations and additions over time), followed by Hamilton (4), and Windsor, Sault Ste. Marie, Mississauga, Kingston, Oshawa, and Sarnia (3 each). The remaining cities/towns each have 1-2 station locations. A complete per-station listing with cities is provided in Section 8.

# 4. Total Number of Hourly Measurements

* Total station-day rows in the Ontario subset: 376,584
* Total possible hourly measurement slots (station-days x 24 hours): 9,038,016
* Valid (non-missing) hourly measurements: 8,282,819
* Missing hourly measurements (coded -999): 755,197
* Overall missing rate: 8.36%

# 5. Sample Measurements

Example rows from the extracted dataset (Ottawa, NAPS ID 60104), showing hourly PM2.5 concentrations in µg/m³ for a subset of hours:

|  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **NAPS ID** | **City** | **Method Code** | **Date** | **H01** | **H02** | **H03** | **H12** | **H24** |
| 60104 | Ottawa | 706 | 2000-01-01 | 8 | 11 | 15 | 11 | 45 |
| 60104 | Ottawa | 706 | 2000-01-02 | 39 | 34 | 29 | 7 | 16 |
| 60104 | Ottawa | 706 | 2000-01-03 | 19 | 20 | 7 | 0 | 0 |

# 6. Data Quality

## 6.1 Missing Value Convention

The source data uses -999 as a sentinel value for "no data available." Genuine zero readings are valid and distinct from missing data. All missing-percentage calculations in this document treat -999 as missing and exclude it from valid-value statistics.

## 6.2 Value Range Check

Among valid (non-missing) hourly values, concentrations ranged from -3 to 667 µg/m³ (mean 7.04, median 5). 2,332 valid readings were negative (but not the -999 missing code) - small negative values are a known artifact of some PM2.5 monitors near zero concentration and are retained as reported by NAPS rather than altered.

## 6.3 Multiple Method Codes per Station

Starting around 2022, several stations report parallel measurements from more than one instrument/method code on the same day (e.g., a reference method alongside a newer continuous monitor). This is expected NAPS reporting behaviour during instrument transitions, not duplicate data - each row is uniquely identified by the combination of NAPS ID, Method Code, and Date. It explains the elevated row counts and missing-value rates seen for 2022-2023 in Section 7, since the two parallel instruments at a given site do not always report on the same days.

## 6.4 Uniqueness

No duplicate rows were found for the (NAPS ID, Method Code, Date) key - each combination occurs at most once in the dataset.

# 7. Missing Values by Year

Percentage of missing hourly measurements (-999) by calendar year, across all Ontario stations:

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Year** | **Total Hourly Slots** | **Valid** | **Missing (-999)** | **% Missing** |
| 2000 | 175,680 | 151,399 | 24,281 | 13.82% |
| 2001 | 227,760 | 187,867 | 39,893 | 17.52% |
| 2002 | 219,000 | 185,368 | 33,632 | 15.36% |
| 2003 | 315,360 | 280,605 | 34,755 | 11.02% |
| 2004 | 351,360 | 330,062 | 21,298 | 6.06% |
| 2005 | 359,160 | 344,063 | 15,097 | 4.20% |
| 2006 | 350,400 | 344,554 | 5,846 | 1.67% |
| 2007 | 376,680 | 372,230 | 4,450 | 1.18% |
| 2008 | 386,496 | 371,336 | 15,160 | 3.92% |
| 2009 | 367,920 | 358,178 | 9,742 | 2.65% |
| 2010 | 376,680 | 358,290 | 18,390 | 4.88% |
| 2011 | 367,920 | 362,021 | 5,899 | 1.60% |
| 2012 | 386,496 | 360,185 | 26,311 | 6.81% |
| 2013 | 376,680 | 358,618 | 18,062 | 4.80% |
| 2014 | 376,680 | 362,308 | 14,372 | 3.82% |
| 2015 | 359,160 | 352,906 | 6,254 | 1.74% |
| 2016 | 377,712 | 361,146 | 16,566 | 4.39% |
| 2017 | 376,680 | 368,002 | 8,678 | 2.30% |
| 2018 | 367,920 | 361,959 | 5,961 | 1.62% |
| 2019 | 394,200 | 372,544 | 21,656 | 5.49% |
| 2020 | 377,712 | 372,326 | 5,386 | 1.43% |
| 2021 | 376,680 | 371,170 | 5,510 | 1.46% |
| 2022 | 630,720 | 362,541 | 268,179 | 42.52% |
| 2023 | 455,520 | 355,243 | 100,277 | 22.01% |
| 2024 | 307,440 | 277,898 | 29,542 | 9.61% |

The elevated missing rates in 2022 (42.52%) and 2023 (22.01%) correspond to the dual-method reporting period described in Section 6.3.

# 8. Stations and Cities Covered

Full list of the 70 Ontario NAPS stations included in this subset, with coordinates, active date range, number of station-day rows, and percentage of missing hourly values:

|  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **NAPS ID** | **City** | **Lat** | **Lon** | **First Date** | **Last Date** | **Days** | **% Missing** |
| 60104 | Ottawa | 45.4343 | -75.6760 | 2000-01-01 | 2024-12-31 | 9497 | 7.16% |
| 60106 | Ottawa | 45.3829 | -75.7139 | 2007-01-01 | 2017-12-31 | 4018 | 1.87% |
| 60203 | Windsor | 42.3381 | -82.9272 | 2000-01-01 | 2000-12-31 | 366 | 3.24% |
| 60204 | Windsor | 42.3158 | -83.0437 | 2001-01-01 | 2024-12-31 | 9131 | 6.46% |
| 60211 | Windsor | 42.2929 | -83.0731 | 2002-01-01 | 2024-12-31 | 8766 | 6.45% |
| 60302 | Kingston | 44.2307 | -76.5088 | 2003-01-01 | 2004-12-31 | 731 | 10.65% |
| 60303 | Kingston | 44.2201 | -76.5214 | 2007-01-01 | 2013-12-31 | 2557 | 2.48% |
| 60304 | Kingston | 44.2199 | -76.5211 | 2013-01-01 | 2024-12-31 | 4748 | 16.16% |
| 60403 | Toronto | 43.6192 | -79.5183 | 2000-01-01 | 2001-12-31 | 731 | 45.45% |
| 60410 | Toronto | 43.7479 | -79.2741 | 2002-01-01 | 2024-12-31 | 8766 | 5.31% |
| 60413 | Toronto | 43.6485 | -79.5914 | 2002-01-01 | 2010-12-31 | 2922 | 6.40% |
| 60415 | Mississauga | 43.5686 | -79.6106 | 2000-01-01 | 2004-12-31 | 1827 | 15.88% |
| 60421 | Toronto | 43.7816 | -79.4177 | 2000-01-01 | 2016-12-31 | 6210 | 2.55% |
| 60424 | Toronto | 43.6630 | -79.3881 | 2000-01-01 | 2002-12-31 | 1096 | 13.44% |
| 60428 | Brampton | 43.6987 | -79.7809 | 2000-01-01 | 2016-12-31 | 6210 | 4.67% |
| 60429 | Toronto | 43.6136 | -79.5075 | 2001-01-01 | 2012-12-31 | 3288 | 22.00% |
| 60430 | Toronto | 43.7094 | -79.5435 | 2000-01-01 | 2024-12-31 | 8767 | 5.84% |
| 60432 | Mississauga | 43.6158 | -79.6525 | 2004-01-01 | 2007-12-31 | 1461 | 9.63% |
| 60433 | Toronto | 43.6642 | -79.3872 | 2003-01-01 | 2019-12-31 | 6209 | 4.96% |
| 60434 | Mississauga | 43.5470 | -79.6587 | 2008-01-01 | 2024-12-31 | 6575 | 7.17% |
| 60435 | Toronto | 43.6108 | -79.5219 | 2010-01-01 | 2024-12-31 | 5844 | 10.19% |
| 60438 | Toronto | 43.7111 | -79.5434 | 2016-01-01 | 2024-12-31 | 3288 | 2.68% |
| 60439 | Toronto | 43.6590 | -79.3954 | 2019-01-01 | 2019-12-31 | 365 | 85.88% |
| 60440 | Toronto | 43.7804 | -79.4675 | 2017-01-01 | 2024-12-31 | 3287 | 12.23% |
| 60445 | Toronto | 43.6454 | -79.3891 | 2019-01-01 | 2024-12-31 | 2192 | 9.41% |
| 60450 | Brampton | 43.6696 | -79.7657 | 2016-01-01 | 2024-12-31 | 3653 | 20.54% |
| 60512 | Hamilton | 43.2578 | -79.8617 | 2000-01-01 | 2024-12-31 | 9497 | 5.52% |
| 60513 | Hamilton | 43.2294 | -79.8628 | 2000-01-01 | 2018-12-31 | 6940 | 3.12% |
| 60515 | Hamilton | 43.2574 | -79.9077 | 2010-01-01 | 2024-12-31 | 5844 | 13.54% |
| 60521 | Hamilton | 43.2413 | -79.8894 | 2019-01-01 | 2024-12-31 | 2557 | 15.05% |
| 60609 | Sudbury | 46.4757 | -80.9630 | 2004-01-01 | 2012-12-31 | 3288 | 6.83% |
| 60610 | Sudbury | 46.4919 | -81.0031 | 2013-01-01 | 2024-12-31 | 4383 | 0.99% |
| 60707 | Sault Ste. Marie | 46.5279 | -84.3543 | 2003-01-01 | 2003-12-31 | 365 | 53.47% |
| 60708 | Sault Ste. Marie | 46.5167 | -84.3833 | 2000-01-01 | 2001-12-31 | 731 | 15.92% |
| 60709 | Sault Ste. Marie | 46.5332 | -84.3099 | 2004-01-01 | 2024-12-31 | 8036 | 5.90% |
| 60807 | Thunder Bay | 48.3730 | -89.2916 | 2001-01-01 | 2024-12-31 | 1461 | 35.61% |
| 60809 | Thunder Bay | 48.3794 | -89.2902 | 2004-01-01 | 2024-12-31 | 7671 | 4.70% |
| 60903 | London | 43.0067 | -81.2064 | 2001-01-01 | 2012-12-31 | 4018 | 4.15% |
| 60904 | London | 42.9745 | -81.2009 | 2013-01-01 | 2024-12-31 | 4748 | 8.84% |
| 61004 | Sarnia | 42.9823 | -82.4051 | 2000-01-01 | 2015-12-31 | 5844 | 4.66% |
| 61007 | Sarnia | 42.9126 | -82.4168 | 2017-01-01 | 2024-12-31 | 3652 | 25.94% |
| 61009 | Sarnia | 42.9903 | -82.3953 | 2016-01-01 | 2024-12-31 | 3653 | 13.19% |
| 61104 | Peterborough | 44.3018 | -78.3464 | 2001-01-01 | 2024-12-31 | 9131 | 5.94% |
| 61201 | Cornwall | 45.0180 | -74.7353 | 2003-01-01 | 2024-12-31 | 9132 | 14.09% |
| 61302 | St. Catharines | 43.1601 | -79.2348 | 2000-01-01 | 2024-12-31 | 9497 | 10.10% |
| 61402 | Brantford | 43.1386 | -80.2926 | 2004-01-01 | 2024-12-31 | 8036 | 5.76% |
| 61501 | Kitchener | 43.4578 | -80.4722 | 2014-01-01 | 2014-12-31 | 365 | 0.37% |
| 61502 | Kitchener | 43.4438 | -80.5038 | 2000-01-01 | 2024-12-31 | 9863 | 10.61% |
| 61603 | Oakville | 43.4869 | -79.7023 | 2003-01-01 | 2024-12-31 | 8401 | 7.50% |
| 61701 | Oshawa | 43.8891 | -78.8500 | 2000-01-01 | 2008-12-31 | 2558 | 26.06% |
| 61702 | Oshawa | 43.9459 | -78.8949 | 2005-01-01 | 2017-12-31 | 4748 | 3.98% |
| 61703 | Oshawa | 43.9522 | -78.9125 | 2018-01-01 | 2024-12-31 | 2923 | 15.12% |
| 61802 | Guelph | 43.5516 | -80.2642 | 2000-01-01 | 2024-12-31 | 9497 | 7.94% |
| 62001 | North Bay | 46.3232 | -79.4493 | 2000-01-01 | 2024-12-31 | 9497 | 7.05% |
| 62201 | Merlin | 42.2441 | -82.2230 | 2003-01-01 | 2004-12-31 | 731 | 22.72% |
| 62501 | Tiverton | 44.3145 | -81.5497 | 2000-01-01 | 2024-12-31 | 9497 | 10.33% |
| 62601 | Simcoe | 42.8568 | -80.2696 | 2000-01-01 | 2024-12-31 | 9132 | 6.08% |
| 63001 | Burlington | 43.3146 | -79.8028 | 2001-01-01 | 2023-12-31 | 8765 | 6.60% |
| 63301 | Dorset | 45.2243 | -78.9329 | 2000-01-01 | 2023-12-31 | 8766 | 6.70% |
| 63701 | Grand Bend | 43.3332 | -81.7428 | 2003-01-01 | 2023-12-31 | 8035 | 8.19% |
| 65001 | Barrie | 44.3823 | -79.7024 | 2001-01-01 | 2023-12-31 | 8765 | 9.54% |
| 65101 | Newmarket | 44.0443 | -79.4832 | 2001-01-01 | 2023-12-31 | 8765 | 7.19% |
| 65201 | Parry Sound | 45.3379 | -80.0382 | 2003-01-01 | 2023-12-31 | 8035 | 6.85% |
| 65301 | Port Stanley | 42.6721 | -81.1629 | 2002-01-01 | 2023-12-31 | 8400 | 8.63% |
| 65401 | Belleville | 44.1505 | -77.3955 | 2002-01-01 | 2023-12-31 | 8400 | 8.74% |
| 65601 | Essex | 42.1600 | -82.8333 | 2005-01-01 | 2008-12-31 | 1461 | 5.00% |
| 65701 | Morrisburg | 44.8998 | -75.1899 | 2005-01-01 | 2014-12-31 | 3652 | 1.15% |
| 65801 | Chatham | 42.4037 | -82.2083 | 2005-01-01 | 2023-12-31 | 7304 | 6.89% |
| 66201 | Petawawa | 45.9967 | -77.4412 | 2007-01-01 | 2022-12-31 | 5844 | 7.66% |
| 67001 | Milton | 43.5296 | -79.8624 | 2019-01-01 | 2023-12-31 | 2191 | 18.01% |
