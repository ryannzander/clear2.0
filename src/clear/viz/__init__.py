"""CLEAR figure language: style, colors, size presets, maps and provenance-tracked saving.

Every figure script uses this package and nothing else for visual decisions. Colors,
fonts, sizes and the map projection come from ``tokens.yaml`` (:mod:`clear.viz.tokens`);
layout rules from ``clear.mplstyle``; the map domain from ``config/grid.yaml``
(:mod:`clear.viz.maps`); saving from :mod:`clear.viz.save`.
Standard: ``docs/standards/figures.md``.

Typical script::

    from clear import viz

    viz.use_style("paper-2col")
    fig, ax = viz.new_figure("paper-2col")
    ax.plot(x, y, color=viz.color("source.naps"))
    viz.save_figure(fig, "naps-hourly", caption="...", inputs=["data/processed/x.parquet"],
                    preset="paper-2col")
"""

from collections.abc import Sequence
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from cycler import cycler
from matplotlib.axes import Axes
from matplotlib.colors import BoundaryNorm, Colormap, ListedColormap
from matplotlib.figure import Figure

from clear.viz.maps import MapDomain, map_axes, map_domain, map_projection
from clear.viz.save import SavedFigure, save_figure
from clear.viz.tokens import (
    AlertLevels,
    Fonts,
    MapProjection,
    MapTokens,
    Preset,
    Tokens,
    load_tokens,
    preset,
)

__all__ = [
    "AlertLevels",
    "Fonts",
    "MapDomain",
    "MapProjection",
    "MapTokens",
    "Preset",
    "SavedFigure",
    "Tokens",
    "alert_cmap",
    "color",
    "load_tokens",
    "map_axes",
    "map_domain",
    "map_projection",
    "new_figure",
    "plotly_template",
    "pm25_cmap",
    "pm25_norm",
    "preset",
    "save_figure",
    "use_style",
]

STYLE_PATH = Path(__file__).with_name("clear.mplstyle")


def color(role: str) -> str:
    """Resolve a semantic color role to a hex string.

    Method: docs/standards/figures.md#colors-srcclearviztokensyaml

    Parameters
    ----------
    role : str
        ``alert.<level>``, ``source.<source>``, ``neutral.<name>``, ``cat.<index>``
        or ``aqhi.<value>``, e.g. ``"alert.high"``, ``"source.purpleair"``, ``"cat.0"``.
        ``<source>`` is a GLOSSARY.md canonical code name.

    Returns
    -------
    str
        Hex color such as ``"#0072B2"``.

    Raises
    ------
    KeyError
        If the role is unknown. Add new roles to ``tokens.yaml``, never inline a hex code.
    """
    tokens = load_tokens()
    group, _, key = role.partition(".")
    tables: dict[str, dict[str, str]] = {
        "alert": tokens.alert_levels.colors,
        "source": tokens.sources,
        "neutral": tokens.neutrals,
        "aqhi": tokens.aqhi_scale,
        "cat": {str(i): c for i, c in enumerate(tokens.categorical)},
    }
    if group not in tables or key not in tables[group]:
        raise KeyError(f"Unknown color role {role!r}. Groups: {sorted(tables)}")
    return tables[group][key]


def alert_cmap() -> ListedColormap:
    """Return a discrete colormap of the alert levels, lowest to highest.

    Method: docs/standards/figures.md#colors-srcclearviztokensyaml

    Returns
    -------
    ListedColormap
        One color per alert level, in ``alert_levels.order``. PROVISIONAL palette.
    """
    levels = load_tokens().alert_levels
    return ListedColormap([levels.colors[k] for k in levels.order], name="clear_alerts")


def pm25_cmap() -> Colormap:
    """Return the continuous PM2.5 colormap named in the tokens (cividis).

    Method: docs/standards/figures.md#colors-srcclearviztokensyaml

    Returns
    -------
    Colormap
        The matplotlib colormap named by ``sequential.pm25``.
    """
    return mpl.colormaps[load_tokens().sequential["pm25"]]


