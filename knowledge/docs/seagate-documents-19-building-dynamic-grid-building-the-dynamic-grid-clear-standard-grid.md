---
source: archive/seagate/Documents/19. Building Dynamic Grid/Building_the_Dynamic_Grid_CLEAR_Standard_Grid.docx
aliases: []
sha256: 5fe4e620b42d2ca2534b4da48c22ac2a68b2524203eb82bcc749bb9a51d003fc
converted: 2026-10-24
converter: markitdown
status: current
kind: mirror
---

**C.L.E.A.R. 2.0**

**Building the Dynamic Grid: the CLEAR Standard Grid (CSG-1)**

*Hugo Bui & Ryan Zander · University of Toronto Schools · October 2026*

C.L.E.A.R. needs one standard grid for Canada, Alaska and the lower 48 states that every data set and future alert system can share. This document (1) measures the **effective radius** of a ground PM2.5 monitoring station, the distance over which its hourly reading still represents the air around it, from 1,074 government monitors across North America; (2) uses that radius to size the cells, starting with square cells at the equator and widening them east–west going north, so every cell keeps the same effective radius; and (3) sets a **naming system** based on latitude and longitude. No model results are used; the analysis uses measured hourly PM2.5 only.

|  |
| --- |
| **Main results**   * **Effective radius of a ground PM2.5 monitor: about 45–50 km** in eastern North America and Canada (east of 100°W 49 km; Ontario/Québec 50 km), and 55–63 km in the smoke season (June–August). In the mountainous West it is only **about 16 km**. * **Design value: 45 km.** Every point of a cell must lie within 45 km of the cell centre. * **Rows are 0.5° of latitude everywhere** (55.7 km). At the equator the cell is a 0.5° × 0.5° square. Going north, the east–west width steps up from 0.5° to 0.75° (from 32°N), 1.0° (50.5°N), 1.25° (59.5°N), 1.5° (65°N), 2° (71.5°N), 2.5° (75.5°N), 3° (78°N), 3.75° (80°N) and 4.5–5° (82°N), so cells stay 47–71 km wide and the centre-to-corner distance never exceeds 45 km. * **The grid has 6,418 cells**: Canada 3,377, Alaska 560, lower 48 states 2,466 and the Great Lakes 15. A uniform 0.5° grid would need **12,834** cells. Canada and Alaska need 58–59% fewer cells, and the share of cells with a ground monitor rises (lower 48: 20% → 26%; Ontario 5.5% → 8.8%; Québec 3.2% → 5.3%). * **Cell name = south-west corner**, e.g. **N4350W07950** (Toronto): hemisphere + latitude × 100 + hemisphere + longitude × 100. Names are always 11 characters, need no rounding, and any point is placed in its cell with two FLOOR operations. |

# **1. The effective radius of a ground PM2.5 monitor**

## **1.1 Data**

| **Monitors (hourly PM2.5, 2021–2025)** | **Monitors** | **Notes** |
| --- | --- | --- |
| **US EPA reference monitors (FRM/FEM, parameter 88101)** | 981 | All states incl. Alaska; Hawaii, Puerto Rico and Mexico excluded |
| **Ontario provincial** | 40 | Most are also NAPS sites (one ID per site) |
| **Québec provincial** | 43 |  |
| **NAPS (sites with no provincial ID)** | 14 | Montréal network, Toronto, Sarnia, Simcoe |
| **Reference monitors with at least one usable pair** | **1,074** | 19,209 monitor pairs up to 250 km apart with ≥ 4,000 hours of overlapping data |
| **US EPA non-reference continuous (88502)** | 185 | Sensitivity test only (Alaska) |

Only monitors with at least 4,000 valid hours since 2021 are used. Readings above 1,000 µg/m³ are removed. PurpleAir sensors are not used: the radius is defined for government monitoring stations.

## **1.2 Method**

For every pair of monitors, the hourly PM2.5 readings were correlated (Pearson r) and plotted against the distance between the two monitors. The **effective radius** is the distance at which a monitor’s readings stop being a good stand-in for the air at another location.

