---
source: archive/seagate/Documents/15. The Grid Approach/The_Grid_Approach.docx
aliases: []
sha256: f802b4c8b664dd76a1461161b5b89e8b3ddec8dd84056da046c5543da69a45e6
converted: 2026-10-24
converter: markitdown
status: current
kind: mirror
---

**The Grid Approach**

**C.L.E.A.R. 2.0 methodology: forecasting Toronto PM2.5 on a 0.5° grid of measured and virtual PM2.5, wind and fire data**

*Hugo Bui & Ryan Zander · University of Toronto Schools · October 2026*

This is a **methodology document**. It describes how C.L.E.A.R. 2.0 will represent wildfire smoke on a regular grid around Toronto, fill every grid square with a PM2.5 value (measured where there are monitors, **virtual** where there are none), add wind at the surface and aloft, and forecast the probability and timing of smoke reaching Toronto on the NVIDIA RTX 5080 workstation. It contains no modelling results; those will be reported separately once the steps below are carried out.

|  |
| --- |
| **The grid approach in brief**   * **A grid like the tiles of a video game.** The region within 1,000 km of Toronto is divided into **1,416 squares** of 0.5° latitude × 0.5° longitude (about 55 km north–south by 40 km east–west at Toronto). * **One PM2.5 value per square, every hour.** Where a square has monitors, their readings are **averaged** into one value, so dense city clusters are not over-represented. **510 squares** (36%) have at least one monitor. * **Virtual PM2.5 for the empty squares.** The other **906 squares** (lakes, ocean, northern forest, rural areas) receive a virtual PM2.5 value derived from modelled and satellite smoke data (ECCC FireWork, NOAA HRRR-Smoke, NOAA HMS smoke maps, Sentinel-5P aerosol index), corrected against the measured squares and clearly flagged as virtual. * **Wind for every square** at 10 m, about 1.5 km (850 hPa) and about 3 km (700 hPa), plus the boundary layer height, from ERA5. * **Count elevated squares, not sensors:** the more squares along the wind path show smoke, the higher the predicted chance for Toronto. * **A probabilistic forecast and a cautious alert rule:** the model tracks the plume across the grid and issues an alert, with a predicted arrival time, only when the forecast is reliable. * **Scale:** about 10,000 land squares would cover Canada and the lower-48 United States, about seven times the Toronto grid. |

# **1. Why a grid**

Air-quality monitors are scattered unevenly. Government monitors and PurpleAir sensors cluster in cities: Toronto alone has 24 PurpleAir sensors, and one square near Boston contains 79 monitors, while most of the boreal forest where large smoke plumes start has none. Feeding the model a scattered list of stations has three problems:

* **Over-weighting of cities.** A cluster of sensors in one city carries more weight than a single monitor that sees the plume first, simply because there are more of them.
* **Large gaps.** The model sees nothing over the Great Lakes, the ocean or the northern forest, where smoke travels before it reaches Toronto.
* **An inconsistent picture.** The set of stations changes from hour to hour and year to year as monitors are added, removed or go offline.

The grid approach, an idea Ryan took from video games, replaces the scattered stations with a **fixed board of equal tiles**. Every tile has a value every hour, measured or virtual, and every tile has the same neighbours. This gives the model a consistent spatial picture of where the smoke is and how it is moving.

![Grid approach flow](data:image/png;base64...)

*The five stages of the grid approach, repeated every hour.*

# **2. The grid around Toronto**

![The grid around Toronto](data:image/png;base64...)

*The 0.5° grid within 1,000 km of Toronto. Dark blue: at least one government monitor; purple: PurpleAir only; outlined: no monitor.*

| **Grid squares within 1,000 km of Toronto** | **Squares** | **Share** |
| --- | --- | --- |
| **With a government monitor (Ontario, Québec, NAPS or US EPA)** | 287 | 20% |
| **With PurpleAir sensor(s) only** | 223 | 16% |
| **With at least one monitor (measured squares)** | **510** | **36%** |
| **Without a monitor, on land (virtual squares)** | 673 | 48% |
| **Without a monitor, over lakes or ocean (virtual squares)** | 233 | 16% |
| **Total** | **1,416** | **100%** |

Monitors: the 1,931 stations active since 2018 within 1,000 km (44 Ontario provincial, 42 Québec provincial, 15 NAPS, 441 US EPA in all states — 419 reference-method monitors and 22 continuous monitors at sites without a reference monitor — and 1,389 PurpleAir). The circle reaches from 34.7°N (North Carolina) to 52.6°N (James Bay), and from eastern Minnesota to the Gulf of St. Lawrence.

