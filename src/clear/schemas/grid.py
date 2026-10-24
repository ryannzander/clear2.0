"""pandera schemas of the grid part's outputs.

Spec: methodology/grid.md#outputs.
"""

import pandera.pandas as pa

from clear.schemas.common import non_negative

__all__ = ["CELLS", "STATION_CELLS"]

# pyright ignores in this module: pandera leaves its built-in Check methods untyped.
_CELL_ID = r"^[NS]\d{4}[EW]\d{5}$"


def _deg(lo: float, hi: float) -> pa.Column:
    return pa.Column(float, pa.Check.in_range(lo, hi))  # pyright: ignore[reportUnknownMemberType]


CELLS = pa.DataFrameSchema(
    {
        "cell_id": pa.Column(str, pa.Check.str_matches(_CELL_ID)),  # pyright: ignore[reportUnknownMemberType]
        "row": pa.Column(int),
        "col": pa.Column(int),
        "lat_min_deg": _deg(-90.0, 90.0),
        "lat_max_deg": _deg(-90.0, 90.0),
        "lon_min_deg": _deg(-180.0, 180.0),
        "lon_max_deg": _deg(-180.0, 180.0),
        "lat_center_deg": _deg(-90.0, 90.0),
        "lon_center_deg": _deg(-180.0, 180.0),
        "city_frac": _deg(0.0, 1.0),
        "is_in_toronto": pa.Column(bool),
        "n_stations": pa.Column(int, non_negative()),
        "n_sites": pa.Column(int, non_negative()),
        "n_sites_active": pa.Column(int, non_negative()),
        "site_ids": pa.Column(str),
        "coverage_class": pa.Column(str, pa.Check.isin(["0", "1", ">1"])),  # pyright: ignore[reportUnknownMemberType]
    },
    unique=["cell_id"],
    strict=True,
)

STATION_CELLS = pa.DataFrameSchema(
    {
        "station_id": pa.Column(str),
        "site_id": pa.Column(str),
        "source": pa.Column(str),
        "is_in_toronto": pa.Column(bool),
        "lat_deg": _deg(-90.0, 90.0),
        "lon_deg": _deg(-180.0, 180.0),
        "cell_id": pa.Column(str, pa.Check.str_matches(_CELL_ID), nullable=True),  # pyright: ignore[reportUnknownMemberType]
    },
    unique=["station_id"],
    strict=True,
)
