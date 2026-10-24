---
source: archive/seagate/Documents/19. Building Dynamic Grid/Choosing_the_Alert_Radius_48h_Warning.docx
aliases: [archive/seagate/Documents/19. Building Dynamic Grid/Choosing_the_Alert_Radius_48h_Warning.pdf]
sha256: ede8f66254473f7048ad8449137ad967cc9d7a4882426f6330d4d39649ab5e68
converted: 2026-10-24
converter: markitdown
status: current
kind: mirror
---

**C.L.E.A.R. 2.0**

**Choosing the alert radius for a 48-hour PM2.5 warning**

*Hugo Bui & Ryan Zander · University of Toronto Schools · October 2026*

C.L.E.A.R. currently uses ground monitors within **1,000 km** of Toronto (a 2,000 km diameter). The goal is a **48-hour warning** of Toronto PM2.5 ≥ 30 µg/m³, with wind data to be added later. This document tests, with measured data from 2018–2025, how far the network must reach to give that warning, and how much larger or smaller the radius could be. No model results are used: the tests use only monitor readings, NOAA smoke polygons and ERA5 winds.

|  |
| --- |
| **Recommendation**   * **Radius: 1,500 km** (3,000 km diameter). **Acceptable range: 1,250–2,000 km.** All radii in this range warn significantly better than 1,000 km, and none of them is significantly better than another. * **Better still: a direction-dependent domain,** 1,500 km to the south-west, west, north-west and north (upwind, where 48-hour warnings come from) and 1,000 km to the north-east, east and south. It has 1,366 grid cells instead of 1,611 for the full 1,500 km circle (839 today). * **Why:** for a new Toronto episode 48 hours ahead, the warning skill (ROC AUC) rises from 0.82 at 1,000 km to **0.88 at 1,500 km** (+0.06, 90% interval +0.03 to +0.09), stays flat to 2,000 km, and falls beyond 2,500 km as distant, unrelated smoke adds false alarms. * **Physics agrees:** PM2.5 reaches Toronto at about **17 km/h**, so 48 hours of travel is about **1,070 km**; a 1,500 km radius covers that with a margin for slower and more northerly paths. * **The best radius scales with lead time:** about 1,250 km for 24 hours, 1,500 km for 48 hours and 2,000 km for 72 hours. * **With wind data,** the domain can extend to 2,000–2,500 km to the west and north-west for 72-hour warnings, because wind (at the height smoke travels, not only at the surface) can separate Toronto-bound plumes from others. Surface (10 m) wind alone is not enough: it moves air only 420–480 km in 48 hours. |

# **1. Data and approach**

| **Item** | **Details** |
| --- | --- |
| **Target** | Toronto 4-station mean PM2.5 (Downtown, East, North, West), hourly 2018–2025 |
| **Upstream monitors** | 1,247 government monitors up to 3,500 km from Toronto: US EPA reference (88101) in every lower-48 state, EPA continuous (88502) at sites without a reference monitor, Ontario, Québec and NAPS |
| **Smoke over Toronto** | NOAA Hazard Mapping System smoke polygons (May–September) |
| **Wind** | ERA5 10 m wind, 38–53°N, 96–57°W (the upper-level winds are not yet available) |
| **Elevated monitor** | 3-hour mean PM2.5 ≥ 30 µg/m³ |
| **Distances and directions** | Bands 0–250, 250–500, …, 3,000–3,500 km; 8 compass sectors (from Toronto) |

**The test.** In May–September, at every hour when Toronto was below 30 µg/m³, the share of elevated monitors within radius R was compared with whether a **new** Toronto episode (≥ 30) began **36–60 hours later** (28,484 hours, 1,051 of them followed by an episode). The skill is the ROC AUC: 0.5 means the signal is useless, 1.0 means it separates the two cases perfectly. Week-long blocks were resampled 200 times for 90% intervals, using the same samples for every radius so that radii can be compared directly. The same test was run 24 hours (12–36 h) and 72 hours (60–84 h) ahead.

# **2. Toronto’s PM2.5 ≥ 30 episodes**

![Episodes and domain size](data:image/png;base64...)

