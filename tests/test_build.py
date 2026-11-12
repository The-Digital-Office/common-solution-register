"""The site generator: the home page and record pages (specification 6.8 and 6.13)."""

import datetime as dt
import re
from html.parser import HTMLParser

import pytest
from helpers import TODAY, demonstration_ids

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
        assert f'href="{"../" * depth or "./"}static/csr.css?v=' in html
        assert "http://localhost:8000" not in html  # all links relative


def test_every_page_has_the_layout(site):
    for path in site.pages:
        html = page(site, path)
        p = Parsed(html)
        for cls in ("ds_skip-links", "ds_site-header", "csr-notice", "ds_site-footer", "ds_site-navigation--mobile"):
            assert cls in p.classes, (path, cls)
        assert "ds_phase-banner" not in p.classes  # replaced by the notice (W4)
        # The same short notice on every page, home included (W4).
        assert '<div class="csr-notice" role="region" aria-label="Demonstrator notice">' in html, path
        assert "This is a demonstrator, not an official register. Inclusion does not mean endorsement." in " ".join(p.text), path
        # The host's logo, whose alt text says who hosts the demonstrator.
        logo = re.search(r'<img class="ds_site-footer__org-logo" src="([^"]+)" alt="([^"]+)"', html)
        assert logo and logo[2] == "Hosted for demonstration by The Digital Office for Scottish Local Government", path
        assert logo[1].endswith("static/host/digital-office-logo.svg")
        assert '<a class="ds_site-footer__org-link" href="https://digitaloffice.scot/"><img class="ds_site-footer__org-logo"' in html


def test_the_footer_names_the_host_in_text_without_a_logo(tmp_path):
    import dataclasses

    from csr.build import Site

    config = dataclasses.replace(load_config(ROOT, base_url="http://localhost:8000/"), host_logo="")
    html = Site(tmp_path, config, None, TODAY).env.get_template("partials/footer.html").render(config=config, root="", FOOTER=[])
    assert "<p>Hosted for demonstration by The Digital Office for Scottish Local Government.</p>" in html
    assert "<img" not in html


def test_the_finder_lists_records_without_javascript(site):
    html = page(site, "solutions/index.html")
    p = Parsed(html)
    items = re.findall(r'<li class="ds_search-result" data-id="(csr-\d+)"( hidden)?>', html)
    shown = [i for i, hidden in items if not hidden]
    assert shown[:7] == [
        "csr-0001", "csr-0002", "csr-9002", "csr-9001", "csr-9006", "csr-9003", "csr-9004",
    ]  # fmt: skip
    assert sorted(shown[7:]) == demonstration_ids()  # never confirmed, so listed last
    assert [i for i, hidden in items if hidden] == ["csr-9005"]  # withdrawn: shown only when asked for
    assert f"{len(shown)} solutions" in p.text  # unpublished records are not listed at all
    assert "csr-js-only" in p.classes  # search, filters and sorting hidden without JavaScript
    assert "Confirmed by owner (2)" in p.text and "Software (0)" in p.text


def test_home_page_introduces_the_register(site):
    html = page(site, "index.html")
    p = Parsed(html)
    assert p.h2 == ["What is a common solution?", "Who is this register for?", "Recently updated", "Ways in",
                    "Is your solution missing?"]  # fmt: skip
    assert 'action="./solutions/" method="get"' in html  # the search goes to the finder
    assert "./solutions/?sort=changed" in p.links and "./solutions/" in p.links
    for anchor in ("h-capabilities", "h-sectors", "h-service-areas"):  # each lands on its Browse column
        assert f"./browse/#{anchor}" in p.links and f'id="{anchor}"' in page(site, "browse/index.html")
    assert "search.js" not in html and "csr-js-only" not in html  # the home page needs no script
    listed = [e for e in site.register.entries if not e.withdrawn]
    owners = {e.data["owner"]["organisation"] for e in listed}
    assert f"{len(listed)} solutions from {len(owners)} owners" in p.text
    assert html.count('<p class="csr-update">') == 3


def test_recently_updated_rule():
    from csr.build import recently_updated
    from csr.register import Entry

    def entry(id, confirmed=None, changed=None):
        data = {"confirmation": {"last_confirmed": confirmed}} if confirmed else {}
        return Entry(id=id, data=data, file="", text="", last_changed=dt.date.fromisoformat(changed) if changed else None)

    entries = [
        entry("a", confirmed="2026-10-01", changed="2026-09-01"),  # confirmed after its last change
        entry("b", changed="2026-11-01"),  # changed (a demonstration entry: never confirmed)
        entry("c", confirmed="2026-05-01", changed="2026-10-15"),  # changed after it was confirmed
        entry("d"),  # no dates (built without git history): left out
        entry("e", confirmed="2026-01-01"),
    ]
    assert [(e.id, what, str(when)) for e, what, when in recently_updated(entries)] == [
        ("b", "changed", "2026-11-01"), ("c", "changed", "2026-10-15"), ("a", "confirmed", "2026-10-01"),
    ]  # fmt: skip


def test_the_finder_and_records_point_at_solutions(site):
    record = Parsed(page(site, "assets/csr-0001/index.html"))
    assert "../../solutions/" in record.links  # the "Solutions" breadcrumb
    assert 'aria-current="page" href="../../solutions/">Find solutions' in page(site, "assets/csr-0001/index.html")
    finder = page(site, "solutions/index.html")
    assert 'aria-current="page" href="../solutions/">Find solutions' in finder
    assert 'aria-current="page" href="./">Home' in page(site, "index.html")


