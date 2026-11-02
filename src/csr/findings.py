"""Validation findings: what a check found, where, and how to fix it."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True, order=True)
class Finding:
    """One problem found in one file.

    ``rule`` is a rule number from appendix C (``R01``), ``SCHEMA`` for a schema
    error or ``YAML`` for a file that cannot be read. ``path`` is the field,
    as a dotted path with list indexes (``codebases[0].repository_url``), or
    empty for the whole record.
    """

    file: str
    rule: str
    severity: Severity
    path: str
    message: str
    fix: str = ""

    def __str__(self) -> str:
        where = f" {self.path}" if self.path else ""
        return f"{self.file}: {self.severity} {self.rule}{where}: {self.message}"

    def as_dict(self) -> dict[str, str]:
        return {k: str(v) for k, v in asdict(self).items()}


def error(file: str, rule: str, path: str, message: str, fix: str = "") -> Finding:
    return Finding(file, rule, Severity.ERROR, path, message, fix)


def warning(file: str, rule: str, path: str, message: str, fix: str = "") -> Finding:
    return Finding(file, rule, Severity.WARNING, path, message, fix)


def has_errors(findings: list[Finding]) -> bool:
    return any(f.severity is Severity.ERROR for f in findings)