## **Size of a grid square**

A 0.5° square is always about 55.6 km from south to north, but narrows from west to east as the lines of longitude converge toward the pole:

| **Latitude** | **North–south** | **West–east** | **Area** |
| --- | --- | --- | --- |
| 35°N (North Carolina) | 55.6 km | 45.6 km | 2,540 km² |
| **43.65°N (Toronto)** | **55.6 km** | **40.3 km** | **2,240 km²** |
| 50°N (James Bay area) | 55.6 km | 35.8 km | 1,990 km² |
| 55°N | 55.6 km | 31.9 km | 1,770 km² |
| 60°N | 55.6 km | 27.8 km | 1,550 km² |

Toronto’s five active monitoring stations fall in **two adjacent squares**: Toronto Downtown, East and North in one, and Toronto West and the NAPS Toronto station in the square immediately to the west.

# **3. Scale: Canada and the United States**

To understand how much data a national system would involve, the same 0.5° grid was laid over Canada and the United States (land squares only, counted from the centre of each square):

| **Region** | **Land squares (0.5°)** | **Notes** |
| --- | --- | --- |
| **1,000 km around Toronto** | **1,416 (incl. 233 water)** | The grid used in this methodology |
| **Canada, south of 60°N** | 3,162 | Where most people live and most Canadian monitors are |
| **Canada, all** | 6,733 | Includes the territories and the Arctic islands |
| **United States, lower 48 states** | 3,263 |  |
| **Alaska** | 1,120 |  |
| **Canada + lower-48 United States** | **about 10,000** | About 7 times the Toronto grid |
| **Canada + all of the United States** | **about 11,100** | Adding Alaska |

## **Data volume**

| **Hourly data, 2018–2025 (70,128 hours)** | **1,000 km grid** | **Canada + lower 48** |
| --- | --- | --- |
| **Squares** | 1,416 | ≈ 10,000 |
| **Square-hours** | 99 million | ≈ 700 million |
| **Values with about 50 inputs per square-hour** | 5 billion | ≈ 35 billion |
| **Storage in 16-bit numbers** | ≈ 10 GB | ≈ 70 GB |

* **The 1,000 km grid fits the RTX 5080 workstation comfortably:** about 10 GB of inputs, memory-mapped from the SSD with only the time windows of each training batch loaded.
* **A national grid is about seven times larger:** still feasible, but it would need more storage, regional training (for example one region at a time) or cloud computing.
* **Virtual values dominate at national scale.** Canada has about 230 NAPS stations and the national US EPA files contain about 1,200 reference-method and 860 continuous monitors, spread over 10,000 squares; most northern squares will rely on virtual PM2.5 (Step 3).

# **Step 1. Build the grid**

| **Item** | **Definition** |
| --- | --- |
| **Square index** | Row = floor(latitude ÷ 0.5), column = floor(longitude ÷ 0.5); every station is assigned to exactly one square |
| **Squares used** | Every square whose centre lies within 1,000 km of Toronto, plus any edge square that contains a monitor (1,416, including two edge squares just beyond 1,000 km) |
| **Square properties** | Centre latitude and longitude, distance and bearing to Toronto, land or water, province or state, and whether it lies inside the NOAA HRRR-Smoke domain |
| **Neighbours** | The 8 surrounding squares (north, north-east, east, … like the tiles of a game board), plus a direct link from every square to the two Toronto squares so that a distant signal reaches Toronto in one step |
| **Toronto targets** | The five active Toronto stations (Downtown, East, North, West and NAPS Toronto) are kept as individual target nodes attached to their squares, so each station is still forecast separately, together with the Toronto 4-station mean |

# **Step 2. Measured PM2.5: average the monitors in each square**

For every hour, all monitors reporting in a square are combined into **one value for the square**:

* **Quality control first:** missing-data flags and negative values are removed; PurpleAir readings use the US EPA Barkjohn correction (calculated from the raw CF-1 reading and the sensor’s humidity) and PurpleAir’s faulty-sensor flag.
* **Average:** the square’s PM2.5 is the average of the readings that pass the checks.
* **Keep the detail as extra inputs:** the government-monitor average and the PurpleAir average separately, the number of each, and the spread (lowest and highest reading), so the model can learn how much to trust each square.
* **Weighting to be tested:** a simple average treats a government monitor and a PurpleAir sensor equally. Because government monitors are more accurate (PurpleAir correlates at about r = 0.8 with nearby government monitors), the evaluation (Step 12) will compare a simple average, a median and an average that gives government monitors more weight.

