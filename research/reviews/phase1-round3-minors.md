# Phase 1 review — deferred minors (round 3, pass)

Combined review of 8d1bb27 (`feat: Phase 1 stations + grid`) passed in round 3 with no
blockers. These minors are open; fix them when the stations/grid code is next touched.

1. Contract tests: a good frame for MERGED and STATION_CELLS (incl. null `cell_id`); unique-key
   bad frames for COMPLETENESS and CELLS; naive `first_time_utc` and bad `source` for REGISTRY.
2. `clear.geo.read_city_boundary`: test the no-CRS, projected-CRS and empty-file paths
   (tiny shapefile zips, `pytest.importorskip("geopandas")`).
3. Size: `readers.py` 408 lines; `build_stations` 102, `toronto_report` 95, `completeness` 78,
   `read_airnow` 64, `map_axes` 57 lines. Move AirNow to its own module; extract a
   validate-then-write helper and a metrics builder.
4. Docstrings without Parameters/Returns: `cell_id`, `hour_index`, `Bounds.expanded`,
   `StationsOutputs.interim`, `StationsConfig.source`; DataFrame shapes nowhere.
5. `report.py` `fillna(0)` in `mean_present_frac` / `merged_vs_best_member`: keep NaN or assert.
6. Figures: "2021+", "8 October", "2000-2026" and the lon/lat extent are hard-coded in
   captions; "Bold cells" does not match the drawing (same line width).
7. `fig_station-completeness`: "not active" grey is close to mid-cividis; use a hatch or a more
   distinct neutral and check in greyscale.
8. `figures.md#maps` does not mention `map_axes(lonlat_box_deg=…)`; update it or add a named
   extent helper in `clear.viz`.
9. Names: config booleans `hour_ending`, `negative_is_missing` lack `is_`; counts
   `complete_years`, `toronto_stations`, `toronto_sites`, `cells_built` lack `n_`.
10. stations.md and ADR 0005 say "the build re-checks" MECP's hour label; only `report` and
    the validation driver do. Assert it in the build or reword.
11. Validation driver: lag row always writes 0 failing; years from interim not registry; "one
    polygon" not checked; area tolerance hard-coded; no "no sentinel survives" check.
12. MECP parser silently skips digit-keyed non-date lines and cells after H24; make it raise.
13. `build_registry` inner join drops stations with no valid hour silently; count or test it.
14. `src/clear/INDEX.md` stations line misses `settings`; code.md layout table has no `geo.py`.
15. One 95-file commit instead of logical units (accepted for this phase; split next time).
