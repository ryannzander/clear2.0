"""Download one resource of a City of Toronto Open Data (CKAN) package into ``inbox/``.

Run: ``uv run python -m clear.ingest.toronto_open_data --package <id> --resource <name>
--out inbox/<dataset-slug>``. The package is looked up with the CKAN ``package_show``
action; the resource is chosen by its exact name and saved under the provider's file name.
No credentials: the portal is public. Provenance goes in ``data/sources.yaml``.
"""

import hashlib
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from http.client import HTTPMessage
from pathlib import Path, PurePosixPath
from typing import IO, Annotated
from urllib.parse import unquote, urlencode, urlparse

import typer
from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
)

__all__ = [
    "CKAN_BASE_URL",
    "CkanPackage",
    "CkanResource",
    "DownloadedFile",
    "Fetcher",
    "app",
    "fetch_resource",
    "main",
    "package_show_url",
    "parse_package",
    "provider_file_name",
    "select_resource",
]

# CKAN API host of open.toronto.ca; open.toronto.ca/api/3/... itself returns 404 (2026-10-24).
CKAN_BASE_URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca"
_TIMEOUT_S = 60
_USER_AGENT = "clear-ingest/0.1"
# Characters that would let a file name leave out_dir or name a drive on Windows.
_UNSAFE_NAME_CHARS = ("/", "\\", ":")

Fetcher = Callable[[str], bytes]


class CkanResource(BaseModel):
    """One downloadable file of a CKAN package (fields used by this module).

    Method: docs/standards/code.md#error-handling-fail-loud-at-boundaries
    ``size_bytes`` is CKAN's ``size`` field, in bytes.
    """

    model_config = ConfigDict(extra="ignore", frozen=True)
    id: str
    name: str
    format: str
    url: str
    last_modified: str | None = None
    size_bytes: int | None = Field(default=None, alias="size")


class CkanPackage(BaseModel):
    """The parts of a CKAN ``package_show`` result that provenance needs.

    Method: docs/standards/code.md#error-handling-fail-loud-at-boundaries
    """

    model_config = ConfigDict(extra="ignore", frozen=True)
    id: str
    name: str
    title: str
    license_id: str | None = None
    license_title: str | None = None
    last_refreshed: str | None = None
    resources: list[CkanResource]


class _PackageShowResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)
    success: bool
    result: CkanPackage | None = None


class DownloadedFile(BaseModel):
    """What was saved: path, size, hash and receipt time of the file, plus its package.

    Method: .claude/skills/ingest/SKILL.md#steps
    Step 3 (download) and step 4 (provenance). ``n_bytes`` is in bytes; ``downloaded_utc``
    is tz-aware UTC, taken when the file body was received.
    """

    model_config = ConfigDict(frozen=True)
    path: Path
    n_bytes: int
    sha256: str
    url: str
    downloaded_utc: AwareDatetime
    package: CkanPackage

    @field_validator("downloaded_utc")
    @classmethod
    def _must_be_utc(cls, value: datetime) -> datetime:
        if value.utcoffset() != timedelta(0):
            raise ValueError(f"downloaded_utc must be UTC, got offset {value.utcoffset()}")
        return value


def _require_https(url: str) -> None:
    if urlparse(url).scheme != "https":
        raise ValueError(f"only https URLs are fetched: {url}")


def package_show_url(base_url: str, package_id: str) -> str:
    """Return the CKAN ``package_show`` URL for ``package_id``.

    Method: .claude/skills/ingest/SKILL.md#steps
    Step 2: query parameters are arguments.

    Parameters
    ----------
    base_url : str
        CKAN host, e.g. :data:`CKAN_BASE_URL`; must be https.
    package_id : str
        Package name or id, e.g. ``"regional-municipal-boundary"``; URL-encoded here.

    Returns
    -------
    str
        ``<base_url>/api/3/action/package_show?id=<package_id>``.

    Raises
    ------
    ValueError
        If ``base_url`` is not https.
    """
    _require_https(base_url)
    return f"{base_url.rstrip('/')}/api/3/action/package_show?{urlencode({'id': package_id})}"


def parse_package(payload: bytes) -> CkanPackage:
    """Validate a ``package_show`` response body and return the package.

    Method: docs/standards/code.md#error-handling-fail-loud-at-boundaries

    Parameters
    ----------
    payload : bytes
        Raw JSON body returned by the CKAN API.

    Returns
    -------
    CkanPackage
        The ``result`` object of the response.

    Raises
    ------
    ValueError
        If the body is not a CKAN response with a valid package, or CKAN reports
        ``success: false`` or no ``result``.
    """
    try:
        response = _PackageShowResponse.model_validate_json(payload)
    except ValidationError as err:
        raise ValueError(f"package_show response not understood: {payload[:300]!r}") from err
    if not response.success or response.result is None:
        raise ValueError(f"package_show reported failure: {payload[:300]!r}")
    return response.result


def select_resource(package: CkanPackage, resource_name: str) -> CkanResource:
    """Return the one resource of ``package`` whose name equals ``resource_name``.

    Method: docs/standards/code.md#error-handling-fail-loud-at-boundaries

    Parameters
    ----------
    package : CkanPackage
        Parsed package.
    resource_name : str
        Exact CKAN resource name, e.g. ``"toronto-boundary-wgs84"``.

    Returns
    -------
    CkanResource
        The matching resource.

    Raises
    ------
    ValueError
        If no resource or more than one resource has that name, or its URL is not https.
    """
    matches = [r for r in package.resources if r.name == resource_name]
    if len(matches) != 1:
        names = [r.name for r in package.resources]
        raise ValueError(
            f"{len(matches)} resources named {resource_name!r} in {package.name!r}; "
            f"available: {names}"
        )
    resource = matches[0]
    _require_https(resource.url)
    return resource