def pm25_norm(breakpoints_ugm3: Sequence[float]) -> BoundaryNorm:
    """Build a norm that steps the PM2.5 colormap at the alert thresholds.

    Method: docs/standards/figures.md#colors-srcclearviztokensyaml

    Parameters
    ----------
    breakpoints_ugm3 : sequence of float
        Increasing bin edges in µg/m³, read from ``config/`` (never typed in a script).
        Length ``n_bins + 1``.

    Returns
    -------
    BoundaryNorm
        Norm with one color band per interval; values above the last edge use ``extend``.

    Raises
    ------
    ValueError
        If there are fewer than two edges or they are not strictly increasing.
    """
    edges = list(breakpoints_ugm3)
    if len(edges) < 2 or any(b <= a for a, b in zip(edges, edges[1:], strict=False)):
        raise ValueError(
            f"breakpoints_ugm3 must be at least two strictly increasing values, got {edges}"
        )
    return BoundaryNorm(edges, ncolors=pm25_cmap().N, extend="max")


def use_style(preset_name: str = "paper-2col") -> None:
    """Apply the CLEAR style and the preset's fonts and sizes to matplotlib globally.

    Method: docs/standards/figures.md#the-figure-language

    Parameters
    ----------
    preset_name : str, default "paper-2col"
        Size preset whose font sizes (pt), line width (pt) and figure size (in) to apply.

    Raises
    ------
    KeyError
        If the preset is not defined in ``tokens.yaml``.
    """
    tokens = load_tokens()
    p = preset(preset_name)
    ink = tokens.neutrals["ink"]
    plt.style.use(STYLE_PATH)
    mpl.rcParams.update(
        {
            "font.family": tokens.fonts.family,
            "font.size": p.font_size_pt,
            "axes.titlesize": p.title_size_pt,
            "axes.labelsize": p.font_size_pt,
            "xtick.labelsize": p.font_size_pt * 0.9,
            "ytick.labelsize": p.font_size_pt * 0.9,
            "legend.fontsize": p.font_size_pt * 0.9,
            "lines.linewidth": p.line_width_pt,
            "figure.figsize": (p.width_in, p.height_in),
            "figure.dpi": p.dpi,
            "savefig.dpi": p.dpi,
            "axes.prop_cycle": cycler(color=tokens.categorical),
            "text.color": ink,
            "axes.labelcolor": ink,
            "axes.edgecolor": ink,
            "xtick.color": ink,
            "ytick.color": ink,
            "grid.color": tokens.neutrals["grid"],
            "figure.facecolor": tokens.neutrals["background"],
            "axes.facecolor": tokens.neutrals["background"],
        }
    )


def new_figure(
    preset_name: str, *, nrows: int = 1, ncols: int = 1, height_in: float | None = None
) -> tuple[Figure, Axes]:
    """Create a figure sized to a preset, with a single Axes.

    Method: docs/standards/figures.md#presets

    For multi-panel figures pass ``nrows``/``ncols`` and use ``fig.axes``; the returned
    Axes is the first panel.

    Parameters
    ----------
    preset_name : str
        Size preset; sets the width (in), which is fixed.
    nrows, ncols : int, default 1
        Panel grid.
    height_in : float, optional
        Overrides the preset height, in inches.

    Returns
    -------
    tuple of (Figure, Axes)
        The figure and its first panel.

    Raises
    ------
    KeyError
        If the preset is not defined in ``tokens.yaml``.
    """
    p = preset(preset_name)
    size = (p.width_in, height_in or p.height_in)
    # matplotlib stubs leave pyplot.figure **kwargs untyped.
    fig = plt.figure(figsize=size)  # pyright: ignore[reportUnknownMemberType]
    axes = [fig.add_subplot(nrows, ncols, i + 1) for i in range(nrows * ncols)]
    return fig, axes[0]


def plotly_template() -> dict[str, object]:
    """Return a plotly template dict built from the same tokens (for the dashboard).

    Method: docs/standards/figures.md#plotly-dashboard

    Use as ``fig.update_layout(template=viz.plotly_template())``.

    Returns
    -------
    dict
        ``{"layout": {...}}`` with the categorical colorway, font and neutral colors.
    """
    tokens = load_tokens()
    ink, grid = tokens.neutrals["ink"], tokens.neutrals["grid"]
    axis = {"gridcolor": grid, "linecolor": ink, "zeroline": False, "ticks": "outside"}
    return {
        "layout": {
            "colorway": list(tokens.categorical),
            "font": {"family": tokens.fonts.plotly_family, "color": ink},
            "paper_bgcolor": tokens.neutrals["background"],
            "plot_bgcolor": tokens.neutrals["background"],
            "xaxis": axis,
            "yaxis": axis,
            "legend": {"bgcolor": "rgba(0,0,0,0)"},
        }
    }
