---
source: data/raw/seagate/Documents/15. The Grid Approach
aliases: []
sha256: null                      # folder card: per-file hashes in manifests/inventory.csv
converted: 2026-10-24
converter: manual
status: current
kind: data-card
dataset: legacy-grid-approach-tables
provider: CLEAR legacy work (Hugo Bui & Ryan Zander), derived; not a provider dataset
variables: [centre_lat_deg, centre_lon_deg, distance_km, n_monitors, n_gov_monitors]
units: {centre_lat_deg: °, centre_lon_deg: °, distance_km: km, n_monitors: count, n_gov_monitors: count}
time_coverage: null               # static grid; monitor counts use monitors active since 2018 (per the doc)
time_convention: not applicable (no time dimension)
spatial_coverage: 1,416 cells of 0.5° x 0.5° whose centre is within ~1,000 km of Toronto (43.65N, 79.38W); lat 34.5-52.5N, lon 92.0-67.0W
rows: 1416                        # grid_cells_by_country.csv; grid_cell_counts.csv has 6 summary rows
validation: unvalidated
validation_report: null
---

# legacy-grid-approach-tables

## What it is
Two tables behind the old "Grid Approach" documents: the uniform 0.5° grid within 1,000 km of
Toronto, one row per cell, and a 6-line cell-type summary. Reference for the grid ADR only, not a
pipeline input. Explained by the mirrors
[the-grid-approach](../docs/seagate-documents-15-the-grid-approach-the-grid-approach.md) and
[the-grid-methodology](../docs/seagate-documents-15-the-grid-approach-the-grid-methodology.md).
Script that wrote them: `<verify>` (not named in the docs).

## Files and columns
`grid_cells_by_country.csv` (1,416 rows, comma-separated, header row):

| Original name | Canonical name | Type | Unit | Meaning / notes |
|---|---|---|---|---|
| `iy` | — | int | — | Row index = floor(lat ÷ 0.5); 69–104 |
| `ix` | — | int | — | Column index = floor(lon ÷ 0.5); −184 to −135 |
| `clat` | `centre_lat_deg` | float | ° | Cell centre = (iy + 0.5) × 0.5 |
| `clon` | `centre_lon_deg` | float | ° | Cell centre = (ix + 0.5) × 0.5 |
| `km` | `distance_km` | float | km | Great-circle distance from Toronto (43.65, −79.38) to the centre (haversine, R ≈ 6,371 km; matches to 0.0015 km) |
| `n` | `n_monitors` | float | count | Monitors in the cell, government + PurpleAir; sums to 1,931 |
| `gov` | `n_gov_monitors` | float | count | Government monitors (ON, QC, NAPS, US EPA); sums to 542 |
| `country` | — | str | — | `Canada` 501, `US` 682, `Water` 233 (by cell centre) |
| `region` | — | str | — | Province or state; empty for water |
| `kind` | — | str | — | `gov` 287 (gov > 0), `pa` 223 (PurpleAir only), `none` 906 |

`grid_cell_counts.csv` (6 rows; header `,0`, i.e. unnamed index and value): `v_hrrr` 845,
`gov` 287, `pa` 223, `v_fw` 61, `total` 1416, `empty_water` 233. Per the methodology mirror,
`v_hrrr` = empty cells to fill from FireWork + HRRR-Smoke + satellite, `v_fw` = empty cells north
of the HRRR-Smoke domain (FireWork + satellite only). 845 + 61 = 906 = `kind none`.

## Grid geometry (Phase 1 facts)
- CRS: plain WGS 84 lon/lat degrees by construction (floor of degrees); no CRS stated in the file.
- Cell size: 0.5° × 0.5° (55.6 km N–S, 40.3 km E–W at 43.65°N per the doc).
- Alignment: **edges on 0.5° multiples, centres at .25/.75**. Checked on all 1,416 rows:
  iy = floor(clat ÷ 0.5), ix = floor(clon ÷ 0.5), centre = (index + 0.5) × 0.5.
- Cell id: the pair (`iy`, `ix`); no string name.
- Cells near Toronto:

| iy, ix | Lat edges | Lon edges | Centre | km to Toronto | n / gov |
|---|---|---|---|---|---|
| 87, −159 | 43.5–44.0 | −79.5 to −79.0 | 43.75, −79.25 | 15.3 | 29 / 4 |
| 87, −160 | 43.5–44.0 | −80.0 to −79.5 | 43.75, −79.75 | 31.8 | 11 / 5 |
| 86, −159 | 43.0–43.5 | −79.5 to −79.0 | 43.25, −79.25 | 45.7 | 4 / 1 |

- Toronto present: yes. The City of Toronto boundary
  ([toronto-city-boundary](toronto-city-boundary.md)) falls in 2 cells, split at −79.5°:
  (87, −159) holds 483.9 km² of the City, (87, −160) 157.8 km² (geodesic, 2026-10-24).

## Coverage
Rows 69–104 (34.5–52.5°N), columns −184 to −135 (92.0–67.0°W). Cells whose centre is within
1,000 km of Toronto plus edge cells with a monitor.

## Time convention
Not applicable.

## Known issues
- The docs say "two edge cells just beyond 1,000 km"; the table has 3 cells with `km` > 1,000
  (69/−164 at 1,010.4 km, 82/−183 at 1,008.8 km, both `gov`; 84/−184 at 1,017.8 km, `pa`).
- `n` and `gov` are floats although they are counts.
- Monitor set: "active since 2018" per the doc; the station list it used is not in this folder.

## Validation
`unvalidated` — reference only. 2026-10-24.
