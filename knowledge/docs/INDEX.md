# knowledge/docs/ — text mirrors of the original documents

One `.md` mirror per logical doc (docx preferred over pdf). Paths are slugified: lowercase,
hyphens. Frontmatter links each mirror to its original (`source`, `aliases`, `sha256`).
Superseded versions get no mirror unless they hold unique content.

Line format: `- [slug](slug.md) — what the doc is · current|superseded · key fact`.
Phase 1 (stations + grid) only: folders 04, 15, 19, 23, 35 of the Seagate Documents, plus two dataset summaries.

## Toronto stations (`archive/seagate/Documents/04. Toronto Stations`)

- [seagate-documents-04-toronto-stations-clear-2-0-mean-vs-max-methodology](seagate-documents-04-toronto-stations-clear-2-0-mean-vs-max-methodology.md) — test of mean vs max of 4 Toronto station predictions as the alert target (companion notes part 11) · current · mean beats max on recall in 5 of 6 cases; recommends mean plus a live Watch trigger
- [seagate-documents-04-toronto-stations-toronto-pm25-station-statistical-analysis](seagate-documents-04-toronto-stations-toronto-pm25-station-statistical-analysis.md) — statistics of the 10 Toronto NAPS and Ontario stations, 2000-2025 (companion notes part 10) · current · station agreement r = 0.75-0.94; proposes a two-stage Watch/Alert design

## Grid (`archive/seagate/Documents/15. The Grid Approach`, `19. Building Dynamic Grid`)

- [seagate-documents-15-the-grid-approach-the-grid-approach](seagate-documents-15-the-grid-approach-the-grid-approach.md) — methodology of forecasting Toronto PM2.5 on a 0.5 degree grid of measured and virtual PM2.5, wind and fire data · current · 1,416 squares within 1,000 km of Toronto; no modelling results
- [seagate-documents-15-the-grid-approach-the-grid-methodology](seagate-documents-15-the-grid-approach-the-grid-methodology.md) — step-by-step build of the 0.5 degree grid from ground monitors and virtual PM2.5 (pdf alias) · current · 510 of 1,416 cells hold a ground monitor, 906 need virtual PM2.5
- [seagate-documents-19-building-dynamic-grid-building-the-dynamic-grid-clear-standard-grid](seagate-documents-19-building-dynamic-grid-building-the-dynamic-grid-clear-standard-grid.md) — effective radius of a ground monitor and the CLEAR Standard Grid CSG-1 (sizes, naming) · current · 6,418 cells; design radius 45 km
- [seagate-documents-19-building-dynamic-grid-choosing-the-alert-radius-48h-warning](seagate-documents-19-building-dynamic-grid-choosing-the-alert-radius-48h-warning.md) — tests how far the network must reach for a 48-hour Toronto PM2.5 >= 30 ug/m3 warning (pdf alias) · current · recommends 1,500 km (range 1,250-2,000), direction-dependent domain

## Data completeness and sources (`archive/seagate/Documents/23. Data Completeness`, `35. AirNow`)

- [seagate-documents-23-data-completeness-clear2-data-completeness-continental](seagate-documents-23-data-completeness-clear2-data-completeness-continental.md) — share of each dataset held for Canada, Alaska and the lower 48, fire seasons 2021-2026 (pdf alias) · current · 16 datasets, 87% average; updated 21 Oct 2026
- [documents-23-data-completeness-clear2-data-completeness-continental](documents-23-data-completeness-clear2-data-completeness-continental.md) — earlier copy of the doc above, from the legacy folder (pdf alias) · superseded · older figures (15 datasets, 90%); the seagate copy is canonical
- [seagate-documents-23-data-completeness-clear2-data-timeline-2018-2026](seagate-documents-23-data-completeness-clear2-data-timeline-2018-2026.md) — which data is held per fire season 2018-2026 (pdf alias) · current · no missing years in training 2021-2024; 2026 test season has gaps
- [seagate-documents-23-data-completeness-clear2-validation-and-test-data-2025-2026](seagate-documents-23-data-completeness-clear2-validation-and-test-data-2025-2026.md) — what is held and missing for validation (2025) and test (2026) (pdf alias) · current · only NAPS 2025 missing (about March 2027); 2026 usable via AirNow
- [seagate-documents-35-airnow-clear2-airnow-summary](seagate-documents-35-airnow-clear2-airnow-summary.md) — what AirNow is and whether CLEAR can use it (pdf alias) · current · preliminary real-time government data; about 117 million rows held, 2014 to 8 Oct 2026

