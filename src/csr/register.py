"""The register as the site sees it: every record with its derived fields (specification 6.4).

Owner-hosted records whose source is a file in this repository's default
branch are read from the working tree, so the build needs no network. Other
sources are fetched by the harvester (slice S11); until then they are not
published.
"""

from __future__ import annotations

import datetime as dt
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from csr.config import Config
from csr.findings import Finding, has_errors
from csr.records import Record, read_file, read_register
from csr.rules import Context
from csr.taxonomy import load_all
from csr.validate import check_record


@dataclass
class Entry:
    """One record in the register, ready to publish."""

    id: str
    data: dict[str, Any]
    file: str  # the record's file in records/
    text: str  # the descriptor as YAML, for "Download solution.yml"
    hosting: str = "local"  # local | owner-hosted
    source: str | None = None
    last_changed: dt.date | None = None
    merged_in: int | None = None
    history_url: str = ""
    currency: str | None = None  # current | due | stale | unconfirmed; None for withdrawn
    next_due: dt.date | None = None
    stale_from: dt.date | None = None

    @property
    def withdrawn(self) -> bool:
        return self.data.get("record_status") == "withdrawn"


@dataclass
class Unpublished:
    """A pointer whose source could not be published, with the reason."""

    id: str
    source: str
    reason: str
    findings: list[Finding] = field(default_factory=list)


@dataclass
class Register:
    entries: list[Entry]
    unpublished: list[Unpublished]

    def get(self, record_id: str) -> Entry | None:
        return next((e for e in self.entries if e.id == record_id), None)


def add_months(date: dt.date, months: int) -> dt.date:
    month = date.month - 1 + months
    year, month = date.year + month // 12, month % 12 + 1
    days = [31, 29 if year % 4 == 0 and (year % 100 or year % 400 == 0) else 28, 31, 30, 31, 30,
            31, 31, 30, 31, 30, 31]  # fmt: skip
    return dt.date(year, month, min(date.day, days[month - 1]))


def currency(data: dict[str, Any], today: dt.date, config: Config) -> tuple[str | None, dt.date | None]:
    """The record's currency state and the date its next confirmation is due."""
    status = data.get("record_status")
    if status == "withdrawn":
        return None, None
    if status == "demonstration":
        return "unconfirmed", None
    confirmed = dt.date.fromisoformat(data["confirmation"]["last_confirmed"])
    due = add_months(confirmed, config.due_after_months)
    if today >= add_months(confirmed, config.stale_after_months):
        return "stale", due
    if today >= due:
        return "due", due
    return "current", due


def _git_last_change(root: Path, path: str) -> tuple[dt.date | None, int | None]:
    """The date of the last commit to a file, and the pull request it was merged in."""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "log", "-1", "--format=%cs%x09%s", "--", path],
            capture_output=True, text=True, check=True,
        ).stdout.strip()  # fmt: skip
    except (OSError, subprocess.CalledProcessError):
        return None, None
    if not out:
        return None, None
    date, _, subject = out.partition("\t")
    match = re.search(r"\(#(\d+)\)\s*$", subject)
    return dt.date.fromisoformat(date), int(match.group(1)) if match else None


def load_register(root: Path, config: Config, today: dt.date) -> Register:
    """Read every record, resolve pointers to files in this repository, and derive fields."""
    records, _ = read_register(root / "records", root=root)
    known = frozenset(r.id for r in records if r.id)
    context = Context(taxonomies=load_all(), today=today, known_ids=known)
    entries: list[Entry] = []
    unpublished: list[Unpublished] = []
    for record in records:
        if record.data is None or not record.id:
            continue
        if record.is_pointer:
            source = record.data["source"]
            hosted = _local_source(root, source, config)
            if hosted is None:
                unpublished.append(Unpublished(record.id, source, "Not yet harvested"))
                continue
            findings = check_record(hosted, context)
            problem = _owner_mismatch(record, hosted)
            if problem or has_errors(findings) or hosted.data is None:
                unpublished.append(Unpublished(record.id, source, problem or "Fails validation", findings))
                continue
            entry = _entry(root, record, hosted, config, today)
            entry.hosting, entry.source = "owner-hosted", source
        else:
            if has_errors(check_record(record, context)):
                continue  # csr validate reports it; the build publishes only valid records
            entry = _entry(root, record, record, config, today)
        entries.append(entry)
    entries.sort(key=lambda e: e.data["name"].casefold())
    return Register(entries, unpublished)


def _local_source(root: Path, source: str, config: Config) -> Record | None:
    if not source.startswith(config.raw_prefix):
        return None
    path = root / source.removeprefix(config.raw_prefix)
    return read_file(path, root=root) if path.is_file() else None


def _owner_mismatch(pointer: Record, hosted: Record) -> str | None:
    """R14: the harvested id and owner must match the pointer."""
    if not isinstance(hosted.data, dict):
        return None
    owner = hosted.data.get("owner", {}).get("organisation") if isinstance(hosted.data.get("owner"), dict) else None
    if hosted.data.get("id") != pointer.id or owner != pointer.data.get("expected_owner"):
        return "Source does not match the pointer's id and expected owner"
    return None


def _entry(root: Path, record: Record, descriptor: Record, config: Config, today: dt.date) -> Entry:
    text = (root / descriptor.label).read_text(encoding="utf-8")
    last_changed, _ = _git_last_change(root, descriptor.label)
    _, merged_in = _git_last_change(root, record.label)  # for a pointer: the pull request that registered it
    as_of = config.examples_as_of if record.id >= "csr-9000" and config.examples_as_of else today
    state, next_due = currency(descriptor.data, as_of, config)
    confirmed = descriptor.data.get("confirmation", {}).get("last_confirmed")
    stale_from = add_months(dt.date.fromisoformat(confirmed), config.stale_after_months) if confirmed else None
    return Entry(
        id=record.id,
        data=descriptor.data,
        file=record.label,
        text=text,
        last_changed=last_changed,
        merged_in=merged_in,
        history_url=f"{config.repository_url}/commits/{config.default_branch}/{record.label}",
        currency=state,
        next_due=next_due,
        stale_from=stale_from,
    )