![Filling a grid square](data:image/png;base64...)

*How every square gets a PM2.5 value each hour: measured where there are monitors, virtual where there are none.*

# **Step 3. Virtual PM2.5: fill the empty squares**

A square with no monitor still has smoke information from weather-and-smoke models and from satellites. A **virtual PM2.5** value is built for each empty square, every hour, from the sources below. Virtual values are always flagged so the model never confuses them with measurements.

## **Data sources for virtual PM2.5**

| **Source** | **What it provides** | **Coverage** | **Role** |
| --- | --- | --- | --- |
| **ECCC FireWork (RAQDPS-FW)** | Modelled surface PM2.5 including wildfire smoke, hourly, about 10 km grid | All of Canada and the United States, including the far north | Main virtual source, essential north of the HRRR-Smoke domain; already downloaded (2018–2025) |
| **NOAA HRRR-Smoke** | Modelled near-surface smoke PM2.5, hourly, 3 km grid | United States and southern Canada, up to about 52°N in Ontario and 49–50°N in eastern Québec | Second model where available (2021–2025); downloaded |
| **NOAA HMS smoke polygons** | Satellite analysts’ daily maps of light, medium and heavy smoke | Everywhere, including lakes and the far north | Confirms whether smoke is present; downloaded (2018–2025) |
| **Sentinel-5P TROPOMI aerosol index** | Daily satellite index of smoke in the whole atmospheric column, 0.25° | Everywhere, now from 34°N (re-exported October 2026) | Shows smoke aloft and plume extent; downloaded |
| **CWFIS Fire M3 and NASA FIRMS** | Active fires, fire power and fire perimeters | Everywhere | Where smoke comes from (not PM2.5 itself); downloaded |
| **Candidates to evaluate** | ECCC air-quality analysis (RDAQA); NASA GEOS-CF and MERRA-2 PM2.5; NOAA GOES-16/18 aerosol optical depth (every 10 minutes in daylight); Copernicus CAMS | North America | Not yet downloaded; archive periods and access to be checked |

![Data source by grid square](data:image/png;base64...)

*Where each square’s value comes from. Blue and purple: measured. Yellow: virtual from FireWork, HRRR-Smoke and satellite smoke data. Red: virtual from FireWork and satellite data only, north of the HRRR-Smoke domain, where FireWork becomes essential.*

| **Squares in the 1,000 km grid** | **Squares** | **Share** |
| --- | --- | --- |
| **Measured (government and/or PurpleAir)** | 510 | 36% |
| **Virtual: FireWork + HRRR-Smoke + satellite smoke** | 845 | 60% |
| **Virtual: FireWork + satellite smoke only (north of HRRR-Smoke)** | 61 | 4% |

## **How a virtual value is calculated**

| **#** | **Stage** | **What is done** |
| --- | --- | --- |
| 1 | **Sample each source over the square** | Average FireWork and HRRR-Smoke surface PM2.5 over all their grid points inside the square for that hour; take the HMS smoke density (none, light, medium, heavy) covering the square; average the TROPOMI aerosol index over the square’s four 0.25° cells (previous day) |
| 2 | **Learn the correction from measured squares** | In the 510 squares that do have monitors, the same model and satellite values can be compared with the measured average. A correction model (starting with gradient-boosted trees) learns to turn the model and satellite values, plus boundary layer height, humidity, season and hour, into surface PM2.5 |
| 3 | **Apply it to the empty squares** | The correction is applied to every empty square, giving the virtual PM2.5 |
| 4 | **Smooth the transition zone** | Near the northern edge of HRRR-Smoke, the weight given to HRRR-Smoke tapers off gradually so the virtual values do not jump where its coverage ends; north of the edge, FireWork and the satellite data take over |
| 5 | **Attach a flag and an uncertainty** | Every virtual value carries a “virtual” flag, which sources were available, and an uncertainty estimated from how well the correction reproduces measured squares it was not trained on |

* **Column versus surface:** the satellite aerosol index measures smoke in the whole atmospheric column, which may be high above the ground. Boundary layer height and the HMS density help decide whether that smoke is likely to reach the surface.
* **Missing satellite data:** clouds, night and low sun create gaps in the satellite data; the square then relies on the models alone, and its flags record this.

