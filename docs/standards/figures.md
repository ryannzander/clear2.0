# Figure standard

Every figure is code. A script in `figures/src/` builds it; `clear.viz` supplies style,
color and saving. Time labels: [naming-units-time.md](naming-units-time.md#time-rules).
Skill: `/figure`. Map: `figures/INDEX.md`.

## The figure language

Matplotlib through `clear.viz` (`src/clear/viz/`):

| Call | Use it to |
|---|---|
| `use_style()` | Apply `clear.mplstyle` (fonts, grid, spines, sizes). First line of every figure. |
| `color(role)` | Get a color by semantic role. The only way to get a color. |
| `alert_cmap()` | Get the alert-level colormap and norm. |
| `preset(name)` | Get size and font settings for an output target. |
| `save_figure(fig, slug, *, caption, inputs, preset, headline=False)` | Write png + svg + sidecar. |
| `map_axes(fig)` | Add a map panel in the CLEAR projection, zoomed to the study domain. |
| `plotly_template()` | Same tokens for the dashboard. |

Exact signatures and return types: `src/clear/viz/__init__.py` (it wins on conflict).

```python
"""Figure <slug>. Spec: methodology/<part>.md#<section>."""
import matplotlib.pyplot as plt
from clear.viz import color, preset, save_figure, use_style

use_style()
p = preset("paper-1col")
fig, ax = plt.subplots(figsize=p.figsize)          # attribute name: check viz/__init__.py
ax.plot(df["time_utc"], df["pm25_ugm3"], color=color("source.<name>"))
ax.set_ylabel("PM2.5 (µg/m³)")
ax.set_xlabel("Time (UTC)")
save_figure(fig, "<slug>", caption="<one sentence>", inputs=["<path>"], preset="paper-1col")
```

## Colors: `src/clear/viz/tokens.yaml`

Colors are **semantic roles**. Read `tokens.yaml` for the exact keys; do not copy values.

| Role family | Rule |
|---|---|
| Alert levels | CLEAR alert palette aligned to the official AQHI colors. **PROVISIONAL** until `methodology/alert-levels.md` is spec'd. |
| Continuous PM2.5 | `cividis`, with breakpoints at the alert thresholds. Thresholds come from `config/`, never typed into a figure. |
| Categorical | Okabe-Ito (colorblind-safe). Same category, same color across figures. |
| Data source | One permanent color per source, keyed by its GLOSSARY code name (`source.naps`, `source.mecp`, `source.aqs`, ...). Never reused for something else. |
| Neutrals | Text, grid, background, "missing data". |

- New color need → add a role to `tokens.yaml` (reviewed change), then use it.
- Check every figure in grayscale and for color-vision deficiency before it ships.
- Alert colors mean the alert level and nothing else.

## Presets

| Preset | Target |
|---|---|
| `paper-1col` | Single column of a journal page |
| `paper-2col` | Full page width |
| `slide-16x9` | 16:9 presentation slide |
| `poster` | Poster panel; larger fonts and lines |

Size, DPI and font sizes live in the preset. A figure script never sets `figsize` by hand.

## Maps

- Library: `cartopy` (install with `uv sync --group geo`).
- One fixed projection: **Lambert Conformal Conic, Canada-centred**, in `tokens.yaml`.
  `viz.map_axes(fig)` builds every map panel; a figure script never creates its own
  projection or extent.
- Extent: the study domain from `config/grid.yaml` (`viz.map_domain()`), **PROVISIONAL**
  until `methodology/grid.md`. Other extents are added to `clear.viz`, not set inline.
- Data in geographic coordinates (`lat_deg`, `lon_deg`) is drawn with an explicit source
  transform.
- Mark the scale (km) and name the projection and extent in "what it shows".

## Plotly (dashboard)

- Use `plotly_template()`. It reads the same `tokens.yaml`, so dashboard and paper match.
- Hover and axis text carry units and the time zone. The dashboard shows Toronto local
  time, labelled (see Time below).

## Time on figures

- Data is UTC until the last step. Local Toronto time is allowed here, and only here.
- Every time axis says the zone: "Time (UTC)" or "Time (Toronto local, EST/EDT)".
- Never mix both on one axis. If both matter, use two labelled panels or a secondary axis.

## Provenance

Command: `uv run clear figures build [--only SLUG]`; list with `uv run clear figures list`.

```
figures/src/fig_<slug>.py      the code (reviewed)
figures/out/fig_<slug>.png     raster
figures/out/fig_<slug>.svg     vector
figures/out/fig_<slug>.md      sidecar
```

Sidecar fields (written by `save_figure`; do not hand-edit):

| Field | Content |
|---|---|
| caption | One or two sentences, ready for a paper |
| what it shows | Plain description of axes, groups, period, units |
| inputs | Each input path with its sha256 |
| git commit | Commit of the code that built it; `<sha>-dirty` if the script, an input or `src/clear/` differs from it or is untracked; `uncommitted` before the first commit |
| preset | One of the four presets |
| headline | `false` or `true` |

## Headline gate

- `headline: false` by default. Only the Lead sets `true`, and only after Ryan has seen
  the figure ([AGENTS.md](../../AGENTS.md) rule 5).
- Anything headed for a paper, pitch or competition entry is headline.
- Changing the data or code behind a `true` figure resets it to `false` until Ryan re-approves.

## Do / Don't

| Do | Don't |
|---|---|
| Get every color from `color(role)` or `alert_cmap()` | Write a hex code, RGB tuple or named color outside `tokens.yaml` |
| Rebuild the figure from its script | Edit png/svg by hand, or touch it up in another tool |
| Use cividis, Okabe-Ito, the alert palette | Use rainbow, jet, hsv or any non-perceptual colormap |
| Label units on every axis and colorbar | Leave a quantity unitless |
| Label UTC vs Toronto local | Show an unlabelled time axis |
| Take thresholds and extents from `config/` and presets | Hard-code a threshold line or `figsize` |
| Write the caption so it stands alone | Say "see text" in a caption |
| Keep the script for one figure per file | Share state between figure scripts |

## Diagrams (Mermaid)

Diagrams are Mermaid in markdown. Use the same node shapes everywhere.

| Shape | Mermaid | Meaning |
|---|---|---|
| Cylinder | `[(...)]` | Data or a folder of artifacts |
| Box | `[...]` | Process or script |
| Diamond | `{...}` | Decision |
| Hexagon | `{{...}}` | Human gate (Ryan) |
| Rounded | `(...)` | Agent |

- Source of the shape table: [00-overview.md](../system/00-overview.md#node-shapes-used-in-every-diagram-in-this-repo).
- Prefer `flowchart LR`; fewer than ~15 nodes per diagram; label edges with the action.
- Mermaid is for process and structure. Data plots are matplotlib figures.
