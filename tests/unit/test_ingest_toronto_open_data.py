# No network: every test injects a fake fetcher. The package payload is trimmed from the real
# package_show response for regional-municipal-boundary (2026-10-24).
import hashlib
import io
import json
import urllib.request
from datetime import UTC, datetime, timedelta, timezone
from http.client import HTTPMessage
from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from clear.ingest import toronto_open_data as tod
from clear.ingest.toronto_open_data import (
    CKAN_BASE_URL,
    DownloadedFile,
    fetch_resource,
    package_show_url,
    parse_package,
    provider_file_name,
    select_resource,
)

PACKAGE_ID = "regional-municipal-boundary"
RESOURCE = "toronto-boundary-wgs84"
ZIP_URL = (
    "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/841fb820-46d0-46ac-8dcb-d20f27e57bcc"
    "/resource/41bf97f0-da1a-46a9-ac25-5ce0078d6760/download/toronto-boundary-wgs84.zip"
)
ZIP_BYTES = b"PK\x03\x04 fake shapefile zip"
RECEIVED = datetime(2026, 10, 24, 20, 47, 8, tzinfo=UTC)


def package_payload(
    *, success: bool = True, resources: list[dict] | None = None, result: bool = True
) -> bytes:
    if resources is None:
        resources = [
            {
                "id": "41bf97f0-da1a-46a9-ac25-5ce0078d6760",
                "name": RESOURCE,
                "format": "SHP",
                "url": ZIP_URL,
                "last_modified": "2019-07-23T17:56:39.415158",
                "size": 195966,
            }
        ]
    package = {
        "id": "841fb820-46d0-46ac-8dcb-d20f27e57bcc",
        "name": PACKAGE_ID,
        "title": "Regional Municipal Boundary",
        "license_id": "open-government-licence-toronto",
        "license_title": "open-government-licence-toronto",
        "last_refreshed": "2019-07-23 17:56:39.415158",
        "resources": resources,
    }
    return json.dumps({"success": success, "result": package if result else None}).encode()


def one_resource(url: str) -> list[dict]:
    return [{"id": "a", "name": "x", "format": "SHP", "url": url}]


def fake_fetcher(responses: dict[str, bytes]):
    calls: list[str] = []

    def fetch(url: str) -> bytes:
        calls.append(url)
        return responses[url]

    return fetch, calls


def standard_fetcher(resources: list[dict] | None = None):
    meta_url = package_show_url(CKAN_BASE_URL, PACKAGE_ID)
    zip_url = ZIP_URL if resources is None else resources[0]["url"]
    return fake_fetcher({meta_url: package_payload(resources=resources), zip_url: ZIP_BYTES})


# --- package_show_url / parse_package -------------------------------------------------


def test_package_show_url_encodes_the_id():
    url = package_show_url(CKAN_BASE_URL + "/", "a b&c")
    assert url == (
        "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show?id=a+b%26c"
    )


def test_package_show_url_refuses_plain_http():
    with pytest.raises(ValueError, match="only https"):
        package_show_url("http://ckan.example", PACKAGE_ID)


def test_parse_package_keeps_licence_and_resource_size():
    package = parse_package(package_payload())
    assert package.license_id == "open-government-licence-toronto"
    assert [r.name for r in package.resources] == [RESOURCE]
    assert package.resources[0].size_bytes == 195966


def test_parse_package_rejects_ckan_failure():
    with pytest.raises(ValueError, match="failure"):
        parse_package(package_payload(success=False))


def test_parse_package_rejects_success_without_result():
    with pytest.raises(ValueError, match="failure"):
        parse_package(package_payload(result=False))


def test_parse_package_rejects_non_json():
    with pytest.raises(ValueError, match="not understood"):
        parse_package(b"<html>404</html>")


# --- select_resource / provider_file_name ---------------------------------------------