def test_record_page_structure(site):
    p = Parsed(page(site, "assets/csr-0001/index.html"))
    assert p.h2[:8] == ["On this page", "About this solution", "Owner and contact", "Classification",
                        "Using this solution", "Codebases", "Open data", "About this record"]  # fmt: skip
    assert "Help improve this record" in p.h2  # the band at the foot of the page
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


def facts(html):
    """The key facts grid as {label: value text}."""
    grid = re.search(r'<dl class="csr-facts"[^>]*>(.*?)</dl>', html, re.S)[1]
    return {k: re.sub(r"<[^>]+>", " ", v).split() for k, v in re.findall(r"<dt>(.*?)</dt><dd>(.*?)</dd>", grid)}


def band(html):
    """The page band: the header area of the record page."""
    return re.search(r'<div class="ds_layout__header">(.*?)<div class="ds_layout__content">', html, re.S)[1]


def test_record_summary_card(site):
    hosted = page(site, "assets/csr-0001/index.html")
    assert band(hosted).count('class="ds_tag') == 1 and "Confirmed by owner" in band(hosted)  # provenance only
    assert list(facts(hosted)) == ["Owner", "Lifecycle status", "Last confirmed", "Currency", "Hosting", "Record"]
    f = facts(hosted)
    assert " ".join(f["Hosting"]).startswith("Owner-hosted Harvested") and "View as JSON" in " ".join(f["Record"])
    assert " ".join(f["Last confirmed"]).endswith("By the owner, in their hosted solution.yml")
    # No service address or owner's page: downloading the record is the one main action.
    assert '<a class="ds_button" href="solution.yml"' in band(hosted)
    assert "ds_layout__sidebar" not in hosted and "Report a problem" not in hosted
    assert "Harvest history" in hosted

    demo = page(site, "assets/csr-0003/index.html")
    f = facts(demo)
    assert "Sources checked" in f and "Last confirmed" not in f
    assert " ".join(f["Currency"]) == "Not confirmed by owner Becomes current once the owner confirms it"
    assert re.search(r'<a class="ds_button" href="[^"]+">Go to the service</a>', band(demo))
    assert "ds_button--secondary" in band(demo) and "Is this your service?" in demo
    assert "csr-owner" in demo and "Confirm or correct" in demo

    example = page(site, "assets/csr-9003/index.html")
    f = facts(example)
    assert " ".join(f["Lifecycle status"]) == "Deprecated Since 31 March 2026"
    assert " ".join(f["Currency"]) == "Stale Not confirmed for more than 12 months"


def test_owner_hint_is_left_out_when_it_repeats_the_owner(site):
    for path in site.pages:
        if path.startswith("assets/") and path.endswith("index.html") and "csr-fact" in (html := page(site, path)):
            owner = facts(html)["Owner"]
            assert len(owner) < 2 or owner[: len(owner) // 2] != owner[len(owner) // 2 :], path


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


def test_a_charging_summary_is_shown_with_no_charge_and_not_stated(site):
    scotaccount = " ".join(Parsed(page(site, "assets/csr-0003/index.html")).text)
    assert "No charge. Beta participants get access" in scotaccount
    spatial_hub = " ".join(Parsed(page(site, "assets/csr-0006/index.html")).text)
    assert "Charges Not stated in public sources . Accounts are free" in spatial_hub  # text nodes joined by spaces


def test_the_host_logo_is_a_plain_svg():
    svg = (ROOT / "src/csr/static/host/digital-office-logo.svg").read_text(encoding="utf-8")
    assert "<svg" in svg and "<title>" in svg
    for unsafe in ("<script", "href", "<image", "url(", "on"+"load"):
        assert unsafe not in svg, unsafe


def test_the_site_s_own_files_are_fetched_again_when_they_change(site):
    """Browsers cache scripts; their addresses carry a version that changes with them."""
    from csr.build import static_version

    v = static_version()
    assert f'static/js/init.js?v={v}"' in page(site, "index.html")
    assert f'static/js/search.js?v={v}"' in page(site, "solutions/index.html")
    draft = (site.out / "static/js/draft.js").read_text(encoding="utf-8")
    assert f"from './draft-core.js?v={v}'" in draft and f"from './record-check.js?v={v}'" in draft
    assert "js-yaml/5.5.0/js-yaml.mjs'" in draft  # vendored files keep their versioned folders
    assert re.fullmatch(r"[0-9a-f]{10}", v)


def test_a_preview_asks_search_engines_not_to_index_it(site, tmp_path, monkeypatch):
    import dataclasses

    import csr.build

    assert load_config(ROOT).preview  # published as a preview on 9 November 2026
    for path in site.pages:
        assert '<meta name="robots" content="noindex, nofollow">' in page(site, path), path
    published = dataclasses.replace(load_config(ROOT, base_url="http://localhost:8000/"), preview=False)
    monkeypatch.setattr(csr.build, "load_config", lambda root, base_url: published)
    beta = build(ROOT, tmp_path / "site", base_url="http://localhost:8000/", today=TODAY)
    assert 'name="robots"' not in page(beta, "index.html")
