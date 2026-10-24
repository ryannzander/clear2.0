---
source: archive/seagate/Documents/15. The Grid Approach/The_Grid_Methodology.docx
aliases: [archive/seagate/Documents/15. The Grid Approach/The_Grid_Methodology.pdf]
sha256: c7ac53d3ee474c16734e6ddd4ca6d06637f3cdb8a13b5412f733133b27df9796
converted: 2026-10-24
converter: markitdown
status: current
kind: mirror
---

**The Grid Methodology**

**C.L.E.A.R. 2.0: building a 0.5° PM2.5 grid around Toronto from ground monitors and virtual PM2.5**

*Hugo Bui & Ryan Zander · University of Toronto Schools · October 2026*

This document sets out, step by step, how the C.L.E.A.R. 2.0 PM2.5 grid is built: the grid itself, how its cells are filled with ground measurements, how many cells are empty, and how those empty cells will be filled with **virtual PM2.5** from satellite and modelled data. It compares each virtual PM2.5 source: how it determines PM2.5, whether it represents the ground or the air higher up, and the issues that matter for C.L.E.A.R. It is a methodology document and contains **no results from AI model simulations**.

|  |
| --- |
| **The grid in numbers**   * **1,416 cells** of 0.5° × 0.5° within 1,000 km of Toronto: **501 in Canada**, **682 in the United States** and **233 over lakes and ocean**. * **510 cells (36%)** contain at least one ground monitor: **287** with a government monitor and **223** with PurpleAir sensors only. * **906 cells (64%) are empty** and need virtual PM2.5: 673 on land and 233 over water. * Virtual PM2.5 will come mainly from **ECCC FireWork** and **NOAA HRRR-Smoke** (modelled ground-level PM2.5), checked against **NOAA HMS** smoke maps and the **Sentinel-5P TROPOMI** aerosol index (satellite observations of the whole atmospheric column). * For scale, the same grid would have about **6,700 cells over Canada** and about **4,400 over the United States** (3,263 in the lower 48 states and 1,120 in Alaska). |

# **Step 1. Create the grid**

* **Centre:** Toronto (43.65°N, 79.38°W).
* **Radius:** 1,000 km, reaching from North Carolina (34.7°N) to James Bay (52.6°N) and from eastern Minnesota to the Gulf of St. Lawrence.
* **Cells:** squares of 0.5° latitude × 0.5° longitude. Every cell whose centre lies within 1,000 km is included, plus two edge cells just beyond 1,000 km that contain a monitor: **1,416 cells**.
* **Cell index:** row = floor(latitude ÷ 0.5), column = floor(longitude ÷ 0.5). Every monitor belongs to exactly one cell.

| **Latitude** | **North–south** | **West–east** | **Area of one cell** |
| --- | --- | --- | --- |
| 35°N | 55.6 km | 45.6 km | 2,540 km² |
| **43.65°N (Toronto)** | **55.6 km** | **40.3 km** | **2,240 km²** |
| 50°N | 55.6 km | 35.8 km | 1,990 km² |

A 0.5° cell is always 55.6 km from south to north but narrows from west to east toward the pole, because lines of longitude converge.

# **Step 2. Count the cells in Canada and the United States**

## **Within the 1,000 km grid**

| **Location of the cell centre** | **Cells** | **Notes** |
| --- | --- | --- |
| **Canada** | **501** | Ontario 247, Québec 245, New Brunswick 9 |
| **United States** | **682** | 24 states and the District of Columbia |
| **Lakes and ocean** | 233 | Great Lakes, James Bay, Atlantic Ocean |
| **Total** | **1,416** |  |

A cell is assigned to Canada, the United States or water by the location of its centre; cells on the shore that contain a monitor are assigned to the nearest country.

## **For the whole of Canada and the United States**

| **Region** | **Land cells (0.5°)** | **Comparison** |
| --- | --- | --- |
| **Canada, all** | 6,733 | About 13 times the Canadian part of the Toronto grid |
| **Canada, south of 60°N** | 3,162 | Where most people and monitors are |
| **United States, lower 48 states** | 3,263 |  |
| **Alaska** | 1,120 |  |
| **Canada + lower-48 United States** | **about 10,000** | About 7 times the Toronto grid |
| **Canada + all of the United States** | **about 11,100** |  |

