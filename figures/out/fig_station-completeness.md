---
slug: station-completeness
caption: Fraction of hours with a valid PM2.5 value per station and UTC year, for
  every NAPS, Ontario MECP and AirNow station inside the City of Toronto. Grey = not
  active. Vertical lines mark the train, validation and test splits; 2026 runs to
  8 October.
preset: paper-2col
headline: false
inputs:
- path: data/processed/stations/registry.parquet
  sha256: ab93436704e85c37c31ca2d06aea0893694e2a2481ebad752c41ff180c4246f7
- path: data/processed/stations/completeness.parquet
  sha256: 5aef534297f51ec378d400e035668d30e254592bb8cd07f4a0cb782e9a4d11ed
script: figures/src/fig_station-completeness.py
git_commit: cf5d49b-dirty
generated_utc: '2026-10-24T22:40:15Z'
---

# fig_station-completeness

Fraction of hours with a valid PM2.5 value per station and UTC year, for every NAPS, Ontario MECP and AirNow station inside the City of Toronto. Grey = not active. Vertical lines mark the train, validation and test splits; 2026 runs to 8 October.

## What it shows

Heatmap; rows are stations labelled with their site (co-located stations share a site), columns are years 2000-2026, color is the fraction of hours present (cividis, 0-1).