**Why a fixed threshold does not work.** Two monitors only a few kilometres apart correlate at just 0.76–0.85 hour to hour (Figure 1a). This ceiling, called the “nugget”, comes from instrument noise (hourly reference monitors are noisy) and from very local sources near each monitor, not from distance. Because US and Canadian monitors have different nuggets, a fixed threshold such as r = 0.80 mostly measures instrument quality: it gives 8 km for US monitors but 41 km for Ontario/Québec monitors (Table 1, last column).

**Noise-corrected correlation.** The correlation at each distance is therefore divided by the correlation of monitors 0–10 km apart: **ρ(d) = r(d) ÷ r(0–10 km)**. ρ starts at 1 and falls as the air at the two places becomes different. The **effective radius is the distance at which ρ falls to 0.90**, meaning the monitor still shares at least 90% of the correlation that two side-by-side monitors would have (about 81% of the explained hourly variation, ρ² ≈ 0.81).

* **Distance bins** of 0–10, 10–20, …, 200–250 km; the median correlation in each bin (bins with fewer than 5 pairs skipped); linear interpolation between bins.
* **Uncertainty:** 300 bootstrap resamples of the monitors give a 90% interval.
* **Check:** an exponential model r(d) = r₀·e^(−d/L), the standard correlation model in spatial statistics, fitted to the same medians gives the regional correlation length L and a second radius estimate, L·ln(1/0.9).
* **Groups:** United States, Canada, east and west of 100°W, latitude bands, all months and June–August.

## **1.3 Results**

![Correlation vs distance](data:image/png;base64...)

*Figure 1. (a) Median hourly correlation between two government monitors versus distance. (b) Noise-corrected correlation ρ; the dots mark where ρ falls to 0.90 (the effective radius).*

| **Group (2021–2025)** | **Pairs** | **r at 0–10 km** | **Effective radius, all months (90% interval)** | **June–August** | **Exponential model radius (L, km)** | **Fixed r = 0.80 (for comparison)** |
| --- | --- | --- | --- | --- | --- | --- |
| **All reference monitors** | 19,209 | 0.83 | 26 km (15–49) | 31 km | 47 km (441) | 10 km |
| **United States** | 16,930 | 0.82 | 25 km (14–41) | 26 km | 46 km (433) | 8 km |
| **Canada (Ontario, Québec)** | 1,486 | 0.85 | **50 km (34–66)** | 63 km | 53 km (506) | 41 km |
| **East of 100°W** | 14,718 | 0.85 | **49 km (23–61)** | 55 km | 51 km (480) | 15 km |
| **West of 100°W** | 4,491 | 0.76 | **16 km (11–24)** | 16 km | 16 km (155) | – |
| **East, 24–33°N** | 841 | 0.80 | 15 km (11–41) | 23 km | 32 km | – |
| **East, 33–38°N** | 1,525 | 0.73 | 39 km (11–61) | 34 km | 37 km | 17 km |
| **East, 38–42°N** | 7,967 | 0.82 | 66 km (34–83) | 65 km | 55 km | 20 km |
| **East, 42–46°N** | 3,854 | 0.88 | 47 km (13–58) | 52 km | 52 km | 44 km |
| **East, 46–52°N** | 531 | 0.85 | 36 km (28–56) | 65 km | 56 km | 28 km |
| **West, 24–36°N** | 1,284 | 0.68 | 23 km (10–34) | 18 km | 8 km | – |
| **West, 36–42°N** | 2,582 | 0.81 | 14 km (10–22) | 17 km | 19 km | 7 km |
| **West, 42–50°N** | 622 | 0.73 | 26 km (10–105) | 32 km | 28 km | – |

Table 1. Effective radius = distance at which the noise-corrected correlation ρ falls to 0.90. “–”: the median correlation is below 0.80 even at 0–10 km. Latitude bands use the midpoint of each pair. Alaska has only 3 pairs of monitors with enough overlapping data, too few for its own estimate.

![Effective radius by region](data:image/png;base64...)

*Figure 2. Effective radius by region and latitude band (bars: all months with 90% interval; diamonds: June–August).*

