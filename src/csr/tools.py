"""Maintainer tools (specification 6.6, 6.12 and appendix A).

- ``import-publiccode``: add or update a codebase in a record from a publiccode.yml, or draft a new record.
- ``move-to-source``: replace a local record with a pointer to the owner's hosted solution.yml.
- ``move-to-local``: replace a pointer with the last valid harvested version, as a local record.
- ``new --from-issue``: turn a suggest-asset issue into a new record with the next free id.

Each writes a file under records/; the maintainer reviews it and opens a pull request.
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from csr import harvest
from csr.config import Config
from csr.findings import Finding, has_errors
from csr.records import Record, read_file, read_register
from csr.rules import Context
from csr.schema import load_yaml
from csr.taxonomy import load_all
from csr.validate import PLACEHOLDER_ID, check_record

TODO = "TODO"
STATUS_FROM_PUBLICCODE = {
    "concept": "concept", "development": "in-development", "beta": "beta", "stable": "live", "obsolete": "deprecated",
}  # fmt: skip


class ToolError(Exception):
    """A tool cannot do what was asked; the message says why."""


@dataclass
class Outcome:
    """What a tool wrote, what it suggests, and what validation says about the result."""

    path: Path
    messages: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not has_errors(self.findings)


# Shared helpers


class _Dumper(yaml.SafeDumper):
    """Block style, two-space list indentation under keys, as the hand-written records use."""

    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def dump(data: dict[str, Any]) -> str:
    return yaml.dump(data, Dumper=_Dumper, sort_keys=False, allow_unicode=True, width=100, default_flow_style=False)


def register_ids(root: Path) -> set[str]:
    records, _ = read_register(root / "records", root=root)
    return {r.id for r in records if r.id}


def next_free_id(ids: set[str], example: bool = False) -> str:
    """The lowest unused id after the highest in use, in the example range or the real one."""
    span = range(9000, 10000) if example else range(1, 9000)
    used = [int(i[4:]) for i in ids if re.fullmatch(r"csr-\d{4}", i) and int(i[4:]) in span]
    number = max(used, default=span.start - 1) + 1
    if number not in span:
        raise ToolError("no free id is left in the range")
    return f"csr-{number:04d}"


def record_path(root: Path, record_id: str) -> Path:
    if not re.fullmatch(r"csr-\d{4}", record_id):
        raise ToolError(f"{record_id!r} is not a record id (csr- followed by four digits)")
    return root / "records" / f"{record_id}.yaml"


def _validate(root: Path, path: Path, today: dt.date) -> list[Finding]:
    ids = register_ids(root)
    context = Context(taxonomies=load_all(), today=today, known_ids=frozenset(ids))
    return check_record(read_file(path, in_register=True, root=root), context)


def _write(root: Path, path: Path, data: dict[str, Any], header: str, today: dt.date, messages: list[str]) -> Outcome:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(header + dump(data), encoding="utf-8", newline="\n")
    return Outcome(path, messages, _validate(root, path, today))


# import-publiccode (appendix A)


def read_publiccode(location: str, root: Path, config: Config, fetcher) -> tuple[dict[str, Any], str | None]:
    """The publiccode.yml at a URL or path, and its URL (None for a local file)."""
    if location.startswith(("https://", "http://")):
        fetched = harvest.get_source(location, root, config, fetcher)
        if fetched.body is None:
            raise ToolError(f"{location}: {fetched.problem}")
        text, url = fetched.body.decode("utf-8"), location
    else:
        path = Path(location)
        if not path.is_file():
            raise ToolError(f"{location}: no such file")
        text, url = path.read_text(encoding="utf-8"), None
    data = load_yaml(text)
    if not isinstance(data, dict) or "publiccodeYmlVersion" not in data:
        raise ToolError(f"{location} is not a publiccode.yml (it has no publiccodeYmlVersion)")
    return data, url


def codebase_from_publiccode(pc: dict[str, Any], publiccode_url: str | None) -> dict[str, Any]:
    """A codebases[] entry: url, maintenance.type, softwareVersion and maintenance.contacts are copied."""
    maintenance = pc.get("maintenance") if isinstance(pc.get("maintenance"), dict) else {}
    entry: dict[str, Any] = {"repository_url": pc.get("url"), "visibility": "public"}
    if publiccode_url:
        entry["publiccode_url"] = publiccode_url
    entry["maintenance"] = maintenance.get("type", TODO)
    if pc.get("softwareVersion"):
        entry["version"] = str(pc["softwareVersion"])
    entry["kind"] = "implementation"
    contacts = [c for c in maintenance.get("contacts") or [] if isinstance(c, dict) and c.get("name")]
    if contacts:
        # Name, affiliation and email; the phone number is not imported.
        entry["maintainers"] = [{k: c[k] for k in ("name", "affiliation", "email") if c.get(k)} for c in contacts]
    return {k: v for k, v in entry.items() if v is not None}


def _same_repository(a: str | None, b: str | None) -> bool:
    norm = lambda u: (u or "").lower().rstrip("/").removesuffix(".git")  # noqa: E731
    return bool(a) and norm(a) == norm(b)


def _hints(pc: dict[str, Any]) -> list[str]:
    hints = []
    if pc.get("categories"):
        hints.append("publiccode.yml categories, as hints for capabilities: " + ", ".join(map(str, pc["categories"])))
    scope = (pc.get("intendedAudience") or {}).get("scope") if isinstance(pc.get("intendedAudience"), dict) else None
    if scope:
        hints.append("publiccode.yml intendedAudience.scope, as hints for service areas: " + ", ".join(map(str, scope)))
    return hints


def import_to(root: Path, config: Config, location: str, record_id: str, *, fetcher=None,
              today: dt.date | None = None) -> Outcome:  # fmt: skip
    """Add the codebase a publiccode.yml describes to a local record, or update it if it is listed."""
    today = today or dt.date.today()
    path = record_path(root, record_id)
    if not path.is_file():
        raise ToolError(f"{record_id} is not in records/")
    data = load_yaml(path.read_text(encoding="utf-8"))
    if "source" in data and "schema_version" not in data:
        raise ToolError(f"{record_id} is owner-hosted: its owner updates its codebases in their own solution.yml")
    pc, url = read_publiccode(location, root, config, fetcher)
    entry = codebase_from_publiccode(pc, url)
    codebases = data.setdefault("codebases", [])
    for existing in codebases:
        if _same_repository(existing.get("repository_url"), entry.get("repository_url")):
            existing.update({k: v for k, v in entry.items() if k != "kind" or "kind" not in existing})
            message = f"Updated the codebase {entry.get('repository_url')} in {record_id}."
            break
    else:
        codebases.append(entry)
        message = f"Added the codebase {entry.get('repository_url')} to {record_id}."
    owner = (pc.get("organisation") or {}).get("name") or (pc.get("legal") or {}).get("mainCopyrightOwner")
    messages = [message]
    if owner and owner != data.get("owner", {}).get("organisation"):
        messages.append(f"Check: publiccode.yml names {owner!r} as owner, but the record's owner is "
                        f"{data.get('owner', {}).get('organisation')!r}.")  # fmt: skip
    header = _leading_comments(path)
    return _write(root, path, data, header, today, messages + _hints(pc))


def import_new(root: Path, config: Config, location: str, *, fetcher=None, today: dt.date | None = None,
               record_id: str | None = None) -> Outcome:  # fmt: skip
    """Draft a new record from a publiccode.yml. Solution fields are only suggested; anything
    unmapped is TODO, which validation rejects until someone fills it in."""
    today = today or dt.date.today()
    pc, url = read_publiccode(location, root, config, fetcher)
    record_id = record_id or next_free_id(register_ids(root))
    path = record_path(root, record_id)
    if path.exists():
        raise ToolError(f"records/{record_id}.yaml already exists")
    description = {}
    if isinstance(pc.get("description"), dict):
        description = pc["description"].get("en") or next(iter(pc["description"].values()), {}) or {}
    legal = pc.get("legal") if isinstance(pc.get("legal"), dict) else {}
    owner = (pc.get("organisation") or {}).get("name") if isinstance(pc.get("organisation"), dict) else None
    data: dict[str, Any] = {
        "schema_version": "0.1",
        "id": record_id,
        "record_status": "owner-confirmed",
        "name": pc.get("name") or TODO,
        "summary": (description.get("shortDescription") or TODO).strip(),
        "purpose": _shorten((description.get("longDescription") or TODO).strip(), 2000),
        "asset_type": "software",
        "owner": {"organisation": owner or legal.get("mainCopyrightOwner") or TODO, "sector": TODO},
        "contact": {"type": "role-mailbox", "value": TODO},  # never derived from maintainers: must be role-based
        "service_areas": [TODO],
        "capabilities": [TODO],
        "status": STATUS_FROM_PUBLICCODE.get(str(pc.get("developmentStatus")), TODO),
        "intended_adopters": [TODO],
        "terms_of_use": {"type": "open-licence", "licence": legal.get("license") or TODO},
        "adoption_route": {"summary": TODO},
        "charging": {"applies": False},
    }
    if pc.get("landingURL"):
        data["service_page_url"] = pc["landingURL"]
    if description.get("documentation"):
        data["documentation_url"] = description["documentation"]
    data["confirmation"] = {"last_confirmed": TODO, "method": TODO, "reference": TODO}
    if description.get("apiDocumentation"):
        data["interfaces"] = [{"type": TODO, "documentation_url": description["apiDocumentation"]}]
    data["codebases"] = [codebase_from_publiccode(pc, url)]
    if pc.get("roadmap"):
        data["roadmap_url"] = pc["roadmap"]
    depends = pc.get("dependsOn") if isinstance(pc.get("dependsOn"), dict) else {}
    names = [d.get("name") for group in depends.values() if isinstance(group, list) for d in group if isinstance(d, dict)]
    if names:
        data["dependencies"] = sorted({n for n in names if n})
    if pc.get("usedBy"):
        data["adopters"] = [{"organisation": str(o), "evidence": "self-reported"} for o in pc["usedBy"]]
    header = (f"# Drafted with csr import-publiccode from {location} on {today.isoformat()}.\n"
              "# The solution fields are suggestions from the codebase's description: check each one.\n"
              "# Replace every TODO; validation rejects the record until they are gone.\n")  # fmt: skip
    return _write(root, path, data, header, today, [f"Drafted {path.relative_to(root).as_posix()}."] + _hints(pc))


def _shorten(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rsplit(" ", 1)[0] + "…"


def _leading_comments(path: Path) -> str:
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines(keepends=True):
        if not line.startswith("#"):
            break
        lines.append(line)
    return "".join(lines)


# move-to-source and move-to-local (specification 6.12)


def move_to_source(root: Path, config: Config, record_id: str, url: str, *, fetcher=None,
                   today: dt.date | None = None) -> Outcome:  # fmt: skip
    """Replace a local record with a pointer to the owner's solution.yml, after fetching
    and checking that file as the harvester will: HTTPS, owner match, status, validation."""
    today = today or dt.date.today()
    path = record_path(root, record_id)
    if not path.is_file():
        raise ToolError(f"{record_id} is not in records/")
    local = load_yaml(path.read_text(encoding="utf-8"))
    if "source" in local and "schema_version" not in local:
        raise ToolError(f"{record_id} is already owner-hosted, at {local['source']}")
    if not url.startswith("https://"):
        raise ToolError("the owner's solution.yml must be at an HTTPS address")
    owner = (local.get("owner") or {}).get("organisation")
    pointer = Record(f"records/{record_id}.yaml", {"id": record_id, "source": url, "expected_owner": owner},
                     in_register=True, filename=path.name)  # fmt: skip
    ids = register_ids(root)
    context = Context(taxonomies=load_all(), today=today, known_ids=frozenset(ids))
    result = harvest.harvest_source(pointer, root, config, context, fetcher)
    if result.state != "ok":
        problems = "; ".join(f"{f.rule} {f.path}: {f.message}".replace(" :", ":") for f in result.findings if f.severity == "error")
        raise ToolError(f"the owner's file cannot be registered yet ({result.state}): {problems or 'not fetched'}")
    header = (f"# Owner-hosted record: the full descriptor is the owner's own solution.yml.\n"
              f"# Moved from a local record with csr move-to-source on {today.isoformat()}.\n")  # fmt: skip
    path.write_text(header + dump(pointer.data), encoding="utf-8", newline="\n")
    findings = check_record(read_file(path, in_register=True, root=root), context)
    return Outcome(path, [f"{record_id} now points to {url}; the next harvest publishes the owner's file."], findings)


def move_to_local(root: Path, config: Config, record_id: str, state: dict, *, today: dt.date | None = None) -> Outcome:
    """Replace a pointer with the last valid version from the harvest state, as a local record."""
    today = today or dt.date.today()
    path = record_path(root, record_id)
    if not path.is_file():
        raise ToolError(f"{record_id} is not in records/")
    pointer = load_yaml(path.read_text(encoding="utf-8"))
    if not ("source" in pointer and "schema_version" not in pointer):
        raise ToolError(f"{record_id} is already a local record")
    entry = state.get("sources", {}).get(record_id) or {}
    if not entry.get("last_valid"):
        raise ToolError(f"the harvest state has no valid version of {record_id} to keep")
    if entry.get("source") != pointer["source"]:
        raise ToolError(f"the harvest state is for {entry.get('source')}, not the registered {pointer['source']}")
    when = entry.get("harvested_at", "")[:10]
    header = (f"# Moved from owner hosting with csr move-to-local on {today.isoformat()}: the last valid version,\n"
              f"# harvested from {pointer['source']} on {when}.\n")  # fmt: skip
    path.write_text(header + entry["last_valid"].lstrip("﻿"), encoding="utf-8", newline="\n")
    return Outcome(path, [f"{record_id} is now a local record, from the version harvested on {when}."],
                   _validate(root, path, today))  # fmt: skip


# new --from-issue


FENCE = re.compile(r"```(?:ya?ml)?[ \t]*\n(.*?)\n```", re.S)


def yaml_from_issue(body: str) -> str:
    """The solution.yml in a suggest-asset issue: the YAML text area renders as a fenced block."""
    blocks = FENCE.findall(body.replace("\r\n", "\n"))
    for block in blocks:
        try:
            data = load_yaml(block)
        except yaml.YAMLError:
            continue
        if isinstance(data, dict) and "schema_version" in data:
            return block + "\n"
    raise ToolError("the issue has no solution.yml in a YAML block")


def new_from_issue(root: Path, body: str, *, issue_url: str | None = None, today: dt.date | None = None,
                   record_id: str | None = None) -> Outcome:  # fmt: skip
    """Write the solution.yml from a suggest-asset issue as a new record, with the next free id."""
    today = today or dt.date.today()
    text = yaml_from_issue(body)
    data = load_yaml(text)
    example = data.get("record_status") == "example"
    current = data.get("id")
    if record_id is None:
        if current and current != PLACEHOLDER_ID and current in register_ids(root):
            raise ToolError(f"the issue's record says id {current}, which is already in the register: "
                            "use suggest-correction for changes to an existing record")  # fmt: skip
        record_id = next_free_id(register_ids(root), example=example)
    path = record_path(root, record_id)
    if path.exists():
        raise ToolError(f"records/{record_id}.yaml already exists")
    data["id"] = record_id
    confirmation = data.get("confirmation")
    if issue_url and isinstance(confirmation, dict) and confirmation.get("reference") in (None, "", "Submitted with the draft form"):
        confirmation["reference"] = issue_url
    header = f"# From {issue_url or 'a suggest-asset issue'}, added with csr new --from-issue on {today.isoformat()}.\n"
    messages = [f"Wrote {path.relative_to(root).as_posix()}."]
    if data.get("record_status") == "demonstration":
        messages.append("This is a demonstration entry: check every statement against its sources before merging.")
    elif data.get("record_status") == "owner-confirmed":
        messages.append("Check the submitter is from the owning organisation before merging (inclusion test 2).")
    return _write(root, path, data, header, today, messages)
