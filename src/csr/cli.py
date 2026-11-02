"""The ``csr`` command-line tool.

Commands are added slice by slice (see ``docs/build/PLAN.md``): ``validate``
in S3, ``build`` in S5, ``harvest`` in S11 and the record tools in S12.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections.abc import Sequence

from csr import __version__
from csr.findings import Finding
from csr.validate import BaseError, Result, validate


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser for the ``csr`` command."""
    parser = argparse.ArgumentParser(
        prog="csr",
        description="Validate, harvest and publish the Common Solution Register Demonstrator.",
    )
    parser.add_argument("--version", action="version", version=f"csr {__version__}")
    commands = parser.add_subparsers(dest="command", metavar="command")

    check = commands.add_parser(
        "validate",
        help="check records against the schema and validation rules",
        description="Check records against the schema and the validation rules (schema/README.md). "
        "With no targets, checks every record in records/ and the repository's solution.yml.",
    )
    check.add_argument("targets", nargs="*", metavar="path-or-url", help="files or HTTPS URLs to check instead")
    check.add_argument("--base", metavar="REF", help="also check new records' ids against this git ref (R01)")
    check.add_argument(
        "--check-links", action="store_true", help="check that URLs respond, and compare linked publiccode.yml (R08, R19)"
    )
    check.add_argument("--format", choices=("text", "json", "github"), default="text", help="output format")
    check.add_argument("--today", type=dt.date.fromisoformat, help=argparse.SUPPRESS)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ``csr`` command and return its exit status."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "validate":
        return _validate(args)
    return 0  # pragma: no cover - argparse rejects unknown commands


def _validate(args: argparse.Namespace) -> int:
    try:
        result = validate(args.targets, base=args.base, check_links=args.check_links, today=args.today)
    except BaseError as exc:
        print(f"csr validate: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps({"ok": result.ok, "checked": result.checked,
                          "findings": [f.as_dict() for f in result.findings]}, indent=2))  # fmt: skip
    else:
        for finding in result.findings:
            print(_github(finding) if args.format == "github" else str(finding))
            if args.format == "text" and finding.fix:
                print(f"    Fix: {finding.fix}")
        print(_summary(result))
    return 0 if result.ok else 1


def _github(finding: Finding) -> str:
    message = f"{finding.path}: {finding.message}" if finding.path else finding.message
    message = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    return f"::{finding.severity} file={finding.file},title={finding.rule}::{message}"


def _summary(result: Result) -> str:
    files = len(result.checked)
    errors, warnings = result.count("error"), result.count("warning")
    plural = lambda n, word: f"{n} {word}{'' if n == 1 else 's'}"  # noqa: E731
    return f"Checked {plural(files, 'file')}: {plural(errors, 'error')}, {plural(warnings, 'warning')}."
