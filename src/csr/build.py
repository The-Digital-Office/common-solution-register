"""``csr build``: generate the static site from the register (specification 6.8)."""

from __future__ import annotations

import datetime as dt
import hashlib
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape

import yaml

from csr import __version__, api
from csr.config import Config, load_config
from csr.form import draft_context
from csr.register import Entry, Register, load_register
from csr.rules import RULES
from csr.schema import ROOT, SENTINEL, load_schema
from csr.taxonomy import TAXONOMIES, load_all

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

HARVEST_TAGS = {
    "ok": ("OK", "green"),
    "failing": ("Failing validation", "red"),
    "unavailable": ("Unavailable", "orange"),
    "not-harvested": ("Not yet harvested", "grey"),
}
PUBLICCODE_TAGS = {
    "valid": ("Valid (official parser)", "green"),
    "invalid": ("Fails the official parser", "red"),
    "unavailable": ("Unavailable", "orange"),
    "not-checked": ("Not yet checked", "grey"),
}
RULE_LABELS = {
    "SCHEMA": "Schema", "YAML": "YAML", "R14": "R14 owner match", "R15": "R15 fetch", "R16": "R16 status",
    "R17": "R17 publiccode.yml",
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


def long_datetime(value: str | None) -> str:
    """"2026-11-03T08:33:00Z" as "3 November 2026 at 08:33 UTC"."""
    if not value:
        return ""
    moment = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    return f"{moment.day} {moment:%B %Y} at {moment:%H:%M} UTC"


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
    env.filters.update(display_url=display_url, long_date=long_date, long_datetime=long_datetime)
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
        HARVEST_TAGS=HARVEST_TAGS,
        PUBLICCODE_TAGS=PUBLICCODE_TAGS,
        RULE_LABELS=RULE_LABELS,
        FOOTER=FOOTER,
        SGDS_VERSION=SGDS_VERSION,
        CSR_VERSION=__version__,
    )
    return env


def static_version() -> str:
    """A short hash of the site's own static files (not the vendored ones, whose folders carry their
    versions). Added to their addresses, so browsers fetch them again whenever they change."""
    digest = hashlib.sha256()
    for path in sorted(p for p in STATIC.rglob("*") if p.is_file() and "vendor" not in p.relative_to(STATIC).parts):
        digest.update(path.relative_to(STATIC).as_posix().encode() + b"\0" + path.read_bytes())
    return digest.hexdigest()[:10]


#: A script's import of another of the site's scripts: from './name.js'.
LOCAL_IMPORT = re.compile(r"(from\s+')(\./[\w-]+\.js)(')")


def _version_imports(js_dir: Path, version: str) -> None:
    """Add the version to the scripts' imports of each other, as the pages do for the scripts they load."""
    for path in js_dir.glob("*.js"):
        text = path.read_text(encoding="utf-8")
        path.write_text(LOCAL_IMPORT.sub(rf"\g<1>\g<2>?v={version}\g<3>", text), encoding="utf-8", newline="\n")


class Site:
    """Writes pages into the output directory with relative links."""

    def __init__(self, out: Path, config: Config, register: Register, today: dt.date) -> None:
        self.out = out
        self.env = environment()
        self.env.globals["v"] = static_version()
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
            # Always LF, so pages and files are the same whatever system builds them.
            target.write_text(content, encoding="utf-8", newline="\n")

    def page(self, path: str, template: str, root: str | None = None, **context: Any) -> None:
        """Render a page. ``path`` ends in ``/`` (written as index.html) or ``.html``.
        Links are relative to the page unless ``root`` is given."""
        file = path + "index.html" if path.endswith("/") or not path else path
        depth = file.count("/")
        html = self.env.get_template(template).render(
            root=root or "../" * depth or "./",
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
    state: dict | None = None,
    history: bool = True,
) -> BuildResult:
    """Build the site into ``out`` (default ``site/``), replacing what is there. ``state``
    is the harvest state (``csr harvest``); without it, sources in this repository are
    harvested from the working tree."""
    root = root or ROOT
    out = out or root / "site"
    today = today or dt.date.today()
    config = load_config(root, base_url)
    register = load_register(root, config, today, state, history)

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    shutil.copytree(STATIC, out / "static")

    site = Site(out, config, register, today)
    _version_imports(out / "static" / "js", site.env.globals["v"])
    listed = [e for e in register.entries if not e.withdrawn]
    site.page("", "index.html", nav="home", entries=register.entries, search_index=search_index(site))
    for entry in register.entries:
        _record_pages(site, entry)
    _taxonomy_pages(site, listed)
    _static_pages(site)
    _reference_pages(site, root)
    _data_pages(site)
    form = draft_context()
    # Owning sectors: an audience-only term ("Scottish public sector") cannot own a solution.
    form["sectors"] = [(t.id, t.label) for t in site.taxonomies["sectors"].terms if not t.intended_adopters_only]
    site.page("draft/", "draft.html", nav="contribute", form=form)
    _harvest_page(site)
    site.page("validate/", "validate.html", nav="validate", checker={
        "schemas": {"asset": load_schema("asset"), "pointer": load_schema("pointer")},
        "taxonomies": {name: [{"id": t.id, "status": t.status, "replaced_by": t.replaced_by,
                               "intended_adopters_only": t.intended_adopters_only} for t in tax.terms]
                       for name, tax in site.taxonomies.items()},
        "known_ids": sorted({e.id for e in register.entries} | {u.id for u in register.unpublished}),
        "max_bytes": config.harvest_max_bytes,
    })  # fmt: skip
    return BuildResult(out=out, pages=site.pages, register=register)


