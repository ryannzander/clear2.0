# figures/ — every figure, built from code

Each figure is a script `src/fig_<slug>.py` that writes `out/fig_<slug>.png`, `.svg` and a
sidecar `out/fig_<slug>.md` (caption, inputs + sha256, git commit, preset, headline flag).
Colors come only from `src/clear/viz/tokens.yaml`. Standard: [docs/standards/figures.md](../docs/standards/figures.md).

Rebuild all: `uv run clear figures build` (one: `--only <slug>`). List: `uv run clear figures list`.

Presets: `paper-1col`, `paper-2col`, `slide-16x9`, `poster`.
Headline figures need Ryan's approval before `headline: true`.

Line format: `- [fig_<slug>](out/fig_<slug>.md) — what it shows · preset · headline: false|true`.

- [fig_toronto-stations-grid](out/fig_toronto-stations-grid.md) — City boundary, 0.1° cells (grey = no active site), stations by source (#2) · paper-2col · headline: false
- [fig_station-completeness](out/fig_station-completeness.md) — fraction of hours present per Toronto station and year, splits marked (#1) · paper-2col · headline: false
- [fig_style-tokens](out/fig_style-tokens.md) — the figure language: alert colors, source colors, sequential/diverging maps, type scale · paper-2col · headline: false