# **Step 4. Compare the PM2.5 products before combining them**

Before the sources are combined, each product will be examined so that its meaning and reliability are understood:

| **Question** | **How it will be answered** |
| --- | --- |
| **What does each product represent?** | Document, for FireWork, HRRR-Smoke, HMS, TROPOMI and the NASA candidates, whether it is a model, an analysis or a satellite measurement; surface or column; time and space resolution; how fire emissions are included; and how it is produced |
| **How do the products agree with each other?** | For every square and hour where two or more products exist, calculate their correlation and average difference, separately for smoke and non-smoke periods, by season and by latitude band |
| **How do they agree with ground monitors?** | Compare each product with the measured squares: correlation, bias and how often each detects PM2.5 ≥ 30 and ≥ 60 µg/m³ when the monitors do |
| **Where does each product fail?** | Map the differences to find regions (for example north of 50°N, coasts, mountains) and situations (thin smoke, smoke aloft) where a product is unreliable |
| **How should the US–Canada transition be handled?** | Examine the squares near the HRRR-Smoke northern edge, where both models exist, to set the tapering weights in Step 3 |

# **Step 5. Wind and atmosphere for every square**

Wind is what moves the smoke from square to square. Every square receives, every hour, from the ERA5 reanalysis:

| **Variable** | **Purpose** |
| --- | --- |
| **Wind at 10 m (u, v)** | Local transport and the arrival of smoke at the ground |
| **Wind at 850 hPa (about 1.5 km) and 700 hPa (about 3 km)** | Long-distance transport: large smoke plumes usually travel at about 1–5 km above the ground, where winds are faster and can come from a different direction |
| **Boundary layer height** | How deep the well-mixed air near the ground is, and so how readily smoke aloft mixes down |

* **Area:** 34–60°N and 110–57°W, so the whole 1,000 km grid and the northern and western fire zones (Nord-du-Québec, northern Ontario, Manitoba, Saskatchewan) are covered.
* **Per square:** ERA5 is on a 0.25° grid, so each 0.5° square averages the four ERA5 points inside it.
* **On every link between neighbouring squares,** the model calculates how much of the wind blows from one square toward the other, at each of the three heights:

**wind toward neighbour = u × sin(bearing) + v × cos(bearing)**

* **Combining surface and aloft:** ground PM2.5 and 10 m wind describe what is happening at the surface; the virtual PM2.5 from satellites and the 850/700 hPa winds describe the plume above. The model receives both, and the link values at the three heights let it learn which height matters in each situation.

# **Step 6. Fire and smoke context for every square**

* **Fires:** number of active CWFIS and FIRMS hotspots, total fire power and active fire perimeters in each square (previous day), and upwind fire activity.
* **Satellite smoke:** HMS smoke density and the TROPOMI aerosol index for each square, also used in Step 3.
* **No look-ahead:** daily satellite and fire data are always taken from the previous day, so every input is available at the time a forecast is made.

# **Step 7. Upstream evidence: count elevated squares, not sensors**

|  |
| --- |
| **The key rule: count SQUARES, not individual sensors**  Each square that reports smoke is one independent piece of evidence that a plume is on its way. **The more separate squares along the wind path show elevated PM2.5, the more likely Toronto is to follow.** Twenty sensors in one city are one square and one piece of evidence; twenty squares spread along the wind path are twenty. |

![Count squares not sensors](data:image/png;base64...)

*Left: 20 sensors clustered in one square count once. Right: 20 squares along the wind path count as 20 pieces of evidence.*

Every hour the model receives these counts as inputs: the number of squares with PM2.5 ≥ 30 and ≥ 60 µg/m³; the number whose wind blows toward Toronto; and the number whose travel time to Toronto (distance ÷ wind toward Toronto) is 0–12, 12–24 or 24–48 hours. Measured and virtual squares are counted separately, so measured evidence can carry more weight. A **monotonic constraint** ensures that, other things being equal, more elevated squares can only raise the predicted probability.

## **Why this works: what the data show**

The ground-monitor data (not a model) show the pattern clearly. For every hour from 2018 to 2025 when Toronto was below 30 µg/m³, the squares with PM2.5 ≥ 30 and wind blowing toward Toronto were counted:

