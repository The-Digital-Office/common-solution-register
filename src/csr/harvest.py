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

import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from csr.config import Config
from csr.findings import Finding, error, has_errors, warning
from csr.records import Record, parse, read_register
from csr.rules import Context
from csr.schema import ROOT
from csr.taxonomy import load_all
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
    name: str = ""  # the name the file gives, even if it fails, for the harvest report

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
    harvested, findings = check_source(pointer, fetched.body, context)
    result.findings = findings
    if isinstance(harvested.data, dict) and isinstance(harvested.data.get("name"), str):
        result.name = harvested.data["name"][:200]
    result.hash = content_hash(fetched.body)
    if has_errors(findings):
        result.state = "failing"
    else:
        result.state = "ok"
        result.text = fetched.body.decode("utf-8")
    return result


# State: last valid copies, hashes and dates, carried from one harvest to the next
# (specification 6.11: read from the live site, written back with each deployment).

STATE_VERSION = 1


def empty_state() -> dict:
    return {"state_version": STATE_VERSION, "generated": None, "sources": {}, "publiccode": {}}


def _iso(moment) -> str:
    return moment.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def update_entry(previous: dict | None, result: SourceResult, now) -> dict:
    """The new state of one source, from its previous state and this harvest's result."""
    same_registration = (
        previous is not None
        and previous.get("source") == result.source
        and previous.get("expected_owner") == result.expected_owner
    )
    prev = previous if same_registration else {}
    if result.state == "not-harvested":  # nothing new is known
        return copy.deepcopy(prev) if prev else {
            "source": result.source, "expected_owner": result.expected_owner, "name": "", "state": "not-harvested",
            "checked_at": None, "harvested_at": None, "content_hash": None, "last_changed": None, "last_valid": None,
            "failing_since": None, "unavailable_since": None, "findings": [],
        }  # fmt: skip
    entry = {
        "source": result.source,
        "expected_owner": result.expected_owner,
        "name": result.name or prev.get("name", ""),
        "state": result.state,
        "checked_at": _iso(now),
        "harvested_at": prev.get("harvested_at"),
        "content_hash": prev.get("content_hash"),
        "last_changed": prev.get("last_changed"),
        "last_valid": prev.get("last_valid"),
        "failing_since": None,
        "unavailable_since": None,
        "findings": [f.as_dict() for f in result.findings],
    }
    if result.state == "ok":
        if result.hash != prev.get("content_hash"):
            entry["last_changed"] = now.date().isoformat()
        entry.update(harvested_at=_iso(now), content_hash=result.hash, last_valid=result.text)
    elif result.state == "failing":
        entry["failing_since"] = prev.get("failing_since") if prev.get("state") == "failing" else _iso(now)
    elif result.state == "unavailable":
        entry["unavailable_since"] = prev.get("unavailable_since") if prev.get("state") == "unavailable" else _iso(now)
    return entry


def read_state(location: str | None, fetcher: Fetcher | None, config: Config) -> tuple[dict, str]:
    """The previous state, from a file or the live site. Returns (state, note); a state that
    cannot be read means starting fresh, which is harmless (specification 6.11)."""
    if not location:
        return empty_state(), "no previous state given: starting fresh"
    try:
        if location.startswith("https://"):
            if fetcher is None:
                return empty_state(), "previous state not fetched: the network was not used"
            raw = fetcher(location, 16 * 1024 * 1024, config.harvest_timeout_seconds)
        else:
            raw = Path(location).read_bytes()
        state = json.loads(raw)
    except (FetchError, OSError, ValueError) as exc:
        return empty_state(), f"previous state could not be read ({exc}): starting fresh"
    if not isinstance(state, dict) or state.get("state_version") != STATE_VERSION:
        return empty_state(), "previous state is in an unknown format: starting fresh"
    state.setdefault("sources", {})
    state.setdefault("publiccode", {})
    return state, f"previous state read from {location}"


def run(root: Path, config: Config, previous: dict, *, now, fetcher: Fetcher | None = None,
        only: set[str] | None = None, parser: ParserRunner | None = None) -> tuple[dict, list[SourceResult]]:  # fmt: skip
    """Harvest every pointer (or only the given ids), check every linked publiccode.yml,
    and return the new state and the results."""
    records, _ = read_register(root / "records", root=root)
    pointers = [r for r in records if r.data is not None and r.is_pointer and r.id]
    known = frozenset(r.id for r in records if r.id)
    context = Context(taxonomies=load_all(), today=now.date(), known_ids=known)
    state = {**empty_state(), "generated": _iso(now), "publiccode": dict(previous.get("publiccode", {}))}
    results = []
    for record in sorted(pointers, key=lambda r: r.id):
        before = previous.get("sources", {}).get(record.id)
        if only is not None and record.id not in only:
            if before is not None:
                state["sources"][record.id] = before
            continue
        result = harvest_source(record, root, config, context, fetcher)
        results.append(result)
        state["sources"][record.id] = update_entry(before, result, now)

    runner = parser or run_parser
    for url in publiccode_urls(root, state):
        verdict = check_publiccode(url, root, config, fetcher, runner, now)
        if verdict["state"] == "not-checked" and url in state["publiccode"]:
            continue  # keep what was known
        state["publiccode"][url] = verdict
    for result in results:
        entry = state["sources"][result.id]
        if entry.get("last_valid") and result.state == "ok":
            data = parse(entry["last_valid"], result.source).data
            extra = r17_findings(result.source, data, state["publiccode"])
            result.findings += extra
            entry["findings"] += [f.as_dict() for f in extra]
    return state, results


