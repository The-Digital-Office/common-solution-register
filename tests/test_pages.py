"""The remaining pages, the API and the extracts (specification 6.8 and 6.13)."""

import csv
import datetime as dt
import io
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import pytest
from helpers import TODAY

from csr.api import flatten, to_csv
from csr.build import build, reference_fields
from csr.rules import RULES
from csr.schema import ROOT, check, load_schema

#: Built paths from the page-to-template map in section 6.13: every page.
PAGE_MAP = [
    "index.html", "browse/index.html", "sectors/local-government/index.html",
    "service-areas/housing/index.html", "capabilities/payments/index.html", "assets/csr-0001/index.html",
    "assets/csr-9005/index.html", "contribute/index.html", "reference/index.html",
    "reference/publiccode/index.html", "data/index.html", "currency/index.html", "about/index.html",
    "accessibility/index.html", "privacy/index.html", "404.html", "draft/index.html", "validate/index.html",
    "harvest/index.html",
]  # fmt: skip
LATER = ()


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    return build(ROOT, tmp_path_factory.mktemp("site"), base_url="https://example.github.io/register/", today=TODAY)


def read(site, path):
    return (site.out / path).read_text(encoding="utf-8")


@pytest.mark.parametrize("path", PAGE_MAP)
def test_every_page_in_the_map_is_built(site, path):
    assert path in site.pages


def test_a_page_for_every_taxonomy_term(site):
    for folder, name in (("sectors", "sectors"), ("service-areas", "service-areas"), ("capabilities", "capabilities")):
        terms = json.loads(read(site, f"api/v0/taxonomy/{name}.json"))["terms"]
        assert all(f"{folder}/{t['id']}/index.html" in site.pages for t in terms)


def test_internal_links_resolve(site):
    broken = []
    for page in site.pages:
        if page == "404.html":
            continue
        for href in re.findall(r'href="([^"]+)"', read(site, page)):
            if href.startswith(("http", "mailto:")):
                continue
            parts = urlsplit(urljoin("http://x/" + page, href))
            path = parts.path.lstrip("/")
            if LATER and path.startswith(LATER):
                continue
            target = site.out / path
            if target.is_dir() or not path:
                target = target / "index.html"
            if not target.exists():
                broken.append((page, href))
            elif parts.fragment and target.suffix == ".html":
                if f'id="{parts.fragment}"' not in target.read_text(encoding="utf-8"):
                    broken.append((page, href))
    assert broken == []


def test_404_links_start_from_the_site_root(site):
    html = read(site, "404.html")
    assert 'href="/register/static/csr.css"' in html and 'href="/register/browse/"' in html


def test_browse_counts(site):
    html = read(site, "browse/index.html")
    assert "Local government</a></h3><p class=\"ds_category-item__summary csr-count\">8 solutions" in html
    assert "Police and fire" in html  # every sector is listed, even with no solutions
    assert "Health and care" not in html  # service areas and capabilities without solutions are not
    assert "All 14 service areas, with definitions" in html


def test_term_page(site):
    html = read(site, "capabilities/payments/index.html")
    assert "2 solutions provide this capability" in html
    assert "Also known as" in html and "<code>payments</code>" in html
    assert "Related terms" in html and "../../capabilities/booking-and-scheduling/" in html
    assert "1 solution provides this capability" in read(site, "capabilities/identity-and-access/index.html")


def test_pages_use_the_mailbox_and_mark_inputs_still_to_come(site):
    mailbox = "mailto:solution-register@digitaloffice.scot"
    accessibility = read(site, "accessibility/index.html")
    assert mailbox in accessibility and "within 10 working days" in accessibility
    assert "Email us" in read(site, "contribute/index.html") and mailbox in read(site, "contribute/index.html")
    assert "Give feedback without a GitHub account: email" in read(site, "about/index.html")
    assert mailbox in read(site, "draft/index.html")  # Send by email
    assert "To be completed before publication" in read(site, "privacy/index.html")  # the DPO's inputs are still to come


def test_currency_page(site):
    html = read(site, "currency/index.html")
    assert re.search(r'Current</strong><span class="csr-n">5<', html)
    assert re.search(r'Due</strong><span class="csr-n">1<', html)
    assert re.search(r'Stale</strong><span class="csr-n">1<', html)
    assert "Example: Legacy Waste Booking Service" in html


