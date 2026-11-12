"""The harvester (specification 6.11): R14 to R17, state, and the build."""

import datetime as dt
import io
import json
import re

import pytest
import yaml
from helpers import TODAY

from csr import harvest
from csr.config import load_config
from csr.build import build
from csr.harvest import (
    FetchError, SourceResult, check_source, content_hash, empty_state, get_source, harvest_source, read_state, run,
    update_entry,
)  # fmt: skip
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


# Checkpoint b: state


DAY1 = dt.datetime(2026, 11, 3, 6, 0, tzinfo=dt.UTC)
DAY2 = dt.datetime(2026, 11, 4, 6, 0, tzinfo=dt.UTC)
DAY3 = dt.datetime(2026, 11, 5, 6, 0, tzinfo=dt.UTC)


def result(state, text=None, findings=()):
    return SourceResult("csr-9006", REMOTE, "Example Council", state, list(findings), text,
                        content_hash(text.encode()) if text else None)  # fmt: skip


def test_ok_records_the_valid_copy_and_when_it_changed():
    first = update_entry(None, result("ok", "a: 1\n"), DAY1)
    assert first["state"] == "ok" and first["last_valid"] == "a: 1\n"
    assert first["harvested_at"] == "2026-11-03T06:00:00Z" and first["last_changed"] == "2026-11-03"
    same = update_entry(first, result("ok", "a: 1\n"), DAY2)
    assert same["harvested_at"] == "2026-11-04T06:00:00Z" and same["last_changed"] == "2026-11-03"
    changed = update_entry(same, result("ok", "a: 2\n"), DAY3)
    assert changed["last_changed"] == "2026-11-05" and changed["content_hash"] == content_hash(b"a: 2\n")


def test_failing_keeps_the_last_valid_copy_and_says_since_when():
    ok = update_entry(None, result("ok", "a: 1\n"), DAY1)
    failing = update_entry(ok, result("failing"), DAY2)
    assert failing["last_valid"] == "a: 1\n" and failing["harvested_at"] == "2026-11-03T06:00:00Z"
    assert failing["failing_since"] == "2026-11-04T06:00:00Z"
    still = update_entry(failing, result("failing"), DAY3)
    assert still["failing_since"] == "2026-11-04T06:00:00Z" and still["checked_at"] == "2026-11-05T06:00:00Z"
    unavailable = update_entry(still, result("unavailable"), DAY3)
    assert unavailable["unavailable_since"] == "2026-11-05T06:00:00Z" and unavailable["failing_since"] is None
    recovered = update_entry(unavailable, result("ok", "a: 1\n"), DAY3)
    assert recovered["unavailable_since"] is None and recovered["last_changed"] == "2026-11-03"


def test_a_source_that_never_passed_has_no_valid_copy():
    never = update_entry(None, result("failing"), DAY1)
    assert never["last_valid"] is None and never["harvested_at"] is None


def test_a_changed_registration_starts_afresh():
    ok = update_entry(None, result("ok", "a: 1\n"), DAY1)
    moved = SourceResult("csr-9006", "https://new.example.gov.uk/solution.yml", "Example Council", "failing")
    assert update_entry(ok, moved, DAY2)["last_valid"] is None


def test_not_harvested_keeps_what_was_known():
    ok = update_entry(None, result("ok", "a: 1\n"), DAY1)
    assert update_entry(ok, result("not-harvested"), DAY2) == ok
    assert update_entry(None, result("not-harvested"), DAY2)["state"] == "not-harvested"


def test_run_over_the_register_and_only():
    state, results = run(ROOT, CONFIG, empty_state(), now=DAY1)
    assert {r.id: r.state for r in results} == {"csr-0001": "ok", "csr-9006": "ok", "csr-9007": "failing"}
    assert state["generated"] == "2026-11-03T06:00:00Z"
    assert set(state["sources"]) == {"csr-0001", "csr-9006", "csr-9007"}
    again, results = run(ROOT, CONFIG, state, now=DAY2, only={"csr-9007"})
    assert [r.id for r in results] == ["csr-9007"]
    assert again["sources"]["csr-0001"] == state["sources"]["csr-0001"]
    assert again["sources"]["csr-9007"]["failing_since"] == "2026-11-03T06:00:00Z"


