"""The API and bulk extracts (specification 6.8): static JSON under api/v0/,
and data/register.json and data/register.csv."""

from __future__ import annotations

import csv
import datetime as dt
import io
import json
from typing import Any

from csr.config import Config
from csr.register import Entry, Register
from csr.schema import load_schema
from csr.taxonomy import Taxonomy

API = "api/v0/"
LICENCE = {
    "content": "OGL-UK-3.0",
    "content_url": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
}
#: Fields the register adds to each record (specification 6.4), in output order.
DERIVED = ["hosting", "source", "source_state", "harvested_at", "content_hash", "currency", "last_changed",
           "merged_in", "history_url", "record_url"]


def record_json(entry: Entry) -> dict[str, Any]:
    """A record as published: the descriptor plus its derived fields."""
    derived = {
        "hosting": entry.hosting,
        "source": entry.source,
        "source_state": entry.source_state,
        "harvested_at": entry.harvest.get("harvested_at"),
        "content_hash": entry.harvest.get("content_hash"),
        "currency": entry.currency,
        "last_changed": entry.last_changed.isoformat() if entry.last_changed else None,
        "merged_in": entry.merged_in,
        "history_url": entry.history_url,
        "record_url": f"assets/{entry.id}/",
    }
    return {**entry.data, **{k: v for k, v in derived.items() if v is not None}}


def dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def flatten(record: dict[str, Any]) -> dict[str, str]:
    """One CSV row: nested objects as dotted columns, arrays of values joined
    with "; ", arrays of objects as compact JSON."""
    row: dict[str, str] = {}

    def put(prefix: str, value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                put(f"{prefix}.{key}" if prefix else key, item)
        elif isinstance(value, list):
            if any(isinstance(item, (dict, list)) for item in value):
                row[prefix] = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
            else:
                row[prefix] = "; ".join(_scalar(item) for item in value)
        else:
            row[prefix] = _scalar(value)

    put("", record)
    return row


def _scalar(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _columns(rows: list[dict[str, str]]) -> list[str]:
    """Columns in schema order, then derived fields, then anything else."""
    order = list(load_schema("asset")["properties"]) + DERIVED
    rank = {name: i for i, name in enumerate(order)}
    names = {name for row in rows for name in row}
    return sorted(names, key=lambda n: (rank.get(n.split(".")[0], len(order)), n))


def to_csv(records: list[dict[str, Any]]) -> str:
    rows = [flatten(r) for r in records]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=_columns(rows), lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def taxonomy_json(taxonomy: Taxonomy) -> dict[str, Any]:
    return {
        "taxonomy": taxonomy.name,
        "version": taxonomy.version,
        "terms": [
            {"id": t.id, "label": t.label, "definition": t.definition, "synonyms": list(t.synonyms),
             "status": t.status, **({"replaced_by": t.replaced_by} if t.replaced_by else {})}
            for t in taxonomy.terms
        ],
    }  # fmt: skip


def files(register: Register, taxonomies: dict[str, Taxonomy], config: Config, today: dt.date) -> dict[str, str]:
    """Every API and extract file, as path to content."""
    records = [record_json(e) for e in register.entries]
    generated = today.isoformat()
    out: dict[str, str] = {}
    out[API + "index.json"] = dumps({
        "api_version": "0",
        "generated": generated,
        "schema_version": load_schema("asset")["properties"]["schema_version"]["const"],
        "taxonomy_versions": {name: t.version for name, t in taxonomies.items()},
        "licence": LICENCE,
        "records": len(records),
        "links": {
            "assets": "assets.json",
            "asset": "assets/{id}.json",
            "taxonomy": {name: f"taxonomy/{name}.json" for name in taxonomies},
            "schema": "schema/asset.schema.json",
            "pointer_schema": "schema/pointer.schema.json",
            "register_json": "../../data/register.json",
            "register_csv": "../../data/register.csv",
        },
        "notice": "Version 0: may change without notice. Use record ids, not URLs, as identifiers. "
                  "Every record has record_status, so demonstration and example records can be excluded.",
    })  # fmt: skip
    out[API + "assets.json"] = dumps({"generated": generated, "assets": records})
    for record in records:
        out[f"{API}assets/{record['id']}.json"] = dumps(record)
    for name, taxonomy in taxonomies.items():
        out[f"{API}taxonomy/{name}.json"] = dumps(taxonomy_json(taxonomy))
    for name in ("asset", "pointer", "taxonomy"):
        out[f"{API}schema/{name}.schema.json"] = dumps(load_schema(name))
    out["data/register.json"] = dumps({"generated": generated, "licence": LICENCE, "assets": records})
    out["data/register.csv"] = to_csv(records)
    return out
