"""``csr build``: generate the static site from the register (specification 6.8)."""

from __future__ import annotations

import datetime as dt
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape

from csr import __version__
from csr.config import Config, load_config
from csr.register import Entry, Register, load_register
from csr.schema import ROOT, SENTINEL
from csr.taxonomy import load_all

STATIC = Path(__file__).parent / "static"
SGDS_VERSION = "4.3.0"

TYPE_LABELS = {
    "service": "Service", "platform": "Platform", "component": "Component", "api": "API",
    "standard": "Standard", "pattern": "Pattern", "software": "Software", "artefact": "Artefact",
}  # fmt: skip
STATUS_LABELS = {
    "concept": "Concept", "in-development": "In development", "beta": "Beta", "live": "Live",
    "deprecated": "Deprecated",
}  # fmt: skip
PROVENANCE_TAGS = {
    "owner-confirmed": ("Confirmed by owner", "green"),
    "demonstration": ("From public sources", "blue"),
    "example": ("Fictional example", "purple"),
}
CURRENCY_TAGS = {
    "current": ("Current", "teal"),
    "due": ("Due for confirmation", "orange"),
    "stale": ("Stale", "red"),
    "unconfirmed": ("Not confirmed by owner", "grey"),
}
TERMS_LABELS = {
    "open-licence": "Open licence", "service-terms": "Service terms",
    "commercial-terms": "Commercial terms", "other": "Other terms",
}  # fmt: skip
CHARGING_LABELS = {
    "recharge": "Recharge", "subscription": "Subscription", "per-transaction": "Per transaction", "other": "Other",
}  # fmt: skip
CONTACT_LABELS = {"role-mailbox": "role mailbox", "service-desk": "service desk", "web-form": "web form"}
MAINTENANCE_LABELS = {"internal": "Internal", "contract": "Contract", "community": "Community", "none": "None"}
INTERFACE_LABELS = {"rest": "REST", "soap": "SOAP", "graphql": "GraphQL", "file": "File", "event": "Event",
                    "other": "Other"}  # fmt: skip
RELATIONSHIP_LABELS = {
    "replaced-by": "replacement", "replaces": "replaces this", "uses": "uses", "used-by": "used by",
    "alternative": "alternative", "related": "related",
}  # fmt: skip

NAVIGATION = [
    ("home", "Find solutions", ""),
    ("browse", "Browse", "browse/"),
    ("contribute", "Contribute", "contribute/"),
    ("validate", "Validate", "validate/"),
    ("data", "Data and API", "data/"),
    ("about", "About", "about/"),
]
FOOTER = [
    ("About", "about/"),
    ("Accessibility", "accessibility/"),
    ("Privacy", "privacy/"),
    ("Currency", "currency/"),
    ("Harvest report", "harvest/"),
    ("Field reference", "reference/"),
]


@dataclass
class BuildResult:
    out: Path
    pages: list[str] = field(default_factory=list)
    register: Register | None = None


def display_url(url: str) -> str:
    """An address as people read it: without the scheme or a trailing slash on the host."""
    parts = urlsplit(url)
    text = parts.netloc + parts.path
    return text + (f"?{parts.query}" if parts.query else "")


def long_date(value: dt.date | str | None) -> str:
    if value is None:
        return ""
    date = dt.date.fromisoformat(value) if isinstance(value, str) else value
    return f"{date.day} {date:%B %Y}"


class OptionalUndefined(StrictUndefined):
    """Missing values may be tested (``{% if r.support %}``) or looped over,
    because most record fields are optional, but printing one is still an error."""

    def __bool__(self) -> bool:
        return False

    def __iter__(self):
        return iter(())

    def __len__(self) -> int:
        return 0