Land cells only, counted from the centre of each cell with Natural Earth province and state boundaries.

# **Step 3. Fill the cells with PM2.5 ground measurements**

![Grid filled with ground measurements](data:image/png;base64...)

*The grid around Toronto filled with PM2.5 ground measurements. Dark blue: government monitor; purple: PurpleAir only; white: no sensor on land; light blue: no sensor over water.*

Every hour, all monitors reporting in a cell are combined into one PM2.5 value for that cell:

| **Cell type** | **Canada** | **United States** | **Water** | **Total (share)** |
| --- | --- | --- | --- | --- |
| **Government monitor (Ontario, Québec, NAPS, US EPA)** | 57 | 230 | 0 | **287 (20%)** |
| **PurpleAir sensor(s) only** | 79 | 144 | 0 | **223 (16%)** |
| **No sensor** | 365 | 308 | 233 | **906 (64%)** |
| **Total** | 501 | 682 | 233 | **1,416** |

* **Monitors used:** the 1,931 monitors within 1,000 km active since 2018: Ontario provincial 44, Québec provincial 42, NAPS 15, US EPA 441 (419 federal reference or equivalent method and 22 continuous non-FEM monitors) and PurpleAir 1,389.
* **Quality control:** missing-data flags and negative readings removed; PurpleAir corrected with the US EPA Barkjohn equation (from the raw CF-1 reading and the sensor’s humidity) and its faulty-sensor flag applied.
* **One value per cell:** the average of the readings that pass quality control. The government average, the PurpleAir average, the number of each and the spread are kept as extra information.
* **Monitor types differ in accuracy:** government monitors are the reference; PurpleAir correlates at about r = 0.8 with nearby government monitors; EPA continuous (non-FEM) monitors can read low in smoke. Whether to weight government monitors more heavily will be tested.
* **Why average:** monitors cluster in cities (one cell near Boston has 79); averaging gives each cell one value, so a city cannot outweigh the rest of the region simply because it has more monitors.
* **Canada is the gap:** only 57 of the 501 Canadian cells (11%) have a government monitor, compared with 230 of 682 US cells (34%). PurpleAir adds 79 Canadian cells, many of them north of 47°N toward the fire zones.

# **Step 4. Identify the empty cells that need virtual PM2.5**

| **Empty cells** | **Cells** | **Share of the grid** |
| --- | --- | --- |
| **On land in Canada (mostly northern Ontario and Québec forest)** | 365 | 26% |
| **On land in the United States (mostly rural counties)** | 308 | 22% |
| **Over lakes and ocean** | 233 | 16% |
| **All empty cells needing virtual PM2.5** | **906** | **64%** |

**Nearly two-thirds of the grid has no ground measurement.** In Canada the share is higher still: 365 of 501 cells (73%) are empty. The empty cells include the northern forest where wildfire smoke usually starts and the lakes it crosses on its way to Toronto, so filling them is essential for tracking smoke across the grid.

# **Step 5. Fill the empty cells with virtual PM2.5**

A **virtual PM2.5** value is an estimate of ground-level PM2.5 for a cell without monitors, built every hour from modelled and satellite smoke data. The procedure:

| **#** | **Stage** | **What is done** |
| --- | --- | --- |
| 1 | **Sample each source over the cell** | Average the model PM2.5 (FireWork, HRRR-Smoke) over all its grid points inside the cell for that hour; take the HMS smoke density covering the cell; average the TROPOMI aerosol index over the cell (previous day) |
| 2 | **Learn the relationship in measured cells** | In the 510 cells that have monitors, compare the model and satellite values with the measured average, and fit a correction that turns them into ground-level PM2.5, also using boundary layer height, humidity, season and hour |
| 3 | **Apply it to the empty cells** | The correction is applied to each of the 906 empty cells |
| 4 | **Blend at coverage edges** | Near the northern edge of HRRR-Smoke (about 50–52°N), its weight tapers gradually so that values do not jump where its coverage ends; north of it, FireWork and the satellites take over |
| 5 | **Flag and give an uncertainty** | Each value is marked “virtual”, with the sources that were available and an uncertainty measured by hiding measured cells and estimating them as if they were empty |