| **Squares with PM2.5 ≥ 30 and wind toward Toronto** | **Hours** | **Toronto reached 30 within 24 h** | **Within 48 h** |
| --- | --- | --- | --- |
| 0 | 42,530 | 0.7% | 1.9% |
| 1–2 | 17,591 | 1.7% | 3.4% |
| 3–5 | 4,791 | 5.5% | 9.4% |
| 6–10 | 2,171 | 12.5% | 19.4% |
| 11–20 | 1,352 | 17.8% | 31.4% |
| 21–40 | 579 | 37.3% | 57.9% |
| **41–80** | **229** | **73.8%** | **86.0%** |

Observed frequencies from monitoring data (Ontario, Québec, NAPS, US EPA in five states and PurpleAir, 50–1,000 km from Toronto) and ERA5 10 m wind; not a model result.

![Probability vs elevated squares](data:image/png;base64...)

*The chance that Toronto follows rises steadily with the number of elevated squares heading toward it.*

# **Step 8. Define what the model predicts (the labels)**

| **Label** | **Definition** |
| --- | --- |
| **Exceedance** | For each hour ahead h = 1 … 48, at each Toronto station and for the Toronto 4-station mean: does PM2.5 reach 30 µg/m³? Does it reach 60 µg/m³? |
| **Arrival** | If Toronto is below 30 at the forecast time: the first hour within 72 hours when the 4-station mean reaches 30, or “no arrival within 72 hours” |
| **PM2.5 value** | The PM2.5 at each hour ahead, for a forecast range (10th, 50th and 90th percentiles) |

# **Step 9. The probabilistic model on the grid**

![Model on the grid](data:image/png;base64...)

*The probabilistic spatio-temporal graph neural network (ST-GNN) running on the grid.*

* **Nodes:** the 1,416 grid squares, plus the five Toronto station nodes.
* **Inputs per square, each hour, for the past 72 hours:** measured or virtual PM2.5 with its flags and uncertainty, wind at three heights, boundary layer height, fire and satellite smoke data, the upstream evidence counts, and the time of day and year.
* **Graph attention (GATv2):** each square combines information from its eight neighbours and the Toronto links, with the wind on each link at three heights deciding how much attention each neighbour receives, so the smoke signal moves across the grid with the wind.
* **Memory (GRU) over 72 hours:** repeating the graph step every hour carries the plume across the grid from the fire zones toward Toronto.
* **Decoder:** combines the Toronto nodes, a summary of the whole grid and known-future inputs (forecast winds and FireWork and HRRR-Smoke forecasts) for each hour ahead.
* **Three outputs:** the probability of PM2.5 ≥ 30 and ≥ 60 µg/m³ for each hour ahead; the hourly chance that smoke arrives (from which the arrival time is calculated); and a PM2.5 range.
* **Simpler models first:** before the ST-GNN, the same grid inputs will be used with simpler models (persistence, gradient-boosted trees, a GRU on grid summaries) to set baselines.

# **Step 10. Train, combine and calibrate on the RTX 5080**

| **Item** | **Plan** |
| --- | --- |
| **Hardware and software** | NVIDIA RTX 5080 (16 GB), 32 GB RAM, fast SSD; PyTorch 2.7 or later with CUDA 12.8, PyTorch Geometric; inputs stored in 16-bit and memory-mapped (about 10 GB) |
| **Training** | Mixed precision; smoke episodes oversampled so the rare high-PM2.5 hours are learned; weighted losses for each output |
| **Ensemble** | 5–10 copies trained with different random starts; their average is the probability and their disagreement measures confidence |
| **Calibration** | Probabilities adjusted on seasons not used for training so that “70%” happens about 70% of the time; arrival windows set from past errors |

# **Step 11. Arrival time and the alert rule**

![Illustrative arrival distribution](data:image/png;base64...)

*Illustrative example with synthetic numbers: from the hourly arrival chance to a predicted arrival time and range.*

| **State** | **When (checked every hour)** | **What happens** |
| --- | --- | --- |
| **Low (tracking)** | Chance of smoke reaching Toronto within 48 h below about 30%, or arrival time very uncertain | No public message; the plume keeps being tracked across the grid |
| **Watch** | Chance 30–70% and the arrival estimate narrowing | Health units and the public told a plume is being tracked |
| **Alert** | Chance at least about 70% and arrival known within a narrow window | Alert issued with the predicted arrival time and level, valid for 24 hours (renewed if PM2.5 stays ≥ 30) |

