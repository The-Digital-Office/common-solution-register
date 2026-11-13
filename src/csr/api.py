"""The API and bulk extracts (specification 6.8): static JSON under api/v0/,
and data/register.json and data/register.csv, described in api/v0/metadata.json
with the UK Cross-Government Metadata Exchange Model (DP-57)."""

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


#: The UK Cross-Government Metadata Exchange Model (DP-57): what the register's
#: open data is described with, and where its definition is.
METADATA_MODEL = {
    "name": "UK Cross-Government Metadata Exchange Model",
    "url": "https://co-cddo.github.io/ukgov-metadata-exchange-model/",
}
#: The API is a demonstrator's version 0 (DP-50): ALPHA in the model's service statuses.
SERVICE_STATUS = "ALPHA"


def metadata(register: Register, config: Config, today: dt.date, sizes: dict[str, int]) -> dict[str, Any]:
    """The register's open data described with the UK Cross-Government Metadata Exchange
    Model (DCAT): the dataset, its two download files and the API that serves it.

    Field names and values follow the model. One departure (DP-57): the model takes its
    publisher and creator from a list of GOV.UK organisations, which does not include the
    host, so the host organisation is given by name.
    """
    base = config.base_url
    dataset_id = f"{base}data/"
    api_id = f"{base}{API}"
    changed = [e.last_changed for e in register.entries if e.last_changed]
    modified = max(changed).isoformat() if changed else today.isoformat()
    owner = config.host_organisation
    common: dict[str, Any] = {
        "licence": LICENCE["content_url"],
        "accessRights": "OPEN",
        "securityClassification": "OFFICIAL",
        "publisher": owner,
        "creator": [owner],
        "modified": modified,
    }
    if config.contact_mailbox:
        common["contactPoint"] = {"contactName": config.title, "email": config.contact_mailbox}
    if config.first_published:
        common["issued"] = config.first_published.isoformat()

    def distribution(path: str, title: str, media_type: str, description: str) -> dict[str, Any]:
        return {
            "identifier": f"{base}{path}",
            "type": "dcat:Distribution",
            "title": title,
            "description": description,
            "downloadURL": f"{base}{path}",
            "mediaType": media_type,
            "byteSize": sizes[path],
            "licence": LICENCE["content_url"],
            "accessRights": "OPEN",
            "modified": modified,
            **({"issued": common["issued"]} if "issued" in common else {}),
        }

    return {
        "model": METADATA_MODEL,
        "dataset": {
            "identifier": dataset_id,
            "type": "dcat:Dataset",
            "title": f"{config.title}: records",
            "summary": "Digital solutions that public bodies offer to others in the Scottish public sector "
                       "for reuse: owners, terms, how to adopt them and how current each record is.",
            "description": "Every record in the register, with the fields the register derives (hosting, "
                           "currency, last change). This is a demonstrator, not an official register: records "
                           "are confirmed by their owner, compiled from public sources, or fictional examples, "
                           "and each says which in record_status. Inclusion does not mean endorsement.",
            "keyword": ["common solutions", "reuse", "digital services", "Scottish public sector"],
            **common,
            "version": today.isoformat(),
            "updateFrequency": "freq:daily",
            "distribution": [f"{base}data/register.json", f"{base}data/register.csv"],
            "relatedResource": [api_id, config.repository_url],
        },
        "distributions": [
            distribution("data/register.json", "register.json", "application/json",
                         "Every record as JSON, with its derived fields."),
            distribution("data/register.csv", "register.csv", "text/csv",
                         "Every record as CSV (UTF-8), one row per record; nested fields use dotted column names."),
        ],
        "dataService": {
            "identifier": api_id,
            "type": "dcat:DataService",
            "title": f"{config.title} API",
            "summary": "Static JSON files: all records, one record, the taxonomies and the schema. No key or "
                       "registration is needed.",
            "description": "Version 0 of a read-only API made of static JSON files. It may change without notice; "
                           "use record IDs, not URLs, as identifiers. index.json lists every file.",
            **common,
            "version": "0",
            "endpointURL": api_id,
            "endpointDescription": dataset_id,
            "serviceType": "REST",
            "serviceStatus": SERVICE_STATUS,
            "servesData": [dataset_id],
        },
    }