![Data source by cell](data:image/png;base64...)

*Where each cell’s value comes from: measured cells (blue, purple) and virtual cells from FireWork + HRRR-Smoke + satellite smoke (yellow, 845 cells) or FireWork + satellite smoke only, north of the HRRR-Smoke domain (red, 61 cells).*

| **Virtual-cell coverage** | **Cells** | **Note** |
| --- | --- | --- |
| **FireWork + HRRR-Smoke + satellite smoke** | 845 | All US and southern Canadian empty cells |
| **FireWork + satellite smoke only** | 61 | North of the HRRR-Smoke domain (northern Ontario and Québec) |

# **Step 6. Compare the virtual PM2.5 data sources**

![Ground versus column](data:image/png;base64...)

*Ground monitors and air-quality models give PM2.5 at ground level; satellites see smoke in the whole atmospheric column and cannot tell, on their own, whether it is near the ground or several kilometres up.*

## **Sources already in the project**

| **Source** | **How it determines PM2.5** | **Ground or column** | **Resolution and coverage** | **Issues for C.L.E.A.R.** |
| --- | --- | --- | --- | --- |
| **ECCC FireWork (RAQDPS-FW)** | Computer model: Environment Canada’s weather and air-chemistry model (GEM-MACH) moves pollution, including smoke from fires detected by satellite, and calculates PM2.5 concentrations | **Ground** | About 10 km grid, hourly forecasts; all of Canada and the US; project archive 2018–2025 | A forecast, not a measurement; fire emissions and smoke-plume height are uncertain; the model grid changed twice between 2018 and 2025 |
| **NOAA HRRR-Smoke** | Computer model: NOAA’s rapid-refresh weather model carries smoke emitted by fires detected by satellite (fire radiative power) with a plume-rise calculation | **Ground and column** | 3 km grid, hourly; US and southern Canada only (to about 52°N in Ontario, 49–50°N in eastern Québec); 2021–2025 | Smoke only, not total PM2.5 (no traffic or industry); no data for the far north; starts in 2021 |
| **NOAA HMS smoke polygons** | Satellite analysts draw the outline of smoke visible in satellite images and grade it light, medium or heavy | **Whole column** | Shapes of any size, daily (daytime); all of North America; 2018–2025 | Not a PM2.5 value; cannot tell smoke aloft from smoke at the ground; drawn by people, once a day; gaps under cloud |
| **Sentinel-5P TROPOMI aerosol index** | A satellite instrument measures how much ultraviolet light is absorbed by particles such as smoke in the atmosphere | **Whole column** | About 5 km pixels, averaged to 0.25°; one early-afternoon pass per day; 34–70°N; July 2018–2025 | Not a PM2.5 value; most sensitive to smoke high up and weak for smoke near the ground; no data under cloud or at night |
| **CWFIS Fire M3 and NASA FIRMS** | Satellites detect the heat of active fires; perimeters mapped by fire agencies | **Fire location** | About 375 m to 1 km detections; daily; all of North America | Shows where smoke comes from, not PM2.5 |

## **Candidate sources to evaluate**

| **Source** | **How it determines PM2.5** | **Ground or column** | **Resolution and coverage** | **Issues for C.L.E.A.R.** |
| --- | --- | --- | --- | --- |
| **ECCC RDAQA (air-quality analysis)** | Combines Environment Canada’s model with monitor measurements to give a best estimate of surface PM2.5 | **Ground** | About 10 km, hourly; Canada and the US | Uses monitors, so it must not be tested on the same monitors; archive length to be checked |
| **NASA GEOS-CF** | NASA global atmospheric-composition model with satellite fire emissions | **Ground** | About 25 km, hourly; global | Coarser than a 0.5° cell; to be compared with FireWork |
| **NASA MERRA-2** | NASA reanalysis that adjusts a model to satellite aerosol measurements; PM2.5 calculated from its particle types | **Ground** | About 50 km, hourly; global; since 1980 | Coarse; smoke peaks smoothed; useful for older years |
| **Copernicus CAMS** | European global model and reanalysis of atmospheric composition, adjusted to satellite data | **Ground** | About 40–80 km, hourly to 3-hourly; global | Coarse; useful as an independent comparison |
| **GOES-16/18 aerosol optical depth** | Geostationary satellites measure how much sunlight particles block, every 10 minutes in daylight | **Whole column** | About 2 km; North and South America | Column, daytime only; needs conversion to ground PM2.5; large data volume |
| **NASA MODIS / VIIRS aerosol optical depth** | Polar-orbiting satellites measure how much sunlight particles block, once or twice a day | **Whole column** | About 1–10 km; global | Column; once or twice a day; gaps under cloud |