* **East and Canada: about 45–50 km.** Monitors in eastern North America and in Ontario/Québec represent the air for about 50 km; in the smoke season, when PM2.5 is spread over wide areas, for 55–63 km. The exponential model gives the same answer (51–53 km).
* **West: about 16 km.** Mountains, valleys, temperature inversions and local wood smoke make PM2.5 vary over short distances. This is why the continent-wide and US-wide medians (25–26 km) are lower: they mix the two regimes.
* **Little consistent change with latitude in the East.** North of 33°N the radius is 36–66 km with overlapping intervals, and in summer it is largest in the north (65 km at 46–52°N). Only the humid south-east below 33°N is lower (15 km, wide interval). The radius in kilometres therefore does not shrink going north, so cells can keep the same size in kilometres and grow in degrees of longitude.
* **High Risk hours.** Two eastern monitors 40–50 km apart are both ≥ 60 µg/m³ in 44% of the hours when either is, against 52% for monitors 0–10 km apart; in the West this falls to 11%.
* **Daily averages vary over larger distances** (daily correlation 0.80 at about 110 km; coefficient of divergence 0.20 at about 150 km). C.L.E.A.R. issues hourly alerts, so the hourly radius is the one that matters.

## **1.4 Design value: 45 km**

| **Evidence** | **What it supports** |
| --- | --- |
| **Noise-corrected radius, East of 100°W / Ontario–Québec** | 49 km / 50 km; 45 km sits just below both, inside their 90% intervals |
| **Exponential model, all regions except the West** | 46–56 km |
| **Smoke season (June–August), East / Canada** | 55 km / 63 km: 45 km is conservative in the season that matters most for C.L.E.A.R. |
| **US EPA monitoring scales (40 CFR Part 58, Appendix D)** | An “urban scale” monitor represents 4–50 km; regional-scale monitors more. 45 km is at the top of the urban scale |
| **Earlier Ontario–Québec cell analysis** | r = 0.80 reached at 41 km (Ontario) and 32 km (Québec) with the uncorrected threshold |
| **Geometry** | A 0.5° × 0.5° square at the equator has a centre-to-corner distance of 39 km, inside 45 km |

**Limitation: the West.** West of 100°W a monitor represents only about 16 km, so a 45 km cell is larger than one monitor can cover. The grid is kept the same everywhere so that it stays one standard; in western cells the cell value should lean more on the virtual PM2.5 products and on the per-cell maximum and number of monitors (as recommended in the cell statistics document). Alaska and the provinces outside Ontario and Québec have too few monitors in the C.L.E.A.R. data to measure their own radius; the eastern and Canadian value is applied there.

# **2. From the equator northward: the cell dimensions**

## **2.1 The rule**

* **Rows are 0.5° of latitude everywhere** (55.7 km north–south). 0.5° divides 90° exactly, so rows line up from the equator to the pole.
* **Every point of a cell must be within the effective radius (45 km) of the cell centre.** With rows 55.7 km tall, a cell may be at most **70.7 km wide** (centre-to-corner distance √(27.8² + 35.4²) = 45 km).
* **Each row gets the widest standard width that keeps the cell within 70.7 km at the row’s centre latitude.** The east–west size of one degree of longitude shrinks with latitude (111.3 km × cos latitude), so the width in degrees must grow to keep the same width in kilometres.
* **Standard widths are multiples of 0.25° that divide 180° exactly** (0.5, 0.75, 1, 1.25, 1.5, 2, 2.5, 3, 3.75, 4.5, 5°, …). This keeps every cell edge on the 0.25° grid of ERA5 wind and TROPOMI and on both the Greenwich and the 180th meridian, so cells never straddle the date line in the Aleutians.
* **At the equator** the widest allowed width is 0.5° (0.75° would be 83.5 km wide), so the grid starts as **0.5° × 0.5° squares** (55.7 × 55.7 km).

![Cell size vs latitude](data:image/png;base64...)

*Figure 3. (a) East–west width in degrees: the standard grid follows the width that would keep cells square (dashed) in steps. (b) Cell size in km: the uniform 0.5° grid becomes very narrow in the north, while the standard grid stays 47–71 km wide and never exceeds the 45 km effective radius.*

## **2.2 Zone table**

