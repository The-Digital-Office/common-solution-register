"""Schema problems in plain words, one per field: the same wording as the browser's
checker (src/csr/static/js/record-check.js), so the command line, the harvest report,
the draft form and the validate page say the same thing."""

from __future__ import annotations

import re
from typing import Any

from jsonschema.exceptions import ValidationError

LABELS = {
    "schema_version": "Schema version", "id": "Record ID", "record_status": "Whether you are from the owning organisation",
    "name": "Name", "summary": "Summary", "purpose": "Purpose", "asset_type": "Asset type", "status": "Status",
    "owner.organisation": "Owning organisation", "owner.sector": "Owning sector", "contact": "Contact",
    "contact.value": "Contact", "contact.type": "Contact type", "service_areas": "Service areas",
    "capabilities": "Capabilities", "intended_adopters": "Intended for", "terms_of_use.type": "Terms of use",
    "terms_of_use.licence": "Licence", "terms_of_use.url": "Terms URL",
    "adoption_route.summary": "How another organisation can adopt it", "charging.applies": "Charges",
    "charging.model": "Charging model", "charging.url": "Charging details URL", "charging.summary": "Charging details",
    "support.summary": "Support arrangements", "service_url": "Service address",
    "service_page_url": "Your page describing the service", "documentation_url": "Documentation address",
    "sources[].url": "Address of the public page", "sources[].title": "Title of the page",
    "sources[].accessed": "Date you read it", "deprecation.date": "Deprecation date",
    "deprecation.migration_guidance": "Migration guidance", "withdrawal.date": "Withdrawal date",
    "withdrawal.reason": "Reason for withdrawal", "interfaces[].type": "Interface type",
    "interfaces[].documentation_url": "Interface documentation URL", "codebases[].repository_url": "Repository URL",
    "codebases[].visibility": "Visibility", "codebases[].publiccode_url": "publiccode.yml URL",
    "codebases[].maintenance": "Maintenance", "open_data[].title": "Data link title", "open_data[].url": "Catalogue URL",
    "confirmation.last_confirmed": "Date last confirmed", "source": "Source", "expected_owner": "Expected owner",
}  # fmt: skip

MISSING = {
    "schema_version": 'Add schema_version: "0.1"', "id": "Add the record id (csr- followed by four digits)",
    "asset_type": "Choose the asset type", "status": "Choose the status", "owner": "Enter the owning organisation and sector",
    "owner.sector": "Choose the owning sector",
    "contact.type": "Say whether the contact is a role mailbox, service desk or web form", "contact.value": "Enter a contact",
    "confirmation": "Add the owner's confirmation: the date, how and where it was given",
    "confirmation.last_confirmed": "Enter the date the owner last confirmed the record",
    "confirmation.method": "Say how the owner confirmed the record",
    "confirmation.reference": "Say where the confirmation can be found", "terms_of_use.type": "Choose the terms of use",
    "charging.applies": "Say whether there are charges for adopters", "interfaces[].type": "Choose the interface type",
    "codebases[].maintenance": "Choose how the codebase is maintained",
    "record_status": "Say whether you are from the owning organisation", "name": "Enter the solution's name",
    "summary": "Enter a summary", "purpose": "Enter the purpose", "owner.organisation": "Enter the owning organisation",
    "contact": "Enter a contact", "service_areas": "Choose at least one service area",
    "capabilities": "Choose at least one capability", "intended_adopters": "Choose who it is intended for",
    "adoption_route": "Say how another organisation can adopt it",
    "adoption_route.summary": "Say how another organisation can adopt it",
    "charging": "Say whether there are charges for adopters", "charging.model": "Choose a charging model",
    "support": "Describe the support arrangements", "support.summary": "Describe the support arrangements",
    "service_url": "Enter the service address",
    "service_page_url": "Enter the address of your page describing the service", "sources": "Add at least one public source",
    "sources[].url": "Enter the address of the public page", "sources[].title": "Enter the title of the page",
    "sources[].accessed": "Enter the date you read it",
    "deprecation": "Enter the deprecation date and migration guidance", "deprecation.date": "Enter the deprecation date",
    "deprecation.migration_guidance": "Enter the migration guidance",
    "withdrawal": "Enter the withdrawal date and reason", "withdrawal.date": "Enter the withdrawal date",
    "withdrawal.reason": "Enter the reason for withdrawal", "interfaces": "Add the interface's documentation URL",
    "interfaces[].documentation_url": "Enter the interface's documentation URL",
    "codebases": "Add at least one codebase: software must list one",
    "codebases[].repository_url": "Enter the repository URL",
    "codebases[].visibility": "Choose whether the codebase is public or private",
    "open_data[].title": "Enter a title for the data link", "open_data[].url": "Enter the catalogue URL",
    "terms_of_use": "Choose the terms of use", "source": "Add the HTTPS address of the owner's solution.yml",
    "expected_owner": "Add the expected owner",
}  # fmt: skip