![Illustrative tracking timeline](data:image/png;base64...)

*Illustrative example with synthetic numbers: the probability rises as the plume crosses the grid toward Toronto, and the alert is issued only once it is high and the arrival time is clear. The 30% and 70% thresholds are starting points, to be tuned on past smoke seasons.*

# **Step 12. How the method will be evaluated**

| **Test** | **Method** |
| --- | --- |
| **Virtual PM2.5 accuracy** | Hide measured squares one region at a time, calculate their virtual value as if they were empty, and compare with the monitors |
| **Averaging rule** | Compare a simple average, a median and a government-weighted average inside measured squares (Step 2) |
| **Grid versus stations** | Compare the grid model with the same model run on individual stations, to measure what the grid adds |
| **Forecast skill** | Leave-one-season-out cross-validation over 2018–2025 (train on seven years, test on the eighth); calibration, High Risk recall and precision, alerts per smoke episode, warning time and arrival-time error, false alerts in quiet years |
| **Value of each data source** | Remove one data type at a time (PurpleAir, virtual squares, upper-level wind, satellite data) and measure the change |

# **Step 13. Running it live**

* **Every hour:** collect the latest government and PurpleAir readings, fill each square (measured or virtual), add the latest FireWork and HRRR-Smoke forecasts, satellite smoke and fire data, and forecast winds; run the ensemble; apply calibration and the alert rule; publish to the C.L.E.A.R. app and dashboard.
* **Winds:** ERA5 is published about five days late, so the live system uses weather-forecast winds (for example Environment Canada’s GEM model) for the same variables.

# **Work plan**

| **Phase** | **Work** | **Deliverable** |
| --- | --- | --- |
| 1 | Build the grid; measured-square averages; add the ERA5 34–60°N winds at three heights (Steps 1, 2, 5) | Grid with measured PM2.5 and wind for 2018–2025 |
| 2 | Compare the PM2.5 products and build the virtual-PM2.5 correction (Steps 3, 4) | Every square filled every hour, with flags and uncertainty |
| 3 | Fire and satellite context, upstream evidence counts and labels (Steps 6–8) | Complete grid input tensors (about 10 GB) |
| 4 | Baseline models, then the probabilistic ST-GNN ensemble on the RTX 5080 (Steps 9, 10) | Calibrated forecasts |
| 5 | Arrival times, alert rule and evaluation (Steps 11, 12) | Tested alert system |
| 6 | Live pipeline; later, extend the grid to Canada and the United States (Step 13, Section 3) | Prototype live system; national plan |

# **Risks and open questions**

* **Virtual values are only as good as the models and satellites behind them.** Thin smoke, smoke aloft and the far north are hardest; flags and uncertainty let the model treat virtual squares with caution.
* **Averaging different monitor types:** government monitors and PurpleAir differ in accuracy; the averaging rule must be tested (Step 2).
* **The US–Canada transition:** HRRR-Smoke stops at about 50–52°N; FireWork carries the north, and the transition must not create artificial edges.
* **Few smoke episodes:** only nine High Risk episodes in Toronto from 2018 to 2025, so results will carry real uncertainty and must be reported season by season with confidence intervals.
* **Scale:** a national grid is about seven times larger and will need more storage and computing.

# **Glossary**

| **Term** | **Meaning** |
| --- | --- |
| **Grid square (cell)** | A 0.5° × 0.5° area, about 55 km × 40 km at Toronto’s latitude |
| **Measured square** | A square with at least one monitor; its value is the average of its monitors |
| **Virtual PM2.5** | An estimate of surface PM2.5 for a square without monitors, from modelled and satellite smoke data corrected against measured squares |
| **FireWork / HRRR-Smoke** | Environment Canada’s and NOAA’s air-quality forecast models that include wildfire smoke |
| **HMS / TROPOMI** | NOAA’s satellite smoke maps / the Sentinel-5P satellite aerosol index |
| **ERA5** | The European weather reanalysis: hourly wind and other weather variables for every place and hour since 1940 |
| **850 hPa / 700 hPa** | Air-pressure levels about 1.5 km and 3 km above the ground |
| **ST-GNN** | Spatio-temporal graph neural network: a model that learns from values on a network of places over time |
| **Calibration** | Adjusting probabilities so that events forecast at 70% happen about 70% of the time |
| **Ensemble** | Several copies of a model; their average is more reliable and their disagreement measures uncertainty |
