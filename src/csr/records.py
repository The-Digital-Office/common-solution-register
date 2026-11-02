"""Reading records: local records, pointer records and standalone solution.yml files."""

from __future__ import annotations

import re
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from csr.findings import Finding, error
from csr.schema import ROOT, is_pointer, load_yaml

RECORDS_DIR = ROOT / "records"
RECORD_FILE = re.compile(r"^csr-[0-9]{4}\.yaml$")
MAX_REMOTE_BYTES = 1_000_000
REMOTE_TIMEOUT = 15


@dataclass
class Record:
    """A YAML document read from a file or URL.

    ``in_register`` is true for files in ``records/``, whose names must match
    their ``id`` (R01). ``data`` is ``None`` if the file could not be read.
    """

    label: str
    data: Any
    in_register: bool = False
    filename: str = ""
    findings: list[Finding] = field(default_factory=list)

    @property
    def is_pointer(self) -> bool:
        return is_pointer(self.data)

    @property
    def id(self) -> str | None:
        value = self.data.get("id") if isinstance(self.data, dict) else None
        return value if isinstance(value, str) else None

    @property
    def record_status(self) -> str | None:
        return self.data.get("record_status") if isinstance(self.data, dict) else None


def parse(text: str, label: str, *, in_register: bool = False, filename: str = "") -> Record:
    """Parse YAML text into a record, recording any YAML error as a finding."""
    record = Record(label=label, data=None, in_register=in_register, filename=filename)
    try:
        data = load_yaml(text)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f" (line {mark.line + 1})" if mark else ""
        problem = getattr(exc, "problem", None) or str(exc)
        record.findings.append(
            error(label, "YAML", "", f"cannot be read as YAML{where}: {problem}", "Correct the YAML syntax.")
        )
        return record
    if not isinstance(data, dict):
        record.findings.append(
            error(label, "YAML", "", "is not a YAML mapping of field names to values",
                  "Start the file with fields such as schema_version: \"0.1\".")
        )  # fmt: skip
        return record
    record.data = data
    return record


def read_file(path: Path, *, in_register: bool = False, root: Path | None = None) -> Record:
    """Read one file. Labels are relative to ``root`` (the working directory by default)."""
    base = root or Path.cwd()
    try:
        label = str(path.resolve().relative_to(base.resolve()))
    except ValueError:
        label = str(path)
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        record = Record(label=label, data=None, in_register=in_register, filename=path.name)
        record.findings.append(error(label, "YAML", "", f"cannot be read: {exc}"))
        return record
    return parse(text, label, in_register=in_register, filename=path.name)


def read_url(url: str) -> Record:
    """Fetch a solution.yml over HTTPS, with a size limit and a timeout."""
    record = Record(label=url, data=None)
    if not url.startswith("https://"):
        record.findings.append(error(url, "R18", "", "is not an HTTPS URL", "Use an https:// address."))
        return record
    request = urllib.request.Request(url, headers={"User-Agent": "csr-validate"})
    try:
        with urllib.request.urlopen(request, timeout=REMOTE_TIMEOUT) as response:  # noqa: S310 - HTTPS only
            if not response.geturl().startswith("https://"):
                raise OSError("redirected to an address that is not HTTPS")
            body = response.read(MAX_REMOTE_BYTES + 1)
    except OSError as exc:
        record.findings.append(error(url, "YAML", "", f"cannot be fetched: {exc}"))
        return record
    if len(body) > MAX_REMOTE_BYTES:
        record.findings.append(error(url, "YAML", "", f"is larger than {MAX_REMOTE_BYTES:,} bytes"))
        return record
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        record.findings.append(error(url, "YAML", "", "is not UTF-8 text"))
        return record
    return parse(text, url)


def read_register(directory: Path = RECORDS_DIR, root: Path | None = None) -> tuple[list[Record], list[Finding]]:
    """Read every file in ``records/``. Files not named ``csr-NNNN.yaml`` are reported (R01)."""
    records: list[Record] = []
    findings: list[Finding] = []
    if not directory.is_dir():
        return records, findings
    for path in sorted(p for p in directory.iterdir() if p.is_file()):
        if path.name.startswith("."):
            continue
        record = read_file(path, in_register=True, root=root)
        if not RECORD_FILE.match(path.name):
            findings.append(
                error(record.label, "R01", "", "records must be named csr-NNNN.yaml",
                      "Rename the file to its id followed by .yaml, for example csr-0042.yaml.")
            )  # fmt: skip
            continue
        records.append(record)
    return records, findings
