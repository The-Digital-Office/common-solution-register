"""Workflows, issue forms and the pull request template (specification 6.6 and 6.10)."""

import datetime as dt
import re
import shutil

import pytest
import yaml

from csr.schema import ROOT, load_yaml_file
from csr.tools import dump, new_from_issue

FORMS = ROOT / ".github" / "ISSUE_TEMPLATE"
WORKFLOWS = ROOT / ".github" / "workflows"
REGISTER_FORMS = ["suggest-asset.yml", "suggest-correction.yml", "move-to-owner-hosting.yml", "feedback.yml"]
OGL = "By submitting, you agree your submission may be published under the Open Government Licence v3.0."


def form(name):
    return yaml.safe_load((FORMS / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", REGISTER_FORMS + ["bug_report.yml", "change_request.yml"])
def test_issue_forms_are_well_formed(name):
    data = form(name)
    assert data["name"] and data["description"] and data["body"]
    ids = [item["id"] for item in data["body"] if "id" in item]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("name", REGISTER_FORMS)
def test_register_forms_say_issues_are_public_and_carry_the_licence(name):
    text = " ".join(item["attributes"]["value"] for item in form(name)["body"] if item["type"] == "markdown")
    assert "GitHub issues are public." in text
    assert OGL in text


def test_suggest_asset_has_one_yaml_area_and_three_fields():
    fields = {item["id"]: item for item in form("suggest-asset.yml")["body"] if "id" in item}
    assert set(fields) == {"asset-name", "organisation", "contact", "solution-yml"}
    assert fields["solution-yml"]["type"] == "textarea" and fields["solution-yml"]["attributes"]["render"] == "yaml"
    assert [fields[f]["type"] for f in ("asset-name", "organisation", "contact")] == ["input"] * 3


def test_the_draft_form_prefills_the_suggest_asset_fields():
    script = (ROOT / "src/csr/static/js/draft.js").read_text(encoding="utf-8")
    prefilled = set(re.findall(r"params\.set\('([a-z-]+)'", script))
    assert prefilled == {"asset-name", "organisation", "contact", "solution-yml"}
    assert "template: 'suggest-asset.yml'" in script


def render(form_data, values):
    """An issue body as GitHub renders it from an issue form."""
    parts = []
    for item in form_data["body"]:
        if item["type"] == "markdown":
            continue
        value = values.get(item["id"], "_No response_")
        if item["attributes"].get("render"):
            value = f"```{item['attributes']['render']}\n{value}\n```"
        parts.append(f"### {item['attributes']['label']}\n\n{value}")
    return "\n\n".join(parts)


def test_an_issue_from_the_form_becomes_a_record(tmp_path):
    for name in ("records", "examples"):
        shutil.copytree(ROOT / name, tmp_path / name)
    record = load_yaml_file(ROOT / "tests/fixtures/schema/pass/minimal.yaml")
    record.update(id="csr-NNNN", record_status="owner-confirmed", name="Booking Component")
    body = render(form("suggest-asset.yml"), {"asset-name": "Booking Component", "organisation": "Example Council",
                                              "contact": "booking@example.gov.uk", "solution-yml": dump(record)})  # fmt: skip
    outcome = new_from_issue(tmp_path, body, issue_url="https://github.com/x/y/issues/7", today=dt.date(2026, 11, 3))
    assert outcome.ok and load_yaml_file(outcome.path)["id"] == "csr-0003"


def test_pull_request_template_keeps_the_organisation_template():
    text = (ROOT / ".github/pull_request_template.md").read_text(encoding="utf-8")
    for line in ("## What and why", "## How it was checked", "## Checklist", "Closes #",
                 "- [ ] `CHANGELOG.md` updated under **Unreleased** (if users would notice the change)",
                 "- [ ] Documentation updated (if behaviour or setup changed)",
                 "- [ ] No secrets, credentials or personal data added",
                 "- [ ] `publiccode.yml` still accurate (public software repositories only)"):  # fmt: skip
        assert line in text, line
    assert "Provenance" in text and "Sources" in text and "Open Government Licence v3.0" in text


@pytest.mark.parametrize("path", sorted(WORKFLOWS.glob("*.yml")), ids=lambda p: p.name)
def test_actions_are_pinned_by_sha_and_permissions_are_set(path):
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    assert "permissions" in data
    for uses in re.findall(r"^\s*(?:-\s*)?uses:\s*(\S+)", text, re.M):
        if uses.startswith("./"):
            continue  # this repository's own reusable workflow
        if uses.startswith("The-Digital-Office/.github/"):
            continue  # the organisation's shared standards workflow, called at its release tag (baseline)
        assert re.fullmatch(r"[\w.-]+/[\w.-]+(/[\w./-]+)?@[0-9a-f]{40}", uses), uses
    for checkout in re.findall(r"actions/checkout@[0-9a-f]{40}[^\n]*\n(?:\s+with:\n(?:\s{10,}.*\n)*)?", text):
        assert "persist-credentials: false" in checkout


def test_site_workflow_triggers_concurrency_and_deploy():
    data = yaml.safe_load((WORKFLOWS / "site.yml").read_text(encoding="utf-8"))
    triggers = data[True]  # YAML 1.1 reads the key "on" as true
    assert set(triggers) == {"pull_request", "push", "workflow_dispatch", "schedule"}
    assert data["concurrency"]["group"]
    deploy = data["jobs"]["deploy"]
    assert "vars.PAGES_ENABLED == 'true'" in deploy["if"] and deploy["needs"] == "validate"
    assert data["jobs"]["validate"]["name"] == "Validate"  # the required check's name
    assert data["jobs"]["reusable"]["uses"] == "./.github/workflows/validate-solution.yml"


def test_reusable_workflow():
    data = yaml.safe_load((WORKFLOWS / "validate-solution.yml").read_text(encoding="utf-8"))
    inputs = data[True]["workflow_call"]["inputs"]
    assert set(inputs) == {"path", "publiccode", "register-repository", "register-ref"}
    assert inputs["register-ref"]["default"] == "v0"