def search_index(site: Site) -> list[dict[str, Any]]:
    """What the home page script needs for each record: its facets, dates and search text
    (name, summary, owner, purpose, id, type and the labels and synonyms of its terms)."""
    index = []
    for entry in site.register.entries:
        r = entry.data
        terms = [site.term("sectors", r["owner"]["sector"])]
        terms += [site.term("service-areas", t) for t in r["service_areas"]]
        terms += [site.term("capabilities", t) for t in r["capabilities"]]
        words = [r["name"], r["summary"], r["owner"]["organisation"], r["purpose"], entry.id, TYPE_LABELS[r["asset_type"]]]
        for term in filter(None, terms):
            words += [term.label, *term.synonyms]
        index.append({
            "id": entry.id,
            "name": r["name"],
            "text": " ".join(" ".join(words).casefold().split()),
            "provenance": r["record_status"],
            "type": r["asset_type"],
            "sector": r["owner"]["sector"],
            "areas": r["service_areas"],
            "capabilities": r["capabilities"],
            "currency": entry.currency,
            "withdrawn": entry.withdrawn,
            "changed": entry.last_changed.isoformat() if entry.last_changed else None,
            "confirmed": r.get("confirmation", {}).get("last_confirmed"),
        })  # fmt: skip
    return index


#: Taxonomy name, the folder of its term pages, the record field it classifies, and wording.
TERM_PAGES = {
    "sectors": ("sectors", "Sector", "By owning sector", ("is owned by this sector", "are owned by this sector")),
    "service-areas": ("service-areas", "Service area", "By service area",
                      ("supports this service area", "support this service area")),
    "capabilities": ("capabilities", "Capability", "By capability",
                     ("provides this capability", "provide this capability")),
}  # fmt: skip


def _uses(entry: Entry, taxonomy: str, term_id: str) -> bool:
    r = entry.data
    if taxonomy == "sectors":
        return r["owner"]["sector"] == term_id
    return term_id in r["service_areas" if taxonomy == "service-areas" else "capabilities"]


def _term_ids(entry: Entry, taxonomy: str) -> list[str]:
    r = entry.data
    if taxonomy == "sectors":
        return [r["owner"]["sector"]]
    return r["service_areas" if taxonomy == "service-areas" else "capabilities"]


def _taxonomy_pages(site: Site, entries: list[Entry]) -> None:
    """Browse, and a page for every term (current records only)."""
    columns = []
    for name in TAXONOMIES:
        folder, _, heading, _ = TERM_PAGES[name]
        taxonomy = site.taxonomies[name]
        owners = [t for t in taxonomy.terms if not t.intended_adopters_only]  # "By owning sector" lists owners only
        counted = [(t, sum(_uses(e, name, t.id) for e in entries)) for t in owners]
        shown = counted if name == "sectors" else [(t, n) for t, n in counted if n]
        columns.append({"name": name, "folder": folder, "heading": heading, "terms": shown,
                        "total": len(owners)})  # fmt: skip
        for term in taxonomy.terms:
            kind = TERM_PAGES[name]
            if term.intended_adopters_only:  # an audience: the records intended for it
                matching = [e for e in entries if term.id in e.data["intended_adopters"]]
                kind = (*kind[:3], ("is intended for this audience", "are intended for this audience"))
            else:
                matching = [e for e in entries if _uses(e, name, term.id)]
            together: dict[str, int] = {}
            for e in matching:
                for other in _term_ids(e, name):
                    if other != term.id:
                        together[other] = together.get(other, 0) + 1
            related = [taxonomy.get(t) for t, _ in sorted(together.items(), key=lambda kv: (-kv[1], kv[0]))]
            site.page(f"{folder}/{term.id}/", "term.html", nav="browse", taxonomy=taxonomy,
                      kind=kind, term=term, entries=matching, related_terms=related)  # fmt: skip
    site.page("browse/", "browse.html", nav="browse", columns=columns)


def _static_pages(site: Site) -> None:
    site.page("contribute/", "contribute.html", nav="contribute")
    site.page("about/", "about.html", nav="about")
    site.page("accessibility/", "accessibility.html", nav="")
    site.page("privacy/", "privacy.html", nav="")
    # GitHub Pages serves 404.html at whatever address was asked for, so its links start from the site root.
    site.page("404.html", "404.html", root=urlsplit(site.config.base_url).path or "/", nav="")
    states = [e for e in site.register.entries if e.currency]
    site.page("currency/", "currency.html", nav="", entries=states,
              attention=[e for e in states if e.currency in ("stale", "due", "unconfirmed")])  # fmt: skip


