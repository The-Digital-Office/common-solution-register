"""The taxonomies as SKOS concept schemes (api/v0/taxonomy/<name>.ttl, DP-58), parsed with rdflib."""

from __future__ import annotations

import json

import pytest
import rdflib
from helpers import TODAY
from rdflib.namespace import DCTERMS, OWL, RDF, SKOS

from csr.api import taxonomy_skos
from csr.build import build
from csr.config import load_config
from csr.schema import ROOT
from csr.taxonomy import Taxonomy, Term, load_all

BASE = "https://example.org/register/"


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    return build(ROOT, tmp_path_factory.mktemp("site"), base_url=BASE, today=TODAY)


def graph(text: str) -> rdflib.Graph:
    return rdflib.Graph().parse(data=text, format="turtle")


@pytest.mark.parametrize("name", ["sectors", "service-areas", "capabilities"])
def test_every_term_is_a_concept_at_its_term_page(site, name):
    taxonomy = load_all()[name]
    g = graph((site.out / f"api/v0/taxonomy/{name}.ttl").read_text(encoding="utf-8"))
    scheme = rdflib.URIRef(f"{BASE}browse/#h-{name}")
    assert (scheme, RDF.type, SKOS.ConceptScheme) in g
    assert str(g.value(scheme, OWL.versionInfo)) == taxonomy.version
    assert len(list(g.subjects(RDF.type, SKOS.Concept))) == len(taxonomy.terms)
    for term in taxonomy.terms:
        c = rdflib.URIRef(f"{BASE}{name}/{term.id}/")
        assert (site.out / f"{name}/{term.id}/index.html").exists()  # the concept's URI is a real page
        assert (c, SKOS.inScheme, scheme) in g
        assert str(g.value(c, SKOS.notation)) == term.id
        assert str(g.value(c, SKOS.prefLabel)) == term.label
        assert str(g.value(c, SKOS.definition)) == term.definition
        assert {str(a) for a in g.objects(c, SKOS.altLabel)} == set(term.synonyms)
    browse = (site.out / "browse/index.html").read_text(encoding="utf-8")
    assert f'id="h-{name}"' in browse  # the scheme's URI lands on its column


def test_an_audience_only_term_says_so():
    g = graph(taxonomy_skos(load_all()["sectors"], load_config()))
    note = g.value(rdflib.URIRef(load_config().base_url + "sectors/scottish-public-sector/"), SKOS.scopeNote)
    assert note and "never as the sector that owns it" in str(note)


def test_deprecated_terms_and_awkward_text():
    taxonomy = Taxonomy("capabilities", "9.9", (
        Term("new", 'The "new" term', "Has a \\ backslash\nand a line break.", ("one", "two")),
        Term("old", "Old term", "Retired.", status="deprecated", replaced_by="new"),
    ))  # fmt: skip
    config = load_config()
    g = graph(taxonomy_skos(taxonomy, config))
    new, old = (rdflib.URIRef(f"{config.base_url}capabilities/{i}/") for i in ("new", "old"))
    scheme = rdflib.URIRef(f"{config.base_url}browse/#h-capabilities")
    assert str(g.value(new, SKOS.prefLabel)) == 'The "new" term'
    assert str(g.value(new, SKOS.definition)) == "Has a \\ backslash\nand a line break."
    assert (old, OWL.deprecated, rdflib.Literal(True)) in g and (old, DCTERMS.isReplacedBy, new) in g
    assert list(g.objects(scheme, SKOS.hasTopConcept)) == [new]  # deprecated terms are not top concepts


def test_the_api_index_links_to_the_skos_files(site):
    index = json.loads((site.out / "api/v0/index.json").read_text(encoding="utf-8"))
    for name, path in index["links"]["taxonomy_skos"].items():
        assert path == f"taxonomy/{name}.ttl" and (site.out / "api/v0" / path).exists()


def test_service_areas_are_the_esd_functions():
    """DP-24: the service areas are the ESD Functions list's top level, matched and attributed."""
    taxonomy = load_all()["service-areas"]
    config = load_config()
    g = graph(taxonomy_skos(taxonomy, config))
    scheme = rdflib.URIRef(f"{config.base_url}browse/#h-service-areas")
    assert str(g.value(scheme, DCTERMS.source)) == taxonomy.source["url"]
    assert "LG Inform Plus" in str(g.value(scheme, DCTERMS.rights))  # the attribution the licence requires
    active = [t for t in taxonomy.terms if not t.deprecated]
    assert len(active) == 13
    for term in active:
        c = rdflib.URIRef(f"{config.base_url}service-areas/{term.id}/")
        assert str(g.value(c, SKOS.exactMatch)).startswith("http://id.esd.org.uk/function/")
    for term in taxonomy.terms:
        if term.deprecated:  # version 0.1's made-up terms, each replaced by an ESD function
            assert term.replaced_by and not taxonomy.get(term.replaced_by).deprecated, term.id
