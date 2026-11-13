"""api/v0/metadata.json against the UK Cross-Government Metadata Exchange Model (DP-57).

The model's own LinkML schema (a copy in tests/fixtures) supplies the required
properties, the allowed values and the patterns, so the test follows the model
rather than a list kept here.
"""

from __future__ import annotations

import json
import re

import pytest
import yaml
from helpers import TODAY

from csr.build import build
from csr.schema import ROOT

MODEL = yaml.safe_load((ROOT / "tests/fixtures/ukgov-metadata-exchange-model/"
                        "uk_cross_government_metadata_exchange_model.yaml").read_text(encoding="utf-8"))  # fmt: skip
#: The one departure DP-57 records: these take a GOV.UK organisation, and the host is not one.
ORGANISATION_SLOTS = {"publisher", "creator"}


def slots(cls: str) -> dict[str, dict]:
    """Every property of a class, with inherited properties and the class's own usage applied."""
    c = MODEL["classes"][cls]
    names = (list(slots(c["is_a"])) if c.get("is_a") else []) + c.get("slots", [])
    usage = {}
    for k in ([c["is_a"]] if c.get("is_a") else []) + [cls]:
        usage.update(MODEL["classes"][k].get("slot_usage") or {})
    return {n: {**MODEL["slots"][n], **(usage.get(n) or {})} for n in names}


def problems(cls: str, obj: dict) -> list[str]:
    found = []
    props = slots(cls)
    for name, slot in props.items():
        if slot.get("required") and name not in obj:
            found.append(f"{cls}: {name} is required")
    for name, value in obj.items():
        if name not in props:
            found.append(f"{cls}: {name} is not in the model")
            continue
        slot = props[name]
        values = value if isinstance(value, list) else [value]
        if isinstance(value, list) != bool(slot.get("multivalued")):
            found.append(f"{cls}: {name} should {'' if slot.get('multivalued') else 'not '}be a list")
        rng = slot.get("range", "string")
        for v in values:
            if rng in MODEL["classes"]:
                found += problems(rng, v)
            elif rng in MODEL["enums"] and name not in ORGANISATION_SLOTS:
                if v not in MODEL["enums"][rng]["permissible_values"]:
                    found.append(f"{cls}: {name} {v!r} is not one of {rng}")
            elif slot.get("pattern") and not re.match(slot["pattern"], str(v)):
                found.append(f"{cls}: {name} {v!r} does not match {slot['pattern']}")
            elif rng == "date" and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(v)):
                found.append(f"{cls}: {name} {v!r} is not a date")
            elif rng == "integer" and not isinstance(v, int):
                found.append(f"{cls}: {name} {v!r} is not an integer")
            elif rng in ("uri", "uriorcurie") and not re.match(r"^(https://|[a-z]+:)\S+$", str(v)):
                found.append(f"{cls}: {name} {v!r} is not a URI")
    return found


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    return build(ROOT, tmp_path_factory.mktemp("site"), base_url="https://example.org/register/", today=TODAY)


@pytest.fixture(scope="module")
def meta(site):
    return json.loads((site.out / "api/v0/metadata.json").read_text(encoding="utf-8"))


def test_the_metadata_follows_the_model(meta):
    assert problems("Dataset", meta["dataset"]) == []
    assert problems("DataService", meta["dataService"]) == []
    for d in meta["distributions"]:
        assert problems("Distribution", d) == []
    assert meta["model"]["url"] == "https://co-cddo.github.io/ukgov-metadata-exchange-model/"


def test_the_metadata_describes_what_is_published(site, meta):
    dataset, service, files = meta["dataset"], meta["dataService"], meta["distributions"]
    assert dataset["type"] == "dcat:Dataset" and service["type"] == "dcat:DataService"
    assert dataset["distribution"] == [d["identifier"] for d in files]
    for d in files:  # each file is there, at the size given
        path = d["downloadURL"].removeprefix("https://example.org/register/")
        assert (site.out / path).stat().st_size == d["byteSize"], path
    assert [d["mediaType"] for d in files] == ["application/json", "text/csv"]
    assert service["servesData"] == [dataset["identifier"]] and service["endpointURL"] == "https://example.org/register/api/v0/"
    assert (site.out / "api/v0/index.json").exists()
    assert dataset["licence"] == "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"
    assert dataset["accessRights"] == "OPEN" and dataset["securityClassification"] == "OFFICIAL"
    assert dataset["issued"] == "2026-11-09" and dataset["updateFrequency"] == "freq:daily"
    assert dataset["contactPoint"]["email"] == "solution-register@digitaloffice.scot"


def test_the_host_is_named_as_publisher_although_the_model_lists_only_govuk_organisations(meta):
    # The departure DP-57 records: the model's OrganisationValues are GOV.UK organisations.
    host = "The Digital Office for Scottish Local Government"
    for obj in (meta["dataset"], meta["dataService"]):
        assert obj["publisher"] == host and obj["creator"] == [host]
    assert "uk-gov-orgs" in MODEL["imports"]


def test_the_data_endpoints_link_to_the_metadata(site):
    index = json.loads((site.out / "api/v0/index.json").read_text(encoding="utf-8"))
    assert index["links"]["metadata"] == "metadata.json"
    register = json.loads((site.out / "data/register.json").read_text(encoding="utf-8"))
    assert register["metadata"] == "../api/v0/metadata.json"
    assert (site.out / "data" / register["metadata"]).resolve() == (site.out / "api/v0/metadata.json").resolve()
