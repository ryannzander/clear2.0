---
source: data/raw/seagate/Documents/19. Building Dynamic Grid
aliases: []
sha256: null                      # folder card: per-file hashes in manifests/inventory.csv
converted: 2026-10-24
converter: manual
status: current
kind: data-card
dataset: clear-standard-grid-csg1
provider: CLEAR legacy work (Hugo Bui & Ryan Zander), derived; not a provider dataset
variables: [geometry, centre_lat_deg, centre_lon_deg, width_deg, area_km2, land_frac, n_gov_monitors]
units: {centre_lat_deg: °, centre_lon_deg: °, width_deg: °, area_km2: km², land_frac: 0-1, n_gov_monitors: count}
time_coverage: null               # static grid; gov_monitors counts monitors active since 2021 (Read me sheet)
time_convention: not applicable (no time dimension)
spatial_coverage: 6,418 cells touching land in Canada, Alaska, lower 48, plus Great Lakes open water; lat 24.5-83.5N, lon 179.0-52.5W
rows: 6418                        # cells (geojson features = xlsx "Cells" rows)
validation: unvalidated
validation_report: null
---

# clear-standard-grid-csg1

## What it is
The old "CLEAR Standard Grid, version 1" (CSG-1): rows 0.5° of latitude, east–west width
stepping up with latitude so every point is within 45 km of its cell centre. One row is one cell.
Reference for the grid ADR only, not a pipeline input. Explained by the mirror
[building-the-dynamic-grid](../docs/seagate-documents-19-building-dynamic-grid-building-the-dynamic-grid-clear-standard-grid.md).
Made by `scripts/dynamic_grid/clear_grid.py` and `03_build_grid.py` per that doc (legacy code in
`inbox/seagate/legacy-code/scripts/dynamic_grid/`, not opened).

## Files
| File | What |
|---|---|
| `CLEAR_Standard_Grid_CSG-1.geojson` | FeatureCollection "CLEAR Standard Grid CSG-1", 6,418 Polygon features (5-point rings), properties = the 19 columns below |
| `CLEAR_Standard_Grid_CSG-1.xlsx` | Sheets: Read me, Zones (zone table), Cells (6,418 rows, same names and values as the geojson; checked centre and `gov_monitors`), Examples, Cell counts, Coverage by latitude, Effective radius |

## Columns / variables
| Original name | Canonical name | Type | Unit | Meaning / notes |
|---|---|---|---|---|
| `name` | `cell_id` `<verify>` (not in GLOSSARY) | str | — | South-west corner: `N`/`S` + lat × 100 (4 digits) + `E`/`W` + abs(lon) × 100 (5 digits); e.g. `N4350W07950` |
| `row` | — | int | — | lat_south ÷ 0.5 + 180 (counted from the south pole) |
| `col` | — | int | — | lon_west ÷ width + 180 ÷ width (counted from 180°W within the row's zone) |
| `lat_south`, `lat_north` | — | float | ° | Row edges, multiples of 0.5° |
| `lon_west`, `lon_east` | — | float | ° | Column edges, multiples of the row's width |
| `centre_lat`, `centre_lon` | `centre_lat_deg`, `centre_lon_deg` | float | ° | Cell centre |
| `width_deg` | `width_deg` | float | ° | East–west width from the zone table |
| `ns_km`, `ew_km` | — | float | km | Cell size; `ns_km` is 55.66 everywhere |
| `centre_to_corner_km` | — | float | km | ≤ 45 km by design |
| `area_km2` | `area_km2` | float | km² | |
| `country` | — | str | — | `Canada` 3,377, `Lower 48` 2,466, `Alaska` 560, `Great Lakes` 15 |
| `region` | — | str | — | Province or state |
| `land_fraction` | `land_frac` | float | 0–1 | |
| `gov_monitors` | `n_gov_monitors` | int | count | US EPA 88101/88502 active since 2021, and ON, QC, NAPS monitors in ON/QC only |
| `monitor_lists_complete` | — | bool | — | FALSE for 2,564 Canadian cells outside ON/QC (their monitors are not counted) |

## Grid geometry (Phase 1 facts)
- CRS: no `crs` member in the geojson, so RFC 7946 WGS 84 lon/lat; geopandas reads EPSG:4326.
- Cell size: 0.5° latitude everywhere; width by zone: 0.5° (0–32°N), **0.75° (32–50.5°N, includes
  Toronto)**, 1.0° (50.5–59.5°N), 1.25°, 1.5°, 2°, 2.5°, 3°, 3.75°, 4.5°, 5° further north.
  At Toronto a cell is 0.5° × 0.75° ≈ 55.7 km × 60.3 km, 3,357 km².
- Alignment: **edges on multiples, not centres.** South edges are multiples of 0.5°; west edges
  are multiples of the zone width (here 0.75°, from Greenwich), so every edge is on the 0.25°
  lattice. Checked on all 6,418 cells, and every `name` equals the south-west-corner rule.
- Cells near Toronto:

| Name | Lat edges | Lon edges | Centre | gov_monitors | land_fraction |
|---|---|---|---|---|---|
| N4350W07950 | 43.5–44.0 | −79.50 to −78.75 | 43.75, −79.125 | 4 | 0.447 |
| N4350W08025 | 43.5–44.0 | −80.25 to −79.50 | 43.75, −79.875 | 5 | 0.976 |
| N4300W07950 | 43.0–43.5 | −79.50 to −78.75 | 43.25, −79.125 | 1 | 0.512 |

- Toronto present: yes. The City of Toronto boundary
  ([toronto-city-boundary](toronto-city-boundary.md)) falls in 2 cells, split at −79.50°:
  N4350W07950 holds 483.9 km² of the City, N4350W08025 157.8 km² (geodesic, 2026-10-24).
  Toronto's point (43.65, −79.38) is in N4350W07950, as the doc's Examples sheet states.

## Coverage
6,418 cells, lat 24.5–83.5°N, lon 179.0–52.5°W. Domain per the Read me sheet: cells touching land
in Canada, Alaska or the lower 48, plus open-water Great Lakes cells. The doc's Adak example
(176°E) is not in the grid file.

## Time convention
Not applicable.

## Known issues
- Monitor counts are incomplete for Canada outside Ontario and Québec (`monitor_lists_complete`).
- Edge rule (points on an edge go north/east) is documented, not encoded in the file.

## Validation
`unvalidated` — reference only. 2026-10-24.