*Figure 1. (a) Toronto episodes by month and type. (b) Number of grid cells and 48-hour skill for each radius.*

* **64 episodes in 2018–2025** (hours ≥ 30, separated by at least 24 hours below 30): **24 with wildfire smoke over Toronto** (NOAA HMS), 38 in October–April (winter inversions and local or regional pollution) and 2 in summer without smoke.
* **Smoke episodes are the big ones:** the 10 highest episodes were all smoke (peaks up to 200 µg/m³ on June 27–28, 2023, and 114 µg/m³ on July 14, 2025), and they last longest (up to 118 hours ≥ 30).
* **Winter episodes** are short and come from local or regional sources within a few hundred kilometres; a large network radius does not help predict them, so the radius is chosen for the May–September smoke season.

# **3. How far does smoke travel in 48 hours?**

## **3.1 Travel time measured from the monitors**

For each distance band and direction, the share of elevated monitors was compared with Toronto PM2.5 at lags of 0 to 120 hours; the lag of the best match is the typical travel time from that band to Toronto (summer 2018–2025).

![Travel time vs distance](data:image/png;base64...)

*Figure 2. Lag of best match between upstream monitors and Toronto, by distance and direction (bands with a match r ≥ 0.2).*

| **Direction** | **500–750 km** | **750–1,000 km** | **1,000–1,250 km** | **1,250–1,500 km** |
| --- | --- | --- | --- | --- |
| **West** | 30 h | 45 h | 45 h | 54 h |
| **North-west** | 24 h | 27 h | 45 h | 96 h (weak) |
| **North** | 33 h | – | 48 h | – |
| **South-west** | 15 h | 15 h | – | – |

* **Fitted travel speed: about 17 km/h (4.7 m/s).** At that speed, **24 hours ≈ 670 km, 48 hours ≈ 1,070 km and 72 hours ≈ 1,480 km** upwind.
* A 1,000 km radius therefore reaches only just under 48 hours of travel on average, and less on slow days; a 1,500 km radius covers 48 hours with room for slower transport and for curved paths.

## **3.2 Surface wind back-trajectories**

From Toronto, the ERA5 10 m wind was followed backward for 48 hours at the start of each smoke episode and on every smoke-season day.

| **Back-trajectories, ERA5 10 m wind** | **Median 48-h distance** | **90th percentile** | **Median wind speed** |
| --- | --- | --- | --- |
| **Start of the 24 smoke episodes** | 483 km | 605 km | 3.4 m/s |
| **Every May–September day, 2018–2025 (1,224)** | 419 km | 710 km | 3.3 m/s |

* **Surface air moves only 420–480 km in 48 hours**, less than half the distance smoke actually travels (about 1,070 km). Smoke is carried 1–5 km above the ground where winds are faster than at 10 m, which is slowed by friction.
* **Consequence for the wind data:** the alert system needs winds at the height of the smoke (for example ERA5 850 and 700 hPa) to trace where Toronto’s air will come from; 10 m winds would place the source region far too close.

# **4. Warning skill by radius**

![Skill vs radius](data:image/png;base64...)

*Figure 3. Skill of upstream monitors within each radius for predicting a new Toronto episode 24, 48 and 72 hours ahead (shading: 90% interval).*

| **Radius** | **Diameter** | **48-hour skill (AUC)** | **Difference from 1,000 km (90% interval)** | **24-hour skill** | **72-hour skill** |
| --- | --- | --- | --- | --- | --- |
| 500 km | 1,000 km | 0.69 | −0.13 (−0.18 to −0.09) | 0.75 | 0.62 |
| 750 km | 1,500 km | 0.77 | −0.05 (−0.07 to −0.02) | 0.84 | 0.70 |
| **1,000 km (now)** | 2,000 km | 0.82 | – | 0.89 | 0.74 |
| 1,250 km | 2,500 km | 0.87 | +0.05 (+0.03 to +0.07) | **0.90 (best)** | 0.78 |
| **1,500 km** | 3,000 km | **0.88 (best)** | **+0.06 (+0.03 to +0.09)** | 0.90 | 0.80 |
| 1,750 km | 3,500 km | 0.88 | +0.06 (+0.02 to +0.09) | 0.89 | 0.81 |
| 2,000 km | 4,000 km | 0.87 | +0.05 (+0.02 to +0.09) | 0.88 | **0.81 (best)** |
| 2,500 km | 5,000 km | 0.85 | +0.04 (−0.00 to +0.08) | 0.86 | 0.80 |
| 3,000 km | 6,000 km | 0.83 | +0.01 (−0.04 to +0.05) | 0.84 | 0.77 |
| 3,500 km | 7,000 km | 0.79 | −0.03 (−0.08 to +0.02) | 0.80 | 0.72 |

