"""The maintainer tools: import-publiccode, move-to-source, move-to-local, new --from-issue."""

import datetime as dt
import shutil

import pytest
import yaml

from csr import harvest
from csr.config import load_config
from csr.harvest import FetchError
from csr.schema import ROOT, load_yaml, load_yaml_file
from csr.tools import (
    ToolError, dump, import_new, import_to, move_to_local, move_to_source, new_from_issue, next_free_id,
    yaml_from_issue,
)  # fmt: skip

TODAY = dt.date(2026, 11, 3)
CONFIG = load_config(ROOT)
OWNER_URL = "https://code.example.gov.uk/payments/raw/main/solution.yml"


@pytest.fixture
def root(tmp_path):
    """A copy of the register to change."""
    for name in ("records", "examples"):
        shutil.copytree(ROOT / name, tmp_path / name)
    for name in ("solution.yml", "publiccode.yml", "site.toml"):
        shutil.copy(ROOT / name, tmp_path / name)
    return tmp_path


def serve(responses):
    def fetcher(url, max_bytes, timeout):
        if url not in responses:
            raise FetchError("the address returned HTTP 404")
        return responses[url]

    return fetcher


PUBLICCODE = {
    "publiccodeYmlVersion": "0",
    "name": "Booking engine",
    "url": "https://code.example.gov.uk/booking-engine",
    "landingURL": "https://example.gov.uk/booking",
    "softwareVersion": "3.2.1",
    "developmentStatus": "stable",
    "categories": ["booking", "appointment-scheduling"],
    "roadmap": "https://code.example.gov.uk/booking-engine/roadmap",
    "usedBy": ["Example Council", "Second Example Council"],
    "dependsOn": {"open": [{"name": "PostgreSQL"}, {"name": "Redis"}]},
    "organisation": {"name": "Example Council"},
    "intendedAudience": {"scope": ["local-authorities"]},
    "description": {"en": {
        "shortDescription": "A booking engine for council services.",
        "longDescription": "Lets services offer online booking for collections, appointments and rooms. " * 3,
        "documentation": "https://docs.example.gov.uk/booking-engine/",
        "apiDocumentation": "https://docs.example.gov.uk/booking-engine/api/",
    }},
    "legal": {"license": "EUPL-1.2", "mainCopyrightOwner": "Example Council"},
    "maintenance": {"type": "community", "contacts": [
        {"name": "Alex Example", "email": "alex@example.gov.uk", "phone": "0300 000 0000", "affiliation": "Example Council"},
    ]},
}  # fmt: skip


def write_publiccode(tmp_path, **changes):
    path = tmp_path / "publiccode-in.yml"
    path.write_text(yaml.safe_dump({**PUBLICCODE, **changes}, sort_keys=False))
    return str(path)


# import-publiccode --to


def test_import_adds_a_codebase(root, tmp_path):
    outcome = import_to(root, CONFIG, write_publiccode(tmp_path), "csr-9001", today=TODAY)
    record = load_yaml_file(root / "records/csr-9001.yaml")
    assert record["codebases"] == [{
        "repository_url": "https://code.example.gov.uk/booking-engine", "visibility": "public",
        "maintenance": "community", "version": "3.2.1", "kind": "implementation",
        "maintainers": [{"name": "Alex Example", "affiliation": "Example Council", "email": "alex@example.gov.uk"}],
    }]  # fmt: skip
    assert "phone" not in str(record)  # phone numbers are never imported
    assert outcome.ok
    assert any("categories" in m for m in outcome.messages)
    assert (root / "records/csr-9001.yaml").read_text().startswith("# Fictional example")  # comments kept


def test_import_updates_the_codebase_already_listed(root):
    url = CONFIG.raw_prefix + "publiccode.yml"
    import_to(root, CONFIG, url, "csr-0002", today=TODAY)
    data = load_yaml_file(root / "records/csr-0002.yaml")
    assert len(data["codebases"]) == 3  # a new repository is added...
    shutil.copy(ROOT / "records/csr-0002.yaml", root / "records/csr-0002.yaml")
    pc = load_yaml_file(ROOT / "publiccode.yml")
    pc["url"] = "https://github.com/The-Digital-Office/repository-template.git"
    (root / "pc.yml").write_text(yaml.safe_dump(pc))
    import_to(root, CONFIG, str(root / "pc.yml"), "csr-0002", today=TODAY)
    data = load_yaml_file(root / "records/csr-0002.yaml")
    assert len(data["codebases"]) == 2  # ...an existing one is updated in place
    assert data["codebases"][1]["role"] == "Repository template and setup workflow"  # fields kept
    assert data["codebases"][1]["maintainers"][0]["name"] == "Robbie Harris"


def test_import_from_a_url_records_the_publiccode_url(root):
    url = "https://code.example.gov.uk/booking-engine/raw/main/publiccode.yml"
    import_to(root, CONFIG, url, "csr-9001", fetcher=serve({url: yaml.safe_dump(PUBLICCODE).encode()}), today=TODAY)
    assert load_yaml_file(root / "records/csr-9001.yaml")["codebases"][0]["publiccode_url"] == url


