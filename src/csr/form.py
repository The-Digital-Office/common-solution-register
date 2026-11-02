"""The draft form's options and limits, taken from the schema (specification 6.2: the
form is generated at build time from the schema and taxonomy)."""

from __future__ import annotations

from typing import Any

from csr.schema import load_schema

#: Labels for the schema's enumerated values, as the Draft wireframe words them.
LABELS: dict[str, dict[str, str]] = {
    "asset_type": {"service": "Service", "platform": "Platform", "component": "Component", "api": "API",
                   "standard": "Standard", "pattern": "Pattern", "software": "Software", "artefact": "Artefact"},
    "status": {"concept": "Concept", "in-development": "In development", "beta": "Beta", "live": "Live",
               "deprecated": "Deprecated"},
    "terms_of_use.type": {"open-licence": "Open licence", "service-terms": "Service terms",
                          "commercial-terms": "Commercial terms", "other": "Other"},
    "charging.model": {"recharge": "Recharge", "subscription": "Subscription", "per-transaction": "Per transaction",
                       "other": "Other"},
    "interfaces.type": {"rest": "REST", "soap": "SOAP", "graphql": "GraphQL", "file": "File", "event": "Event",
                        "other": "Other"},
    "codebases.maintenance": {"internal": "Internal: maintained by the owner",
                              "contract": "Contract: maintained by a supplier",
                              "community": "Community: maintained by a community",
                              "none": "None: not maintained"},
    "codebases.visibility": {"public": "Public", "private": "Private"},
}  # fmt: skip


def _property(schema: dict[str, Any], path: str) -> dict[str, Any]:
    node: dict[str, Any] = {"properties": schema["properties"]}
    for part in path.split("."):
        node = node["properties"][part]
        if node.get("type") == "array" and "items" in node:
            node = node["items"]
    return node


def enum(schema: dict[str, Any], path: str) -> list[str]:
    """The allowed values at a dotted path, ignoring the sentinel."""
    node = _property(schema, path)
    if "enum" in node:
        return list(node["enum"])
    for option in node.get("anyOf", []):
        if "enum" in option:
            return list(option["enum"])
    raise KeyError(path)


def options(schema: dict[str, Any], path: str) -> list[tuple[str, str]]:
    """(value, label) pairs for a select or radio group, in schema order."""
    labels = LABELS[path]
    return [(value, labels.get(value, value)) for value in enum(schema, path)]


def limits(schema: dict[str, Any], path: str) -> dict[str, int]:
    node = _property(schema, path)
    for candidate in [node, *node.get("anyOf", [])]:
        if "maxLength" in candidate:
            return {"min": candidate.get("minLength", 0), "max": candidate["maxLength"]}
    return {}


def draft_context() -> dict[str, Any]:
    schema = load_schema("asset")
    return {
        "options": {path: options(schema, path) for path in LABELS},
        "limits": {path: limits(schema, path) for path in ("name", "summary", "purpose", "adoption_route.summary")},
        "order": list(schema["properties"]),
        "schema_version": schema["properties"]["schema_version"]["const"],
        "schema": schema,
    }