def provider_file_name(url: str) -> str:
    """Return the provider's file name: the last segment of the URL path.

    Method: .claude/skills/ingest/SKILL.md#steps
    Step 3: keep the provider's file names.

    Parameters
    ----------
    url : str
        Download URL.

    Returns
    -------
    str
        e.g. ``"toronto-boundary-wgs84.zip"``.

    Raises
    ------
    ValueError
        If the URL path has no file name, or the name could leave the target folder
        (``.``, ``..``, a slash or backslash, or a drive prefix such as ``C:``).
    """
    # Split first, then decode: an encoded slash (%2F) must not become a path separator.
    name = unquote(PurePosixPath(urlparse(url).path).name)
    if name in {"", ".", ".."} or any(c in name for c in _UNSAFE_NAME_CHARS):
        raise ValueError(f"no safe file name in URL path: {url}")
    return name


class _HttpsOnlyRedirect(urllib.request.HTTPRedirectHandler):
    # urllib follows https -> http redirects by default; refuse any non-https hop.
    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: IO[bytes],
        code: int,
        msg: str,
        headers: HTTPMessage,
        newurl: str,
    ) -> urllib.request.Request | None:
        _require_https(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _http_get(url: str) -> bytes:
    _require_https(url)
    opener = urllib.request.build_opener(_HttpsOnlyRedirect())
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with opener.open(request, timeout=_TIMEOUT_S) as response:
        body: bytes = response.read()
    return body


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _write_new_file(target: Path, content: bytes) -> None:
    # "xb" creates the file or fails, so a waiting inbox file is never replaced.
    try:
        handle = target.open("xb")
    except FileExistsError as err:
        raise FileExistsError(f"{target} exists; inbox files are never overwritten") from err
    try:
        with handle:
            handle.write(content)
    except BaseException:
        # A half-written file in inbox/ would be filed by intake as if complete.
        target.unlink(missing_ok=True)
        raise


def fetch_resource(
    package_id: str,
    resource_name: str,
    out_dir: Path,
    *,
    base_url: str = CKAN_BASE_URL,
    fetch: Fetcher = _http_get,
    clock: Callable[[], datetime] = _utc_now,
) -> DownloadedFile:
    """Look up ``package_id``, download ``resource_name`` into ``out_dir``, hash it.

    Method: .claude/skills/ingest/SKILL.md#steps
    Steps 2-3: typed fetch module, download into ``inbox/<dataset-slug>/``.

    Parameters
    ----------
    package_id : str
        CKAN package name or id.
    resource_name : str
        Exact CKAN resource name.
    out_dir : Path
        Destination folder, normally ``inbox/<dataset-slug>``; created if missing.
    base_url : str
        CKAN host; must be https.
    fetch : Callable[[str], bytes]
        Returns the body of an https GET; injected so tests run without the network.
    clock : Callable[[], datetime]
        Returns the current tz-aware UTC time; read once, when the file body arrives.

    Returns
    -------
    DownloadedFile
        Saved path, size (bytes), sha256 (hex), receipt time (UTC) and the package.

    Raises
    ------
    FileExistsError
        If the target file already exists: a waiting inbox file is never overwritten.
    ValueError
        From :func:`package_show_url`, :func:`parse_package`, :func:`select_resource` or
        :func:`provider_file_name`, or if the target would fall outside ``out_dir``.
    """
    package = parse_package(fetch(package_show_url(base_url, package_id)))
    resource = select_resource(package, resource_name)
    target = out_dir / provider_file_name(resource.url)
    if target.resolve().parent != out_dir.resolve():
        raise ValueError(f"{target} is not directly inside {out_dir}")
    if target.exists():
        raise FileExistsError(f"{target} exists; inbox files are never overwritten")
    content = fetch(resource.url)
    downloaded_utc = clock()
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_new_file(target, content)
    return DownloadedFile(
        path=target,
        n_bytes=len(content),
        sha256=hashlib.sha256(content).hexdigest(),
        url=resource.url,
        downloaded_utc=downloaded_utc,
        package=package,
    )


app = typer.Typer(help="Download a City of Toronto Open Data resource into inbox/.")


@app.command()
def main(
    package: Annotated[str, typer.Option(help="CKAN package id or name.")],
    resource: Annotated[str, typer.Option(help="Exact CKAN resource name.")],
    out: Annotated[Path, typer.Option(help="Destination folder: inbox/<dataset-slug>.")],
) -> None:
    """Download one resource; print path, bytes, sha256, receipt time (UTC) and licence.

    Method: .claude/skills/ingest/SKILL.md#steps
    Step 3: ``uv run python -m clear.ingest.toronto_open_data ... --out inbox/<slug>``.
    """
    saved = fetch_resource(package, resource, out)
    received = saved.downloaded_utc.astimezone(UTC).isoformat(timespec="seconds")
    typer.echo(
        f"{saved.path} bytes={saved.n_bytes} sha256={saved.sha256} "
        f"downloaded_utc={received.replace('+00:00', 'Z')} "
        f"license={saved.package.license_id} url={saved.url}"
    )


if __name__ == "__main__":
    app()
