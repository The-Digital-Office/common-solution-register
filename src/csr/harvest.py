"""``csr harvest``: fetch and check owner-hosted records (specification 6.11).

For each pointer record, the harvester fetches the registered ``source``
over HTTPS only, within a size limit and a timeout, never following a
redirect to an address that is not HTTPS (R15). It checks that the file's
``id`` and ``owner.organisation`` match the pointer (R14), that its
``record_status`` may be owner-hosted (R16), and validates it against the
schema and rules. Each linked ``publiccode.yml`` is checked with the official
parser (R17). Sources in this repository's default branch are read from the
working tree, so a pull request is checked with its own changes.
"""

from __future__ import annotations

import hashlib
import re
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from csr.config import Config
from csr.findings import Finding, error, has_errors
from csr.records import Record, parse
from csr.rules import Context
from csr.validate import check_record

#: Fetches a URL within limits. Returns the bytes, or raises FetchError.
Fetcher = Callable[[str, int, int], bytes]


class FetchError(Exception):
    """A source could not be fetched within the rules (R15)."""


class _HttpsOnly(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not newurl.startswith("https://"):
            raise FetchError(f"redirected to an address that is not HTTPS: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url: str, max_bytes: int, timeout: int) -> bytes:
    """Fetch over HTTPS within the size limit and timeout (R15)."""
    if not url.startswith("https://"):
        raise FetchError("the address is not HTTPS")
    opener = urllib.request.build_opener(_HttpsOnly)
    request = urllib.request.Request(url, headers={"User-Agent": "csr-harvest"})
    try:
        with opener.open(request, timeout=timeout) as response:
            body = response.read(max_bytes + 1)
    except FetchError:
        raise
    except urllib.error.HTTPError as exc:
        raise FetchError(f"the address returned HTTP {exc.code}") from exc
    except (urllib.error.URLError, OSError, ValueError) as exc:
        reason = getattr(exc, "reason", exc)
        raise FetchError(f"the address did not respond: {reason}") from exc
    if len(body) > max_bytes:
        raise FetchError(f"the file is larger than {max_bytes:,} bytes")
    return body


def content_hash(body: bytes) -> str:
    return "sha256:" + hashlib.sha256(body).hexdigest()


@dataclass
class Fetched:
    """A source's bytes, or why there are none."""

    body: bytes | None
    problem: str = ""
    from_repository: bool = False


def get_source(url: str, root: Path, config: Config, fetcher: Fetcher | None) -> Fetched:
    """Read a source: from the working tree if it is in this repository, else from the network.
    With no fetcher (no network), other sources are not fetched."""
    if url.startswith(config.raw_prefix):
        path = (root / url.removeprefix(config.raw_prefix)).resolve()
        if root.resolve() not in path.parents or not path.is_file():
            return Fetched(None, "the file is not in this repository", from_repository=True)
        body = path.read_bytes()
        if len(body) > config.harvest_max_bytes:
            return Fetched(None, f"the file is larger than {config.harvest_max_bytes:,} bytes", True)
        return Fetched(body, from_repository=True)
    if fetcher is None:
        return Fetched(None, "not fetched: the network was not used")
    try:
        return Fetched(fetcher(url, config.harvest_max_bytes, config.harvest_timeout_seconds))
    except FetchError as exc:
        return Fetched(None, str(exc))


EXAMPLE_RANGE = re.compile(r"^csr-9\d{3}$")


def check_source(pointer: Record, body: bytes, context: Context) -> tuple[Record, list[Finding]]:
    """Check a harvested file: R14 owner match, R16 status, then the schema and rules."""
    source = pointer.data["source"]
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        record = Record(source, None)
        return record, [error(source, "R15", "", "the file is not UTF-8 text", "Save the file as UTF-8.")]
    record = parse(text, source)
    findings = list(record.findings)
    if record.data is None:
        return record, findings
    data = record.data
    owner = data.get("owner", {}).get("organisation") if isinstance(data.get("owner"), dict) else None
    if data.get("id") != pointer.id:
        findings.append(error(source, "R14", "id", f"the file's id is {data.get('id')!r}, but it is registered as {pointer.id}",
                              f"Set id: {pointer.id} in the hosted file."))  # fmt: skip
    if owner != pointer.data.get("expected_owner"):
        findings.append(error(source, "R14", "owner.organisation",
                              f"the file says owner.organisation: {owner!r}, but the registered owner is "
                              f"{pointer.data.get('expected_owner')!r}",
                              "The owner must match the registration; ask for the registration to be changed if the "
                              "owner has changed."))  # fmt: skip
    status = data.get("record_status")
    allowed = status in ("owner-confirmed", "withdrawn") or (status == "example" and EXAMPLE_RANGE.match(pointer.id or ""))
    if not allowed:
        findings.append(error(source, "R16", "record_status",
                              f"an owner-hosted record cannot be {status!r}",
                              "Owner-hosted records are owner-confirmed or withdrawn: publishing the file is the "
                              "owner's own confirmation."))  # fmt: skip
    findings += check_record(record, context)
    return record, findings


@dataclass
class SourceResult:
    """The outcome of harvesting one pointer."""

    id: str
    source: str
    expected_owner: str
    state: str  # ok | failing | unavailable | not-harvested
    findings: list[Finding] = field(default_factory=list)
    text: str | None = None
    hash: str | None = None
    from_repository: bool = False

    @property
    def problem(self) -> str:
        return next((f.message for f in self.findings if f.rule == "R15"), "")


def harvest_source(pointer: Record, root: Path, config: Config, context: Context,
                   fetcher: Fetcher | None) -> SourceResult:  # fmt: skip
    data = pointer.data
    result = SourceResult(pointer.id, data["source"], data.get("expected_owner", ""), "not-harvested")
    fetched = get_source(data["source"], root, config, fetcher)
    result.from_repository = fetched.from_repository
    if fetched.body is None:
        if fetched.problem.startswith("not fetched"):
            return result
        result.state = "unavailable"
        result.findings = [error(data["source"], "R15", "", fetched.problem,
                                 "Check the address is right, public and served over HTTPS.")]  # fmt: skip
        return result
    _, findings = check_source(pointer, fetched.body, context)
    result.findings = findings
    result.hash = content_hash(fetched.body)
    if has_errors(findings):
        result.state = "failing"
    else:
        result.state = "ok"
        result.text = fetched.body.decode("utf-8")
    return result