| **Latitude (°N)** | **East–west width** | **Cell (lat × lon)** | **East–west size (km)** | **Centre-to-corner (km)** | **Cells in the grid** |
| --- | --- | --- | --- | --- | --- |
| 0–32 | 0.5° | 0.5° × 0.5° | 55.7 → 47.3 | 39.4 → 36.5 | 386 |
| 32–50.5 | **0.75°** | 0.5° × 0.75° | 70.6 → 53.4 | 45.0 → 38.6 | 2,716 |
| 50.5–59.5 | **1.0°** | 0.5° × 1° | 70.4 → 56.9 | 44.9 → 39.8 | 1,359 |
| 59.5–65 | **1.25°** | 0.5° × 1.25° | 70.1 → 59.4 | 44.8 → 40.7 | 812 |
| 65–71.5 | **1.5°** | 0.5° × 1.5° | 69.9 → 53.7 | 44.7 → 38.7 | 783 |
| 71.5–75.5 | **2.0°** | 0.5° × 2° | 69.7 → 56.7 | 44.6 → 39.7 | 178 |
| 75.5–78 | **2.5°** | 0.5° × 2.5° | 68.5 → 59.0 | 44.1 → 40.6 | 85 |
| 78–80 | **3.0°** | 0.5° × 3° | 68.0 → 59.4 | 43.9 → 40.7 | 48 |
| 80–82 | **3.75°** | 0.5° × 3.75° | 70.7 → 59.9 | 45.0 → 40.9 | 36 |
| 82–82.5 | **4.5°** | 0.5° × 4.5° | 67.6 | 43.8 | 7 |
| 82.5–84 | **5.0°** | 0.5° × 5° | 70.2 → 60.6 | 44.8 → 41.1 | 8 |

Sizes are for the southern-most and northern-most row of each zone. The southern hemisphere is the mirror image. The full table to the pole and every cell are in CLEAR\_Standard\_Grid\_CSG-1.xlsx (sheet “Zones”). Toronto (43.65°N) is in the 0.75° zone, consistent with the 0.5° × 0.75° cell found in the cell statistics document.

## **2.3 The grid over Canada, Alaska and the lower 48 states**

The C.L.E.A.R. domain is every cell that touches land in Canada or the United States (Alaska and the lower 48; Hawaii excluded), plus the open-water cells of the Great Lakes.

![Standard grid map](data:image/png;base64...)

*Figure 4. The CLEAR Standard Grid: 6,418 cells, shaded by east–west width. Dashed lines: the latitudes where the width steps up. Star: Toronto.*

![Grid close-ups](data:image/png;base64...)

*Figure 5. Close-ups: (a) the step from 0.75° to 1.0° at 50.5°N in northern Ontario; (b) cell names around Toronto.*

| **Region** | **Uniform 0.5° × 0.5°** | **CLEAR Standard Grid** | **Change** | **Cells with a government monitor (uniform → standard)** |
| --- | --- | --- | --- | --- |
| **Lower 48 states** | 3,484 | 2,466 | −29% | 20.4% → 25.8% |
| **Alaska** | 1,364 | 560 | −59% | 0.4% → 0.9% |
| **Canada** | 7,955 | 3,377 | −58% | see Ontario, Québec |
| **Ontario** | 546 | 320 | −41% | 5.5% → 8.8% |
| **Québec** | 901 | 493 | −45% | 3.2% → 5.3% |
| **Great Lakes (open water)** | 31 | 15 | −52% | – |
| **Total** | **12,834** | **6,418** | **−50%** |  |
| **Within 1,000 km of Toronto (land + Great Lakes)** | 1,286 | 839 | −35% | 22% → 29% |

Government monitors: US EPA 88101/88502 monitors active since 2021 in every state, and Ontario, Québec and NAPS monitors in Ontario/Québec. The NAPS station lists for the other provinces and territories are not yet in the C.L.E.A.R. data, so their coverage is not shown. Counts include every cell that touches land, so they are higher than the earlier estimates in “The Grid Approach”, which counted only cells whose centre is on land.

![Cells and coverage](data:image/png;base64...)

*Figure 7. (a) Number of cells, uniform 0.5° grid versus the standard grid. (b) Share of cells with at least one government monitor by latitude (lower 48, Alaska, Ontario and Québec).*

