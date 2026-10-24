# GLOSSARY

One vocabulary for code, docs and figures. Use the **Canonical code name** in code, columns
and file names; never a name from **Avoid**. Format and rules:
[docs/standards/writing.md](docs/standards/writing.md#glossary-entry). Unit suffixes:
[docs/standards/naming-units-time.md](docs/standards/naming-units-time.md).

- `<verify>` = not yet confirmed against the provider's documentation.
- `<defined in methodology/<slug>.md>` = CLEAR-specific; the spec supplies the
  definition when its phase is built. Spec slugs are provisional (see `STATUS.md`); code names for these terms are
  provisional until the spec lands.

## External terms and sources

| Term | Canonical code name | Definition | Units | Avoid |
|---|---|---|---|---|
| PM2.5 | `pm25_ugm3` | Particulate matter with aerodynamic diameter ≤ 2.5 µm; its mass concentration in air. | µg/m³ | `pm2.5`, `PM25`, `pm_25` |
| AQHI | `aqhi` | Air Quality Health Index: Canadian health-risk index built from ground-level ozone, NO2 and PM2.5, reported 1 to 10+. | index | `aqi` (a different index) |
| NAPS | `naps` | National Air Pollution Surveillance program: Canada's ambient air monitoring network, run by Environment and Climate Change Canada. | — | — |
| Ontario MECP air monitoring | `mecp` | Ambient air monitoring network of Ontario's Ministry of the Environment, Conservation and Parks (ministry name may change `<verify>`). | — | `ontario`, `moe` |
| US EPA AQS | `aqs` | Air Quality System: the US EPA's database of ambient air monitoring data from US monitors. | — | `epa` alone |
| AirNow | `airnow` | US EPA program that publishes near-real-time air quality observations; values are preliminary, not the final quality-assured record. | — | `epa` alone |
| Parameter 88101 | `aqs_param_88101` | AQS parameter code for PM2.5 "Local Conditions" from FRM/FEM monitors (exact title `<verify>`). | — | `88101` bare |
| Parameter 88502 | `aqs_param_88502` | AQS parameter code for PM2.5 from non-FRM/FEM (non-regulatory) monitors (exact title `<verify>`). | — | `88502` bare |
| FRM / FEM | `frm_fem` | Federal Reference Method / Federal Equivalent Method: EPA-designated regulatory measurement methods for PM2.5. | — | — |
| PurpleAir | `purpleair` | Commercial low-cost optical particle sensors with a public data network; raw readings usually need correction against reference monitors `<verify>`. | — | `pa` |
| ERA5 | `era5` | ECMWF/Copernicus fifth-generation global atmospheric reanalysis; hourly gridded fields such as wind. | per variable | `era-5`, `era` |
| NOAA HMS smoke | `hms_smoke` | NOAA Hazard Mapping System smoke product: analyst-drawn smoke plume polygons from satellite imagery, with density classes `<verify>`. | — | `hms` alone |
| FIRMS | `firms` | NASA Fire Information for Resource Management System: near-real-time active-fire detections from satellite sensors. | — | — |
| AOD | `aod` | Aerosol optical depth: dimensionless, column-integrated light extinction by aerosols; product and wavelength set the meaning `<verify>`. | dimensionless | `aot` |
| Satellite fire/smoke products | `satellite` | Umbrella for the satellite-derived sources (`hms_smoke`, `firms`, `aod`) where a figure or legend shows them as one source family. Data, columns and station IDs use the specific code name. | — | `sat`, `remote_sensing` |
| GBM | `gbm` | Gradient-boosted decision-tree model. | — | library names (`xgb`, `lgbm`) as a generic term |
| ST-GNN | `stgnn` | Spatio-temporal graph neural network: a graph neural network over locations that also models time. | — | `gnn` alone |

## Data terms

| Term | Canonical code name | Definition | Units | Avoid |
|---|---|---|---|---|
| station | `station_id` | One monitor of one source, `<source>:<provider id>` with leading zeros kept (`naps:060410`, `mecp:33003`, `airnow:000060410`); methodology/stations.md. | — | `monitor_id` |
| site | `site_id` | One physical location: stations of any source within 500 m (ADR 0008), named by the `station_id` of its highest-priority member. | — | `location_id` |
| completeness | `present_frac` | Fraction of hours in a period with a valid value; flagged at 0.75 (ADR 0004). | fraction | `completeness_pct` |
| hourly mean | `hourly_mean` | Mean of the readings inside one clock hour, labelled by the time convention. The minimum-valid-reading rule comes from the spec. | as the variable | `hourly_avg`, `hr_avg` |
| time_utc | `time_utc` | tz-aware UTC timestamp. Hourly tables: start of the hour (ADR 0005). | UTC | `datetime`, `timestamp`, `date`, `time_local` |
| wind speed | `wind_speed_ms` | Magnitude of the horizontal wind vector. | m/s | `ws`, `wind_mps`, `wind_kmh` |
| bytes (unit suffix) | `_bytes` | Suffix for sizes in bytes, e.g. `size_bytes`; see naming-units-time.md. | B | `_b`, `_size` |
| seconds (unit suffix) | `_s` | Suffix for durations in seconds, e.g. a network timeout `_TIMEOUT_S`; see naming-units-time.md. | s | `_sec`, `_secs`; `_ms` (that is metres per second) |
| prior outputs | `data/prior` | Old pipeline outputs from earlier CLEAR work (per-cell extracts, features, training sets, models); reference and golden numbers only, not a pipeline input. | — | `cleaned_data`, `cleaned data` as a code name |

## CLEAR-specific terms

| Term | Canonical code name | Definition | Units | Avoid |
|---|---|---|---|---|
| alert level | `alert_level` | `<defined in methodology/alert-levels.md>` | — | — |
| bad-air day | `bad_air_day` | `<defined in methodology/bad-air-events.md>` | — | — |
| event cluster | `event_cluster` | `<defined in methodology/bad-air-events.md>` | — | — |
| lag time | `lag_h` | `<defined in methodology/lag-plume.md>` | h | `lag` without a unit |
| smoke plume | `smoke_plume` | `<defined in methodology/lag-plume.md>` | — | — |
| grid | `grid` | Cells of fixed size in degrees with edges on multiples of the size, over Toronto (Phase 1: 0.1°, methodology/grid.md). | — | — |
| cell | `cell_id` | One grid cell, named by its south-west corner in hundredths of a degree, e.g. `N4360W07940`. | — | `cell_name`, `tile` |
| dynamic grid | `dynamic_grid` | `<defined in methodology/grid.md>` | — | — |
| domain | `domain` | `<defined in methodology/grid.md>` | — | — |
| target series | `target_series` | `<defined in methodology/target-pm25.md>` | — | — |