Skill of the share of elevated monitors (3-hour mean ≥ 30) within the radius, May–September 2018–2025, at hours when Toronto was below 30. Every radius from 1,250 to 2,000 km beat 1,000 km in all 200 paired resamples.

* **Smaller than 1,000 km loses skill quickly** (750 km: −0.05; 500 km: −0.13). The monitors near Toronto see smoke only when it is already arriving.
* **1,250–2,000 km is a plateau** for the 48-hour warning: 0.87–0.88, all significantly better than 1,000 km. 1,500 km is the peak.
* **Beyond 2,000–2,500 km skill falls.** Without wind, distant smoke (for example western US fires) is counted whether or not it is heading to Toronto, which adds false alarms.
* **The best radius grows with the lead time** (24 h: 1,250 km; 48 h: 1,500 km; 72 h: 2,000 km), matching the travel speed in Section 3.
* **A simple counting rule is only a starting point.** The best rule at 1,500 km (12 or more elevated monitors upwind) catches about half of the hours 36–60 hours before an episode, and about 63% of its alerts are false. The machine-learning model will use these signals together with wind and smoke products; the radius only decides which monitors it can see.

# **5. Direction matters**

![Skill by direction](data:image/png;base64...)

*Figure 4. 48-hour skill of each distance band and direction (wedges). Blank areas have no monitors in the C.L.E.A.R. data.*

| **Direction** | **500–750 km** | **750–1,000 km** | **1,000–1,250 km** | **1,250–1,500 km** | **1,500–2,000 km** |
| --- | --- | --- | --- | --- | --- |
| **West** | 0.68 | 0.70 | 0.70 | 0.70 | 0.59 |
| **North-west** | 0.63 | 0.66 | 0.68 | 0.64 | 0.58 |
| **North** | 0.63 | – | 0.56 | – | – |
| **South-west** | 0.60 | 0.60 | 0.56 | 0.52 | 0.52 |
| **North-east** | 0.55 | 0.57 | 0.50 | – | – |
| **East, south-east, south** | 0.52–0.53 | 0.50–0.51 | 0.52 | 0.50 | 0.51 |

“–”: no monitors with enough data in that band and direction.

* **48-hour warnings come from the west and north-west at 500–1,500 km** (skill 0.63–0.70 for a single band), consistent with the prevailing westerly winds and with smoke from fires in western and northern Canada.
* **East, south-east and south carry no 48-hour information** beyond 500 km (0.50–0.53). Extending the domain in those directions adds cells without adding warning time, so they can stay at 1,000 km (which still covers Québec, the source of the June 2023 smoke).
* **North-west and north are under-sampled:** the C.L.E.A.R. data has no monitors in Manitoba, Saskatchewan, Alberta, British Columbia, the territories or northern Ontario, so only 2–5 monitors per band represent the north-west beyond 1,000 km. These are the directions of the 2023 and 2025 Prairie fires, so the true north-west signal is probably stronger than measured here, which supports extending the domain to the north-west once the national NAPS data are added.

# **6. Recommended domain and how much it can change**

![Domain options](data:image/png;base64...)

*Figure 5. Domain options on the CLEAR Standard Grid. Shaded: the recommended direction-dependent domain. Crosses: where the surface air was 48 hours before each smoke episode (ERA5 10 m wind), showing how much shorter surface paths are than actual smoke transport.*

