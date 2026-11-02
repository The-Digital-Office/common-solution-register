"""The draft form page is generated from the schema and taxonomy (specification 6.2 and 6.13)."""

import json
import re

import pytest
from helpers import TODAY

from csr.build import build
from csr.form import LABELS, enum
from csr.schema import ROOT, load_schema
from csr.taxonomy import load_all

SELECTS = {"type": "asset_type", "status": "status", "terms": "terms_of_use.type", "chmodel": "charging.model",
           "itype-__N__": "interfaces.type", "maint-__N__": "codebases.maintenance"}  # fmt: skip


@pytest.fixture(scope="module")
def html(tmp_path_factory):
    out = tmp_path_factory.mktemp("site")
    build(ROOT, out, today=TODAY)
    return (out / "draft/index.html").read_text(encoding="utf-8")


def options_of(html, select_id):
    block = re.search(rf'<select class="ds_select" id="{re.escape(select_id)}"[^>]*>(.*?)</select>', html, re.S).group(1)
    return re.findall(r'<option value="([^"]*)"(?! data-show-when)', block)


@pytest.mark.parametrize(("select_id", "path"), SELECTS.items())
def test_select_options_come_from_the_schema(html, select_id, path):
    assert options_of(html, select_id) == enum(load_schema("asset"), path)


def test_every_schema_value_has_a_label():
    schema = load_schema("asset")
    for path, labels in LABELS.items():
        assert set(enum(schema, path)) == set(labels), path


def test_every_taxonomy_term_is_offered(html):
    taxonomies = load_all()
    for name, taxonomy in (("service_areas", "service-areas"), ("capabilities", "capabilities"),
                           ("intended_adopters", "sectors")):  # fmt: skip
        offered = re.findall(rf'name="{name}" type="checkbox" value="([^"]+)"', html)
        assert offered == taxonomies[taxonomy].ids
    assert options_of(html, "sector") == taxonomies["sectors"].ids


def test_conditional_sections_and_repeaters_are_present(html):
    for section in ("interfaces", "deprecation", "support", "sources", "withdrawal", "charging", "software"):
        assert f'data-section="{section}"' in html
    for group in ("interfaces", "sources", "codebases", "open_data"):
        assert f'data-repeater="{group}"' in html and f'id="tpl-{group}"' in html


def test_summary_limit_comes_from_the_schema(html):
    limit = load_schema("asset")["properties"]["summary"]["maxLength"]
    assert f'maxlength="{limit}"' in html and f"20 to {limit} characters" in html


def test_config_gives_the_schema_order(html):
    config = json.loads(re.search(r'id="csr-draft-config">(.*?)</script>', html, re.S).group(1))
    assert config["order"] == list(load_schema("asset")["properties"])


def test_without_javascript_the_form_is_hidden(html):
    assert '<div class="ds_layout__content csr-js-only">' in html
    assert "This page needs JavaScript." in html