def test_examples_keep_their_states_as_time_passes(tmp_path):
    later = build(ROOT, tmp_path / "later", today=dt.date(2028, 1, 1)).register
    states = {e.id: e.currency for e in later.entries}
    assert states["csr-9003"] == "stale" and states["csr-9004"] == "due" and states["csr-9001"] == "current"
    assert states["csr-0001"] == "stale"  # real records are judged on the build date


def test_reference_generated_from_the_schema(site):
    schema = load_schema("asset")
    fields = reference_fields(schema)
    names = {name.split(".")[0] for name, _, _ in fields["mandatory"] + fields["optional"]}
    assert names == set(schema["properties"])
    html = read(site, "reference/index.html")
    assert "<code>owner.sector</code>" in html and "20 to 200 characters" in html
    assert all(rule in html for rule, _, _ in RULES)


def test_rules_list_matches_schema_readme():
    readme = (ROOT / "schema" / "README.md").read_text(encoding="utf-8")
    assert [r for r, _, _ in RULES] == re.findall(r"^\| (R\d\d) \|", readme, re.MULTILINE)


def test_publiccode_page_shows_the_real_files(site):
    html = read(site, "reference/publiccode/index.html")
    assert "softwareType: standalone/web" in html and "id: csr-0001" in html


# API and extracts


def test_api_files(site):
    index = json.loads(read(site, "api/v0/index.json"))
    assert index["generated"] == TODAY.isoformat() and index["schema_version"] == "0.1"
    assets = json.loads(read(site, "api/v0/assets.json"))["assets"]
    assert [a["id"] for a in assets] == [a["id"] for a in json.loads(read(site, "data/register.json"))["assets"]]
    assert "csr-9007" not in {a["id"] for a in assets}
    one = json.loads(read(site, "api/v0/assets/csr-0001.json"))
    assert one["hosting"] == "owner-hosted" and one["record_url"] == "assets/csr-0001/"
    assert json.loads(read(site, "api/v0/schema/asset.schema.json")) == load_schema("asset")


def test_published_records_still_match_the_schema(site):
    derived = {"hosting", "source", "source_state", "harvested_at", "content_hash", "currency", "last_changed",
               "merged_in", "history_url", "record_url"}  # fmt: skip
    for record in json.loads(read(site, "data/register.json"))["assets"]:
        assert check({k: v for k, v in record.items() if k not in derived}) == []


def test_csv(site):
    rows = list(csv.DictReader(io.StringIO(read(site, "data/register.csv"))))
    assert len(rows) == len(json.loads(read(site, "data/register.json"))["assets"])
    row = next(r for r in rows if r["id"] == "csr-9003")
    assert row["owner.organisation"] == "Example Council"
    assert row["capabilities"] == "booking-and-scheduling; payments"
    assert json.loads(row["codebases"])[0]["role"] == "Booking front end"
    assert row["charging.applies"] == "true"


def test_flatten():
    assert flatten({"a": {"b": 1, "c": [1, 2]}, "d": [{"e": None}], "f": False}) == {
        "a.b": "1", "a.c": "1; 2", "d": '[{"e":null}]', "f": "false",
    }  # fmt: skip
    assert to_csv([{"id": "x", "name": "Café, \"quoted\""}]).splitlines()[1] == 'x,"Café, ""quoted"""'


def test_data_page_lists_sizes_and_a_real_sample(site):
    html = read(site, "data/index.html")
    assert re.search(r"JSON, [\d.]+ KB", html)
    assert "&#34;id&#34;: &#34;csr-0001&#34;" in html or '"id": "csr-0001"' in html


def test_validate_page_carries_what_the_checker_needs(site):
    html = read(site, "validate/index.html")
    config = json.loads(re.search(r'id="csr-validate-config">(.*?)</script>', html, re.S).group(1))
    assert config["schemas"]["asset"] == load_schema("asset")
    assert config["schemas"]["pointer"] == load_schema("pointer")
    assert "csr-0001" in config["known_ids"] and "csr-9007" in config["known_ids"]
    assert [t["id"] for t in config["taxonomies"]["capabilities"]][0] == "identity-and-access"
    assert config["max_bytes"] == 262144
    assert "ajv2020.min.js" in html and "This page needs JavaScript" in html
