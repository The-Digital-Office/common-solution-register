"""Tests for the taxonomy files (specification 6.5)."""

import pytest
import yaml

from csr.schema import load_yaml_file
from csr.taxonomy import TAXONOMIES, TAXONOMY_DIR, load_all, load_taxonomy

EXPECTED = {
    "sectors": [
        "scottish-public-sector",  # an audience only (added at the author's request, 9 November 2026)
        "scottish-government", "executive-agencies", "local-government", "nhs-scotland",
        "police-and-fire", "non-departmental-public-bodies", "further-and-higher-education",
        "uk-public-sector",
    ],
    "service-areas": [
        "health-and-care", "social-care-and-social-work", "children-and-families",
        "education-and-skills", "housing", "social-security-and-benefits", "revenues-and-tax",
        "justice-and-community-safety", "environment-and-waste", "planning-and-building-standards",
        "transport-and-roads", "economy-and-business", "culture-and-communities",
        "corporate-and-cross-cutting",
    ],
    "capabilities": [
        "identity-and-access", "payments", "booking-and-scheduling", "case-management",
        "forms-and-transactions", "notifications", "document-and-records-management",
        "integration-and-apis", "data-and-analytics", "mapping-and-location",
        "content-and-publishing", "cyber-security", "information-governance",
        "collaboration-and-productivity",
    ],
}  # fmt: skip


@pytest.mark.parametrize("name", TAXONOMIES)
def test_terms_match_specification(name):
    assert load_taxonomy(name).ids == EXPECTED[name]


@pytest.mark.parametrize("name", TAXONOMIES)
def test_file_names_its_taxonomy(name):
    assert load_taxonomy(name).name == name


@pytest.mark.parametrize("name", TAXONOMIES)
def test_labels_are_unique(name):
    labels = [term.label.casefold() for term in load_taxonomy(name).terms]
    assert len(labels) == len(set(labels))


@pytest.mark.parametrize("name", TAXONOMIES)
def test_replacements_exist_and_are_active(name):
    taxonomy = load_taxonomy(name)
    for term in taxonomy.terms:
        if term.replaced_by:
            assert term.deprecated
            replacement = taxonomy.get(term.replaced_by)
            assert replacement is not None and not replacement.deprecated


def test_invalid_file_is_rejected(tmp_path):
    data = load_yaml_file(TAXONOMY_DIR / "sectors.yaml")
    del data["terms"][0]["definition"]
    (tmp_path / "sectors.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ValueError, match="definition"):
        load_taxonomy("sectors", tmp_path)


def test_load_all():
    taxonomies = load_all()
    assert set(taxonomies) == set(TAXONOMIES)
    assert "payments" in taxonomies["capabilities"]
    assert "payments" not in taxonomies["sectors"]
