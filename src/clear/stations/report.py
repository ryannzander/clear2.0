"""Toronto station report: years active, completeness per split, source agreement.

Spec: methodology/stations.md#completeness and #combine-sources. Feeds EXP-001 and EXP-003.
"""

from itertools import combinations

import numpy as np
import pandas as pd

from clear.stations.settings import StationsConfig

__all__ = ["source_agreement", "toronto_report", "years_active"]

_LAGS_H = (-1, 0, 1)  # lag check of the time conventions (methodology/stations.md#open-questions)


def source_agreement(hourly: pd.DataFrame, registry: pd.DataFrame) -> pd.DataFrame:
    """Compare every pair of stations at the same site over their shared hours.

    Method: methodology/stations.md#combine-sources

    Parameters
    ----------
    hourly : pandas.DataFrame
        Valid station-hours (``station_id``, ``time_utc``, ``pm25_ugm3``).
    registry : pandas.DataFrame
        ``station_id``, ``site_id``, ``source`` of the stations to compare.

    Returns
    -------
    pandas.DataFrame
        One row per station pair: ``site_id``, ``station_a``, ``station_b``, ``shared_h``,
        ``bias_ugm3`` (mean b − a), ``rmse_ugm3``, ``r`` and ``r_lag_m1h``/``r_lag_p1h`` (b shifted
        one hour earlier/later). Pairs with no shared hour are left out.
    """
    rows: list[dict[str, object]] = []
    wide: pd.DataFrame = hourly[hourly["station_id"].isin(registry["station_id"])].pivot_table(
        index="time_utc", columns="station_id", values="pm25_ugm3"
    )
    for site_id, members in registry.groupby("site_id"):
        ids = sorted(str(m) for m in members["station_id"] if m in wide.columns)
        for a, b in combinations(ids, 2):
            pair = wide[[a, b]].dropna()
            if pair.empty:
                continue
            diff = pair[b] - pair[a]
            row: dict[str, object] = {
                "site_id": site_id,
                "station_a": a,
                "station_b": b,
                "shared_h": len(pair),
                "bias_ugm3": float(diff.mean()),
                "rmse_ugm3": float(np.sqrt((diff**2).mean())),
            }
            for lag in _LAGS_H:
                shifted = (
                    wide[a].to_frame().join(wide[b].shift(lag, freq="h"), how="inner").dropna()
                )
                key = {-1: "r_lag_m1h", 0: "r", 1: "r_lag_p1h"}[lag]
                row[key] = float(shifted[a].corr(shifted[b])) if len(shifted) > 2 else float("nan")
            rows.append(row)
    return pd.DataFrame(rows)


def years_active(registry: pd.DataFrame, config: StationsConfig) -> pd.DataFrame:
    """First and last year with data per station, in each source's own calendar.

    Method: methodology/stations.md#completeness

    The calendar is the source's ``utc_offset_h`` (EST for NAPS and MECP, UTC for AirNow),
    so a file's last evening does not count in the next UTC year (ADR 0009).

    Parameters
    ----------
    registry : pandas.DataFrame
        ``source``, ``first_time_utc`` and ``last_time_utc`` per station.
    config : StationsConfig
        ``config/stations.yaml`` (``sources.*.utc_offset_h``).

    Returns
    -------
    pandas.DataFrame
        ``first_year`` and ``last_year`` (int64), same index as ``registry``.
    """
    offsets_h = {str(name): src.utc_offset_h for name, src in config.sources.items()}
    offset = pd.to_timedelta(registry["source"].map(offsets_h).astype("int64"), unit="h")
    return pd.DataFrame(
        {
            "first_year": (registry["first_time_utc"] + offset).dt.year.astype("int64"),
            "last_year": (registry["last_time_utc"] + offset).dt.year.astype("int64"),
        },
        index=registry.index,
    )


def _split_fracs(completeness: pd.DataFrame, unit_kind: str) -> pd.DataFrame:
    split = completeness[
        (completeness["unit_kind"] == unit_kind) & (completeness["period"] == "split")
    ]
    return split.pivot(index="unit_id", columns="period_label", values="present_frac")