def environment() -> Environment:
    env = Environment(
        loader=PackageLoader("csr", "templates"),
        autoescape=select_autoescape(["html"]),
        undefined=OptionalUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.filters.update(display_url=display_url, long_date=long_date)
    env.globals.update(
        SENTINEL=SENTINEL,
        TYPE_LABELS=TYPE_LABELS,
        STATUS_LABELS=STATUS_LABELS,
        PROVENANCE_TAGS=PROVENANCE_TAGS,
        CURRENCY_TAGS=CURRENCY_TAGS,
        TERMS_LABELS=TERMS_LABELS,
        CHARGING_LABELS=CHARGING_LABELS,
        CONTACT_LABELS=CONTACT_LABELS,
        MAINTENANCE_LABELS=MAINTENANCE_LABELS,
        INTERFACE_LABELS=INTERFACE_LABELS,
        RELATIONSHIP_LABELS=RELATIONSHIP_LABELS,
        NAVIGATION=NAVIGATION,
        FOOTER=FOOTER,
        SGDS_VERSION=SGDS_VERSION,
        CSR_VERSION=__version__,
    )
    return env


class Site:
    """Writes pages into the output directory with relative links."""

    def __init__(self, out: Path, config: Config, register: Register, today: dt.date) -> None:
        self.out = out
        self.env = environment()
        self.config = config
        self.register = register
        self.taxonomies = load_all()
        self.today = today
        self.pages: list[str] = []

    def term(self, taxonomy: str, term_id: str):
        return self.taxonomies[taxonomy].get(term_id)

    def write(self, path: str, content: str | bytes) -> None:
        target = self.out / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            target.write_bytes(content)
        else:
            target.write_text(content, encoding="utf-8")

    def page(self, path: str, template: str, **context: Any) -> None:
        """Render a page. ``path`` ends in ``/`` (written as index.html) or ``.html``."""
        file = path + "index.html" if path.endswith("/") or not path else path
        depth = file.count("/")
        html = self.env.get_template(template).render(
            root="../" * depth or "./",
            path=path,
            config=self.config,
            site=self,
            today=self.today,
            **context,
        )
        self.write(file, html)
        self.pages.append(file)


def build(
    root: Path | None = None,
    out: Path | None = None,
    *,
    base_url: str | None = None,
    today: dt.date | None = None,
) -> BuildResult:
    """Build the site into ``out`` (default ``site/``), replacing what is there."""
    root = root or ROOT
    out = out or root / "site"
    today = today or dt.date.today()
    config = load_config(root, base_url)
    register = load_register(root, config, today)

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    shutil.copytree(STATIC, out / "static")

    site = Site(out, config, register, today)
    listed = [e for e in register.entries if not e.withdrawn]
    site.page("", "index.html", nav="home", entries=listed)
    for entry in register.entries:
        _record_pages(site, entry)
    return BuildResult(out=out, pages=site.pages, register=register)


def example_state(entry: Entry) -> str:
    """What a fictional example is there to show, for the "Other states shown by examples" links."""
    r = entry.data
    if entry.withdrawn:
        return "Withdrawn"
    if r.get("status") == "deprecated":
        return "Deprecated and stale" if entry.currency == "stale" else "Deprecated"
    if entry.currency == "due":
        return "Due for confirmation"
    if entry.currency == "stale":
        return "Stale"
    if r.get("interfaces"):
        return "API with interfaces"
    if entry.hosting == "owner-hosted":
        return "Owner-hosted"
    if r.get("charging", {}).get("applies") is True:
        return "Charges and support"
    return "Example"


def _other_examples(site: Site, current: Entry) -> list[tuple[str, str, str]]:
    links = [
        (example_state(e), f"assets/{e.id}/", e.id)
        for e in site.register.entries
        if e.data.get("record_status") in ("example", "withdrawn") and e.id.startswith("csr-9") and e.id != current.id
    ]
    links += [("Failing hosted source", f"harvest/#{u.id}", u.id) for u in site.register.unpublished
              if u.id.startswith("csr-9")]  # fmt: skip
    return sorted(links, key=lambda link: link[2])


def _record_pages(site: Site, entry: Entry) -> None:
    path = f"assets/{entry.id}/"
    template = "record-withdrawn.html" if entry.withdrawn else "record.html"
    related = [
        (site.register.get(item["id"]), item.get("relationship", "related"))
        for item in entry.data.get("related_assets", [])
    ]
    site.page(
        path,
        template,
        nav="home",
        entry=entry,
        r=entry.data,
        related=[(e, rel) for e, rel in related if e],
        other_examples=_other_examples(site, entry),
    )
    site.write(path + "solution.yml", entry.text)