# R17: each linked publiccode.yml is checked with the official parser
# (publiccode-parser-go, installed by tools/install-publiccode-parser.py).

PARSER_VERSION = "v5.4.3"
#: Runs the parser on a file. Returns its findings ([{key, description, line, column, type}]),
#: or None if the parser is not installed.
ParserRunner = Callable[[Path], "list[dict] | None"]


def find_parser() -> str | None:
    """The parser binary: CSR_PUBLICCODE_PARSER, the pinned install in .tools/, or on PATH."""
    explicit = os.environ.get("CSR_PUBLICCODE_PARSER")
    if explicit:
        return explicit
    pinned = ROOT / ".tools" / "publiccode-parser" / PARSER_VERSION / "publiccode-parser"
    if pinned.is_file():
        return str(pinned)
    return shutil.which("publiccode-parser")


def run_parser(path: Path) -> list[dict] | None:
    binary = find_parser()
    if binary is None:
        return None
    # -no-network: the harvester reaches only registered sources (specification 6.1).
    completed = subprocess.run([binary, "-json", "-no-network", str(path)], capture_output=True, text=True,
                               timeout=60, check=False)  # fmt: skip
    try:
        found = json.loads(completed.stdout or "[]")
    except ValueError:
        return [{"type": "error", "key": "", "description": (completed.stderr or completed.stdout).strip()[:500],
                 "line": 0, "column": 0}]  # fmt: skip
    return found if isinstance(found, list) else []


def check_publiccode(url: str, root: Path, config: Config, fetcher: Fetcher | None,
                     runner: ParserRunner, now) -> dict:  # fmt: skip
    """The parser's verdict on one publiccode.yml: valid, invalid, unavailable or not-checked."""
    result = {"state": "not-checked", "checked_at": _iso(now), "parser": PARSER_VERSION, "messages": []}
    fetched = get_source(url, root, config, fetcher)
    if fetched.body is None:
        if fetched.problem.startswith("not fetched"):
            result["messages"] = ["Not fetched: the network was not used."]
        else:
            result.update(state="unavailable", messages=[fetched.problem[0].upper() + fetched.problem[1:] + "."])
        return result
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "publiccode.yml"
        path.write_bytes(fetched.body)
        found = runner(path)
    if found is None:
        result["messages"] = ["The official parser is not installed where the harvest ran."]
        return result
    errors = [f for f in found if f.get("type", "error") == "error"]
    result["state"] = "invalid" if errors else "valid"
    result["messages"] = [
        f"{f.get('type', 'error')}: {f.get('key') + ': ' if f.get('key') else ''}{f.get('description', '')}"
        + (f" (line {f['line']})" if f.get("line") else "")
        for f in found
    ]
    return result


def publiccode_urls(root: Path, state: dict) -> list[str]:
    """Every publiccode_url linked from a local record or from a harvested copy."""
    records, _ = read_register(root / "records", root=root)
    documents = [r.data for r in records if isinstance(r.data, dict) and not r.is_pointer]
    for entry in state.get("sources", {}).values():
        if entry.get("last_valid"):
            documents.append(parse(entry["last_valid"], entry["source"]).data)
    urls = set()
    for data in filter(None, documents):
        for codebase in data.get("codebases") or []:
            if isinstance(codebase, dict) and isinstance(codebase.get("publiccode_url"), str):
                urls.add(codebase["publiccode_url"])
    return sorted(urls)


def r17_findings(source_label: str, data: dict, publiccode: dict) -> list[Finding]:
    """R17 warnings for a harvested record's codebases whose publiccode.yml fails the parser."""
    found = []
    for i, codebase in enumerate(data.get("codebases") or []):
        url = codebase.get("publiccode_url") if isinstance(codebase, dict) else None
        verdict = publiccode.get(url or "", {})
        if verdict.get("state") == "invalid":
            detail = "; ".join(m for m in verdict["messages"] if m.startswith("error"))[:400]
            found.append(warning(source_label, "R17", f"codebases[{i}].publiccode_url",
                                 f"the linked publiccode.yml fails the official parser: {detail}",
                                 "Correct the codebase's publiccode.yml; the parser's messages say what to change."))  # fmt: skip
    return found