def toronto_report(
    registry: pd.DataFrame,
    completeness: pd.DataFrame,
    hourly: pd.DataFrame,
    merged: pd.DataFrame,
    *,
    config: StationsConfig,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Build the Toronto station table and the EXP-001 / EXP-003 metrics.

    Method: methodology/stations.md#completeness

    Years active follow methodology/stations.md#completeness: each source's own calendar
    (``utc_offset_h``: EST for NAPS and MECP, UTC for AirNow), so a file's last evening does
    not spill into the next UTC year. Completeness uses UTC periods.

    Parameters
    ----------
    registry, completeness, hourly, merged : pandas.DataFrame
        The four stations outputs.
    config : StationsConfig
        ``config/stations.yaml`` (threshold, local standard offset).

    Returns
    -------
    (pandas.DataFrame, dict)
        One row per Toronto station; a JSON-ready metrics dict.
    """
    toronto = registry[registry["is_in_toronto"]].copy()
    toronto[["first_year", "last_year"]] = years_active(toronto, config)
    years = completeness[
        (completeness["unit_kind"] == "station") & (completeness["period"] == "year")
    ]
    complete_years = years[years["is_complete"]].groupby("unit_id").size()
    toronto["complete_years"] = toronto["station_id"].map(complete_years).fillna(0).astype("int64")
    station_split = _split_fracs(completeness, "station")
    site_split = _split_fracs(completeness, "site")
    split_names = list(station_split.columns)
    for name in split_names:
        toronto[f"{name}_frac"] = toronto["station_id"].map(station_split[name]).round(3)
    table = toronto.sort_values(["site_id", "source", "station_id"])[
        [
            "site_id",
            "station_id",
            "source",
            "station_name",
            "first_year",
            "last_year",
            "complete_years",
        ]
        + [f"{n}_frac" for n in split_names]
    ]

    min_frac = config.completeness_min_frac
    sites = sorted(toronto["site_id"].unique())
    site_fracs = site_split.reindex(sites)
    station_fracs = station_split.reindex(toronto["station_id"])
    agreement = source_agreement(hourly, toronto)
    metrics: dict[str, object] = {
        "toronto_stations": len(toronto),
        "toronto_sites": len(sites),
        "stations_by_source": {
            str(k): int(v) for k, v in toronto["source"].value_counts().sort_index().items()
        },
        "station_years_active": {
            str(r.station_id): f"{r.first_year}-{r.last_year}" for r in toronto.itertuples()
        },
        "completeness_min_frac": min_frac,
        "separate": {
            "series": len(toronto),
            "meeting_threshold": {
                n: int((station_fracs[n] >= min_frac).sum()) for n in split_names
            },
            "mean_present_frac": {
                n: round(float(station_fracs[n].fillna(0).mean()), 4) for n in split_names
            },
        },
        "merged": {
            "series": len(sites),
            "meeting_threshold": {n: int((site_fracs[n] >= min_frac).sum()) for n in split_names},
            "mean_present_frac": {
                n: round(float(site_fracs[n].fillna(0).mean()), 4) for n in split_names
            },
            "hours_by_source": {
                str(k): int(v)
                for k, v in merged[merged["site_id"].isin(sites)]["source"]
                .value_counts()
                .sort_index()
                .items()
            },
        },
        "merged_vs_best_member": _merged_vs_best(toronto, site_fracs, station_fracs, split_names),
        "agreement": agreement.round(4).to_dict(orient="records"),
    }
    return table, metrics


def _merged_vs_best(
    toronto: pd.DataFrame, site_fracs: pd.DataFrame, station_fracs: pd.DataFrame, splits: list[str]
) -> list[dict[str, object]]:
    """Per site and split: merged present_frac against its best single member's."""
    rows: list[dict[str, object]] = []
    for site_id, members in toronto.groupby("site_id", sort=True):
        member_fracs = station_fracs.reindex(members["station_id"]).fillna(0.0)
        merged = site_fracs.reindex([site_id]).fillna(0.0)
        for split in splits:
            best = member_fracs[split]
            rows.append(
                {
                    "site_id": str(site_id),
                    "split": split,
                    "merged_frac": round(float(merged[split].iloc[0]), 4),
                    "best_member_frac": round(float(best.max()), 4),
                    "best_member": str(best.idxmax()),
                }
            )
    return rows