def test_read_state(tmp_path):
    path = tmp_path / "state.json"
    state, _ = run(ROOT, CONFIG, empty_state(), now=DAY1)
    path.write_text(json.dumps(state))
    assert read_state(str(path), None, CONFIG)[0] == state
    assert read_state(str(tmp_path / "missing.json"), None, CONFIG)[0] == empty_state()
    path.write_text('{"state_version": 99}')
    assert "unknown format" in read_state(str(path), None, CONFIG)[1]
    assert read_state("https://example.github.io/state.json", serve({}), CONFIG)[0] == empty_state()


def test_build_publishes_the_last_valid_copy_of_a_failing_source(tmp_path):
    state, _ = run(ROOT, CONFIG, empty_state(), now=DAY1)
    entry = state["sources"]["csr-9006"]
    valid = entry["last_valid"]
    failing = SourceResult("csr-9006", entry["source"], entry["expected_owner"], "failing")
    state["sources"]["csr-9006"] = update_entry(entry, failing, DAY2)
    site = build(ROOT, tmp_path / "site", today=TODAY, state=state)
    hosted = site.register.get("csr-9006")
    assert hosted is not None and hosted.text == valid and hosted.source_state == "failing"
    record = json.loads((tmp_path / "site/api/v0/assets/csr-9006.json").read_text())
    assert record["source_state"] == "failing" and record["harvested_at"] == "2026-11-03T06:00:00Z"
    published = json.loads((tmp_path / "site/api/v0/harvest-state.json").read_text())
    assert published == state
    assert [u.id for u in site.register.unpublished] == ["csr-9007"]


# Checkpoint c: the official parser (R17)

OWN_PUBLICCODE = CONFIG.raw_prefix + "publiccode.yml"


def parser_says(*findings):
    def runner(path):
        assert path.read_text()  # the parser is given the fetched file
        return list(findings)

    return runner


def test_publiccode_valid_invalid_and_warnings():
    from csr.harvest import check_publiccode

    valid = check_publiccode(OWN_PUBLICCODE, ROOT, CONFIG, None, parser_says(), DAY1)
    assert valid["state"] == "valid" and valid["messages"] == [] and valid["parser"] == "v5.4.3"
    warned = check_publiccode(OWN_PUBLICCODE, ROOT, CONFIG, None,
                              parser_says({"type": "warning", "key": "logo", "description": "missing", "line": 3}), DAY1)
    assert warned["state"] == "valid" and warned["messages"] == ["warning: logo: missing (line 3)"]
    invalid = check_publiccode(OWN_PUBLICCODE, ROOT, CONFIG, None,
                               parser_says({"type": "error", "key": "url", "description": "is required"}), DAY1)
    assert invalid["state"] == "invalid" and invalid["messages"] == ["error: url: is required"]


def test_publiccode_not_installed_unavailable_and_not_fetched():
    from csr.harvest import check_publiccode

    assert check_publiccode(OWN_PUBLICCODE, ROOT, CONFIG, None, lambda path: None, DAY1)["state"] == "not-checked"
    remote = "https://code.example.gov.uk/booking/raw/main/publiccode.yml"
    assert check_publiccode(remote, ROOT, CONFIG, serve({}), parser_says(), DAY1)["state"] == "unavailable"
    assert check_publiccode(remote, ROOT, CONFIG, None, parser_says(), DAY1)["state"] == "not-checked"