def test_select_resource_needs_exactly_one_match():
    two = one_resource(ZIP_URL) * 2
    with pytest.raises(ValueError, match="2 resources named 'x'"):
        select_resource(parse_package(package_payload(resources=two)), "x")
    with pytest.raises(ValueError, match="0 resources named 'missing'"):
        select_resource(parse_package(package_payload()), "missing")


def test_select_resource_rejects_plain_http():
    http = one_resource(ZIP_URL.replace("https", "http"))
    with pytest.raises(ValueError, match="only https"):
        select_resource(parse_package(package_payload(resources=http)), "x")


def test_provider_file_name_is_last_path_segment():
    assert provider_file_name(ZIP_URL) == "toronto-boundary-wgs84.zip"
    assert provider_file_name("https://h/x/My%20File.zip?dl=1") == "My File.zip"


@pytest.mark.parametrize(
    "url",
    [
        "https://h/",  # no name
        "https://h/x/..",  # parent directory
        "https://h/x/%2E%2E",  # encoded parent directory
        "https://h/x/..%5Cevil.zip",  # encoded backslash (Windows separator)
        "https://h/x/C:evil.zip",  # drive prefix: Path("inbox") / "C:evil.zip" leaves inbox
        "https://h/x/a%2F..%2Fevil.zip",  # encoded slash
    ],
)
def test_provider_file_name_rejects_names_that_leave_the_folder(url: str):
    with pytest.raises(ValueError, match="no safe file name"):
        provider_file_name(url)


# --- https only -----------------------------------------------------------------------


def test_http_get_refuses_plain_http_before_any_network_call():
    with pytest.raises(ValueError, match="only https"):
        tod._http_get("http://ckan.example/file.zip")


def test_redirect_to_http_is_refused():
    handler = tod._HttpsOnlyRedirect()
    request = urllib.request.Request("https://ckan.example/file.zip")
    new_url = "http://evil.example/f.zip"
    with pytest.raises(ValueError, match="only https"):
        handler.redirect_request(request, io.BytesIO(), 302, "Found", HTTPMessage(), new_url)


def test_redirect_to_https_is_followed():
    handler = tod._HttpsOnlyRedirect()
    request = urllib.request.Request("https://ckan.example/file.zip")
    new_url = "https://mirror.example/f.zip"
    redirected = handler.redirect_request(
        request, io.BytesIO(), 302, "Found", HTTPMessage(), new_url
    )
    assert redirected is not None
    assert redirected.full_url == new_url


# --- fetch_resource -------------------------------------------------------------------


def test_fetch_resource_saves_provider_name_hash_and_receipt_time(tmp_path: Path):
    fetch, calls = standard_fetcher()
    out = tmp_path / "inbox" / "toronto-city-boundary"
    saved = fetch_resource(PACKAGE_ID, RESOURCE, out, fetch=fetch, clock=lambda: RECEIVED)
    assert calls == [package_show_url(CKAN_BASE_URL, PACKAGE_ID), ZIP_URL]
    assert saved.path == out / "toronto-boundary-wgs84.zip"
    assert saved.path.read_bytes() == ZIP_BYTES
    assert saved.n_bytes == len(ZIP_BYTES)
    assert saved.sha256 == hashlib.sha256(ZIP_BYTES).hexdigest()
    assert saved.downloaded_utc == RECEIVED
    assert sorted(p.name for p in out.iterdir()) == ["toronto-boundary-wgs84.zip"]


def test_fetch_resource_default_clock_is_utc_now(tmp_path: Path):
    fetch, _ = standard_fetcher()
    before = datetime.now(UTC)
    saved = fetch_resource(PACKAGE_ID, RESOURCE, tmp_path, fetch=fetch)
    assert saved.downloaded_utc.utcoffset() == timedelta(0)
    assert before <= saved.downloaded_utc <= datetime.now(UTC)


def test_downloaded_file_rejects_non_utc_time(tmp_path: Path):
    toronto = timezone(timedelta(hours=-4))
    with pytest.raises(ValidationError, match="must be UTC"):
        DownloadedFile(
            path=tmp_path / "f.zip",
            n_bytes=1,
            sha256="0" * 64,
            url=ZIP_URL,
            downloaded_utc=RECEIVED.astimezone(toronto),
            package=parse_package(package_payload()),
        )