## Dataset summaries (docs that live in `data/raw`, not moved)

- [data-raw-canada-government-monitors-canada-naps-hourly-pm2-5-2000-2024-whole-year-naps-ontario-pm25-2000-2024-summary](data-raw-canada-government-monitors-canada-naps-hourly-pm2-5-2000-2024-whole-year-naps-ontario-pm25-2000-2024-summary.md) — summary of the Ontario-only NAPS hourly PM2.5 subset, 2000-2024 · current · 70 stations, 37 cities, 8.36% missing (-999)
- [data-raw-canada-government-monitors-on-provincial-hourly-pm2-5-2000-2025-whole-year-ontario-pm2-5-summary-report](data-raw-canada-government-monitors-on-provincial-hourly-pm2-5-2000-2025-whole-year-ontario-pm2-5-summary-report.md) — summary of the combined Air Quality Ontario hourly PM2.5 files, 2000-2025 · current · data 2003-2025, 58 station codes, 1.97% missing

## Images and media

PNGs get a one-line description here instead of a mirror. Embedded doc images are extracted only when a spec cites them.

Line format: `- [name](archive path) — what it shows · media · where it is used`.

- [Toronto_PM25_Stations_Map.png](<../../archive/seagate/Documents/04. Toronto Stations/Toronto_PM25_Stations_Map.png>) — map of the 10 Toronto PM2.5 stations 2000-2025 (circles active, triangles retired; navy Ontario, orange NAPS) · media · mean-vs-max doc
- [Toronto_Stations_Years_Active_Completeness.png](<../../archive/seagate/Documents/04. Toronto Stations/Toronto_Stations_Years_Active_Completeness.png>) — years active and per-year completeness of the 10 Toronto stations · media · station statistical analysis doc
- [GA_Fig1_Grid_Approach_Flow.png](<../../archive/seagate/Documents/15. The Grid Approach/GA_Fig1_Grid_Approach_Flow.png>) — the five stages of the grid approach, repeated hourly · media · grid approach doc
- [GA_Fig2_Grid_Around_Toronto.png](<../../archive/seagate/Documents/15. The Grid Approach/GA_Fig2_Grid_Around_Toronto.png>) — 0.5 degree grid within 1,000 km of Toronto (government monitor, PurpleAir only, no monitor) · media · grid approach doc
- [GA_Fig3_Filling_A_Cell.png](<../../archive/seagate/Documents/15. The Grid Approach/GA_Fig3_Filling_A_Cell.png>) — how each square gets an hourly PM2.5 value, measured or virtual · media · grid approach doc
- [GA_Fig4_Data_Source_By_Cell.png](<../../archive/seagate/Documents/15. The Grid Approach/GA_Fig4_Data_Source_By_Cell.png>) — source of each square value: measured, or virtual from FireWork, HRRR-Smoke, satellite · media · grid approach doc
- [GA_Fig5_Model_On_The_Grid.png](<../../archive/seagate/Documents/15. The Grid Approach/GA_Fig5_Model_On_The_Grid.png>) — probabilistic ST-GNN running on the grid · media · grid approach doc
- [GA_Fig6_Probability_vs_Elevated_Squares.png](<../../archive/seagate/Documents/15. The Grid Approach/GA_Fig6_Probability_vs_Elevated_Squares.png>) — chance Toronto follows rises with the number of elevated squares heading toward it · media · grid approach doc
- [GA_Fig7_Count_Squares_Not_Sensors.png](<../../archive/seagate/Documents/15. The Grid Approach/GA_Fig7_Count_Squares_Not_Sensors.png>) — 20 clustered sensors count once, 20 squares along the wind path count as 20 · media · grid approach doc
- [GA_Fig8_Illustrative_Tracking_Timeline.png](<../../archive/seagate/Documents/15. The Grid Approach/GA_Fig8_Illustrative_Tracking_Timeline.png>) — illustrative (synthetic numbers) probability timeline with 30% and 70% thresholds · media · grid approach doc
- [GA_Fig9_Illustrative_Arrival_Distribution.png](<../../archive/seagate/Documents/15. The Grid Approach/GA_Fig9_Illustrative_Arrival_Distribution.png>) — illustrative (synthetic numbers) from hourly arrival chance to arrival time and range · media · grid approach doc
- [GM_Fig1_Grid_Ground_Measurements.png](<../../archive/seagate/Documents/15. The Grid Approach/GM_Fig1_Grid_Ground_Measurements.png>) — grid filled with ground measurements (government, PurpleAir only, empty land, empty water) · media · grid methodology doc
- [GM_Fig3_Ground_vs_Column.png](<../../archive/seagate/Documents/15. The Grid Approach/GM_Fig3_Ground_vs_Column.png>) — ground-level PM2.5 (monitors, models) vs whole-column smoke (satellites) · media · grid methodology doc
- [AR_Fig1_Skill_vs_Radius.png](<../../archive/seagate/Documents/19. Building Dynamic Grid/AR_Fig1_Skill_vs_Radius.png>) — skill of upstream monitors within each radius for a new Toronto episode 24, 48, 72 h ahead · media · alert radius doc
- [AR_Fig2_Skill_by_Direction.png](<../../archive/seagate/Documents/19. Building Dynamic Grid/AR_Fig2_Skill_by_Direction.png>) — 48 h skill by distance band and direction (wedges) · media · alert radius doc
- [AR_Fig3_Travel_Time_vs_Distance.png](<../../archive/seagate/Documents/19. Building Dynamic Grid/AR_Fig3_Travel_Time_vs_Distance.png>) — lag of best match between upstream monitors and Toronto, by distance and direction · media · alert radius doc
- [AR_Fig4_Domain_Options_Map.png](<../../archive/seagate/Documents/19. Building Dynamic Grid/AR_Fig4_Domain_Options_Map.png>) — domain options on the CLEAR Standard Grid; shaded recommended direction-dependent domain · media · alert radius doc
- [AR_Fig5_Episodes_and_Domain_Size.png](<../../archive/seagate/Documents/19. Building Dynamic Grid/AR_Fig5_Episodes_and_Domain_Size.png>) — Toronto episodes by month and type; cells and 48 h skill per radius · media · alert radius doc
- [DG_Fig1_Correlation_vs_Distance.png](<../../archive/seagate/Documents/19. Building Dynamic Grid/DG_Fig1_Correlation_vs_Distance.png>) — median hourly correlation between monitors vs distance; effective radius where rho = 0.90 · media · standard grid doc
- [DG_Fig2_Effective_Radius_by_Region.png](<../../archive/seagate/Documents/19. Building Dynamic Grid/DG_Fig2_Effective_Radius_by_Region.png>) — effective radius by region and latitude band · media · standard grid doc
- [DG_Fig3_Cell_Size_vs_Latitude.png](<../../archive/seagate/Documents/19. Building Dynamic Grid/DG_Fig3_Cell_Size_vs_Latitude.png>) — east-west cell width in degrees and km vs latitude, uniform 0.5 degree vs standard grid · media · standard grid doc
- [DG_Fig4_Standard_Grid_Map.png](<../../archive/seagate/Documents/19. Building Dynamic Grid/DG_Fig4_Standard_Grid_Map.png>) — CLEAR Standard Grid, 6,418 cells shaded by east-west width; star marks Toronto · media · standard grid doc
- [DG_Fig5_Grid_Closeups.png](<../../archive/seagate/Documents/19. Building Dynamic Grid/DG_Fig5_Grid_Closeups.png>) — close-ups: width step 0.75 to 1.0 degree at 50.5N; cell names around Toronto · media · standard grid doc
- [DG_Fig6_Cell_Naming.png](<../../archive/seagate/Documents/19. Building Dynamic Grid/DG_Fig6_Cell_Naming.png>) — a cell is named by its south-west corner · media · standard grid doc
- [DG_Fig7_Cells_and_Coverage.png](<../../archive/seagate/Documents/19. Building Dynamic Grid/DG_Fig7_Cells_and_Coverage.png>) — cell counts, uniform vs standard grid; share of cells with a government monitor by latitude · media · standard grid doc
- [AirNow_Completeness_Polygon_2025_2026.png](<../../archive/seagate/Documents/23. Data Completeness/AirNow_Completeness_Polygon_2025_2026.png>) — AirNow PM2.5 completeness in the 1,250 km upwind polygon, 2025 (356 monitors) and 2026 (358), median 99% of hours · media · standalone, no mirrored doc
- [Completeness_Fig1_All_Datasets.png](<../../archive/seagate/Documents/23. Data Completeness/Completeness_Fig1_All_Datasets.png>) — share of each dataset held, fire seasons 2021-2026 · media · completeness doc
- [Completeness_Fig2_By_Area.png](<../../archive/seagate/Documents/23. Data Completeness/Completeness_Fig2_By_Area.png>) — same datasets split into Canada, Alaska, lower 48 · media · completeness doc
- [Completeness_Fig3_Maps.png](<../../archive/seagate/Documents/23. Data Completeness/Completeness_Fig3_Maps.png>) — fire seasons held per grid cell, gridded datasets · media · completeness doc
- [Completeness_Fig4_PurpleAir.png](<../../archive/seagate/Documents/23. Data Completeness/Completeness_Fig4_PurpleAir.png>) — PurpleAir sensor-seasons that exist and that we hold, May-September 2021-2026 · media · completeness doc
- [Timeline_Fig1_2018-2026.png](<../../archive/seagate/Documents/23. Data Completeness/Timeline_Fig1_2018-2026.png>) — share of each fire season held, by dataset and year · media · data timeline doc
- [Timeline_Fig2_Ground_Monitors.png](<../../archive/seagate/Documents/23. Data Completeness/Timeline_Fig2_Ground_Monitors.png>) — monitors reporting each fire season in the main networks · media · data timeline doc
- [Validation_Fig1_Status_2025_2026.png](<../../archive/seagate/Documents/23. Data Completeness/Validation_Fig1_Status_2025_2026.png>) — status of each source for 2025 and 2026; expected release of missing data · media · validation and test doc
- [Completeness_Fig1_All_Datasets.png](<../../archive/Documents/23. Data Completeness/Completeness_Fig1_All_Datasets.png>) — earlier render of the completeness figure (legacy copy; differs from the archive/seagate file) · media · legacy completeness doc
- [Completeness_Fig2_By_Area.png](<../../archive/Documents/23. Data Completeness/Completeness_Fig2_By_Area.png>) — earlier render of the by-area figure (legacy copy; differs from the archive/seagate file) · media · legacy completeness doc
- [Completeness_Fig3_Maps.png](<../../archive/Documents/23. Data Completeness/Completeness_Fig3_Maps.png>) — earlier render of the cell-coverage maps (legacy copy; differs from the archive/seagate file) · media · legacy completeness doc
- [AirNow_Fig1_Monitors_by_Year.png](<../../archive/seagate/Documents/35. AirNow/AirNow_Fig1_Monitors_by_Year.png>) — AirNow PM2.5 monitors each fire season, 2014-2026 · media · AirNow summary doc
- [AirNow_Fig2_Map_2025.png](<../../archive/seagate/Documents/35. AirNow/AirNow_Fig2_Map_2025.png>) — AirNow PM2.5 monitors in the 2025 season, coloured by whether the same monitor is held in validated form · media · AirNow summary doc