def test_run_checks_every_linked_publiccode_and_warns_r17_on_harvested_records():
    remote = "https://code.example.gov.uk/booking/raw/main/publiccode.yml"
    network = serve({remote: b"publiccodeYmlVersion: '0'\n"})

    def runner(path):
        return [] if "common-solution-register" in path.read_text() else [{"type": "error", "key": "name",
                                                                           "description": "is required"}]  # fmt: skip

    state, results = run(ROOT, CONFIG, empty_state(), now=DAY1, fetcher=network, parser=runner)
    assert state["publiccode"][OWN_PUBLICCODE]["state"] == "valid"
    assert state["publiccode"][remote]["state"] == "invalid"
    hosted = next(r for r in results if r.id == "csr-9006")
    assert hosted.state == "ok"  # R17 is a warning: the record is still published
    assert [(f.rule, f.path) for f in hosted.findings] == [("R17", "codebases[0].publiccode_url")]
    assert state["sources"]["csr-9006"]["findings"][0]["rule"] == "R17"
    # The fictional notifications component's publiccode.yml does not exist, so it is unavailable.
    assert state["publiccode"]["https://code.example.gov.uk/notifications/raw/main/publiccode.yml"]["state"] == "unavailable"


def test_a_verdict_is_kept_when_it_cannot_be_checked_again():
    state, _ = run(ROOT, CONFIG, empty_state(), now=DAY1, parser=parser_says())
    later, _ = run(ROOT, CONFIG, state, now=DAY2, parser=lambda path: None)
    assert later["publiccode"][OWN_PUBLICCODE] == state["publiccode"][OWN_PUBLICCODE]


@pytest.mark.skipif(harvest.find_parser() is None, reason="the official parser is not installed (tools/install-publiccode-parser.py)")
def test_the_official_parser_accepts_this_repository_and_rejects_a_broken_file(tmp_path):
    """Runs where the parser is installed, as in CI."""
    from csr.harvest import check_publiccode, run_parser

    assert check_publiccode(OWN_PUBLICCODE, ROOT, CONFIG, None, run_parser, DAY1)["state"] == "valid"
    broken = tmp_path / "publiccode.yml"
    broken.write_text("publiccodeYmlVersion: '0'\nname: broken\n")
    assert any(f.get("type") == "error" for f in run_parser(broken))


# Checkpoint d: the harvest report and the record page


def built(tmp_path, state):
    return build(ROOT, tmp_path / "site", today=dt.date(2026, 11, 20), state=state)


def page(site, path):
    return (site.out / path).read_text(encoding="utf-8")


def test_harvest_report(tmp_path):
    state, _ = run(ROOT, CONFIG, empty_state(), now=DAY1, parser=parser_says())
    site = built(tmp_path, state)
    html = page(site, "harvest/index.html")
    assert "3 November 2026 at 06:00 UTC (daily)" in html
    assert re.search(r'Registered sources</dt><dd class="ds_metadata__value">3<', html)
    for record_id, tag in (("csr-0001", "OK"), ("csr-9006", "OK"), ("csr-9007", "Failing validation")):
        assert re.search(rf'<tr id="{record_id}">.*?{tag}</strong>', html, re.S), record_id
    assert '<tr id="csr-9007"><td>csr-9007 Example: Failing Hosted Source</td>' in html  # named, not linked
    assert "csr-9007: failing validation since 3 November 2026 at 06:00 UTC (never published)" in html
    assert "<strong>R03:</strong> <code>service_areas[0]</code>" in html
    assert "api/v0/harvest-state.json" in html


def test_report_and_record_page_for_a_failing_and_an_unavailable_source(tmp_path):
    state, _ = run(ROOT, CONFIG, empty_state(), now=DAY1, parser=parser_says())
    entry9006 = state["sources"]["csr-9006"]
    gone = SourceResult("csr-9006", entry9006["source"], entry9006["expected_owner"], "unavailable",
                        [harvest.error(entry9006["source"], "R15", "", "the address returned HTTP 404")])  # fmt: skip
    state["sources"]["csr-9006"] = update_entry(entry9006, gone, DAY2)
    site = built(tmp_path, state)  # 16 days after it became unavailable
    report = page(site, "harvest/index.html")
    assert "csr-9006: unavailable since 4 November 2026 at 06:00 UTC (last valid version from 3 November 2026" in report
    assert "Unavailable for 16 days. A maintainer decides whether to withdraw the record" in report
    record = page(site, "assets/csr-9006/index.html")
    assert "Source unavailable since 4 November 2026 at 06:00 UTC" in record
    assert "harvested on 3 November 2026 at 06:00 UTC" in record
    assert "Last harvested</dt><dd class=\"ds_summary-list__value\">4 November 2026 at 06:00 UTC: source unavailable" in record


