---
source: archive/seagate/Documents/23. Data Completeness/CLEAR2_Data_Completeness_Continental.docx
aliases: [archive/seagate/Documents/23. Data Completeness/CLEAR2_Data_Completeness_Continental.pdf]
sha256: 6923258307ab02e3e4c0b6ac92086b8992e146065095d0414af8a811ebefdb2e
converted: 2026-10-24
converter: markitdown
status: current
kind: mirror
---

**Data Completeness: Canada, Alaska and the Lower 48**

**What we have for a continental CLEAR network, fire seasons 2021–2026**

*Hugo Bui & Ryan Zander · University of Toronto Schools · October 2026*

|  |
| --- |
| **Summary**  Across the 16 datasets CLEAR uses, we have on average **87%** of what a continental network needs (May–September 2021–2026, on the 6,418 CLEAR grid cells). **11 datasets are complete** for the whole continent.  **By area:** Canada 89%, the lower 48 87%, Alaska 86%. The weather, satellite, fire and smoke-forecast data are now complete or nearly complete everywhere; the remaining gaps are PurpleAir, FireWork 2026, CWFIS 2026 and CAMS (still downloading).  **Biggest gaps:** PurpleAir (6% of sensor-seasons), FireWork (83%) and CWFIS 2026 (83%). Only CWFIS is free to download; PurpleAir and FireWork need requests.  **New (21 October 2026).** **CAMS** global smoke forecasts (ECMWF) were added: 21% of the fire-season days are downloaded so far (the download runs two requests at a time and should finish in about 1–1½ weeks). **FireWork was re-counted:** from 11 June 2024 ECCC merged RAQDPS-FW into the regular RAQDPS forecast, which now includes wildfire smoke, so 2024 and 2025 are complete and only the 2026 season is missing (83%, up from 71%). **Ground monitors:** BC, Alberta, Saskatchewan and New Brunswick provincial data and the 2026 US data submitted to EPA (AQS Data API) were added; AirNow was checked against validated data (r = 0.99–1.00). The year-by-year timeline 2018–2026 and the status of the 2025 validation and 2026 test data are in two new documents in this folder: CLEAR2\_Data\_Timeline\_2018-2026 and CLEAR2\_Validation\_and\_Test\_Data\_2025-2026.  **New (18 October 2026): two more datasets.** **BlueSky Canada** smoke forecasts from UBC (0.1° grid, 51 hours ahead, four runs a day): 97% of the fire-season runs are archived (3,556 of 3,672), covering the continent from 32°N to 70°N and 160°W to 52°W. **ERA5 humidity** (2 m temperature and dewpoint, giving relative humidity) is complete (100%) for every grid cell.  **New (15 October 2026): ERA5-Land wind (0.1°) is complete (100%, up from 47%).** The north box (62–83.5°N) and the west box (24.5–62°N, 179–105°W) finished, so every land cell has ERA5-Land wind for May–September 2021–2026. ERA5-Land covers land and lakes, including the Great Lakes; only the ocean has no values.  **New (14 October 2026): ERA5 wind is now complete (100%, up from 82%).** The western download (Alaska, Yukon, BC, the Northwest Territories and the Pacific states) finished, so every grid cell has raw ERA5 files for every month of 2021–2025 and May–September 2026. With it, Alaska rose from 70% to 79% overall (and to 86% with ERA5-Land). **The 48 h HRRR / RAP smoke forecasts are also complete (100%, up from 80%):** the raw HRRR forecast files (hours 2–48) are on disk for all 918 fire-season days, for the whole HRRR domain including the western US.  **Raw HRRR smoke data:** the 1-hour HRRR smoke grids are complete and raw for 2021–2026, and the raw files for forecast hours 2–48 are complete for every fire-season day (918 days, 262 GB, on HDD and SPCX). Keeping the other months and HRRR-Alaska raw as well would need several hundred GB more (a larger drive). |

# **1. How completeness is measured**