EITHER = {
    "terms_of_use": "Enter a licence (SPDX identifier, for example MIT) or the address of the terms",
    "charging": "Enter the charging details or their address",
}
RANK = ["required", "minItems", "format", "pattern", "minLength", "maxLength", "enum", "type",
        "additionalProperties", "uniqueItems", "const", "not"]  # fmt: skip
SKIP = {"if", "anyOf", "oneOf", "allOf", "then", "else"}


def dotted(path) -> str:
    return "".join(f"[{p}]" if isinstance(p, int) else f".{p}" for p in path).lstrip(".")


def generic(path: str) -> str:
    return re.sub(r"\[\d+\]", "[]", path)


def label(path: str) -> str:
    return LABELS.get(generic(path), generic(path))


def _message(error: ValidationError, path: str) -> str:
    name = label(path)
    kind = error.validator
    value: Any = error.validator_value
    if kind == "required":
        return MISSING.get(generic(path), f"Enter {name.lower()}")
    if kind == "minLength":
        return f"{name} must be at least {value} characters"
    if kind == "maxLength":
        return f"{name} must be {value} characters or fewer"
    if kind == "minItems":
        return MISSING.get(generic(path), f"{name}: add at least {value}")
    if kind == "format":
        if value == "date":
            return f"{name} must be a real date, for example 31/03/2026"
        if value == "email":
            return f"{name} must be an email address, a web address starting https://, or a phone number"
        return f"{name} must be a full web address starting https://"
    if kind == "pattern":
        if value.startswith("^https://"):
            return f"{name} must be a full web address starting https://"
        if value.startswith("^[0-9]{4}"):
            return f"{name} must be a date, for example 31/03/2026"
        if "@" in value:
            return f"{name} must be an email address, a web address starting https://, or a phone number"
        if value.startswith("^csr-"):
            return f"{name} must be csr- followed by four digits"
        if value.startswith("^[A-Za-z0-9.+-]+"):
            return f"{name} must be an SPDX licence identifier, for example MIT or OGL-UK-3.0"
        return f"{name} is not in the right form"
    if kind == "enum":
        return f"Choose {name.lower()} from the list"
    if kind == "const":
        return f"{name} must be {value!r}"
    if kind == "not":
        return '"Not stated in public sources" can only be used by people who are not from the owning organisation'
    if kind == "additionalProperties":
        extra = re.findall(r"'([^']+)'", error.message)
        return f'{name}: "{extra[0] if extra else "a field"}" is not a field the register uses'
    if kind == "type":
        return f"{name} must be {'a list' if value == 'array' else 'a group of fields' if value == 'object' else f'a {value}'}"
    if kind == "uniqueItems":
        return f"{name} lists the same choice twice"
    return f"{name} is not valid"


def _fix(error: ValidationError, path: str) -> str:
    kind = error.validator
    if kind in ("required", "minItems"):
        if generic(path) in ("service_areas", "capabilities", "intended_adopters", "owner.sector"):
            return "Choose from the taxonomy (see the field reference)."
        return "Add it: see the field reference for what it should contain."
    if kind in ("format", "pattern"):
        return "Correct the value: see the field reference for the format."
    if kind in ("minLength", "maxLength"):
        return "Change the length of the text."
    if kind == "enum":
        return "Use one of the values in the field reference."
    if kind == "not":
        return "Give the actual value: the owner can state it."
    if kind == "additionalProperties":
        return "Remove the field, or check its spelling against the field reference."
    return "See the field reference for what is allowed."


def _flatten(errors):
    """Every leaf error, looking inside anyOf so the most useful branch can be chosen."""
    for error in errors:
        if error.validator == "anyOf" and error.context:
            yield error
            yield from _flatten(error.context)
        else:
            yield error


def plain(errors) -> list[tuple[str, str, str]]:
    """(path, message, fix) for schema errors, one per field."""
    errors = list(_flatten(errors))
    either = {dotted(e.absolute_path) for e in errors if e.validator == "anyOf" and generic(dotted(e.absolute_path)) in EITHER}
    best: dict[str, tuple[int, str, str]] = {}
    for error in errors:
        if error.validator in SKIP:
            continue
        parent = dotted(error.absolute_path)
        if parent in either and "anyOf" in error.relative_schema_path or (parent in either and error.parent is not None
                                                                            and error.parent.validator == "anyOf"):
            continue
        if error.validator == "const" and error.validator_value == "not-publicly-stated":
            continue  # the other branch is reported
        if error.validator == "required":
            missing = re.findall(r"'([^']+)'", error.message)[0]
            path = f"{parent}.{missing}" if parent else missing
        else:
            path = parent
        rank = RANK.index(error.validator) if error.validator in RANK else len(RANK)
        if path not in best or rank < best[path][0]:
            best[path] = (rank, _message(error, path), _fix(error, path))
    for path in either:
        best[path] = (-1, EITHER[generic(path)], "Add one of them.")
    return [(path, message, fix) for path, (_, message, fix) in sorted(best.items())]
