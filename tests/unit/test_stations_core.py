import numpy as np
import pandas as pd
import pytest
from shapely.geometry import box

from clear.geo import city_bounds, in_city
from clear.stations.combine import merged_series
from clear.stations.completeness import completeness, periods_for
from clear.stations.registry import build_registry, haversine_m, link_sites
from clear.stations.report import source_agreement
from clear.stations.settings import SplitYears

SPLITS = {"train": SplitYears(first_year=2024, last_year=2024)}


def utc(text: str) -> pd.Timestamp:
    return pd.Timestamp(text, tz="UTC")


def hours(station: str, source: str, start: str, n: int, value: float = 1.0) -> pd.DataFrame:
    t = pd.date_range(utc(start), periods=n, freq="h")
    return pd.DataFrame(
        {"station_id": station, "source": source, "time_utc": t, "pm25_ugm3": value}
    )


def test_haversine_one_degree_latitude():
    d = haversine_m(np.array([43.0]), np.array([-79.0]), np.array([44.0]), np.array([-79.0]))
    assert d[0] == pytest.approx(111_195, rel=1e-3)


def test_registry_and_site_linking():
    stations = pd.DataFrame(
        {
            "station_id": ["airnow:1", "mecp:2", "naps:3", "naps:9"],
            "source": ["airnow", "mecp", "naps", "naps"],
            "station_name": ["a", "b", "c", "far"],
            "lat_deg": [43.6620, 43.66297, 43.66417, 43.75],
            "lon_deg": [-79.3853, -79.38811, -79.38722, -79.27],
        }
    )
    hourly = pd.concat(
        [
            hours("airnow:1", "airnow", "2024-01-01", 5),
            hours("mecp:2", "mecp", "2024-01-01", 3),
            hours("naps:3", "naps", "2023-01-01", 2),
            hours("naps:9", "naps", "2024-01-01", 1),
        ]
    )
    reg = build_registry(stations, hourly)
    assert reg.set_index("station_id").loc["airnow:1", "present_h"] == 5
    sites = link_sites(reg, max_distance_m=500, source_priority=["naps", "mecp", "airnow"])
    by_station = dict(zip(reg["station_id"], sites, strict=True))
    # The three downtown stations (< 500 m apart) become one site named after the NAPS member.
    assert by_station["airnow:1"] == by_station["mecp:2"] == by_station["naps:3"] == "naps:3"
    assert by_station["naps:9"] == "naps:9"


def test_completeness_counts_gaps_and_caps_at_coverage_end():
    # 2024-01-01 00:00..09:00 present, then a 5 h gap, then 3 h; data ends 2024-01-01 17:00.
    series = pd.concat(
        [hours("s:1", "naps", "2024-01-01 00:00", 10), hours("s:1", "naps", "2024-01-01 15:00", 3)]
    )
    out = completeness(
        series,
        unit_kind="station",
        unit_column="station_id",
        splits=SPLITS,
        coverage_end_utc=utc("2024-01-01 20:00"),
        min_frac=0.75,
    )
    year = out[(out["period"] == "year")].iloc[0]
    assert year["expected_h"] == 20  # capped at coverage end
    assert year["present_h"] == 13
    assert year["longest_gap_h"] == 5
    assert bool(year["is_complete"]) is False  # 13 / 20 = 0.65
    jan = out[(out["period"] == "month") & (out["period_label"] == "2024-01")].iloc[0]
    assert jan["present_h"] == 13
    assert set(out["period"]) == {"year", "month", "split"}
    # Months after coverage end have no expected hours and are left out.
    assert "2024-02" not in set(out["period_label"])


def test_periods_cover_whole_years_and_splits():
    ps = periods_for(utc("2023-06-01"), utc("2024-02-01"), SPLITS)
    assert [p.label for p in ps if p.period == "year"] == ["2023", "2024"]
    assert sum(p.period == "month" for p in ps) == 24
    assert [p.label for p in ps if p.period == "split"] == ["train"]


def test_merged_series_prefers_priority_and_averages_same_source():
    hourly = pd.concat(
        [
            hours("airnow:1", "airnow", "2024-01-01 00:00", 2, 9.0),
            hours("naps:3", "naps", "2024-01-01 01:00", 1, 4.0),
            hours("naps:4", "naps", "2024-01-01 01:00", 1, 6.0),
        ]
    )
    reg = pd.DataFrame({"station_id": ["airnow:1", "naps:3", "naps:4"], "site_id": ["naps:3"] * 3})
    out = merged_series(hourly, reg, source_priority=["naps", "mecp", "airnow"])
    assert out["source"].tolist() == ["airnow", "naps"]
    assert out["pm25_ugm3"].tolist() == [9.0, 5.0]