#: What each taxonomy is, for its SKOS concept scheme.
SCHEME_TITLES = {
    "sectors": "Sectors: who owns a common solution, and who it is intended for",
    "service-areas": "Service areas that common solutions support",
    "capabilities": "Capabilities that common solutions provide",
}


def _turtle(text: str) -> str:
    """A Turtle string literal, in English."""
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")
    return f'"{escaped}"@en'


def taxonomy_skos(taxonomy: Taxonomy, config: Config) -> str:
    """A taxonomy as a SKOS concept scheme in Turtle (decision point DP-58).

    Each term is a concept whose URI is its page on the site (``<taxonomy>/<id>/``); the
    scheme's URI is its column on the Browse page. Labels, synonyms and definitions become
    preferred labels, alternative labels and definitions; a deprecated term is marked
    deprecated and points to its replacement.
    """
    base = config.base_url
    scheme = f"{base}browse/#h-{taxonomy.name}"
    concept = lambda term_id: f"<{base}{taxonomy.name}/{term_id}/>"  # noqa: E731
    lines = [
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
        "@prefix dct: <http://purl.org/dc/terms/> .",
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
        "",
        f"<{scheme}> a skos:ConceptScheme ;",
        f"    skos:prefLabel {_turtle(SCHEME_TITLES.get(taxonomy.name, taxonomy.name))} ;",
        f"    dct:title {_turtle(SCHEME_TITLES.get(taxonomy.name, taxonomy.name))} ;",
        f'    owl:versionInfo "{taxonomy.version}" ;',
        f"    dct:license <{LICENCE['content_url']}> ;",
        f"    dct:publisher {_turtle(config.host_organisation)} ;",
        "    skos:hasTopConcept " + ", ".join(concept(t.id) for t in taxonomy.terms if not t.deprecated) + " .",
    ]
    for term in taxonomy.terms:
        lines += [
            "",
            f"{concept(term.id)} a skos:Concept ;",
            f"    skos:inScheme <{scheme}> ;",
            f'    skos:notation "{term.id}" ;',
            f"    skos:prefLabel {_turtle(term.label)} ;",
            f"    skos:definition {_turtle(term.definition)} ;",
        ]
        lines += [f"    skos:altLabel {_turtle(s)} ;" for s in term.synonyms]
        if term.intended_adopters_only:
            lines.append(f"    skos:scopeNote {_turtle('An audience only: used for who a solution is intended for, never as the sector that owns it.')} ;")
        if term.deprecated:
            lines.append("    owl:deprecated true ;")
            if term.replaced_by:
                lines.append(f"    dct:isReplacedBy {concept(term.replaced_by)} ;")
        else:
            lines.append(f"    skos:topConceptOf <{scheme}> ;")
        lines[-1] = lines[-1][:-2] + " ."
    return "\n".join(lines) + "\n"


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
            "taxonomy_skos": {name: f"taxonomy/{name}.ttl" for name in taxonomies},
            "schema": "schema/asset.schema.json",
            "pointer_schema": "schema/pointer.schema.json",
            "register_json": "../../data/register.json",
            "register_csv": "../../data/register.csv",
            "metadata": "metadata.json",
        },
        "notice": "Version 0: may change without notice. Use record ids, not URLs, as identifiers. "
                  "Every record has record_status, so demonstration and example records can be excluded.",
    })  # fmt: skip
    out[API + "assets.json"] = dumps({"generated": generated, "assets": records})
    for record in records:
        out[f"{API}assets/{record['id']}.json"] = dumps(record)
    for name, taxonomy in taxonomies.items():
        out[f"{API}taxonomy/{name}.json"] = dumps(taxonomy_json(taxonomy))
        out[f"{API}taxonomy/{name}.ttl"] = taxonomy_skos(taxonomy, config)
    for name in ("asset", "pointer", "taxonomy"):
        out[f"{API}schema/{name}.schema.json"] = dumps(load_schema(name))
    out["data/register.json"] = dumps({"generated": generated, "licence": LICENCE,
                                       "metadata": "../api/v0/metadata.json", "assets": records})  # fmt: skip
    out["data/register.csv"] = to_csv(records)
    sizes = {path: len(content.encode("utf-8")) for path, content in out.items()}
    out[API + "metadata.json"] = dumps(metadata(register, config, today, sizes))
    return out
