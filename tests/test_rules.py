"""Each validation rule in appendix C, passing and failing."""

import pytest
from helpers import TODAY, as_record

from csr.findings import Severity
from csr.rules import walk
from csr.schema import SENTINEL
from csr.validate import check_record


def rules(data, context, label="records/test.yaml"):
    return [(f.rule, f.path) for f in check_record(as_record(data, label), context) if f.rule != "SCHEMA"]


def test_minimal_record_has_no_findings(minimal, context):
    assert check_record(as_record(minimal), context) == []


# R02: ID range matches provenance


@pytest.mark.parametrize(
    ("status", "record_id", "ok"),
    [
        ("example", "csr-9100", True),
        ("example", "csr-0100", False),
        ("owner-confirmed", "csr-0100", True),
        ("owner-confirmed", "csr-9100", False),
        ("demonstration", "csr-8999", True),
        ("demonstration", "csr-9000", False),
        ("owner-confirmed", "csr-0000", False),
        ("withdrawn", "csr-9100", True),
        ("withdrawn", "csr-0100", True),
    ],
)
def test_r02_id_range(minimal, context, status, record_id, ok):
    minimal.update(id=record_id, record_status=status)
    assert (("R02", "id") not in rules(minimal, context)) is ok


# R03 and R04: taxonomy terms


def test_r03_unknown_terms(minimal, context):
    minimal["owner"]["sector"] = "local-govt"
    minimal["service_areas"] = ["housing", "parks"]
    minimal["capabilities"] = ["teleportation"]
    minimal["intended_adopters"] = ["nhs-scotland", "health-boards"]
    assert sorted(rules(minimal, context)) == [
        ("R03", "capabilities[0]"),
        ("R03", "intended_adopters[1]"),
        ("R03", "owner.sector"),
        ("R03", "service_areas[1]"),
    ]


def test_r03_an_audience_is_not_an_owning_sector(minimal, context):
    minimal["intended_adopters"] = ["scottish-public-sector"]
    assert rules(minimal, context) == []
    minimal["owner"]["sector"] = "scottish-public-sector"
    assert rules(minimal, context) == [("R03", "owner.sector")]


def test_r03_terms_from_the_wrong_taxonomy(minimal, context):
    minimal["service_areas"] = ["payments"]
    assert rules(minimal, context) == [("R03", "service_areas[0]")]


def test_r04_deprecated_term(minimal, context):
    from dataclasses import replace

    taxonomies = dict(context.taxonomies)
    capabilities = taxonomies["capabilities"]
    terms = tuple(
        replace(t, status="deprecated", replaced_by="integration-and-apis") if t.id == "payments" else t
        for t in capabilities.terms
    )
    taxonomies["capabilities"] = replace(capabilities, terms=terms)
    minimal["capabilities"] = ["payments", "integration-and-apis"]
    findings = check_record(as_record(minimal), replace(context, taxonomies=taxonomies))
    assert [(f.rule, f.severity, f.path) for f in findings] == [("R04", Severity.WARNING, "capabilities[0]")]
    assert "integration-and-apis" in findings[0].fix


# R05: related assets exist


def test_r05_related_assets(minimal, context):
    minimal["related_assets"] = [{"id": "csr-0001", "relationship": "replaced-by"}, {"id": "csr-0404"}]
    assert rules(minimal, context) == [("R05", "related_assets[1].id")]


def test_r05_skipped_without_a_register(minimal, context):
    from dataclasses import replace

    minimal["related_assets"] = [{"id": "csr-0404"}]
    assert rules(minimal, replace(context, known_ids=None)) == []


# R06: last_confirmed is not in the future


@pytest.mark.parametrize(("date", "ok"), [(TODAY.isoformat(), True), ("2026-11-03", False), ("2025-01-01", True)])
def test_r06_confirmation_date(minimal, context, date, ok):
    minimal["confirmation"]["last_confirmed"] = date
    assert (rules(minimal, context) == []) is ok


# R07: personal-looking contact


@pytest.mark.parametrize(
    ("value", "personal"),
    [
        ("digital@example.gov.uk", False),
        ("digital.services@example.gov.uk", False),
        ("service_desk@example.gov.uk", False),
        ("jane.smith@example.gov.uk", True),
        ("jane_smith2@example.gov.uk", True),
        ("jsmith@example.gov.uk", False),
        ("solution-register@digitaloffice.scot", False),
        ("jane-smith@example.gov.uk", False),  # hyphens are taken as a role mailbox
    ],
)
def test_r07_personal_contact(minimal, context, value, personal):
    minimal["contact"]["value"] = value
    findings = check_record(as_record(minimal), context)
    assert ([(f.rule, f.severity) for f in findings] == [("R07", Severity.WARNING)]) is personal
    if not personal:
        assert findings == []