def test_source_agreement_finds_lag_zero():
    t = pd.date_range(utc("2024-01-01"), periods=200, freq="h")
    signal = np.sin(np.arange(200) / 5.0) + 2
    hourly = pd.concat(
        [
            pd.DataFrame({"station_id": "naps:1", "time_utc": t, "pm25_ugm3": signal}),
            pd.DataFrame({"station_id": "mecp:2", "time_utc": t, "pm25_ugm3": signal + 0.5}),
        ]
    )
    reg = pd.DataFrame(
        {"station_id": ["naps:1", "mecp:2"], "site_id": ["naps:1"] * 2, "source": ["naps", "mecp"]}
    )
    row = source_agreement(hourly, reg).iloc[0]
    assert row["shared_h"] == 200
    assert row["bias_ugm3"] == pytest.approx(-0.5)  # naps:1 minus mecp:2 (station_b - station_a)
    assert row["r"] > row["r_lag_m1h"]
    assert row["r"] > row["r_lag_p1h"]


def test_in_city_and_bounds():
    city = box(-79.6, 43.6, -79.1, 43.9)
    lat = pd.Series([43.7, 43.5, 43.9])
    lon = pd.Series([-79.4, -79.4, -79.3])
    assert in_city(city, lat, lon).tolist() == [True, False, True]  # on the edge counts
    b = city_bounds(city)
    assert (b.lon_min_deg, b.lat_max_deg) == (-79.6, 43.9)


def test_link_sites_chains_and_breaks_ties_by_latest_last_hour():
    # a-b 400 m and b-c 400 m apart (a-c ~800 m): single linkage joins all three.
    reg = pd.DataFrame(
        {
            "station_id": ["naps:1", "naps:2", "mecp:3"],
            "source": ["naps", "naps", "mecp"],
            "lat_deg": [43.700, 43.7036, 43.7072],
            "lon_deg": [-79.4, -79.4, -79.4],
            "last_time_utc": [utc("2010-01-01"), utc("2024-12-31"), utc("2025-12-31")],
        }
    )
    sites = link_sites(reg, max_distance_m=500, source_priority=["naps", "mecp", "airnow"])
    assert set(sites) == {"naps:2"}  # NAPS beats MECP; of the two NAPS, the later one


def test_toronto_report_years_in_source_calendar_and_merged_vs_best():
    from clear.stations.report import toronto_report
    from clear.stations.settings import load_stations_config

    registry = pd.DataFrame(
        {
            "station_id": ["naps:1", "airnow:2"],
            "source": ["naps", "airnow"],
            "station_name": ["a", "b"],
            "lat_deg": [43.7, 43.7],
            "lon_deg": [-79.4, -79.4],
            # NAPS: last hour 2025-01-01 04:00Z = 2024-12-31 23:00 EST -> last year 2024.
            "first_time_utc": [utc("2021-01-01 05:00"), utc("2024-01-01 00:00")],
            "last_time_utc": [utc("2025-01-01 04:00"), utc("2024-12-31 23:00")],
            "present_h": [10, 10],
            "is_in_toronto": [True, True],
            "site_id": ["naps:1", "naps:1"],
        }
    )
    completeness_rows = pd.DataFrame(
        {
            "unit_kind": ["station", "station", "site"],
            "unit_id": ["naps:1", "airnow:2", "naps:1"],
            "period": ["split"] * 3,
            "period_label": ["train"] * 3,
            "present_frac": [0.6, 0.5, 0.9],
            "is_complete": [False, False, True],
        }
    )
    empty = pd.DataFrame(columns=["station_id", "time_utc", "pm25_ugm3", "source", "site_id"])
    table, metrics = toronto_report(
        registry, completeness_rows, empty, empty, config=load_stations_config()
    )
    years = dict(
        zip(
            table["station_id"],
            zip(table["first_year"], table["last_year"], strict=True),
            strict=True,
        )
    )
    assert years == {"naps:1": (2021, 2024), "airnow:2": (2024, 2024)}
    assert metrics["merged_vs_best_member"] == [
        {
            "site_id": "naps:1",
            "split": "train",
            "merged_frac": 0.9,
            "best_member_frac": 0.6,
            "best_member": "naps:1",
        }
    ]
