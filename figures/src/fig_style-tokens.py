"""Style sheet of the CLEAR figure language: every palette in tokens.yaml, one panel each.

Rebuild: uv run clear figures build --only style-tokens
"""

import numpy as np
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

from clear import viz

PRESET = "paper-2col"
SLOTS = 8  # swatch slots per row, so every row's swatches share one size
# Illustrative only: real alert thresholds come from config/ once alert-levels is spec'd.
PLACEHOLDER_EDGES_UGM3 = [0.0, 1.0, 2.0, 3.0, 4.0]


def swatch_row(ax: Axes, roles: list[str], labels: list[str], title: str) -> None:
    edge = viz.color("neutral.grid")
    for i, (role, label) in enumerate(zip(roles, labels, strict=True)):
        hex_code = viz.color(role)
        ax.add_patch(Rectangle((i, 0.25), 0.9, 0.75, facecolor=hex_code, edgecolor=edge, lw=0.5))
        ax.text(i + 0.45, 0.08, label, ha="center", va="top")
        ax.text(
            i + 0.45,
            -0.3,
            f"{role}\n{hex_code}",
            ha="center",
            va="top",
            fontsize=5,
            color=viz.color("neutral.muted"),
        )
    ax.set_xlim(-0.05, SLOTS)
    ax.set_ylim(-0.95, 1.05)
    ax.set_axis_off()
    ax.set_title(title)


def pm25_row(ax: Axes) -> None:
    # endpoint=False keeps the ramp inside the top bin (no over-range sliver).
    gradient = np.linspace(0.0, PLACEHOLDER_EDGES_UGM3[-1], 256, endpoint=False)[None, :]
    extent = (0.0, SLOTS - 0.1, 0.55, 1.0)
    ax.imshow(gradient, aspect="auto", cmap=viz.pm25_cmap(), extent=extent)
    stepped_extent = (0.0, SLOTS - 0.1, 0.0, 0.45)
    ax.imshow(
        gradient,
        aspect="auto",
        cmap=viz.pm25_cmap(),
        extent=stepped_extent,
        norm=viz.pm25_norm(PLACEHOLDER_EDGES_UGM3),
    )
    ax.text(
        0.0,
        -0.08,
        "continuous (top) · stepped at alert thresholds (bottom; placeholder "
        "bins until config/ defines them)",
        va="top",
        color=viz.color("neutral.muted"),
    )
    ax.set_xlim(-0.05, SLOTS)
    ax.set_ylim(-0.45, 1.05)
    ax.set_axis_off()
    ax.set_title("PM2.5 concentration · sequential.pm25 (cividis)")


def main() -> None:
    viz.use_style(PRESET)
    tokens = viz.load_tokens()
    fig, _ = viz.new_figure(PRESET, nrows=5, height_in=6.4)
    ax_alert, ax_source, ax_cat, ax_neutral, ax_pm25 = fig.axes

    levels = tokens.alert_levels
    swatch_row(
        ax_alert,
        [f"alert.{k}" for k in levels.order],
        [levels.labels[k] for k in levels.order],
        "Alert levels · PROVISIONAL, aligned to AQHI risk categories",
    )
    sources = list(tokens.sources)
    swatch_row(
        ax_source,
        [f"source.{k}" for k in sources],
        [tokens.source_labels[k] for k in sources],
        "Data sources · one permanent color each, keyed by GLOSSARY code name",
    )
    swatch_row(
        ax_cat,
        [f"cat.{i}" for i in range(len(tokens.categorical))],
        [str(i) for i in range(len(tokens.categorical))],
        "Categorical · Okabe-Ito, colorblind-safe, in cycle order",
    )
    neutrals = list(tokens.neutrals)
    swatch_row(ax_neutral, [f"neutral.{k}" for k in neutrals], neutrals, "Neutrals")
    pm25_row(ax_pm25)

    viz.save_figure(
        fig,
        "style-tokens",
        caption="CLEAR 2.0 figure language: every palette defined in tokens.yaml.",
        description=(
            "Five rows of color swatches, each labelled with its semantic role and hex code: "
            "alert levels (provisional), data sources, Okabe-Ito categorical cycle, neutrals, "
            "and the cividis PM2.5 ramp shown continuous and stepped at placeholder bins."
        ),
        inputs=["src/clear/viz/tokens.yaml"],
        preset=PRESET,
    )


if __name__ == "__main__":
    main()
