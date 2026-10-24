from pathlib import Path

import pandas as pd
import pytest

from clear.geo import Bounds
from clear.stations.pipeline import source_files
from clear.stations.qc import apply_qc, clean_values
from clear.stations.readers import read_airnow, read_mecp, read_naps, to_number, wide_to_long
from clear.stations.settings import SourceConfig, load_stations_config

BOX = Bounds(-80.0, 43.0, -79.0, 44.0)
NAPS = SourceConfig(folders={"naps-x": "x"}, utc_offset_h=-5, hour_ending=True, sentinels=[-999])
MECP = SourceConfig(folders={"mecp-x": "x"}, utc_offset_h=-5, hour_ending=True, sentinels=[9999])
HOURS = ",".join(f"H{h:02d}//H{h:02d}" for h in range(1, 25))


def utc(text: str) -> pd.Timestamp:
    return pd.Timestamp(text, tz="UTC")


def day_row(date: str, **hours: object) -> dict[str, object]:
    row: dict[str, object] = {"station_id": "naps:000001", "date": date, "method_code": "184"}
    return row | {f"H{h:02d}": "" for h in range(1, 25)} | hours


def test_to_number_empty_is_nan_and_garbage_raises():
    out = to_number(pd.Series(["5", "", " -999 ", None]))
    assert out.isna().tolist() == [False, True, False, True]
    with pytest.raises(ValueError, match="1 non-numeric"):
        to_number(pd.Series(["5", "N/A"]))


def test_clean_values_drops_sentinels_and_negatives():
    out = clean_values(
        pd.Series([5.0, -999.0, -1.0, 0.0, 9999.0]),
        sentinels=[-999, 9999],
        negative_is_missing=True,
    )
    assert out.isna().tolist() == [False, True, True, False, True]


def test_wide_to_long_shifts_hour_ending_lst_to_utc_hour_beginning():
    row = day_row("2025-03-09") | {f"H{h:02d}": str(h) for h in range(1, 25)}
    out = wide_to_long(pd.DataFrame([row]), source="naps", dataset="naps-x", config=NAPS)
    by_value = out.set_index("pm25_raw_ugm3")["time_utc"]
    # H01 covers 00:00-01:00 LST (UTC-5) = 05:00-06:00 UTC; the DST day changes nothing.
    assert by_value[1.0] == utc("2025-03-09 05:00")
    # H24 covers 23:00-24:00 LST = 04:00-05:00 UTC next day.
    assert by_value[24.0] == utc("2025-03-10 04:00")


def test_wide_to_long_fall_back_day_has_24_distinct_hours():
    row = day_row("2025-11-02") | {f"H{h:02d}": "1" for h in range(1, 25)}
    out = wide_to_long(pd.DataFrame([row]), source="naps", dataset="naps-x", config=NAPS)
    assert out["time_utc"].is_unique
    assert len(out) == 24  # standard time all year: no repeated or missing hour


def test_wide_to_long_keeps_raw_values_and_drops_only_empty_cells():
    row = day_row("2024-01-01", H01="-999", H02="-3", H03="7")
    out = wide_to_long(pd.DataFrame([row]), source="naps", dataset="naps-x", config=NAPS)
    assert out["pm25_raw_ugm3"].tolist() == [-999.0, -3.0, 7.0]
    assert set(out["dataset"]) == {"naps-x"}


def test_apply_qc_cleans_per_source_and_averages_repeats():
    t = pd.to_datetime(["2024-01-01 00:00"] * 3 + ["2024-01-01 01:00"], utc=True)
    raw = pd.DataFrame(
        {
            "station_id": ["naps:1", "naps:1", "naps:1", "mecp:2"],
            "source": ["naps", "naps", "naps", "mecp"],
            "time_utc": t,
            "pm25_raw_ugm3": [2.0, 4.0, -999.0, 9999.0],
        }
    )
    out = apply_qc(raw, load_stations_config())
    assert out.to_dict("records") == [
        {"station_id": "naps:1", "source": "naps", "time_utc": t[0], "pm25_ugm3": 3.0}
    ]


