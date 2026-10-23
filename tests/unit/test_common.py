"""scripts/_common.py: sha256 survives a transient out-of-memory."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

COMMON = Path(__file__).resolve().parents[2] / "scripts" / "_common.py"


def load_common() -> ModuleType:
    spec = importlib.util.spec_from_file_location("common_under_test", COMMON)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses look the module up while it executes
    spec.loader.exec_module(module)
    return module


class FailingDigest:
    def __init__(self, error: BaseException) -> None:
        self.error = error

    def update(self, data: bytes) -> None:
        raise self.error

    def hexdigest(self) -> str:
        raise AssertionError("never reached")


def setup(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, failures: int, error: BaseException
) -> tuple[ModuleType, Path, list[int], list[float]]:
    """Load _common with a hashlib whose first ``failures`` digests raise ``error``.

    Returns the module, a file holding b"abc", the digest calls and the sleep calls.
    """
    common = load_common()
    calls: list[int] = []
    sleeps: list[float] = []

    def sha256() -> object:
        calls.append(1)
        return FailingDigest(error) if len(calls) <= failures else hashlib.sha256()

    monkeypatch.setattr(common, "hashlib", SimpleNamespace(sha256=sha256))
    monkeypatch.setattr(common, "time", SimpleNamespace(sleep=sleeps.append))
    path = tmp_path / "a.bin"
    path.write_bytes(b"abc")
    return common, path, calls, sleeps


def test_hash_retries_after_out_of_memory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    common, path, calls, sleeps = setup(monkeypatch, tmp_path, 1, MemoryError())

    assert common.sha256_file(path) == hashlib.sha256(b"abc").hexdigest()
    assert len(calls) == 2
    assert sleeps == [common.HASH_RETRY_WAIT_MIN * 60]
    assert f"retry 1/{common.HASH_TRIES - 1}" in capsys.readouterr().err


def test_hash_gives_up_after_the_last_try(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    common, path, calls, sleeps = setup(monkeypatch, tmp_path, 10**6, MemoryError())

    with pytest.raises(MemoryError):
        common.sha256_file(path)
    assert len(calls) == common.HASH_TRIES
    assert len(sleeps) == common.HASH_TRIES - 1  # no wait after the final failure


@pytest.mark.parametrize("errno_", [5, 22])  # EIO; EINVAL is also how Windows reports low memory
def test_hash_does_not_retry_read_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, errno_: int
) -> None:
    common, path, calls, sleeps = setup(monkeypatch, tmp_path, 1, OSError(errno_, "read failed"))

    with pytest.raises(OSError, match="read failed"):
        common.sha256_file(path)
    assert len(calls) == 1
    assert sleeps == []