def test_import_refuses_pointers_missing_records_and_other_files(root, tmp_path):
    with pytest.raises(ToolError, match="owner-hosted"):
        import_to(root, CONFIG, write_publiccode(tmp_path), "csr-0001", today=TODAY)
    with pytest.raises(ToolError, match="not in records"):
        import_to(root, CONFIG, write_publiccode(tmp_path), "csr-0404", today=TODAY)
    (tmp_path / "not.yml").write_text("name: x\n")
    with pytest.raises(ToolError, match="not a publiccode.yml"):
        import_to(root, CONFIG, str(tmp_path / "not.yml"), "csr-9001", today=TODAY)


def test_import_warns_when_the_owner_differs(root, tmp_path):
    outcome = import_to(root, CONFIG, write_publiccode(tmp_path, organisation={"name": "Another Council"}),
                        "csr-9001", today=TODAY)  # fmt: skip
    assert any("Another Council" in m for m in outcome.messages)


# import-publiccode --new (appendix A)


def test_import_new_drafts_a_record_with_suggestions_and_todos(root, tmp_path):
    outcome = import_new(root, CONFIG, write_publiccode(tmp_path), today=TODAY)
    assert outcome.path.name == "csr-0003.yaml"  # the next free id
    record = load_yaml_file(outcome.path)
    assert record["name"] == "Booking engine"
    assert record["summary"] == "A booking engine for council services."
    assert record["purpose"].startswith("Lets services offer online booking")
    assert record["status"] == "live"  # stable
    assert record["owner"]["organisation"] == "Example Council"
    assert record["terms_of_use"] == {"type": "open-licence", "licence": "EUPL-1.2"}
    assert record["service_page_url"] == "https://example.gov.uk/booking"
    assert record["documentation_url"] == "https://docs.example.gov.uk/booking-engine/"
    assert record["interfaces"] == [{"type": "TODO", "documentation_url": "https://docs.example.gov.uk/booking-engine/api/"}]
    assert record["roadmap_url"] == "https://code.example.gov.uk/booking-engine/roadmap"
    assert record["dependencies"] == ["PostgreSQL", "Redis"]
    assert record["adopters"] == [{"organisation": "Example Council", "evidence": "self-reported"},
                                  {"organisation": "Second Example Council", "evidence": "self-reported"}]  # fmt: skip
    assert record["contact"]["value"] == "TODO"  # never derived from maintainers
    assert not outcome.ok and {f.rule for f in outcome.findings} >= {"R09"}
    assert outcome.path.read_text().startswith("# Drafted with csr import-publiccode")


def test_import_new_falls_back_to_the_copyright_owner(root, tmp_path):
    outcome = import_new(root, CONFIG, write_publiccode(tmp_path, organisation=None), today=TODAY, record_id="csr-0050")
    assert load_yaml_file(outcome.path)["owner"]["organisation"] == "Example Council"
    with pytest.raises(ToolError, match="already exists"):
        import_new(root, CONFIG, write_publiccode(tmp_path), today=TODAY, record_id="csr-0050")


# move-to-source


def test_move_to_source_checks_the_owner_file_then_writes_a_pointer(root):
    hosted = (root / "records/csr-9001.yaml").read_bytes()
    outcome = move_to_source(root, CONFIG, "csr-9001", OWNER_URL, fetcher=serve({OWNER_URL: hosted}), today=TODAY)
    pointer = load_yaml_file(root / "records/csr-9001.yaml")
    assert pointer == {"id": "csr-9001", "source": OWNER_URL, "expected_owner": "Example Council"}
    assert outcome.ok


@pytest.mark.parametrize(("serving", "match"), [
    ({}, "unavailable"),
    ({OWNER_URL: b"id: csr-9001\nname: 'Example: Wrong'\n"}, "failing"),
])  # fmt: skip
def test_move_to_source_refuses_a_file_that_would_not_be_published(root, serving, match):
    before = (root / "records/csr-9001.yaml").read_text()
    with pytest.raises(ToolError, match=match):
        move_to_source(root, CONFIG, "csr-9001", OWNER_URL, fetcher=serve(serving), today=TODAY)
    assert (root / "records/csr-9001.yaml").read_text() == before  # unchanged


def test_move_to_source_refuses_another_owner_and_http(root):
    other = yaml.safe_dump({**load_yaml_file(root / "records/csr-9001.yaml"),
                            "owner": {"organisation": "Another Council", "sector": "local-government"}}).encode()  # fmt: skip
    with pytest.raises(ToolError, match="R14"):
        move_to_source(root, CONFIG, "csr-9001", OWNER_URL, fetcher=serve({OWNER_URL: other}), today=TODAY)
    with pytest.raises(ToolError, match="HTTPS"):
        move_to_source(root, CONFIG, "csr-9001", "http://example.gov.uk/solution.yml", today=TODAY)
    with pytest.raises(ToolError, match="already owner-hosted"):
        move_to_source(root, CONFIG, "csr-9006", OWNER_URL, today=TODAY)


