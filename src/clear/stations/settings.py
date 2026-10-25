"""Typed config of the ``stations`` part: ``config/stations.yaml`` and ``config/splits.yaml``."""

from pathlib import Path
from typing import Literal

from pydantic import Field

from clear.config import ConfigModel, load_config

__all__ = [
    "SourceConfig",
    "SourceName",
    "SplitYears",
    "SplitsConfig",
    "StationsConfig",
    "load_splits_config",
    "load_stations_config",
]

type SourceName = Literal["naps", "mecp", "airnow"]


class SourceConfig(ConfigModel):
    """How one source is read: dataset folders under ``data/raw``, clock, hour label, sentinels.

    Method: methodology/stations.md#read-sources

    ``folders`` maps each data-card slug to its folder; the slug also names the interim table.
    """

    folders: dict[str, str] = Field(min_length=1)
    utc_offset_h: int = Field(ge=-12, le=14)
    hour_ending: bool
    sentinels: list[float]


class StationsConfig(ConfigModel):
    """Constants of the stations part (``config/stations.yaml``).

    Method: methodology/stations.md#constants
    """

    sources: dict[SourceName, SourceConfig]
    negative_is_missing: bool
    source_priority: list[SourceName] = Field(min_length=1)
    overlap_mode: Literal["merged", "separate"]
    merged_exclude_stations: list[str]
    crosswalk_max_distance_m: float = Field(gt=0.0)
    completeness_min_frac: float = Field(ge=0.0, le=1.0)
    registry_margin_deg: float = Field(ge=0.0)

    def source(self, name: str) -> SourceConfig:
        """Return the config of one source key (``naps``, ``mecp``, ``airnow``).

        Method: methodology/stations.md#read-sources

        Raises
        ------
        KeyError
            If ``name`` is not a configured source.
        """
        for key, value in self.sources.items():
            if key == name:
                return value
        raise KeyError(f"no source {name!r} in config/stations.yaml")


class SplitYears(ConfigModel):
    """One split as an inclusive range of calendar years (UTC).

    Method: decisions/0001-data-split.md#decision
    """

    first_year: int
    last_year: int


class SplitsConfig(ConfigModel):
    """Train / validation / test years (``config/splits.yaml``).

    Method: decisions/0001-data-split.md#decision
    """

    splits: dict[str, SplitYears]


def load_stations_config(*, directory: Path | None = None) -> StationsConfig:
    """Load ``config/stations.yaml``.

    Method: methodology/stations.md#constants

    Parameters
    ----------
    directory : Path, optional
        Alternative config directory (tests).

    Returns
    -------
    StationsConfig
        Validated constants.
    """
    return load_config("stations", StationsConfig, directory=directory)


def load_splits_config(*, directory: Path | None = None) -> SplitsConfig:
    """Load ``config/splits.yaml``.

    Method: decisions/0001-data-split.md#decision

    Parameters
    ----------
    directory : Path, optional
        Alternative config directory (tests).

    Returns
    -------
    SplitsConfig
        Split name to inclusive year range.
    """
    return load_config("splits", SplitsConfig, directory=directory)