def test_record_page_shows_the_parser_verdict(tmp_path):
    state, _ = run(ROOT, CONFIG, empty_state(), now=DAY1,
                   parser=parser_says({"type": "error", "key": "url", "description": "is required"}))  # fmt: skip
    site = built(tmp_path, state)
    record = page(site, "assets/csr-0001/index.html")
    assert "Fails the official parser</strong><br><span class=\"ds_hint-text\">error: url: is required</span>" in record
    assert "Harvested 3 November 2026 at 06:00 UTC: passed validation" in record  # the Hosting fact
    valid, _ = run(ROOT, CONFIG, empty_state(), now=DAY1, parser=parser_says())
    other = build(ROOT, tmp_path / "valid", today=dt.date(2026, 11, 20), state=valid)
    assert "Valid (official parser)" in page(other, "assets/csr-0001/index.html")
    assert "Valid (official parser)</strong> (publiccode-parser-go v5.4.3" in page(other, "reference/publiccode/index.html")



# For the workflows (S13)


def test_markdown_report():
    from csr.harvest import markdown_report

    state, results = run(ROOT, CONFIG, empty_state(), now=DAY1, parser=parser_says())
    report = markdown_report(state, results)
    assert report.startswith("## Harvest report")
    assert "| csr-9007 |" in report and "Failing validation" in report
    assert "**csr-9007** (Failing validation):" in report
    assert "### publiccode.yml (official parser)" in report


def test_cli_fail_on_problems_and_summary(tmp_path, monkeypatch, capsys):
    from csr.cli import main

    monkeypatch.setattr("csr.cli.harvest.run_parser", lambda path: [])
    summary = tmp_path / "summary.md"
    args = ["harvest", "--no-network", "--state", str(tmp_path / "none.json"), "--out", str(tmp_path / "state.json")]
    assert main(args + ["--only", "csr-9006", "--fail-on-problems", "--summary", str(summary)]) == 0
    assert "## Harvest report" in summary.read_text()
    # csr-9007 fails on purpose, but it is in this repository: --fail-on-problems is for owners' sources.
    assert main(args + ["--only", "csr-9007", "--fail-on-problems"]) == 0


def test_cli_fail_on_problems_for_an_owner_source(tmp_path, monkeypatch, capsys):
    import shutil

    from csr.cli import main

    for name in ("records", "examples"):
        shutil.copytree(ROOT / name, tmp_path / name)
    (tmp_path / "records" / "csr-0010.yaml").write_text(
        "id: csr-0010\nsource: https://owner.example.gov.uk/solution.yml\nexpected_owner: Example Council\n")
    monkeypatch.setattr("csr.cli.ROOT", tmp_path)
    monkeypatch.setattr("csr.cli.harvest.fetch", serve({}))  # the owner's address returns 404
    args = ["harvest", "--state", str(tmp_path / "none.json"), "--out", str(tmp_path / "state.json")]
    assert main(args + ["--only", "csr-0010", "--fail-on-problems"]) == 1
    assert "csr-0010 (unavailable)" in capsys.readouterr().err
    assert main(args + ["--only", "csr-0010"]) == 0  # a scheduled harvest carries on


def test_cli_check_publiccode(tmp_path, monkeypatch, capsys):
    from csr.cli import main

    monkeypatch.setattr("csr.cli.harvest.run_parser",
                        lambda path: [{"type": "error", "key": "url", "description": "is required", "line": 2}])  # fmt: skip
    assert main(["check-publiccode", str(ROOT / "publiccode.yml")]) == 1
    assert "::error file=" in capsys.readouterr().out
    monkeypatch.setattr("csr.cli.harvest.run_parser", lambda path: None)
    assert main(["check-publiccode", str(ROOT / "publiccode.yml")]) == 2
    assert main(["check-publiccode", str(tmp_path / "missing.yml")]) == 2
