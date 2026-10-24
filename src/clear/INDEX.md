# src/clear/ — the CLEAR package

One module per methodology part, named like its spec slug (`methodology/<slug>.md` →
`src/clear/<slug_with_underscores>/`). Parts are added in Phase 4. Standard:
`docs/standards/code.md`.

## Foundation (Phase 0)

- [__init__.py](__init__.py) — package version · stable
- [cli.py](cli.py) — `uv run clear` entry point; mounts sub-apps (`figures`, more per part) · stable
- [geo.py](geo.py) — `Bounds`, `read_city_boundary()`, `city_bounds()`, `in_city()`: the City of Toronto polygon (ADR 0002) · stable
- [paths.py](paths.py) — repo root, `data_dir()` and standard folders; `CLEAR_ROOT` overrides · stable
- [config.py](config.py) — `ConfigModel` + `load_config(name, Model)` for `config/<name>.yaml` · stable
- [timeutil.py](timeutil.py) — `to_utc()` source timestamps → tz-aware UTC; `lst_zone()` · hour-beginning label (ADR 0005) · stable
- [schemas/common.py](schemas/common.py) — pandera pieces: `time_utc_column()`, `concentration_column()` · stable
- [viz/__init__.py](viz/__init__.py) — figure language API: `use_style`, `new_figure`, `color`, `save_figure`, `map_axes`, `plotly_template` · stable
- [viz/tokens.py](viz/tokens.py) — typed models of `tokens.yaml`: `load_tokens()`, `preset()` · stable
- [viz/save.py](viz/save.py) — `save_figure()`: png + svg + sidecar (input sha256, git commit, `-dirty` flag) · stable
- [viz/maps.py](viz/maps.py) — `map_axes()`, `map_projection()`, `map_domain()` (domain from `config/grid.yaml`); `map_axes(lonlat_box_deg=…)` for a lon/lat extent · domain PROVISIONAL (Phase 2)
- [viz/tokens.yaml](viz/tokens.yaml) — the only home of colors, fonts, size presets, map projection · alert colors provisional
- [viz/clear.mplstyle](viz/clear.mplstyle) — matplotlib layout rules (no colors) · stable
- [viz/cli.py](viz/cli.py) — `clear figures build [--only SLUG]` and `clear figures list` · stable

## Ingest (fetch modules, `/ingest`)

- [ingest/toronto_open_data.py](ingest/toronto_open_data.py) — download one Toronto Open Data (CKAN) resource into `inbox/`; `python -m clear.ingest.toronto_open_data` · stable

## Methodology parts

- [stations/](stations/) — `methodology/stations.md`: `readers` (NAPS, MECP, AirNow → lossless long UTC tables), `qc` (ADR 0007), `registry` (stations, 500 m site crosswalk), `completeness`, `combine` (merged series), `report`, `pipeline`, `cli` (`clear stations build|report`) · built
- [grid/](grid/) — `methodology/grid.md`: `cells` (0.1° cells, City fraction), `assign` (stations → cells, coverage), `pipeline`, `cli` (`clear grid build`) · built
- [schemas/stations.py](schemas/stations.py), [schemas/grid.py](schemas/grid.py) — pandera schemas of both parts' outputs · stable
