"""Validation rules from appendix C that need no network access.

Each rule takes a record and the context and returns its findings. Rules run
after the schema check and must cope with records that failed it.
"""

from __future__ import annotations

import datetime as dt
import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any

from csr.findings import Finding, error, warning
from csr.records import Record
from csr.schema import SENTINEL
from csr.taxonomy import Taxonomy

EXAMPLE_RANGE = range(9000, 10000)
REGISTER_RANGE = range(1, 9000)

#: Local parts of email addresses that name a role, not a person (R07).
ROLE_WORDS = {
    "admin", "contact", "contactus", "customer", "customers", "data", "digital", "dpo", "enquiries",
    "enquiry", "feedback", "foi", "hello", "help", "helpdesk", "info", "information", "it", "mail",
    "office", "platform", "platforms", "product", "products", "service", "servicedesk", "services",
    "support", "team", "technology", "web", "webmaster",
}  # fmt: skip
PERSONAL_EMAIL = re.compile(r"^([a-z]{2,})[._-]([a-z]{2,})[0-9]*@", re.IGNORECASE)


@dataclass(frozen=True)
class Context:
    """What the rules need beyond the record itself."""

    taxonomies: dict[str, Taxonomy]
    today: dt.date
    known_ids: frozenset[str] | None = None  # None when there is no register to check against


Rule = Callable[[Record, Context], list[Finding]]


