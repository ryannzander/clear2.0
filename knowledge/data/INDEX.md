# knowledge/data/ — data cards for every `data/raw` and `data/prior` dataset

One card per dataset: `<dataset-slug>.md`. Cards hold provider, variables, units, time
coverage, time convention, spatial coverage, rows and validation status. Agents read the
card, never the raw file. Validation reports sit beside the card as `<dataset-slug>.validation.md`.
Prior-output cards have `source: data/prior/<folder>`.

Line format: `- [dataset-slug](dataset-slug.md) — what it is · validation: unvalidated|partial|validated · time and space coverage`.

Provenance of each dataset: [data/sources.yaml](../../data/sources.yaml). Pipeline outputs: [data/INDEX.md](../../data/INDEX.md).

## Raw (`data/raw`)

- [airnow-hourlyaqobs](airnow-hourlyaqobs.md) — AirNow HourlyAQObs PM2.5, monthly parquet, UTC hour-beginning, preliminary · validation: partial ([report](airnow-hourlyaqobs.validation.md)) · 2019-05-29 to 2026-10-08 UTC; US + Canada, 1,841 sites, 4 Toronto in 2026
- [airnow-hourlydata-2014-2019](airnow-hourlydata-2014-2019.md) — AirNow HourlyData PM2.5 (no coordinates) + site-location snapshots, UTC hour-beginning · validation: partial ([report](airnow-hourlydata-2014-2019.validation.md)) · 2014-01 to 2019-05-28 UTC; 1,436 sites, 1 Toronto
- [clear-standard-grid-csg1](clear-standard-grid-csg1.md) — old CLEAR Standard Grid CSG-1 (geojson + xlsx): 0.5° rows, zone widths (0.75° at Toronto), edges on multiples, SW-corner names; reference only · validation: unvalidated · static; 6,418 cells, Canada + US, Toronto in N4350W07950/N4350W08025
- [legacy-grid-approach-tables](legacy-grid-approach-tables.md) — old uniform 0.5° grid within 1,000 km of Toronto, cell table + type counts; edges on 0.5° multiples; reference only · validation: unvalidated · static; 1,416 cells, Toronto in (87,−159)/(87,−160)
- [mecp-hourly-pm25](mecp-hourly-pm25.md) — Air Quality Ontario hourly PM2.5, yearly CSVs (all stations; `_124_` = PM2.5), wide H01–H24, EST, 9999/-999 missing · validation: partial ([report](mecp-hourly-pm25.validation.md)) · 2003–2025; Ontario, 57 stations, 6 Toronto
- [naps-hourly-pm25](naps-hourly-pm25.md) — ECCC NAPS hourly PM2.5, yearly CSVs, wide H01–H24, hour-ending LST, -999 missing · validation: partial ([report](naps-hourly-pm25.validation.md)) · 2000–2024; Canada, 358 stations, 13 Toronto
- [toronto-city-boundary](toronto-city-boundary.md) — City of Toronto boundary polygon, WGS 84 shapefile zip (Toronto Open Data) · validation: validated ([report](toronto-city-boundary.validation.md)) · static; 641.7 km², 1 feature

## Prior (`data/prior`)

- [prior-stations](prior-stations.md) — old pipeline station lists and registries, 26 parquet tables; reference only · validation: unvalidated · 2008–2026; Canada + US
