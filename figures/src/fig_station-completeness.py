"""Toronto government stations: fraction of hours present per station and year.

Answers issue #1 (years active, missing data). Input: the stations outputs
(uv run clear stations build). Rebuild: uv run clear figures build --only station-completeness
"""

import matplotlib
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap

from clear import viz
from clear.schemas.stations import COMPLETENESS, REGISTRY
from clear.stations.pipeline import outputs
from clear.stations.report import years_active
from clear.stations.settings import load_splits_config, load_stations_config

PRESET = "paper-2col"
HEIGHT_IN = 5.6


def main() -> None:
    viz.use_style(PRESET)
    paths = outputs()
    registry = REGISTRY.validate(pd.read_parquet(paths.registry))
    complete = pd.read_parquet(paths.completeness)
    splits = load_splits_config().splits

    toronto = registry[registry["is_in_toronto"]].sort_values(["site_id", "source", "station_id"])
    complete = COMPLETENESS.validate(complete)
    years = complete[(complete["unit_kind"] == "station") & (complete["period"] == "year")]
    grid = years.pivot(index="unit_id", columns="period_label", values="present_frac")
    grid = grid.reindex(index=toronto["station_id"], columns=sorted(grid.columns))
    # Hide years outside each station's active span in its own calendar (EST for NAPS/MECP,
    # UTC for AirNow): the last local evening of a file falls in the next UTC year.
    years = years_active(toronto, load_stations_config())
    first, last = years["first_year"].to_numpy(), years["last_year"].to_numpy()
    year_of_col = np.array([int(c) for c in grid.columns])
    outside = (year_of_col[None, :] < first[:, None]) | (year_of_col[None, :] > last[:, None])
    values = np.ma.masked_array(
        grid.to_numpy(dtype="float64"), mask=outside | grid.isna().to_numpy()
    )

    fig, ax = viz.new_figure(PRESET, height_in=HEIGHT_IN)
    base = matplotlib.colormaps[viz.load_tokens().sequential["fraction"]]
    cmap = ListedColormap(base(np.linspace(0.0, 1.0, 256)))
    cmap.set_bad(viz.color("neutral.missing"))
    image = ax.imshow(values, aspect="auto", cmap=cmap, vmin=0.0, vmax=1.0, interpolation="none")
    labels = [
        f"{s}  ({site})" for s, site in zip(toronto["station_id"], toronto["site_id"], strict=True)
    ]
    ax.set_yticks(range(len(labels)), labels, fontsize="xx-small")
    cols = list(grid.columns)
    ax.set_xticks(range(len(cols)), cols, rotation=90, fontsize="xx-small")
    ink = viz.color("neutral.ink")
    for name, span in splits.items():
        label = str(span.first_year)
        if label in cols:
            x = cols.index(label) - 0.5
            ax.axvline(x, color=ink, lw=0.8)
            ax.text(x + 0.1, -0.8, name, fontsize="x-small", color=ink, va="bottom")
    ax.set_xlabel("Calendar year (UTC)")
    ax.set_ylabel("Station (site)")
    bar = fig.colorbar(image, ax=ax, fraction=0.03, pad=0.01)
    bar.set_label("Hours present (fraction of the year, 0-1)")
    ax.set_title("Toronto government PM2.5 stations: data completeness by year", pad=14)

    viz.save_figure(
        fig,
        "station-completeness",
        caption=(
            "Fraction of hours with a valid PM2.5 value per station and UTC year, for every NAPS, "
            "Ontario MECP and AirNow station inside the City of Toronto. Grey = not active. "
            "Vertical lines mark the train, validation and test splits; 2026 runs to 8 October."
        ),
        description=(
            "Heatmap; rows are stations labelled with their site (co-located stations share a "
            "site), "
            "columns are years 2000-2026, color is the fraction of hours present (cividis, 0-1)."
        ),
        inputs=[paths.registry, paths.completeness],
        preset=PRESET,
    )


if __name__ == "__main__":
    main()