def walk(value: Any, path: str = "") -> Iterator[tuple[str, Any]]:
    """Yield (path, value) for every scalar in a document."""
    if isinstance(value, dict):
        for key, item in value.items():
            yield from walk(item, f"{path}.{key}" if path else str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk(item, f"{path}[{index}]")
    else:
        yield path, value


def get_path(data: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(data, dict):
            return None
        data = data.get(key)
    return data


def list_items(data: Any, key: str) -> list[tuple[int, dict]]:
    value = data.get(key) if isinstance(data, dict) else None
    if not isinstance(value, list):
        return []
    return [(i, item) for i, item in enumerate(value) if isinstance(item, dict)]


def r02_id_range(record: Record, context: Context) -> list[Finding]:
    """R02: example records use csr-9000 to csr-9999, and only example records do.
    Withdrawn records may use either range (specification 5.1)."""
    match = re.fullmatch(r"csr-([0-9]{4})", record.id or "")
    if not match:
        return []
    number = int(match.group(1))
    status = record.record_status
    if status == "example" and number not in EXAMPLE_RANGE:
        return [error(record.label, "R02", "id", f"{record.id} is an example record outside csr-9000 to csr-9999",
                      "Give fictional example records an id from csr-9000 to csr-9999.")]  # fmt: skip
    if status in ("owner-confirmed", "demonstration") and number not in REGISTER_RANGE:
        return [error(record.label, "R02", "id", f"{record.id} is reserved for fictional examples or is not allowed",
                      "Give real records an id from csr-0001 to csr-8999.")]  # fmt: skip
    return []


def r03_r04_taxonomy(record: Record, context: Context) -> list[Finding]:
    """R03: taxonomy terms exist. R04: a referenced term is deprecated."""
    findings = []
    data = record.data
    references: list[tuple[str, str, Any]] = [("sectors", "owner.sector", get_path(data, "owner", "sector"))]
    for field, taxonomy in (("intended_adopters", "sectors"), ("service_areas", "service-areas"),
                            ("capabilities", "capabilities")):  # fmt: skip
        values = data.get(field)
        if isinstance(values, list):
            references += [(taxonomy, f"{field}[{i}]", v) for i, v in enumerate(values)]
    for taxonomy_name, path, value in references:
        if not isinstance(value, str):
            continue
        taxonomy = context.taxonomies[taxonomy_name]
        term = taxonomy.get(value)
        if term is None:
            findings.append(error(record.label, "R03", path, f"'{value}' is not a term in taxonomy/{taxonomy_name}.yaml",
                                  f"Use one of: {', '.join(taxonomy.ids)}."))  # fmt: skip
        elif term.deprecated:
            fix = f"Use '{term.replaced_by}' instead." if term.replaced_by else "Choose a current term."
            findings.append(warning(record.label, "R04", path, f"'{value}' is a deprecated term", fix))
    return findings


def r05_related_assets(record: Record, context: Context) -> list[Finding]:
    """R05: related_assets ids exist in the register."""
    if context.known_ids is None:
        return []
    return [
        error(record.label, "R05", f"related_assets[{i}].id", f"{item['id']} is not a record in the register",
              "Check the id, or remove the related asset.")
        for i, item in list_items(record.data, "related_assets")
        if isinstance(item.get("id"), str) and item["id"] not in context.known_ids
    ]  # fmt: skip


def r06_confirmation_date(record: Record, context: Context) -> list[Finding]:
    """R06: last_confirmed is not in the future."""
    value = get_path(record.data, "confirmation", "last_confirmed")
    try:
        date = dt.date.fromisoformat(value) if isinstance(value, str) else None
    except ValueError:
        return []  # the schema reports invalid dates
    if date and date > context.today:
        return [error(record.label, "R06", "confirmation.last_confirmed", f"{value} is in the future",
                      "Give the date the owner actually confirmed the record.")]  # fmt: skip
    return []


def r07_personal_contact(record: Record, context: Context) -> list[Finding]:
    """R07: a contact value that looks like a named person's email address."""
    value = get_path(record.data, "contact", "value")
    if not isinstance(value, str):
        return []
    match = PERSONAL_EMAIL.match(value)
    if match and not ({match.group(1).lower(), match.group(2).lower()} & ROLE_WORDS):
        return [warning(record.label, "R07", "contact.value", f"'{value}' looks like a named person's address",
                        "Use a role mailbox, service desk or web form, so the contact survives staff changes.")]  # fmt: skip
    return []


def r09_todo(record: Record, context: Context) -> list[Finding]:
    """R09: no value starts with TODO."""
    return [
        error(record.label, "R09", path, "still starts with TODO", "Replace the placeholder with the real value.")
        for path, value in walk(record.data)
        if isinstance(value, str) and value.lstrip().startswith("TODO")
    ]


def r10_sentinel(record: Record, context: Context) -> list[Finding]:
    """R10: the sentinel is used outside a demonstration record."""
    if record.record_status == "demonstration":
        return []
    return [
        error(record.label, "R10", path, f"'{SENTINEL}' is allowed only in demonstration records",
              "Give the actual value: the owner can state it.")
        for path, value in walk(record.data)
        if value == SENTINEL
    ]  # fmt: skip


def r11_example_name(record: Record, context: Context) -> list[Finding]:
    """R11: an example record's name begins "Example:"."""
    name = record.data.get("name")
    if record.record_status == "example" and isinstance(name, str) and not name.startswith("Example:"):
        return [error(record.label, "R11", "name", "a fictional example's name must begin \"Example:\"",
                      f"Rename it \"Example: {name}\".")]  # fmt: skip
    return []


def r12_publiccode_url(record: Record, context: Context) -> list[Finding]:
    """R12: a public codebase has no publiccode_url."""
    return [
        warning(record.label, "R12", f"codebases[{i}]", "public codebase has no publiccode_url",
                "Add a publiccode.yml to the codebase's repository and link it.")
        for i, item in list_items(record.data, "codebases")
        if item.get("visibility") == "public" and not item.get("publiccode_url")
    ]  # fmt: skip


def r18_https(record: Record, context: Context) -> list[Finding]:
    """R18: the web addresses an adopter follows are HTTPS URLs."""
    data = record.data
    candidates = [(f, data.get(f)) for f in ("service_url", "service_page_url", "documentation_url")]
    candidates += [(f"codebases[{i}].repository_url", c.get("repository_url")) for i, c in list_items(data, "codebases")]
    candidates += [(f"open_data[{i}].url", d.get("url")) for i, d in list_items(data, "open_data")]
    demonstration = record.record_status == "demonstration"
    return [
        error(record.label, "R18", path, f"'{value}' is not an HTTPS URL", "Use a full address starting https://.")
        for path, value in candidates
        if value is not None
        and not (demonstration and value == SENTINEL)
        and not (isinstance(value, str) and re.match(r"^https://[^\s/$.?#][^\s]*$", value))
    ]


#: Rules for full records, in rule order.
RECORD_RULES: tuple[Rule, ...] = (
    r02_id_range,
    r03_r04_taxonomy,
    r05_related_assets,
    r06_confirmation_date,
    r07_personal_contact,
    r09_todo,
    r10_sentinel,
    r11_example_name,
    r12_publiccode_url,
    r18_https,
)

#: Rules for pointer records.
POINTER_RULES: tuple[Rule, ...] = (r09_todo,)


#: The validation rules (appendix C), as listed in schema/README.md and on the field reference page.
RULES: tuple[tuple[str, str, str], ...] = (
    ("R01", "id matches the file name and is unique, including against the base branch", "Error"),
    ("R02", "ID range matches provenance: example records use csr-9000 to csr-9999", "Error"),
    ("R03", "Taxonomy references exist", "Error"),
    ("R04", "A referenced taxonomy term is deprecated", "Warning"),
    ("R05", "related_assets ids exist", "Error"),
    ("R06", "last_confirmed is not in the future", "Error"),
    ("R07", "A contact value that looks personal", "Warning"),
    ("R08", "Repository and source URLs respond (checked separately; never blocks a merge)", "Warning"),
    ("R09", "No value starts with TODO", "Error"),
    ("R10", "\"Not stated in public sources\" is used outside a demonstration record", "Error"),
    ("R11", "An example record's name does not begin \"Example:\"", "Error"),
    ("R12", "A public codebase has no publiccode_url", "Warning"),
    ("R13", "Vendored files match their pinned hashes", "Test failure"),
    ("R14", "A harvested id and owner match the pointer's id and expected_owner", "Error (not published)"),
    ("R15", "A source is not HTTPS, is too large, times out, or redirects to an address that is not HTTPS",
     "Error (last valid version kept)"),
    ("R16", "A pointer resolves to a record that is not owner-confirmed or withdrawn (or an example)", "Error"),
    ("R17", "A codebase's publiccode.yml fails the official parser", "Warning"),
    ("R18", "A service, documentation, repository or open data address is not an HTTPS URL", "Error"),
    ("R19", "A codebase's publiccode.yml disagrees with the record's repository URL or maintenance", "Warning"),
)
