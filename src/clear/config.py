"""Typed loading of ``config/<name>.yaml``.

Every methodological constant (thresholds, radii, lag windows, cutoffs) lives in
``config/`` with a comment linking its spec section or ADR. Code never hard-codes them:
it declares a :class:`ConfigModel` subclass and loads the file through :func:`load_config`.

Example::

    class AlertConfig(ConfigModel):
        thresholds_ugm3: list[float]

    alerts = load_config("alerts", AlertConfig)
"""

from pathlib import Path
from typing import cast

import yaml
from pydantic import BaseModel, ConfigDict

from clear.paths import config_dir


class ConfigModel(BaseModel):
    """Base for config schemas: unknown keys are errors and values are immutable.

    Method: docs/standards/code.md#config-no-magic-numbers
    """

    model_config = ConfigDict(extra="forbid", frozen=True)


def config_path(name: str, *, directory: Path | None = None) -> Path:
    """Return the path of ``config/<name>.yaml``.

    Method: docs/standards/code.md#config-no-magic-numbers

    Parameters
    ----------
    name : str
        File stem inside ``config/``, e.g. ``"grid"``.
    directory : Path, optional
        Alternative config directory (tests).

    Returns
    -------
    Path
        ``<directory>/<name>.yaml``; existence is not checked.
    """
    return (directory or config_dir()) / f"{name}.yaml"


def load_raw_config(name: str, *, directory: Path | None = None) -> dict[str, object]:
    """Read ``config/<name>.yaml`` as a plain mapping (prefer :func:`load_config`).

    Method: docs/standards/code.md#config-no-magic-numbers

    Parameters
    ----------
    name : str
        File stem inside ``config/``.
    directory : Path, optional
        Alternative config directory (tests).

    Returns
    -------
    dict of str to object
        Top-level mapping of the file; an empty file gives ``{}``.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    TypeError
        If the top level of the file is not a mapping.
    """
    path = config_path(name, directory=directory)
    with path.open(encoding="utf-8") as fh:
        data: object = yaml.safe_load(fh)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a mapping at the top level")
    return cast(dict[str, object], data)


def load_config[M: ConfigModel](name: str, model: type[M], *, directory: Path | None = None) -> M:
    """Load ``config/<name>.yaml`` and validate it against ``model``.

    Method: docs/standards/code.md#config-no-magic-numbers

    Parameters
    ----------
    name : str
        File stem inside ``config/``, e.g. ``"alerts"``.
    model : type[ConfigModel]
        Pydantic schema the file must satisfy.
    directory : Path, optional
        Alternative config directory (tests).

    Returns
    -------
    ConfigModel
        Validated, frozen instance of ``model``.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    TypeError
        If the top level of the file is not a mapping.
    pydantic.ValidationError
        If a key is missing, unknown or of the wrong type.
    """
    return model.model_validate(load_raw_config(name, directory=directory))