## **How the comparison will be carried out**

| **Question** | **Method** |
| --- | --- |
| **What does each source represent?** | Document whether it is a model, an analysis or a satellite measurement; ground or column; time and space resolution; how fire emissions are included; how it is produced |
| **How well do the sources agree with each other?** | In every cell and hour where two or more sources exist: correlation and average difference, for smoke and non-smoke periods, by season and by latitude band |
| **How well do they agree with ground monitors?** | In measured cells: correlation, bias, and how often each source detects PM2.5 ≥ 30 and ≥ 60 µg/m³ when the monitors do |
| **Where does each source fail?** | Map the differences to find regions (for example north of 50°N) and situations (thin smoke, smoke aloft) where it is unreliable |
| **How should the US–Canada transition be handled?** | Use the cells where both HRRR-Smoke and FireWork exist, near the HRRR-Smoke edge, to set the blending weights |

# **Issues relevant to C.L.E.A.R.**

| **Issue** | **Why it matters and how it is handled** |
| --- | --- |
| **Ground versus column** | C.L.E.A.R. alerts on ground-level PM2.5. Satellites see smoke in the whole column, which can pass high over Toronto without affecting the ground. Satellite data are therefore used to show where smoke is, while ground-level values come from monitors and models; boundary layer height helps decide whether smoke aloft will mix down |
| **Models are forecasts, not measurements** | FireWork and HRRR-Smoke estimate PM2.5 from fire detections and weather. Their errors depend on fire emissions and plume height, so they are corrected against measured cells and flagged as virtual |
| **Smoke-only versus total PM2.5** | HRRR-Smoke gives smoke only; FireWork and ground monitors give total PM2.5. The correction in Step 5 accounts for the difference |
| **Northern coverage** | HRRR-Smoke stops at about 50–52°N, and Canada has few monitors (73% of Canadian cells are empty). FireWork is the only model covering the far north, where smoke plumes start, so it is essential |
| **Time coverage** | HRRR-Smoke starts in 2021 and TROPOMI in July 2018; models must handle years when a source is missing (data-present flags) |
| **Once-a-day satellites** | HMS and TROPOMI give one picture per day, while the grid is hourly; satellite values are carried from the previous day and never from the future |
| **Changing model versions** | FireWork’s grid and version changed between 2018 and 2025; each period is mapped to the 0.5° cells separately |
| **Monitor quality** | Government, PurpleAir and EPA continuous monitors differ in accuracy; monitor types are kept as extra information and weighting is tested |
| **Independence when testing** | Analyses such as RDAQA already include monitor data; when testing virtual values, the monitors being predicted must not be used to make them |
| **Live operation** | For live alerts, each source must be available in near real time; ERA5 winds and some archives are delayed, so forecast and near-real-time products are needed |

# **Summary of the methodology**

| **Step** | **Action** | **Result** |
| --- | --- | --- |
| 1 | Create the 0.5° grid within 1,000 km of Toronto | 1,416 cells |
| 2 | Count cells by country | 501 Canada, 682 United States, 233 water; about 10,000 cells for Canada + the lower 48 |
| 3 | Fill cells with ground measurements | 287 government, 223 PurpleAir-only cells (510, 36%) |
| 4 | Identify empty cells | 906 cells (64%) need virtual PM2.5 |
| 5 | Fill empty cells with virtual PM2.5 | FireWork + HRRR-Smoke + satellite smoke, corrected against measured cells, flagged and with uncertainty |
| 6 | Compare the virtual sources | Ground versus column, how each determines PM2.5, agreement with each other and with monitors |
