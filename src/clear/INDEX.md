# src/clear/ — the CLEAR package

One module per methodology part, named like its spec slug (`methodology/<slug>.md` →
`src/clear/<slug_with_underscores>/`). Parts are added in Phase 4. Standard:
`docs/standards/code.md`.

## Foundation (Phase 0)

- [__init__.py](__init__.py) — package version · stable
- [cli.py](cli.py) — `uv run clear` entry point; mounts sub-apps (`figures`, more per part) · stable
- [paths.py](paths.py) — repo root and standard folders; `CLEAR_ROOT` overrides · stable
- [config.py](config.py) — `ConfigModel` + `load_config(name, Model)` for `config/<name>.yaml` · stable
- [timeutil.py](timeutil.py) — `to_utc()` source timestamps → tz-aware UTC; `lst_zone()` · hour-beginning label PROVISIONAL (open question, STATUS.md)
- [schemas/common.py](schemas/common.py) — pandera pieces: `time_utc_column()`, `concentration_column()` · stable
- [viz/__init__.py](viz/__init__.py) — figure language API: `use_style`, `new_figure`, `color`, `save_figure`, `map_axes`, `plotly_template` · stable
- [viz/tokens.py](viz/tokens.py) — typed models of `tokens.yaml`: `load_tokens()`, `preset()` · stable
- [viz/save.py](viz/save.py) — `save_figure()`: png + svg + sidecar (input sha256, git commit, `-dirty` flag) · stable
- [viz/maps.py](viz/maps.py) — `map_axes()`, `map_projection()`, `map_domain()` (domain from `config/grid.yaml`) · domain PROVISIONAL
- [viz/tokens.yaml](viz/tokens.yaml) — the only home of colors, fonts, size presets, map projection · alert colors provisional
- [viz/clear.mplstyle](viz/clear.mplstyle) — matplotlib layout rules (no colors) · stable
- [viz/cli.py](viz/cli.py) — `clear figures build [--only SLUG]` and `clear figures list` · stable

## Methodology parts (Phase 4)

<one line per part module, added as each is built>