| **Domain** | **Grid cells** | **Cells with a government monitor** | **Assessment** |
| --- | --- | --- | --- |
| **Circle 750 km** | 520 | 170 | Too small: −0.05 skill at 48 h |
| **Circle 1,000 km (current)** | 839 | 241 | Good for 24 hours; misses about 0.06 of 48-hour skill |
| **Circle 1,250 km** | 1,210 | 294 | Minimum for a 48-hour warning |
| **1,500 km to the SW–W–NW–N, 1,000 km elsewhere** | **1,366** | 315 | Recommended: keeps the upwind reach of 1,500 km with 245 fewer cells than the full circle |
| **Circle 1,500 km** | 1,611 | 336 | Best skill; simplest to describe |
| **2,000 km to the SW–W–NW–N, 1,000 km elsewhere** | 2,020 | 380 | For 72-hour warnings once upper-level wind data are in the model |
| **Circle 2,000 km** | 2,524 | 425 | Largest radius with full 48-hour skill; many cells in directions that add nothing |

Cells: land and Great Lakes cells of the CLEAR Standard Grid (CSG-1) whose centre lies inside the domain. Cells with a government monitor are counted from US EPA, Ontario, Québec and NAPS monitors only.

## **6.1 How much larger or smaller?**

| **Change from 1,000 km** | **Effect on a 48-hour warning** |
| --- | --- |
| **Smaller (750 km or less)** | Loses skill quickly (−0.05 at 750 km, −0.13 at 500 km). Not recommended. |
| **+250 km (1,250 km)** | Captures most of the gain (+0.05); the minimum for 48 hours. |
| **+500 km (1,500 km)** | Peak skill (+0.06); covers 48 hours of travel at 17 km/h with a margin. Recommended. |
| **+1,000 km (2,000 km)** | Same skill as 1,500 km without wind data; the best radius for 72-hour warnings. |
| **+1,500 km or more (2,500–3,500 km)** | Skill falls without wind data (distant, unrelated smoke). Only useful in the west and north-west once wind-based filtering is in place. |

## **6.2 What the wind data will change**

* **Direction:** wind data justify the direction-dependent domain now (westerlies dominate); with winds in the model, each monitor can be weighted by whether its air is moving toward Toronto.
* **Height:** use winds at the height of the smoke (ERA5 850 and 700 hPa, planned), not only 10 m winds, which underestimate the transport distance by more than half.
* **Larger reach without more false alarms:** once the model follows plumes with these winds, monitors 2,000–2,500 km to the west and north-west can add 72-hour warnings, because the wind tells the model which distant smoke will arrive. Beyond about 2,500 km the measured signal is close to zero even in the best directions (0.50–0.55), so there is little to gain.

## **6.3 Limitations**

* Only 24 smoke episodes in 2018–2025, dominated by 2021, 2023 and 2025; the intervals in the tables reflect this.
* No monitors in western and northern Canada in the C.L.E.A.R. data; adding the national NAPS station list will strengthen the north-west and north estimates.
* The skill test uses one simple signal (share of elevated monitors). It ranks radii fairly, but the full model will reach higher skill at any radius.
* Travel speed is a summer average from the timing of the best match; individual events can be much faster (strong jet-level transport) or slower (stagnant highs).

# **Data and files**

* PNG images (this folder): AR\_Fig1\_Skill\_vs\_Radius, AR\_Fig2\_Skill\_by\_Direction, AR\_Fig3\_Travel\_Time\_vs\_Distance, AR\_Fig4\_Domain\_Options\_Map, AR\_Fig5\_Episodes\_and\_Domain\_Size.
* Scripts: scripts/dynamic\_grid/05\_alert\_radius.py (episodes, skill by distance and direction, travel times) and 06\_alert\_radius\_leads\_and\_trajectories.py (24/48/72-hour skill with bootstrap, travel speed, back-trajectories, cells per domain). Results: Cleaned Data/analysis/dynamic\_grid/alert\_radius/.
* Data: Toronto 4-station mean PM2.5; US EPA AQS hourly PM2.5 (88101, 88502); Ontario and Québec provincial networks; NAPS; NOAA HMS smoke polygons; ERA5 10 m wind; CLEAR Standard Grid (CSG-1).