# R09: no TODO placeholders


def test_r09_todo(minimal, context):
    minimal["purpose"] = "TODO: describe what this solution does, the problem it solves and who it is for."
    minimal["owner"]["organisation"] = "TODO"
    assert sorted(rules(minimal, context)) == [("R09", "owner.organisation"), ("R09", "purpose")]


def test_r09_todo_in_pointer(context):
    pointer = {"id": "csr-0001", "source": "https://example.gov.uk/solution.yml", "expected_owner": "TODO"}
    assert rules(pointer, context) == [("R09", "expected_owner")]


def test_r09_allows_todo_inside_text(minimal, context):
    minimal["purpose"] = "Keeps a shared TODO list for service teams, so that work across councils is visible."
    assert rules(minimal, context) == []


# R10: sentinel only in demonstration records


def test_r10_sentinel_outside_demonstration(minimal, context):
    minimal["adoption_route"]["summary"] = SENTINEL
    assert ("R10", "adoption_route.summary") in rules(minimal, context)


def test_r10_sentinel_in_demonstration(minimal, context):
    minimal.update(
        id="csr-0100",
        name="Fixture Demonstration",
        record_status="demonstration",
        sources=[{"url": "https://example.gov.uk/", "title": "Home page", "accessed": "2026-10-01"}],
    )
    minimal["adoption_route"]["summary"] = SENTINEL
    assert check_record(as_record(minimal), context) == []


# R11: example names


def test_r11_example_name(minimal, context):
    minimal["name"] = "Minimal Component"
    findings = check_record(as_record(minimal), context)
    assert [(f.rule, f.path) for f in findings] == [("R11", "name")]
    assert findings[0].fix == 'Rename it "Example: Minimal Component".'


def test_r11_applies_only_to_examples(minimal, context):
    minimal.update(id="csr-0100", name="Minimal Component", record_status="owner-confirmed")
    assert rules(minimal, context) == []


# R12: public codebases link their publiccode.yml


def test_r12_publiccode_url(minimal, context):
    minimal["codebases"] = [
        {"repository_url": "https://github.com/example/a", "visibility": "public", "maintenance": "internal"},
        {
            "repository_url": "https://github.com/example/b",
            "visibility": "public",
            "maintenance": "internal",
            "publiccode_url": "https://github.com/example/b/raw/main/publiccode.yml",
        },
        {"visibility": "private", "maintenance": "contract"},
    ]
    findings = check_record(as_record(minimal), context)
    assert [(f.rule, f.severity, f.path) for f in findings] == [("R12", Severity.WARNING, "codebases[0]")]


# R18: HTTPS addresses


def test_r18_https(minimal, context):
    minimal["documentation_url"] = "http://docs.example.gov.uk/"
    minimal["open_data"] = [{"title": "Data", "url": "ftp://data.example.gov.uk/"}]
    minimal["codebases"] = [{"repository_url": "git@github.com:x/y", "visibility": "public", "maintenance": "none",
                             "publiccode_url": "https://github.com/x/y/raw/main/publiccode.yml"}]  # fmt: skip
    assert sorted(rules(minimal, context)) == [
        ("R18", "codebases[0].repository_url"),
        ("R18", "documentation_url"),
        ("R18", "open_data[0].url"),
    ]


def test_r18_accepts_https_and_demonstration_sentinel(minimal, context):
    minimal["documentation_url"] = "https://docs.example.gov.uk/"
    assert rules(minimal, context) == []
    minimal.update(id="csr-0100", name="Fixture", record_status="demonstration", service_url=SENTINEL,
                   sources=[{"url": "https://example.gov.uk/", "title": "Home", "accessed": "2026-10-01"}])  # fmt: skip
    assert rules(minimal, context) == []


# Robustness: rules cope with records that fail the schema


def test_rules_cope_with_wrong_types(context):
    data = {"id": 7, "owner": "Example Council", "service_areas": "housing", "codebases": {"a": 1},
            "related_assets": ["csr-0001"], "contact": ["x"], "confirmation": "yesterday"}  # fmt: skip
    findings = check_record(as_record(data), context)
    assert findings and all(f.rule == "SCHEMA" for f in findings)


def test_walk():
    assert list(walk({"a": [1, {"b": "x"}], "c": None})) == [("a[0]", 1), ("a[1].b", "x"), ("c", None)]
