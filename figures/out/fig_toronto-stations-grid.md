---
slug: toronto-stations-grid
caption: 0.1° cells over the City of Toronto (Lambert conformal, Canada-centred).
  Bold cells overlap the City; grey ones hold no government site with data since 2021.
  Markers are NAPS, Ontario MECP and AirNow stations inside the City, all years; co-located
  markers overlap (one site, several networks).
preset: paper-2col
headline: false
inputs:
- path: data/processed/grid/toronto_0p1.parquet
  sha256: 9ba6fb7deac3091907d2e31560575a85ace56a3f09040afd87013aa4b1f89eee
- path: data/processed/stations/registry.parquet
  sha256: ab93436704e85c37c31ca2d06aea0893694e2a2481ebad752c41ff180c4246f7
- path: data/raw/City of Toronto boundary/toronto-boundary-wgs84.zip
  sha256: 7c4b32f9d4532eedcb5f533973d6b55f27370dad7b2fa91b03cfb7942e8d0a4f
script: figures/src/fig_toronto-stations-grid.py
git_commit: b288303-dirty
generated_utc: '2026-10-25T00:07:03Z'
---

# fig_toronto-stations-grid

0.1° cells over the City of Toronto (Lambert conformal, Canada-centred). Bold cells overlap the City; grey ones hold no government site with data since 2021. Markers are NAPS, Ontario MECP and AirNow stations inside the City, all years; co-located markers overlap (one site, several networks).

## What it shows

Map, lon -79.7 to -79.1, lat 43.5 to 43.9 (about 48 km x 44 km). Each Toronto cell is labelled with its cell_id and number of active government sites. Station markers by source: circle NAPS, square MECP, triangle AirNow.
