"""The harvester (specification 6.11): R14 to R17, state, and the build."""

import io

import pytest
import yaml
from helpers import TODAY

from csr import harvest
from csr.config import load_config
from csr.harvest import FetchError, check_source, content_hash, get_source, harvest_source
from csr.records import Record
from csr.rules import Context
from csr.schema import ROOT, load_yaml_file
from csr.taxonomy import load_all

CONFIG = load_config(ROOT)
HOSTED = ROOT / "examples" / "hosted" / "csr-9006" / "solution.yml"
REMOTE = "https://owner.example.gov.uk/solution.yml"


@pytest.fixture
def context():
    return Context(taxonomies=load_all(), today=TODAY, known_ids=frozenset({"csr-9003", "csr-9006", "csr-0001"}))


def pointer(record_id="csr-9006", source=REMOTE, owner="Example Council"):
    return Record(f"records/{record_id}.yaml", {"id": record_id, "source": source, "expected_owner": owner},
                  in_register=True, filename=f"{record_id}.yaml")  # fmt: skip


def body(**changes):
    data = load_yaml_file(HOSTED)
    data.update(changes)
    return yaml.safe_dump(data, sort_keys=False).encode()


def serve(responses):
    """A fake network: URL to bytes, or to a FetchError message."""

    def fetcher(url, max_bytes, timeout):
        value = responses.get(url, "the address returned HTTP 404")
        if isinstance(value, str):
            raise FetchError(value)
        return value

    return fetcher


# Checkpoint a: fetching (R15), owner match (R14), status (R16) and validation


def test_a_valid_source_is_ok(context):
    result = harvest_source(pointer(), ROOT, CONFIG, context, serve({REMOTE: HOSTED.read_bytes()}))
    assert result.state == "ok" and result.findings == []
    assert result.text == HOSTED.read_text() and result.hash == content_hash(HOSTED.read_bytes())


def test_r14_id_and_owner_must_match(context):
    result = harvest_source(pointer(), ROOT, CONFIG, context,
                            serve({REMOTE: body(id="csr-9010", owner={"organisation": "Another Council",
                                                                     "sector": "local-government"})}))  # fmt: skip
    assert result.state == "failing"
    assert sorted((f.rule, f.path) for f in result.findings if f.rule == "R14") == [("R14", "id"), ("R14", "owner.organisation")]


@pytest.mark.parametrize(("record_id", "status", "allowed"), [
    ("csr-0006", "owner-confirmed", True), ("csr-0006", "withdrawn", True), ("csr-9006", "example", True),
    ("csr-0006", "example", False), ("csr-0006", "demonstration", False),
])  # fmt: skip
def test_r16_owner_hosted_status(context, record_id, status, allowed):
    _, findings = check_source(pointer(record_id), body(id=record_id, record_status=status), context)
    assert (not any(f.rule == "R16" for f in findings)) is allowed


def test_failing_validation(context):
    result = harvest_source(pointer(), ROOT, CONFIG, context, serve({REMOTE: body(summary="Too short")}))
    assert result.state == "failing" and result.text is None
    assert [f.path for f in result.findings if f.rule == "SCHEMA"] == ["summary"]


@pytest.mark.parametrize(("response", "message"), [
    ("the address returned HTTP 404", "HTTP 404"),
    ("the address did not respond: timed out", "did not respond"),
    ("the file is larger than 262,144 bytes", "larger than"),
    ("redirected to an address that is not HTTPS: http://x", "not HTTPS"),
])  # fmt: skip
def test_r15_unavailable_sources(context, response, message):
    result = harvest_source(pointer(), ROOT, CONFIG, context, serve({REMOTE: response}))
    assert result.state == "unavailable"
    assert [f.rule for f in result.findings] == ["R15"] and message in result.findings[0].message


def test_yaml_and_encoding_problems_fail(context):
    assert harvest_source(pointer(), ROOT, CONFIG, context, serve({REMOTE: b"id: [unclosed\n"})).state == "failing"
    assert harvest_source(pointer(), ROOT, CONFIG, context, serve({REMOTE: b"\xff\xfe"})).state == "failing"


def test_sources_in_this_repository_are_read_from_the_working_tree(context):
    source = CONFIG.raw_prefix + "examples/hosted/csr-9006/solution.yml"
    result = harvest_source(pointer(source=source), ROOT, CONFIG, context, fetcher=None)
    assert result.state == "ok" and result.from_repository
    outside = get_source(CONFIG.raw_prefix + "../../etc/passwd", ROOT, CONFIG, None)
    assert outside.body is None


def test_without_the_network_other_sources_are_not_harvested(context):
    assert harvest_source(pointer(), ROOT, CONFIG, context, fetcher=None).state == "not-harvested"


def test_the_register_examples(context):
    """csr-9006 passes; csr-9007 fails on purpose; csr-0001 is this repository's solution.yml."""
    register = {p.stem: load_yaml_file(p) for p in (ROOT / "records").glob("csr-*.yaml")}
    states = {}
    for record_id in ("csr-0001", "csr-9006", "csr-9007"):
        record = Record(f"records/{record_id}.yaml", register[record_id], True, f"{record_id}.yaml")
        states[record_id] = harvest_source(record, ROOT, CONFIG, context, fetcher=None).state
    assert states == {"csr-0001": "ok", "csr-9006": "ok", "csr-9007": "failing"}


# The real fetch, against a fake opener


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def test_fetch_limits(monkeypatch):
    class Opener:
        def __init__(self, data):
            self.data = data

        def open(self, request, timeout):
            assert timeout == 10 and request.full_url == REMOTE
            return FakeResponse(self.data)

    monkeypatch.setattr(harvest.urllib.request, "build_opener", lambda *handlers: Opener(b"x" * 10))
    assert harvest.fetch(REMOTE, 10, 10) == b"x" * 10
    with pytest.raises(FetchError, match="larger than 9 bytes"):
        harvest.fetch(REMOTE, 9, 10)
    with pytest.raises(FetchError, match="not HTTPS"):
        harvest.fetch("http://owner.example.gov.uk/solution.yml", 10, 10)


def test_redirects_must_stay_on_https():
    handler = harvest._HttpsOnly()
    with pytest.raises(FetchError, match="not HTTPS"):
        handler.redirect_request(None, None, 302, "Found", {}, "http://elsewhere.example/solution.yml")
