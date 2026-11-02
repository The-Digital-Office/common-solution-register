"""``csr validate``: check records against the schema and the rules in appendix C."""

from __future__ import annotations

import datetime as dt
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from csr import links
from csr.findings import Finding, error, has_errors
from csr.records import RECORD_FILE, Record, parse, read_file, read_register, read_url
from csr.rules import POINTER_RULES, RECORD_RULES, Context
from csr.schema import ROOT, check
from csr.taxonomy import load_all


RECORD_ID = re.compile(r"csr-[0-9]{4}")


class BaseError(RuntimeError):
    """The base branch given with ``--base`` cannot be read."""


@dataclass
class Result:
    """The outcome of a validation run."""

    checked: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not has_errors(self.findings)

    def count(self, severity: str) -> int:
        return sum(1 for f in self.findings if f.severity == severity)


def check_record(record: Record, context: Context) -> list[Finding]:
    """Check one record: its schema, then the rules. Returns all findings, including read errors."""
    findings = list(record.findings)
    if record.data is None:
        return findings
    schema = "pointer" if record.is_pointer else "asset"
    findings += [
        error(record.label, "SCHEMA", e.path, e.message, _schema_fix(schema)) for e in check(record.data, schema)
    ]
    if record.in_register and record.id and record.filename and record.filename != f"{record.id}.yaml":
        findings.append(error(record.label, "R01", "id", f"id {record.id} does not match the file name",
                              f"Rename the file {record.id}.yaml, or correct the id."))  # fmt: skip
    for rule in POINTER_RULES if record.is_pointer else RECORD_RULES:
        findings += rule(record, context)
    return findings


def _schema_fix(schema: str) -> str:
    page = "schema/pointer.schema.json" if schema == "pointer" else "the field reference"
    return f"See {page} for the allowed values."


def _duplicates(records: list[Record]) -> list[Finding]:
    """R01: ids are unique within the register."""
    first: dict[str, Record] = {}
    findings = []
    for record in records:
        if not record.id:
            continue
        if record.id in first:
            findings.append(error(record.label, "R01", "id", f"id {record.id} is also used by {first[record.id].label}",
                                  "Give each record its own id."))  # fmt: skip
        else:
            first[record.id] = record
    return findings


def _git(root: Path, *args: str) -> str:
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        raise BaseError(f"git {' '.join(args)} failed: {detail.strip()}") from exc


def base_ids(root: Path, base: str) -> tuple[dict[str, str], set[str]]:
    """Read the base branch: the ids its records use (id to path), and the
    record paths at the merge base, so records added since can be found."""
    merge_base = _git(root, "merge-base", base, "HEAD").strip()
    ids: dict[str, str] = {}
    for path in _git(root, "ls-tree", "-r", "--name-only", base, "--", "records/").splitlines():
        if not RECORD_FILE.match(Path(path).name):
            continue
        record = parse(_git(root, "show", f"{base}:{path}"), path)
        ids[record.id or Path(path).stem] = path
    existing = set(_git(root, "ls-tree", "-r", "--name-only", merge_base, "--", "records/").splitlines())
    return ids, existing


def _against_base(records: list[Record], root: Path, base: str) -> list[Finding]:
    """R01 with --base: a record added on this branch must not take an id
    that the base branch has since used."""
    ids, existing = base_ids(root, base)
    used = {int(i[4:]) for i in [*ids, *(r.id or "" for r in records)] if RECORD_ID.fullmatch(i)}
    findings = []
    for record in records:
        if record.label in existing or not record.id or record.id not in ids:
            continue
        number = int(record.id[4:])
        span = range(9000, 10000) if number >= 9000 else range(1, 9000)
        free = next((n for n in span if n > max(used & set(span), default=0)), None)
        fix = f"Use the next free id, csr-{free:04d}." if free else "Choose an unused id."
        findings.append(error(record.label, "R01", "id", f"id {record.id} is already used on {base} by {ids[record.id]}",
                              fix))  # fmt: skip
    return findings


def validate(
    targets: list[str] | None = None,
    *,
    root: Path | None = None,
    base: str | None = None,
    check_links: bool = False,
    today: dt.date | None = None,
    fetch: links.Fetch = links.fetch,
) -> Result:
    """Validate the register, or the given files and HTTPS URLs.

    With no targets, checks every record in ``records/`` and the repository's
    own ``solution.yml``. Records in ``records/`` are also checked against
    each other (R01, R05) and, with ``base``, against the base branch.
    """
    root = root or ROOT
    result = Result()
    register, findings = read_register(root / "records", root=root)
    result.findings += findings
    known_ids = frozenset(r.id for r in register if r.id) if register else None
    context = Context(taxonomies=load_all(), today=today or dt.date.today(), known_ids=known_ids)

    if targets:
        records = [read_url(t) if t.startswith(("https://", "http://")) else _read_target(Path(t), root) for t in targets]
    else:
        records = list(register)
        if (root / "solution.yml").is_file():
            records.append(read_file(root / "solution.yml", root=root))

    for record in records:
        result.checked.append(record.label)
        result.findings += check_record(record, context)
        if check_links and record.data is not None:
            result.findings += links.check_links(record, fetch)

    if not targets:
        result.findings += _duplicates(register)
        if base:
            result.findings += _against_base(register, root, base)
    result.findings.sort(key=lambda f: (f.file, f.rule, f.path, f.message))
    return result


def _read_target(path: Path, root: Path) -> Record:
    resolved = path if path.is_absolute() else Path.cwd() / path
    try:
        in_register = resolved.resolve().parent == (root / "records").resolve()
    except OSError:
        in_register = False
    return read_file(resolved, in_register=in_register, root=root)
