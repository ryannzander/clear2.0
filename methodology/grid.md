---
part: grid
status: accepted
owner: methodologist
sources:
  - knowledge/data/toronto-city-boundary.md
  - knowledge/data/legacy-grid-approach-tables.md
  - knowledge/data/clear-standard-grid-csg1.md
  - knowledge/docs/seagate-documents-15-the-grid-approach-the-grid-approach.md
  - knowledge/docs/seagate-documents-19-building-dynamic-grid-building-the-dynamic-grid-clear-standard-grid.md
decisions:
  - decisions/0002-toronto-city-boundary.md
  - decisions/0006-grid-0p1-toronto-cells.md
updated: 2026-10-24
---

# Grid — 0.1° cells over Toronto

## Purpose

Cover the City of Toronto with 0.1° × 0.1° cells (~11.1 km × 8.0 km at 43.7°N), place every
government station in its cell, and report which Toronto cells hold 0, 1 or more government
sites (issue #2). Phase 1 covers the Toronto core only; the domain around it (smoke
directions, warning radius, cell size) is Phase 2 (issues #3–#5).

## Inputs

| Name | Source dataset / data card | Units | Time convention |
|---|---|---|---|
| City boundary | `knowledge/data/toronto-city-boundary.md` | ° (WGS 84) | none |
| Station registry | `methodology/stations.md` output `registry.parquet` | ° | UTC |

## Outputs

| Name | Schema | Units |
|---|---|---|
| `data/processed/grid/toronto_0p1.parquet` | `clear.schemas.grid.CELLS` | °, fraction, counts |
| `data/processed/grid/station_cells_0p1.parquet` | `clear.schemas.grid.STATION_CELLS` | ° |

## Method

### Build cells

Snap the City's bounds outward to multiples of `cell_size_deg` and cut cells with edges on
those multiples (ADR 0006). Each cell: `cell_id`, `row` = floor(lat_south / size), `col` =
floor(lon_west / size), edges `lat_min_deg`, `lat_max_deg`, `lon_min_deg`, `lon_max_deg`, and
centre `lat_center_deg`, `lon_center_deg`. `cell_id` names the south-west corner in hundredths
of a degree, as CSG-1 does: `N4360W07940` = the cell 43.6–43.7°N, 79.4–79.3°W.

### Select Toronto cells

`city_frac` = area of (cell ∩ City polygon) / cell area, computed in lon/lat (the ratio
is unaffected at this cell size). `is_in_toronto` = `city_frac > 0` (ADR 0006: any overlap).

### Assign stations

Each registry station goes to the cell that contains its point (`row`, `col` by floor, so a
point on an edge goes north/east). Stations outside the built cells get no cell.

### Coverage report

Per Toronto cell: `n_stations`, `n_sites` (distinct `site_id`), `n_sites_active` (sites with
data on or after the first training year, `config/splits.yaml`), the sites in the cell, and
`coverage_class` = `0`, `1` or `>1` active sites. Every registry station whose point lies in
the cell counts, also one just outside the City in an edge cell (e.g. Mississauga in
`N4360W07970`). Issue #2's one-station-per-cell rule is reported, not enforced.

## Constants

| Name | Value | Config key | Justification / ADR |
|---|---|---|---|
| cell size | 0.1° | `config/grid.yaml: toronto_grid.cell_size_deg` | issue #2; ADR 0006 |
| Toronto cell rule | any overlap | `config/grid.yaml: toronto_grid.min_city_frac` (0 = any) | ADR 0006 |

## Decisions

- [0002-toronto-city-boundary](../decisions/0002-toronto-city-boundary.md) — Toronto = City polygon
- [0006-grid-0p1-toronto-cells](../decisions/0006-grid-0p1-toronto-cells.md) — alignment, Toronto cells

## Open questions

1. The domain extent and a larger cell size are Phase 2 (issues #3–#5); `config/grid.yaml:
   domain` stays provisional until then.

## Validation criteria

- Cells tile the snapped bounds without gaps or overlaps; every `cell_id` is unique.
- The sum of `city_frac` × cell area matches the City area within 1%.
- Every Toronto station lands in a Toronto cell.

## Golden numbers

| Number | Value (from old doc) | Source mirror path | Test name |
|---|---|---|---|
| City split across old 0.5° cells at −79.5° | 483.9 / 157.8 km² | `knowledge/data/legacy-grid-approach-tables.md` | not tested (different cell size) |

## Sources

- `knowledge/data/toronto-city-boundary.md` — City polygon, area check
- `knowledge/data/legacy-grid-approach-tables.md`, `knowledge/data/clear-standard-grid-csg1.md` — old grid alignment
- `knowledge/docs/seagate-documents-15-the-grid-approach-the-grid-approach.md` — old grid approach
- `knowledge/docs/seagate-documents-19-building-dynamic-grid-building-the-dynamic-grid-clear-standard-grid.md` — CSG-1