# move-to-local


def test_move_to_local_writes_the_last_valid_version(root):
    state, _ = harvest.run(root, CONFIG, harvest.empty_state(), now=dt.datetime(2026, 11, 3, tzinfo=dt.UTC))
    outcome = move_to_local(root, CONFIG, "csr-9006", state, today=TODAY)
    text = (root / "records/csr-9006.yaml").read_text()
    assert text.startswith("# Moved from owner hosting with csr move-to-local")
    assert load_yaml(text) == load_yaml_file(root / "examples/hosted/csr-9006/solution.yml")
    assert outcome.ok


def test_move_to_local_refuses_without_a_valid_version(root):
    state, _ = harvest.run(root, CONFIG, harvest.empty_state(), now=dt.datetime(2026, 11, 3, tzinfo=dt.UTC))
    with pytest.raises(ToolError, match="no valid version"):
        move_to_local(root, CONFIG, "csr-9007", state, today=TODAY)
    with pytest.raises(ToolError, match="already a local record"):
        move_to_local(root, CONFIG, "csr-9001", state, today=TODAY)
    moved = {**state, "sources": {**state["sources"], "csr-9006": {**state["sources"]["csr-9006"], "source": OWNER_URL}}}
    with pytest.raises(ToolError, match="not the registered"):
        move_to_local(root, CONFIG, "csr-9006", moved, today=TODAY)


# new --from-issue


def issue(record, extra=""):
    return ("### Solution name\n\nBooking component\n\n### solution.yml\n\n```yaml\n"
            + dump(record) + "```\n\n### Organisation\n\nExample Council\n" + extra)  # fmt: skip


def draft(**changes):
    record = load_yaml_file(ROOT / "tests/fixtures/schema/pass/minimal.yaml")
    record.update(id="csr-NNNN", record_status="owner-confirmed", name="Booking Component",
                  confirmation={"last_confirmed": "2026-11-02", "method": "draft form",
                                "reference": "Submitted with the draft form"})  # fmt: skip
    record.update(changes)
    return record


def test_new_from_issue_allocates_the_next_id(root):
    url = "https://github.com/The-Digital-Office/common-solution-register/issues/42"
    outcome = new_from_issue(root, issue(draft()), issue_url=url, today=TODAY)
    assert outcome.path.name == "csr-0003.yaml"
    record = load_yaml_file(outcome.path)
    assert record["id"] == "csr-0003" and record["confirmation"]["reference"] == url
    assert outcome.ok, [str(f) for f in outcome.findings]
    assert any("owning organisation" in m for m in outcome.messages)


def test_new_from_issue_examples_and_existing_ids(root):
    example = draft(record_status="example", name="Example: Booking Component")
    assert new_from_issue(root, issue(example), today=TODAY).path.name == "csr-9008.yaml"
    with pytest.raises(ToolError, match="already in the register"):
        new_from_issue(root, issue(draft(id="csr-9001")), today=TODAY)
    with pytest.raises(ToolError, match="no solution.yml"):
        new_from_issue(root, "### solution.yml\n\nI forgot to paste it.\n", today=TODAY)


def test_yaml_from_issue_skips_other_blocks():
    body = "```yaml\nnot: a record\n```\n\n```\n" + dump(draft()) + "```\n"
    assert load_yaml(yaml_from_issue(body))["name"] == "Booking Component"


def test_next_free_id():
    assert next_free_id({"csr-0001", "csr-0002", "csr-9001"}) == "csr-0003"
    assert next_free_id({"csr-0001", "csr-9001", "csr-9007"}, example=True) == "csr-9008"
    assert next_free_id(set()) == "csr-0001" and next_free_id(set(), example=True) == "csr-9000"


# The command line


def test_cli_new_from_issue_on_standard_input(root, monkeypatch, capsys):
    import io

    from csr.cli import main

    monkeypatch.setattr("csr.cli.ROOT", root)
    monkeypatch.setattr("sys.stdin", io.StringIO(issue(draft())))
    assert main(["new", "--from-issue", "-", "--issue-url", "https://example.gov.uk/issues/1"]) == 0
    out = capsys.readouterr().out
    assert "Wrote records/csr-0003.yaml." in out and "records/csr-0003.yaml is valid." in out


def test_cli_refusals_and_records_with_problems(root, monkeypatch, capsys, tmp_path):
    from csr.cli import main

    monkeypatch.setattr("csr.cli.ROOT", root)
    assert main(["move-to-local", "csr-9001", "--state", str(tmp_path / "none.json")]) == 2
    assert "already a local record" in capsys.readouterr().err
    assert main(["import-publiccode", write_publiccode(tmp_path), "--new"]) == 1  # drafted, with TODOs to fill in
    assert "errors to resolve before merging" in capsys.readouterr().out
