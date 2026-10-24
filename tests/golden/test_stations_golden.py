"""Golden: the stations part reproduces doc 04's station years and site count.

Spec: methodology/stations.md#golden-numbers. Differences are explained and accepted in
decisions/0009-golden-station-years.md. Needs the built registry; skips otherwise (CI).
"""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import pytest
import yaml

from clear.stations.pipeline import outputs
from clear.stations.report import years_active
from clear.stations.settings import load_stations_config

pytestmark = pytest.mark.golden
EXPECTED = Path(__file__).parent / "expected" / "stations.yaml"


@dataclass(frozen=True)
class Want:
    id: str
    value: float
    tol: float


def load_golden() -> list[Want]:
    return [
        Want(e["id"], float(e["value"]), float(e["tol"]))
        for e in yaml.safe_load(EXPECTED.read_text(encoding="utf-8"))
    ]


def compute(want_id: str, registry: pd.DataFrame) -> float:
    if want_id == "toronto_sites":
        return float(registry.loc[registry["is_in_toronto"], "site_id"].nunique())
    kind, station_id = want_id.split(":", 1)
    years = years_active(registry[registry["station_id"] == station_id], load_stations_config())
    return float(years["first_year" if kind == "first_year" else "last_year"].iloc[0])


@pytest.mark.parametrize("want", load_golden(), ids=lambda w: w.id)
def test_reproduces_reported_number(want: Want):
    path = outputs().registry
    if not path.is_file():
        pytest.skip(f"{path} not available")
    assert compute(want.id, pd.read_parquet(path)) == pytest.approx(want.value, abs=want.tol)