* **Half as many cells overall, and 58–59% fewer in Canada and Alaska,** where monitors are scarce: fewer empty cells that need virtual PM2.5.
* **More cells have a monitor:** in the 32–48°N bands, 25–29% of cells have a government monitor instead of 18–23%.
* **The far south is unchanged** (0.5° × 0.5° below 32°N), because the effective radius does not allow wider cells there.

## **2.4 Sensitivity to the design radius**

| **Design radius** | **Widest cell** | **Width steps** | **Cells (approx.)** |
| --- | --- | --- | --- |
| 40 km | 57.5 km | 0.75° from 46.5°N, 1° from 59°N, 1.25° from 65.5°N, 1.5° from 70°N | ≈ 8,070 |
| **45 km (chosen)** | 70.7 km | 0.75° from 32°N, 1° from 50.5°N, 1.25° from 59.5°N, 1.5° from 65°N | **6,418** |
| 50 km | 83.1 km | 0.75° from 5.5°N, 1° from 41.5°N, 1.25° from 53.5°N, 1.5° from 60°N | ≈ 5,310 |

A 40 km radius would keep Toronto in 0.5° × 0.5° cells and add about 1,650 cells; a 50 km radius would remove about 1,100 cells but put most cells at the edge of the eastern effective radius and well beyond it in the West.

# **3. Naming the cells**

## **3.1 Options compared**

| **Option** | **Toronto’s cell** | **Assessment** |
| --- | --- | --- |
| **South-west corner (recommended)** | **N4350W07950** | Corners are always multiples of 0.25°, so names have a fixed length (11 characters) and need no rounding. A point’s cell is found with two FLOOR operations. Same convention as SRTM / NASADEM and Copernicus elevation tiles (e.g. N43W080). |
| **Cell centre** | 43.75N 79.125W | Natural for maps, but centres need 3 decimals in the 0.75°, 1.25° and 3.75° zones (e.g. 79.125, 73.875), so names change length, and finding a cell needs an extra half-width step. Centres are kept as attributes in the grid table. |
| **Row / column index** | R267 C134 | Compact for arrays and databases, but meaningless to people, and a column number means a different longitude in each zone. Kept as attributes. |
| **Existing systems (geohash, H3 hexagons)** | (opaque codes) | Geohash cells narrow going north like a uniform grid; H3 hexagons are equal-area but have opaque IDs and fixed sizes (nearest resolutions about half and 3.5 times a CSG-1 cell). Neither is tied to the monitor radius. |

## **3.2 The CLEAR cell name**

![Cell naming](data:image/png;base64...)

*Figure 6. A cell is named by its south-west corner; the orange dots are the naming corners.*

| **Part** | **Rule** |
| --- | --- |
| **N or S** | Hemisphere of the corner latitude |
| **4 digits** | Corner latitude × 100 (always a multiple of 50: 0000, 0050, …, 8950) |
| **E or W** | Hemisphere of the corner longitude (0° counts as E) |
| **5 digits** | Corner longitude × 100 (W: the western edge of the cell, e.g. −79.50° → W07950) |
| **Edges** | A point exactly on an edge belongs to the cell to its north / east |
| **Version** | The grid is versioned (CSG-1). Data files should record the grid version; names stay valid as long as the zone table does not change |

| **Place** | **Latitude, longitude** | **Cell** | **Cell extent** |
| --- | --- | --- | --- |
| **Toronto** | 43.65, −79.38 | **N4350W07950** | 43.5–44.0°N, 79.50–78.75°W |
| **Montréal** | 45.50, −73.57 | N4550W07425 | 45.5–46.0°N, 74.25–73.50°W |
| **Vancouver** | 49.28, −123.12 | N4900W12375 | 49.0–49.5°N, 123.75–123.00°W |
| **Winnipeg** | 49.90, −97.14 | N4950W09750 | 49.5–50.0°N, 97.50–96.75°W |
| **Yellowknife** | 62.45, −114.37 | N6200W11500 | 62.0–62.5°N, 115.00–113.75°W |
| **Resolute** | 74.70, −94.83 | N7450W09600 | 74.5–75.0°N, 96.0–94.0°W |
| **Anchorage** | 61.22, −149.90 | N6100W15000 | 61.0–61.5°N, 150.00–148.75°W |
| **Adak, Aleutians (east of 180°)** | 51.88, 176.66 | N5150E17600 | 51.5–52.0°N, 176–177°E |
| **Chicago** | 41.88, −87.63 | N4150W08775 | 41.5–42.0°N, 87.75–87.00°W |
| **Miami** | 25.76, −80.19 | N2550W08050 | 25.5–26.0°N, 80.50–80.00°W |

