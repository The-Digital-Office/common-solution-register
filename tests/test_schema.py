"""Tests for the asset and pointer schemas (specification 6.4)."""

import copy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from csr.schema import SCHEMA_DIR, check, is_pointer, load_schema, load_yaml, load_yaml_file

FIXTURES = Path(__file__).parent / "fixtures" / "schema"
MANDATORY = load_schema("asset")["required"]
DERIVED = [
    "last_changed",
    "history_url",
    "merged_in",
    "currency",
    "hosting",
    "source",
    "harvested_at",
    "content_hash",
    "source_state",
]


@pytest.mark.parametrize("path", sorted(SCHEMA_DIR.glob("*.schema.json")), ids=lambda p: p.name)
def test_schemas_are_valid_draft_2020_12(path):
    Draft202012Validator.check_schema(load_schema(path.name.removesuffix(".schema.json")))


def test_minimal_record_is_valid(minimal):
    assert check(minimal) == []


def test_mandatory_fields_match_specification():
    assert set(MANDATORY) == {
        "schema_version", "id", "record_status", "name", "summary", "purpose", "asset_type",
        "owner", "contact", "service_areas", "capabilities", "status", "intended_adopters",
        "terms_of_use", "adoption_route", "charging",
    }  # fmt: skip


@pytest.mark.parametrize("field", MANDATORY)
def test_each_mandatory_field_is_required(minimal, field):
    record = copy.deepcopy(minimal)
    del record[field]
    assert any(f"'{field}' is a required property" in e.message for e in check(record))


@pytest.mark.parametrize("field", DERIVED)
def test_derived_fields_are_rejected(minimal, field):
    record = copy.deepcopy(minimal)
    record[field] = "2026-01-01"
    assert check(record)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("summary", "Too short"),
        ("summary", "x" * 201),
        ("name", "Ex"),
        ("purpose", "Too short to explain anything."),
        ("id", "csr-12"),
        ("schema_version", "0.2"),
        ("asset_type", "website"),
        ("status", "retired"),
        ("service_areas", []),
        ("documentation_url", "http://example.gov.uk/docs"),
    ],
)
def test_field_formats(minimal, field, value):
    record = copy.deepcopy(minimal)
    record[field] = value
    assert check(record)


def test_contact_type_sets_value_format(minimal):
    record = copy.deepcopy(minimal)
    record["contact"] = {"type": "web-form", "value": "digital@example.gov.uk"}
    assert check(record)
    record["contact"] = {"type": "web-form", "value": "https://example.gov.uk/contact"}
    assert check(record) == []


def test_terms_of_use_needs_licence_or_url(minimal):
    record = copy.deepcopy(minimal)
    record["terms_of_use"] = {"type": "service-terms"}
    assert check(record)
    record["terms_of_use"]["url"] = "https://example.gov.uk/terms"
    assert check(record) == []


def test_public_codebase_needs_repository_url(minimal):
    record = copy.deepcopy(minimal)
    record["codebases"] = [{"visibility": "public", "maintenance": "internal"}]
    assert check(record)
    record["codebases"] = [{"visibility": "private", "maintenance": "internal"}]
    assert check(record) == []


def test_dates_stay_strings():
    assert load_yaml("d: 2026-10-01") == {"d": "2026-10-01"}


def test_invalid_date_is_rejected(minimal):
    record = copy.deepcopy(minimal)
    record["confirmation"]["last_confirmed"] = "2026-13-45"
    assert check(record)


def test_pointer_schema():
    pointer = {
        "id": "csr-0001",
        "source": "https://github.com/The-Digital-Office/common-solution-register/raw/main/solution.yml",
        "expected_owner": "The Digital Office for Scottish Local Government",
    }
    assert is_pointer(pointer)
    assert check(pointer, "pointer") == []
    assert check({**pointer, "source": "http://example.gov.uk/solution.yml"}, "pointer")
    assert check({**pointer, "name": "Extra"}, "pointer")
    assert check({k: v for k, v in pointer.items() if k != "expected_owner"}, "pointer")
