---
source: data/raw/City of Toronto boundary/toronto-boundary-wgs84.zip
aliases: []
sha256: 7c4b32f9d4532eedcb5f533973d6b55f27370dad7b2fa91b03cfb7942e8d0a4f
converted: 2026-10-24
converter: manual
status: current
kind: data-card
dataset: toronto-city-boundary
provider: City of Toronto, Information & Technology (Geospatial Competency Centre), via Toronto Open Data
variables: [geometry]
units: {geometry: degrees (WGS 84 lon/lat)}
time_coverage: null               # static boundary; files dated 2012, CKAN last_refreshed 2019-07-23
time_convention: not applicable (no time dimension)
spatial_coverage: City of Toronto; bounds lon -79.639268..-79.115246, lat 43.581005..43.855466
rows: 1                           # one polygon feature
validation: unvalidated
validation_report: null
---

# toronto-city-boundary

## What it is
The administrative boundary of the City of Toronto as one polygon, from the Toronto Open Data
package "Regional Municipal Boundary" (resource `toronto-boundary-wgs84`, SHP in a zip). It
defines "Toronto" for Phase 1 (Ryan's decision, 2026-10-24).

## Files
`toronto-boundary-wgs84.zip` (195,966 bytes), fetched 2026-10-24 by
`src/clear/ingest/toronto_open_data.py` into `inbox/toronto-city-boundary/`, filed to `data/raw`
by `scripts/intake.py` 2026-10-24T20:56:15Z (sha256 unchanged). Contents (dated 2012-05/08):

| Member | What |
|---|---|
| `citygcs_regional_mun_wgs84.shp/.shx/.dbf/.prj/.sbn/.sbx` | ESRI shapefile |
| `citygcs_regional_mun_wgs84.shp.xml` | ArcGIS metadata (XML) |
| `citygcs.regional_mun_wgs84_metadata.pdf` | Same metadata as a 6-page PDF |
| `Regional_municipality readme file.txt` | Field list |

Read it in place: `geopandas.read_file("zip://<path>")` (`uv run --group geo`).

## Columns / variables
| Original name | Canonical name | Type | Unit | Meaning / notes |
|---|---|---|---|---|
| `AREA_ID` | — | int | — | Internal geographic id; `49886` |
| `AREA_NAME` | — | str | — | `Toronto` |
| `OBJECTID` | — | int | — | Internal object id; `13448849` |
| geometry | `geometry` | Polygon | ° | 1 polygon, no holes, 8,091 coordinates, valid |

## Coverage
- CRS: WGS 84 geographic (`.prj` `GEOGCS["WGS 84"…]`; no EPSG code in the file, so geopandas
  reports `epsg None`). Coordinates are stored x = lon, y = lat; set EPSG:4326 when reading.
- Bounds: lon −79.639268 to −79.115246, lat 43.581005 to 43.855466 (matches the PDF metadata).
- Area check: geodesic area on WGS 84 = 641.69 km² (perimeter 180.1 km). City "Toronto at a
  glance": "Toronto covers 641 sq.km" (Geospatial Competency Centre) and land area 630 km²
  (2023 indicators). 641.69 matches the total; the 11.7 km² (1.8 %) over the land area is
  consistent with water inside the boundary `<verify>` (shoreline/harbour not checked). Pass.
- Projection matters for areas: EPSG:3347 (Lambert conformal) gives 672.6 km²; UTM 17N gives 641.45.

## Time convention
Not applicable. Metadata: "final accepted and approved version … will not change unless Toronto
Council authorizes the Boundary … to change"; update frequency "not planned".

## Known issues
- CKAN `notes` call `AREA_NAME` the "former municipality" name, but the file has one feature,
  `Toronto` (the amalgamated City), not the six former municipalities.
- Package also describes an MTM 3° NAD27 version; only the WGS 84 resource is published now.
- Licence: Open Government Licence – Toronto v1.0; attribution "Contains information licensed
  under the Open Government Licence – Toronto."

## Validation
`unvalidated` — no report yet. 2026-10-24.