def write_naps(path: Path) -> Path:
    lines = [
        "﻿File generated on // Fichier créé sur, 2026-06-19",
        "",
        "Note // Note,Data is hour ending local standard time",
        "",
        "Pollutant//Polluant,Method Code//Code Méthode,NAPS ID//Identifiant SNPA,City//Ville,"
        "Province/Territory//Province/Territoire,Latitude//Latitude,Longitude//Longitude,"
        f"Date//Date,{HOURS}",
        "PM2.5,184,060410,Toronto,ON,43.74792,-79.27406,2024-01-01,"
        + ",".join(["5"] * 23 + ["-999"]),
        "PM2.5,184,050134,Montréal,QC,45.54271,-73.57176,2024-01-01," + ",".join(["1"] * 24),
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_read_naps_keeps_leading_zero_box_and_raw_values(tmp_path: Path):
    tables = read_naps(
        [write_naps(tmp_path / "PM25_2024.csv")], dataset="naps-x", bounds=BOX, config=NAPS
    )
    assert tables.stations["station_id"].tolist() == ["naps:060410"]
    assert len(tables.raw) == 24  # -999 kept in interim
    assert set(tables.raw["method_code"]) == {"184"}


def write_mecp(path: Path) -> Path:
    hours = ",".join(f"H{h:02d}" for h in range(1, 25))
    lines = [
        "Toronto East, (33003) Hourly, Fine particulate matter (PM2.5) Concentrations",
        "Station,Toronto East (33003)",
        "Latitude,43.747917",
        "Longitude,-79.274056",
        f"Station ID,Pollutant,Date,{hours}",
        "33003,Fine Particulate Matter,2024-01-01," + ",".join(["4"] * 23 + ["9999"]) + ",",
        "33003,Fine Particulate Matter,2024-01-01," + ",".join(["6"] + [""] * 23) + ",",
        "33003,Fine Particulate Matter,2024-01-02,7,8,",  # truncated last row
        "Station,Barrie (47045)",
        "Latitude,44.382338",
        "Longitude,-79.702446",
        "No data available",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_read_mecp_blocks_duplicates_truncation(tmp_path: Path):
    tables = read_mecp(
        [write_mecp(tmp_path / "x_124_2024.csv")], dataset="mecp-x", bounds=BOX, config=MECP
    )
    assert tables.stations["station_id"].tolist() == ["mecp:33003"]
    assert tables.stations.loc[0, "station_name"] == "Toronto East"
    assert len(tables.raw) == 24 + 1 + 2  # duplicate row and 9999 kept in interim
    hourly = apply_qc(tables.raw, load_stations_config()).set_index("time_utc")["pm25_ugm3"]
    assert hourly[utc("2024-01-01 05:00")] == 5.0  # (4 + 6) / 2
    assert hourly[utc("2024-01-02 06:00")] == 8.0


def test_read_mecp_raises_on_non_numeric_cell(tmp_path: Path):
    path = write_mecp(tmp_path / "x.csv")
    path.write_text(path.read_text(encoding="utf-8").replace(",7,8,", ",7,bad,"), encoding="utf-8")
    with pytest.raises(ValueError, match="non-numeric"):
        read_mecp([path], dataset="mecp-x", bounds=BOX, config=MECP)


def test_read_airnow_both_folders_and_site_locations(tmp_path: Path):
    aqobs = pd.DataFrame(
        {
            "AQSID": ["124000060445", "124000060445", "840000001"],
            "SiteName": ["Toronto Downtown"] * 2 + ["Far away"],
            "Latitude": [43.64545, 43.64545, 30.0],
            "Longitude": [-79.3891, -79.3891, -90.0],
            "ValidDate": ["10/08/2026", "10/08/21", "10/08/2026"],
            "ValidTime": ["23:00", "05:00", "23:00"],
            "PM25": [7.5, -3.0, 1.0],
        }
    )
    aqobs_path = tmp_path / "airnow_pm25_2026_10.parquet"
    aqobs.to_parquet(aqobs_path)
    hourlydata = pd.DataFrame(
        {
            "AQSID": ["000060424"],
            "SiteName": ["Toronto Downtown"],
            "ValidDate": ["01/01/14"],
            "ValidTime": ["00:00"],
            "Value": ["12.0"],
        }
    )
    hd_path = tmp_path / "airnow_hourlydata_pm25_2014_01.parquet"
    hourlydata.to_parquet(hd_path)
    site_path = tmp_path / "monitoring_site_locations_20190601.dat"
    site_path.write_bytes(
        b"000060424|PM2.5|x|Toronto Downtown|Active|x|MOE|x|43.661900|-79.385300|0|-5|CA|\n"
        b"999999999|PM2.5|x|Caf\x90 site|Active|x|y|x|19.0|-99.0|0|-6|MX|\n"
    )
    tables = read_airnow([aqobs_path], [hd_path], [site_path], bounds=BOX)
    assert sorted(tables.stations["station_id"]) == ["airnow:000060424", "airnow:124000060445"]
    raw = tables.raw.set_index(["station_id", "time_utc"])
    assert raw.loc[("airnow:124000060445", utc("2021-10-08 05:00")), "pm25_raw_ugm3"] == -3.0
    assert set(tables.raw["dataset"]) == {"airnow-hourlyaqobs", "airnow-hourlydata-2014-2019"}


def test_source_files_fails_loud_when_a_folder_is_empty(tmp_path: Path):
    (tmp_path / "x").mkdir()
    with pytest.raises(FileNotFoundError, match="config/stations.yaml"):
        source_files(tmp_path, "x", "*.csv")
