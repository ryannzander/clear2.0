"""Typed access to ``tokens.yaml``: colors, fonts, size presets and the map projection.

``tokens.yaml`` is the only home of design tokens. This module validates it into frozen
pydantic models; :mod:`clear.viz` builds styles, colors and maps from them.
Standard: ``docs/standards/figures.md``.
"""

from functools import cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict

__all__ = [
    "AlertLevels",
    "Fonts",
    "MapProjection",
    "MapTokens",
    "Preset",
    "Tokens",
    "load_tokens",
    "preset",
]

TOKENS_PATH = Path(__file__).with_name("tokens.yaml")


class _Frozen(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Preset(_Frozen):
    """A figure size preset (inches, points, dots per inch).

    Method: docs/standards/figures.md#presets
    """

    width_in: float
    height_in: float
    dpi: int
    font_size_pt: float
    title_size_pt: float
    line_width_pt: float


class AlertLevels(_Frozen):
    """Alert-level palette; provisional until the alert-levels spec exists.

    Method: docs/standards/figures.md#colors-srcclearviztokensyaml
    """

    provisional: bool
    note: str
    order: list[str]
    labels: dict[str, str]
    colors: dict[str, str]


class Fonts(_Frozen):
    """Font families for matplotlib and plotly.

    Method: docs/standards/figures.md#the-figure-language
    """

    family: str
    plotly_family: str


class MapProjection(_Frozen):
    """Lambert Conformal Conic parameters shared by every CLEAR map, in degrees.

    Method: docs/standards/figures.md#maps
    """

    name: Literal["lambert_conformal"]
    central_longitude_deg: float
    central_latitude_deg: float
    standard_parallels_deg: tuple[float, float]


class MapTokens(_Frozen):
    """Map design tokens: the one projection (the extent is config, not a token).

    Method: docs/standards/figures.md#maps
    """

    projection: MapProjection


class Tokens(_Frozen):
    """All design tokens, validated from ``tokens.yaml``.

    Method: docs/standards/figures.md#colors-srcclearviztokensyaml
    """

    version: int
    alert_levels: AlertLevels
    aqhi_scale: dict[str, str]
    categorical: list[str]
    sources: dict[str, str]
    source_labels: dict[str, str]
    sequential: dict[str, str]
    neutrals: dict[str, str]
    fonts: Fonts
    presets: dict[str, Preset]
    maps: MapTokens


@cache
def load_tokens() -> Tokens:
    """Load and validate the design tokens.

    Method: docs/standards/figures.md#colors-srcclearviztokensyaml

    Returns
    -------
    Tokens
        Parsed ``tokens.yaml``. Cached: edit the file, then restart the process.

    Raises
    ------
    pydantic.ValidationError
        If ``tokens.yaml`` has a missing, unknown or mistyped key.
    """
    with TOKENS_PATH.open(encoding="utf-8") as fh:
        return Tokens.model_validate(yaml.safe_load(fh))


def preset(name: str) -> Preset:
    """Return a size preset by name (``paper-1col``, ``paper-2col``, ``slide-16x9``, ``poster``).

    Method: docs/standards/figures.md#presets

    Parameters
    ----------
    name : str
        Preset key in ``tokens.yaml``.

    Returns
    -------
    Preset
        Width and height (in), dpi, font sizes (pt) and line width (pt).

    Raises
    ------
    KeyError
        If the preset is not defined in ``tokens.yaml``.
    """
    presets = load_tokens().presets
    if name not in presets:
        raise KeyError(f"Unknown preset {name!r}. Known: {sorted(presets)}")
    return presets[name]
