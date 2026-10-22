from pathlib import Path

import pytest
from pydantic import ValidationError

from clear.config import ConfigModel, load_config, load_raw_config


class Demo(ConfigModel):
    thresholds_ugm3: list[float]
    window_h: int


def write(directory: Path, name: str, text: str) -> None:
    (directory / f"{name}.yaml").write_text(text, encoding="utf-8")


def test_load_config_validates_into_frozen_model(tmp_path: Path):
    write(tmp_path, "demo", "thresholds_ugm3: [10.5, 20]\nwindow_h: 3\n")
    cfg = load_config("demo", Demo, directory=tmp_path)
    assert cfg.thresholds_ugm3 == [10.5, 20.0]
    with pytest.raises(ValidationError):
        cfg.window_h = 4  # type: ignore[misc]


def test_unknown_keys_are_errors(tmp_path: Path):
    write(tmp_path, "demo", "thresholds_ugm3: [1]\nwindow_h: 3\nsurprise: true\n")
    with pytest.raises(ValidationError):
        load_config("demo", Demo, directory=tmp_path)


def test_missing_file_and_non_mapping(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_raw_config("absent", directory=tmp_path)
    write(tmp_path, "listy", "- 1\n- 2\n")
    with pytest.raises(TypeError):
        load_raw_config("listy", directory=tmp_path)
    write(tmp_path, "empty", "")
    assert load_raw_config("empty", directory=tmp_path) == {}