def _reference_pages(site: Site, root: Path) -> None:
    schema = load_schema("asset")
    site.page("reference/", "reference.html", nav="", schema=schema, fields=reference_fields(schema),
              rules=RULES, pointer=load_schema("pointer"))  # fmt: skip
    worked = site.register.get("csr-0001")
    solution = _excerpt(worked.data, ["id", "name", "asset_type", "status", "owner", "service_url",
                                      "adoption_route", "codebases", "open_data"]) if worked else ""  # fmt: skip
    publiccode_data = yaml.safe_load((root / "publiccode.yml").read_text(encoding="utf-8"))
    publiccode = _excerpt(publiccode_data, ["publiccodeYmlVersion", "name", "url", "developmentStatus",
                                            "softwareType", "organisation", "legal", "maintenance"])  # fmt: skip
    site.page("reference/publiccode/", "publiccode.html", nav="", solution=solution, publiccode=publiccode)


def _excerpt(data: dict[str, Any], keys: list[str]) -> str:
    return yaml.safe_dump({k: data[k] for k in keys if k in data}, sort_keys=False, allow_unicode=True, width=60)


def reference_fields(schema: dict[str, Any]) -> dict[str, list[tuple[str, str, str]]]:
    """Rows for the field reference, generated from the schema:
    mandatory fields (with required sub-fields) and optional fields."""
    properties = schema["properties"]

    def allowed(prop: dict[str, Any]) -> str:
        prop = _resolve(schema, prop)
        if "const" in prop:
            return f'"{prop["const"]}"'
        if "enum" in prop:
            return ", ".join(str(v) for v in prop["enum"])
        if "anyOf" in prop:
            return "; or ".join(filter(None, (allowed(p) for p in prop["anyOf"])))
        if prop.get("type") == "boolean":
            return "true or false"
        if "pattern" in prop and prop["pattern"].startswith("^csr-"):
            return "csr-NNNN"
        if prop.get("pattern", "").startswith("^https://"):
            return "HTTPS URL"
        if prop.get("format") == "date":
            return "Date, YYYY-MM-DD"
        if prop.get("type") == "array":
            item = _resolve(schema, prop.get("items", {}))
            if item.get("pattern", "").startswith("^[a-z0-9]"):
                return "At least one taxonomy term" if prop.get("minItems") else "Taxonomy terms"
            return "List"
        if "minLength" in prop and "maxLength" in prop:
            return f"{prop['minLength']:,} to {prop['maxLength']:,} characters"
        if prop.get("type") == "object":
            return "See its fields"
        return "Text"

    def describe(prop: dict[str, Any]) -> str:
        text = prop.get("description") or _resolve(schema, prop).get("description", "")
        return text.split(". ")[0].rstrip(".")

    mandatory = []
    for name in schema["required"]:
        prop = properties[name]
        if prop.get("type") == "object" and prop.get("required"):
            for sub in prop["required"]:
                subprop = prop["properties"][sub]
                mandatory.append((f"{name}.{sub}", describe(subprop) or describe(prop), allowed(subprop)))
        else:
            mandatory.append((name, describe(prop), allowed(prop)))
    optional = [(name, describe(prop), allowed(prop)) for name, prop in properties.items()
                if name not in schema["required"]]  # fmt: skip
    return {"mandatory": mandatory, "optional": optional}


def _resolve(schema: dict[str, Any], prop: dict[str, Any]) -> dict[str, Any]:
    if "$ref" in prop:
        target = schema
        for part in prop["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        return {**target, **{k: v for k, v in prop.items() if k != "$ref"}}
    return prop


def _harvest_page(site: Site) -> None:
    state = site.register.state
    rows = []
    published = {e.id: e for e in site.register.entries}
    for record_id, harvested in sorted(state.get("sources", {}).items()):
        name = harvested.get("name", "")
        days = None
        if harvested.get("unavailable_since"):
            since = dt.datetime.fromisoformat(harvested["unavailable_since"].replace("Z", "+00:00")).date()
            days = (site.today - since).days
        rows.append({"id": record_id, "entry": published.get(record_id), "source": harvested.get("source", ""),
                     "harvest": harvested, "name": name, "days_unavailable": days})  # fmt: skip
    site.page("harvest/", "harvest.html", nav="", state=state, sources=rows)


def _data_pages(site: Site) -> None:
    files = api.files(site.register, site.taxonomies, site.config, site.today)
    files[api.API + "harvest-state.json"] = api.dumps(site.register.state)
    for path, content in files.items():
        site.write(path, content)
    sizes = {path: len(content.encode("utf-8")) for path, content in files.items()}
    sample = files.get(f"{api.API}assets/csr-0001.json", "")
    site.page("data/", "data.html", nav="data", sizes=sizes, sample=sample)


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