## **3.3 Finding the cell of any point**

**Steps:** (1) row = FLOOR(latitude ÷ 0.5) × 0.5; (2) width = zone table for that row; (3) column = FLOOR(longitude ÷ width) × width; (4) write the name. Python (scripts/dynamic\_grid/clear\_grid.py):

# zone table: (from latitude, east-west width in degrees)

ZONES = [(0.0, 0.5), (32.0, 0.75), (50.5, 1.0), (59.5, 1.25), (65.0, 1.5), (71.5, 2.0),

(75.5, 2.5), (78.0, 3.0), (80.0, 3.75), (82.0, 4.5), (82.5, 5.0)]

import math

def cell\_name(lat, lon):

row = math.floor(lat / 0.5) \* 0.5

width = [w for start, w in ZONES if abs(row + 0.25) >= start][-1]

col = math.floor(round(lon / width, 9)) \* width

return (('N' if row >= 0 else 'S') + f'{round(abs(row) \* 100):04d}' +

('E' if col >= 0 else 'W') + f'{round(abs(col) \* 100):05d}')

cell\_name(43.65, -79.38) # 'N4350W07950'

Excel (latitude in A2, longitude in B2, zone table in sheet “Zones” of the spreadsheet):

=LET(r, FLOOR.MATH(A2/0.5)\*0.5,

w, LOOKUP(r, Zones!$A$2:$A$12, Zones!$C$2:$C$12),

c, FLOOR.MATH(B2/w)\*w,

IF(r>=0,"N","S") & TEXT(ABS(r)\*100,"0000") & IF(c>=0,"E","W") & TEXT(ABS(c)\*100,"00000"))

* **Going back from a name:** south edge = digits 2–5 ÷ 100, west edge = digits 7–11 ÷ 100 (negative for S / W); the width comes from the zone table, so north = south + 0.5° and east = west + width.
* **Neighbours:** east and west neighbours are one width away in the same row. Where the width changes between two rows, a cell can touch two cells of the next row, as in the reduced grids used by weather models.
* **Sorting:** names sort by hemisphere, then latitude, then longitude, which keeps rows together in files and databases.

# **4. Using the grid going forward**

| **Task** | **How** |
| --- | --- |
| **Assign monitors to cells** | cell\_name(lat, lon) for every station (government and PurpleAir); store the cell name with the station |
| **Satellite and model data** | Average FireWork, HRRR-Smoke, ERA5 and TROPOMI points inside each cell (0.25° products fit cells exactly); use the share of the cell covered by HMS smoke |
| **Cell values for the model** | Government mean, PurpleAir mean, maximum or 90th percentile and number of monitors per cell; virtual PM2.5 for empty cells |
| **Alerts and data exchange** | Use the cell name as the key; record grid version CSG-1 |
| **Next steps** | Add the national NAPS station list (all provinces and territories) to complete Canadian coverage; rebuild the virtual PM2.5 grid on CSG-1; review the radius for the West and Alaska when more monitors are available |

# **Data and files**

* CLEAR\_Standard\_Grid\_CSG-1.xlsx: zone table, all 6,418 cells (name, row, column, corners, centre, km size, country, province/state, land fraction, government monitors), examples, cell counts, coverage by latitude, effective radius by group.
* CLEAR\_Standard\_Grid\_CSG-1.geojson: the cells as polygons for GIS.
* Scripts (scripts/dynamic\_grid/): 01\_effective\_radius.py (monitor pairs), 02\_noise\_corrected\_radius.py (effective radius), clear\_grid.py (zone table and naming), 03\_build\_grid.py (grid and coverage), 04\_radius\_sensitivity.py. Results: Cleaned Data/analysis/dynamic\_grid/.
* Hourly PM2.5: US EPA AQS hourly files (88101, 88502), Ontario and Québec provincial networks, NAPS; boundaries: Natural Earth 1:50m.