* **Area:** every CLEAR Standard Grid (CSG-1) cell in Canada (3,377), Alaska (560) and the lower 48 (2,466): about 55 km tall, narrower in the north.
* **Time:** the six fire seasons, May 1 – September 30, 2021–2026. Each season counts equally.
* **Completeness:** the share of cell-seasons we have. Exceptions: PurpleAir counts sensor-seasons (one sensor for one season), FireWork and NOAA’s air-quality forecast count forecast days, and BlueSky Canada counts forecast runs (four a day). Regional products are measured inside the area they cover: HRRR 1-hour grids in the HRRR domain, CWFIS in Canada.
* **Raw data on disk:** a dataset counts as present if its raw files are on disk, even if it has not been turned into grid-cell values yet (for example ERA5 for the cells that have raw files but no cell values yet, section 3).

# **2. Completeness of every dataset**

![Completeness of every dataset](data:image/png;base64...)

*Share of each dataset we have for Canada, Alaska and the lower 48, fire seasons 2021–2026.*

| **Dataset** | **All** | **Canada** | **Alaska** | **Lower 48** | **What is missing** |
| --- | --- | --- | --- | --- | --- |
| **Government monitors (Canada + US)** | **100%** | 100% | 100% | 100% | nothing |
| **NOAA HRRR-Smoke 1 h (raw grids)** | **100%** | 100% | n/a | 100% | nothing |
| **NOAA HRRR / RAP smoke forecasts (48 h)** | **100%** | 100% | 100% | 100% | nothing (raw HRRR hours 2-48 for all 918 fire-season days; 1270 western cells not yet reduced to cell values) |
| **ERA5 wind (Copernicus)** | **100%** | 100% | 100% | 100% | nothing (raw files for every cell; 1,566 cells not yet reduced to cell values) |
| **ERA5-Land wind, 0.1° (Copernicus)** | **100%** | 100% | 100% | 100% | nothing (land and lakes; boxes 25-62°N 105-52°W, north 62-83.5°N, west 24.5-62°N 179-105°W) |
| **ERA5 humidity, 2 m (Copernicus)** | **100%** | 100% | 100% | 100% | nothing |
| **Sentinel-5P aerosol index** | **100%** | 100% | 100% | 100% | nothing |
| **Sentinel-5P smoke-layer height** | **100%** | 100% | 100% | 100% | nothing |
| **NASA FIRMS active fires** | **100%** | 100% | 100% | 100% | nothing |
| **NOAA HMS smoke outlines** | **100%** | 100% | 100% | 100% | nothing |
| **NOAA air-quality forecast (AQM)** | **100%** | 100% | 100% | 99% | 6 runs NOAA never published (each covered by the previous day's run); Alaska domain only exists from May 2024 |
| **BlueSky Canada smoke forecast (UBC)** | **97%** | 97% | 97% | 97% | 116 of 3,672 runs not in UBC's archive (mostly 06/18 UTC runs, May and July 2026); outside its domain: western Alaska, north of 70°N, south of 32°N |
| **FireWork smoke forecast (ECCC)** | **83%** | 83% | 83% | 83% | 153 fire-season days (2026 season, requested from ECCC); 12 h forecasts only |
| **CWFIS fire hotspots and perimeters (NRCan)** | **83%** | 83% | n/a | n/a | 2026 season (not yet posted by NRCan) |
| **CAMS global smoke forecast (ECMWF)** | **21%** | 21% | 21% | 21% | 729 of 918 fire-season days still downloading (Oct 2026) |
| **PurpleAir sensors** | **6%** | 40% | 0% | 3% | 134,793 sensor-seasons |

n/a: the product does not cover that area (HRRR 1-hour grids do not cover Alaska; CWFIS is Canadian). HRRR-Alaska covers Alaska in the 48 h forecast row.

# **3. Completeness by area**

![Completeness by area](data:image/png;base64...)

*The same datasets split into Canada, Alaska and the lower 48.*

* **Canada (89%):** satellite, smoke-forecast and government data are complete or nearly so. The gaps are PurpleAir outside Alberta, Saskatchewan, Manitoba, Ontario and Québec, and CWFIS 2026. ERA5 and ERA5-Land are now complete, including BC, Yukon and the North.
* **Lower 48 (87%):** the gap is PurpleAir everywhere except the states we have north of 41.5°N. ERA5, ERA5-Land and the 48 h HRRR forecasts are now complete, including the West.
* **Alaska (86%):** smoke forecasts (HRRR-Alaska, RAP-Smoke, NOAA AQM), government monitors, HMS, FIRMS, Sentinel-5P, ERA5 and ERA5-Land are complete; PurpleAir has nothing yet.

## **ERA5 wind: complete for the whole continent**

ERA5 (0.25°, hourly wind at 10 m and four heights, boundary-layer height and rain) now comes from three downloads that together cover every one of the 6,418 grid cells. All raw files are kept so cell values can be recomputed if the grid changes:

| **Download** | **Area** | **Raw files** | **Size** | **Where** |
| --- | --- | --- | --- | --- |
| **1,500 km grid** | 1,500 km around Toronto (2021–2025; 2026 comes from the extended box) | 120 | 21 GB | HDD |
| **Extended box** | 24.5–83.5°N, 121.5–52.5°W | 130 | 67 GB | HDD |
| **Western box (new)** | 35.5–77.5°N, 179–120°W: Alaska, Yukon, BC, NWT, Pacific states | 130 | 41 GB | SPCX and HDD |

*ERA5 downloads. Each has every month of 2021–2025 plus May–September 2026 (65 months; upper-level and surface files for each month).*

**Is any ERA5 data missing?** No raw data is missing: every cell has every month. What remains is processing only. 4,852 of the 6,418 cells have been turned into hourly cell values (Cleaned Data/era5\_cells, \_extended, \_rest2000 and the new \_west with 1,309 cells). The other 1,566 cells (983 in the lower 48 and 583 in Canada, between about 94°W and 121°W) have raw files in the extended download but no cell values yet. Making them takes about 20 minutes when they are needed.

# **4. Where the gaps are**

![Coverage maps](data:image/png;base64...)

*How many of the six fire seasons we have in each grid cell, for the gridded datasets.*

The maps show that the gridded datasets now cover the whole continent. FireWork is the same everywhere because its gaps are whole days, not areas.

# **5. PurpleAir**

![PurpleAir sensor-seasons](data:image/png;base64...)

*PurpleAir sensor-seasons that exist and that we have, May–September 2021–2026.*

We have **7,826 of 142,619 PurpleAir sensor-seasons (6%)** across the continent: 40% in Canada, 3% in the lower 48 and none in Alaska. California alone has about 58,700 of the missing sensor-seasons. The PurpleAir request asks for 312 million points for the 2,000 km Toronto network (Step 1); the rest of the continent (Step 2) would need about 716 million points expected (1,023 million at most), or about 78 million with up to 3 sensors per grid cell.

# **6. Raw NOAA HRRR smoke data**

Raw files matter because the grid may change (for example to 0.1°): cell values can be recomputed from raw files, but not from other cell values. What we have:

| **HRRR product** | **Raw files kept?** | **Coverage** | **Space for all raw files** |
| --- | --- | --- | --- |
| **HRRR-Smoke forecast hour 1 (every hourly run)** | Yes | Whole HRRR domain (lower 48 + southern Canada), every day 2021–2026, 24 runs a day | done (80 GB) |
| **HRRR-Smoke forecast hours 2–48 (00 and 12 UTC runs)** | Yes, every fire-season day (918 days) | Whole HRRR domain (lower 48 + southern Canada), May–September 2021–2026 | done for fire seasons (262 GB); other months about 310 GB more |
| **HRRR-Alaska (forecast hour 1 of 8 runs, hours 2–48 of 2 runs)** | No | Cell values for 947 cells in Alaska, Yukon, NWT and northern BC, 2021–2026 | about 170 GB (fire seasons: about 70 GB) |
| **RAP-Smoke (northern Canada and Alaska)** | No | Cell values for 3,310 cells, 2021–2026 | not measured |
| **NOAA air-quality forecast (AQM)** | No | Cell values, lower 48 + southern Canada, Alaska from 2024 | not measured |

Raw HRRR forecast files are in RAW Data/NOAA/HRRR\_smoke\_f02-48\_raw/ on HDD and SPCX, 2021-05-01 to 2026-09-30 (every fire-season day). Cell values have been made for the 2,000 km network; the western cells can be made from these raw files when needed.

**To keep all raw HRRR smoke data** (forecast hours 2–48 for the lower 48 and Alaska, every season), we need about **700 GB** more. A 4 TB external drive would hold it with room for future backups.

# **7. What to download next for the continent**

| **#** | **Download** | **Fills** | **Cost** |
| --- | --- | --- | --- |
| ✓ | NASA FIRMS for the West, the North and Alaska (2021–2026) | FIRMS to 100% | **done** (16.0 million detections) |
| ✓ | Sentinel-5P aerosol index and smoke height for Alaska | Sentinel-5P to 100% | **done** |
| ✓ | ERA5 for the western box (Alaska, Yukon, BC, Pacific coast) | ERA5 to 100% | **done** (130 files, 41 GB, on SPCX and HDD) |
| ✓ | ERA5-Land 0.1° for the rest of the continent (fire seasons): north box (62–83.5°N) and west box (24.5–62°N, 179–105°W) | ERA5-Land to 100% | **done** (60 files, about 18 GB, on SPCX, HDD and the CLEAR 2.0 drive) |
| ✓ | HRRR forecast hours 2–48 for the western lower 48 | 48 h forecasts to 100% | **done** (raw files for all fire-season days) |
| ✓ | ERA5 humidity (2 m temperature and dewpoint), Canada, Alaska and the lower 48 | new dataset, 100% | **done** (65 files, 16 GB) |
| ✓ | BlueSky Canada smoke forecasts (UBC archive), four runs a day, May–September 2021–2026 | new dataset, 97% of runs | **done** (3,556 files, 278 GB; 116 runs not archived by UBC) |
| 6 | CWFIS 2026, once NRCan posts it | CWFIS to 100% | free; minutes |
| 7 | FireWork 2026 season (and forecast hours 13–72) | FireWork | request to ECCC |
| 8 | PurpleAir for the rest of the continent | PurpleAir | API points from PurpleAir (Step 2) |

Steps 1–5 are done. Step 6 (CWFIS 2026) is free once NRCan posts it; FireWork and PurpleAir need requests.

# **8. Method**

* Datasets and areas were checked on disk on 11 October 2026 (updated 14–18 October 2026: ERA5 western download, raw HRRR 48 h files counted, ERA5-Land north and west boxes, ERA5 humidity, BlueSky Canada; 21 October 2026: CAMS, FireWork re-counted) by scripts/data\_completeness\_continental.py; the tables are in Cleaned Data/analysis/data\_completeness\_continental/.
* FireWork’s area is its own grid (rotated 0.09°, 16–80°N), read from one archived file; its completeness is the share of fire-season days with a wildfire-smoke run (RAQDPS-FW or WFSP, or the regular RAQDPS from 11 June 2024, when it began to include wildfire smoke). The archive holds the first 12 forecast hours.
* PurpleAir sensor-seasons come from the PurpleAir sensors list of 10 October 2026: a sensor counts for a season if it was created before 1 October and last reported after 1 May.
* ERA5-Land covers land and lakes but not the ocean, so only cells with land are counted for it.
* BlueSky Canada is measured inside its own domain (32–70°N, 160–52°W, 84% of the grid cells), like FireWork; its completeness is the share of the four daily runs, May–September, that UBC archived.

Scripts: scripts/data\_completeness\_continental.py (analysis and figures), scripts/docs/make\_data\_completeness\_doc.js (this document).
