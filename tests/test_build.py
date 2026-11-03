"""The site generator: the home page and record pages (specification 6.8 and 6.13)."""

import datetime as dt
import re
from html.parser import HTMLParser

import pytest
from helpers import TODAY

from csr.build import build, display_url, long_date
from csr.config import load_config
from csr.register import add_months, currency
from csr.schema import ROOT


class Parsed(HTMLParser):
    """Collects headings, links, classes and text from a page."""

    def __init__(self, html):
        super().__init__()
        self.h2, self.links, self.classes, self.text, self._h2 = [], [], [], [], False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.classes += (attrs.get("class") or "").split()
        if tag == "a":
            self.links.append(attrs.get("href"))
        self._h2 = tag == "h2"

    def handle_endtag(self, tag):
        self._h2 = False

    def handle_data(self, data):
        if data.strip():
            self.text.append(data.strip())
            if self._h2:
                self.h2.append(data.strip())


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    return build(ROOT, tmp_path_factory.mktemp("site"), base_url="http://localhost:8000/", today=TODAY)


def page(site, path):
    return (site.out / path).read_text(encoding="utf-8")


def test_pages_built(site):
    assert "index.html" in site.pages
    assert {f"assets/csr-{n}/index.html" for n in ("0001", "0002", "9001", "9005", "9006")} <= set(site.pages)
    assert "assets/csr-9007/index.html" not in site.pages  # fails validation: never published
    assert [u.id for u in site.register.unpublished] == ["csr-9007"]


def test_static_files_and_relative_links(site):
    assert (site.out / "static/vendor/sgds/4.3.0/design-system.min.css").is_file()
    assert (site.out / "static/js/init.js").is_file()
    for path in site.pages:
        if path == "404.html":  # links from the site root: see test_pages.py
            continue
        html = page(site, path)
        depth = path.count("/")
        assert f'href="{"../" * depth or "./"}static/csr.css"' in html
        assert "http://localhost:8000" not in html  # all links relative


def test_every_page_has_the_layout(site):
    for path in site.pages:
        p = Parsed(page(site, path))
        for cls in ("ds_skip-links", "ds_site-header", "ds_phase-banner", "ds_site-footer", "ds_site-navigation--mobile"):
            assert cls in p.classes, (path, cls)
        assert "This is not an official register." in " ".join(p.text)
        assert "Hosted for demonstration by The Digital Office for Scottish Local Government." in p.text


def test_home_lists_records_without_javascript(site):
    html = page(site, "index.html")
    p = Parsed(html)
    items = re.findall(r'<li class="ds_search-result" data-id="(csr-\d+)"( hidden)?>', html)
    assert [i for i, hidden in items if not hidden] == [
        "csr-0001", "csr-0002", "csr-9002", "csr-9001", "csr-9006", "csr-9003", "csr-9004",
        "csr-0003",
    ]  # fmt: skip
    assert [i for i, hidden in items if hidden] == ["csr-9005"]  # withdrawn: shown only when asked for
    assert "8 solutions" in p.text  # unpublished records are not listed at all
    assert "csr-js-only" in p.classes  # search, filters and sorting hidden without JavaScript
    assert "Confirmed by owner (2)" in p.text and "Software (0)" in p.text


def test_record_page_structure(site):
    p = Parsed(page(site, "assets/csr-0001/index.html"))
    assert p.h2[:8] == ["Hosted by its owner", "About this solution", "Owner and contact", "Classification",
                        "Using this solution", "Codebases", "Open data", "About this record"]  # fmt: skip
    assert "Owner-hosted" in p.text and "Confirmed by owner" in p.text and "Current" in p.text
    assert "solution.yml" in p.links and "../../draft/?from=csr-0001" in p.links
    assert "../../sectors/local-government/" in p.links
    assert (site.out / "assets/csr-0001/solution.yml").read_text() == (ROOT / "solution.yml").read_text()


def test_example_record_notices(site):
    p = Parsed(page(site, "assets/csr-9003/index.html"))
    text = " ".join(p.text)
    assert "csr-fiction" in p.classes
    assert "This service is deprecated" in p.h2 and "This record may be out of date" in p.h2
    assert "Stale: confirmation overdue since 2 September 2026" in text
    assert "../../assets/csr-9006/" in p.links  # replacement
    assert "Other states shown by examples" in p.h2
    assert "../../harvest/#csr-9007" in p.links
    assert ["Go to the service", "More information from the owner"] == [t for t in p.text if t.startswith(("Go to", "More info"))]


def test_due_record(site):
    assert "This record is due for confirmation" in Parsed(page(site, "assets/csr-9004/index.html")).h2


def test_withdrawn_record(site):
    p = Parsed(page(site, "assets/csr-9005/index.html"))
    assert "This record has been withdrawn" in p.h2
    assert "Withdrawn record" in p.text and "30 June 2026" in p.text


def test_text_is_escaped(tmp_path, site):
    html = page(site, "index.html")
    assert "<script>" not in html.replace('<script type="module"', "")


@pytest.mark.parametrize(
    ("confirmed", "state"),
    [("2026-10-01", "current"), ("2025-12-03", "current"), ("2025-12-02", "due"), ("2025-11-02", "stale")],
)
def test_currency(confirmed, state):
    config = load_config(ROOT)
    data = {"record_status": "example", "confirmation": {"last_confirmed": confirmed}}
    assert currency(data, TODAY, config)[0] == state


def test_currency_of_demonstration_and_withdrawn():
    config = load_config(ROOT)
    assert currency({"record_status": "demonstration"}, TODAY, config) == ("unconfirmed", None)
    assert currency({"record_status": "withdrawn"}, TODAY, config) == (None, None)


def test_helpers():
    assert add_months(dt.date(2026, 1, 31), 1) == dt.date(2026, 2, 28)
    assert add_months(dt.date(2025, 12, 1), 11) == dt.date(2026, 11, 1)
    assert display_url("https://example.gov.uk/a/b?c=1") == "example.gov.uk/a/b?c=1"
    assert long_date("2026-03-01") == "1 March 2026"


def test_config_base_url_override():
    assert load_config(ROOT, "http://localhost:8000").base_url == "http://localhost:8000/"
    assert load_config(ROOT).state_url.endswith("/api/v0/harvest-state.json")
