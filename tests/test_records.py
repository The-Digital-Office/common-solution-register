"""The register's own records (specification 5.1 and 5.2)."""

import datetime as dt

import pytest
from helpers import TODAY

from csr.records import read_register
from csr.schema import ROOT, load_yaml_file
from csr.validate import validate

RECORDS = {r.id: r.data for r in read_register(ROOT / "records")[0]}
HOSTED = ROOT / "examples" / "hosted"
RAW = "https://github.com/The-Digital-Office/common-solution-register/raw/main/"


def full(record_id):
    """The full descriptor for a record: the local record, or the file its pointer names."""
    data = RECORDS[record_id]
    if "source" in data:
        return load_yaml_file(ROOT / data["source"].removeprefix(RAW))
    return data


def months_before(date: str) -> int:
    then, now = dt.date.fromisoformat(date), TODAY
    return (now.year - then.year) * 12 + now.month - then.month - (now.day < then.day)


def test_record_set():
    assert sorted(RECORDS) == ["csr-0001", "csr-0002", "csr-0003", *(f"csr-900{n}" for n in range(1, 8))]


def test_register_has_no_errors():
    result = validate(root=ROOT, today=TODAY)
    assert result.ok, [str(f) for f in result.findings]
    assert [(f.file, f.rule) for f in result.findings] == [("records/csr-0002.yaml", "R12")] * 2


@pytest.mark.parametrize("record_id", ["csr-0001", "csr-9006", "csr-9007"])
def test_pointers_name_files_in_this_repository_with_matching_id_and_owner(record_id):
    pointer = RECORDS[record_id]
    assert pointer["source"].startswith(RAW)
    hosted = full(record_id)
    assert hosted["id"] == record_id
    assert hosted["owner"]["organisation"] == pointer["expected_owner"]


def test_hosted_example_passes():
    assert validate([str(HOSTED / "csr-9006" / "solution.yml")], root=ROOT, today=TODAY).findings == []


def test_failing_hosted_source_fails_as_intended():
    result = validate([str(HOSTED / "csr-9007" / "solution.yml")], root=ROOT, today=TODAY)
    assert not result.ok
    assert {f.rule for f in result.findings} == {"SCHEMA", "R03", "R09", "R10", "R18"}


def test_csr_0001_is_a_service_whose_codebase_is_this_repository():
    record = full("csr-0001")
    publiccode = load_yaml_file(ROOT / "publiccode.yml")
    assert record["asset_type"] == "service" and record["record_status"] == "owner-confirmed"
    assert record["terms_of_use"]["licence"] == "MIT AND OGL-UK-3.0"
    [codebase] = record["codebases"]
    assert codebase["repository_url"] == publiccode["url"]  # R19, checked locally
    assert codebase["maintenance"] == publiccode["maintenance"]["type"]
    assert codebase["publiccode_url"] == RAW + "publiccode.yml"
    assert months_before(record["confirmation"]["last_confirmed"]) < 11  # current


def test_csr_0002_has_two_codebases():
    assert len(RECORDS["csr-0002"]["codebases"]) == 2


@pytest.mark.parametrize("record_id", [f"csr-900{n}" for n in range(1, 8)])
def test_examples_are_clearly_fictional(record_id):
    record = full(record_id)
    assert record["name"].startswith("Example:")
    assert "Example" in record["owner"]["organisation"]


def test_examples_exercise_what_5_2_says():
    assert full("csr-9001")["charging"]["applies"] is True and "support" in full("csr-9001")
    assert full("csr-9002")["asset_type"] == "api" and full("csr-9002")["interfaces"]
    assert full("csr-9002")["related_assets"]
    assert full("csr-9003")["status"] == "deprecated" and full("csr-9003")["deprecation"]["migration_guidance"]
    assert full("csr-9004")["status"] == "beta"
    assert full("csr-9005")["record_status"] == "withdrawn" and full("csr-9005")["withdrawal"]
    assert full("csr-9006")["record_status"] == "example"


def test_example_currency_states():
    """At the build date the examples show stale (csr-9003), due (csr-9004) and current
    records. The fictional dates must be moved forward as time passes (see the plan)."""
    assert months_before(full("csr-9003")["confirmation"]["last_confirmed"]) >= 12
    assert 11 <= months_before(full("csr-9004")["confirmation"]["last_confirmed"]) < 12
    for record_id in ("csr-9001", "csr-9002", "csr-9006"):
        assert months_before(full(record_id)["confirmation"]["last_confirmed"]) < 11


def test_example_ids_link_up():
    assert {"id": "csr-9006", "relationship": "replaced-by"} in full("csr-9003")["related_assets"]
    assert {"id": "csr-9003", "relationship": "replaces"} in full("csr-9006")["related_assets"]


def test_no_hosted_file_without_a_pointer():
    assert {p.parent.name for p in HOSTED.glob("*/solution.yml")} == {"csr-9006", "csr-9007"}