def test_fetch_resource_rejects_drive_prefixed_name_and_writes_nothing(tmp_path: Path):
    resources = one_resource("https://h/download/C:evil.zip")
    fetch, calls = standard_fetcher(resources)
    out = tmp_path / "inbox" / "slug"
    with pytest.raises(ValueError, match="no safe file name"):
        fetch_resource(PACKAGE_ID, "x", out, fetch=fetch)
    assert calls == [package_show_url(CKAN_BASE_URL, PACKAGE_ID)]
    assert not out.exists()


def test_fetch_resource_never_overwrites_a_waiting_file(tmp_path: Path):
    fetch, calls = standard_fetcher()
    existing = tmp_path / "toronto-boundary-wgs84.zip"
    existing.write_bytes(b"waiting")
    with pytest.raises(FileExistsError):
        fetch_resource(PACKAGE_ID, RESOURCE, tmp_path, fetch=fetch)
    assert existing.read_bytes() == b"waiting"
    assert ZIP_URL not in calls


def test_write_new_file_refuses_existing_file(tmp_path: Path):
    existing = tmp_path / "f.zip"
    existing.write_bytes(b"waiting")
    with pytest.raises(FileExistsError, match="never overwritten"):
        tod._write_new_file(existing, b"new")
    assert existing.read_bytes() == b"waiting"


def test_failed_write_leaves_no_partial_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    real_open = Path.open

    class BrokenHandle:
        def __enter__(self):
            return self

        def __exit__(self, *exc: object) -> bool:
            return False

        def write(self, data: bytes) -> int:
            raise OSError("disk full")

    def failing_open(self: Path, mode: str = "r", *args, **kwargs):
        handle = real_open(self, mode, *args, **kwargs)
        if mode == "xb":  # the file now exists; the write below fails
            handle.close()
            return BrokenHandle()
        return handle

    monkeypatch.setattr(Path, "open", failing_open)
    fetch, _ = standard_fetcher()
    with pytest.raises(OSError, match="disk full"):
        fetch_resource(PACKAGE_ID, RESOURCE, tmp_path, fetch=fetch)
    assert list(tmp_path.iterdir()) == []


# --- CLI --------------------------------------------------------------------------------


def patch_fetch(monkeypatch: pytest.MonkeyPatch) -> None:
    fetch, _ = standard_fetcher()
    real = tod.fetch_resource

    def offline(package_id: str, resource_name: str, out_dir: Path) -> DownloadedFile:
        return real(package_id, resource_name, out_dir, fetch=fetch, clock=lambda: RECEIVED)

    monkeypatch.setattr(tod, "fetch_resource", offline)


def test_cli_prints_one_provenance_line(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    patch_fetch(monkeypatch)
    out = tmp_path / "inbox" / "toronto-city-boundary"
    args = ["--package", PACKAGE_ID, "--resource", RESOURCE, "--out", str(out)]
    result = CliRunner().invoke(tod.app, args)
    assert result.exit_code == 0, result.output
    line = result.output.strip()
    assert line.startswith(str(out / "toronto-boundary-wgs84.zip"))
    assert f"sha256={hashlib.sha256(ZIP_BYTES).hexdigest()}" in line
    assert "downloaded_utc=2026-10-24T20:47:08Z" in line
    assert "license=open-government-licence-toronto" in line


def test_cli_exits_non_zero_when_the_file_is_waiting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    patch_fetch(monkeypatch)
    (tmp_path / "toronto-boundary-wgs84.zip").write_bytes(b"waiting")
    args = ["--package", PACKAGE_ID, "--resource", RESOURCE, "--out", str(tmp_path)]
    result = CliRunner().invoke(tod.app, args)
    assert result.exit_code != 0
    assert isinstance(result.exception, FileExistsError)
