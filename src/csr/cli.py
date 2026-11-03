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

from pathlib import Path

from csr import __version__, harvest
from csr.build import build
from csr.config import load_config
from csr.findings import Finding
from csr.schema import ROOT
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

    site = commands.add_parser(
        "build",
        help="generate the static site",
        description="Generate the static site from the register into site/ (or --out).",
    )
    site.add_argument("--out", type=Path, help="output folder (default: site/ in the repository)")
    site.add_argument("--base-url", help="the address the site will be served from (default: base_url in site.toml)")
    site.add_argument(
        "--date", type=dt.date.fromisoformat, help="build as on this date, for currency (default: today)"
    )
    site.add_argument("--harvest", metavar="PATH", help="the harvest state to publish from (from csr harvest)")

    reap = commands.add_parser(
        "harvest",
        help="fetch and check owner-hosted records",
        description="Fetch each pointer's source, check it, and write the harvest state. Sources in this "
        "repository are read from the working tree.",
    )
    reap.add_argument("--state", metavar="PATH-OR-URL",
                      help="the previous state (default: state_url in site.toml; unreadable means starting fresh)")  # fmt: skip
    reap.add_argument("--out", type=Path, default=Path(".harvest/harvest-state.json"), help="where to write the new state")
    reap.add_argument("--only", nargs="+", metavar="ID", help="harvest only these records, keeping the others' state")
    reap.add_argument("--no-network", action="store_true", help="read only sources in this repository")
    reap.add_argument("--format", choices=("text", "github"), default="text", help="output format")
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
    if args.command == "harvest":
        return _harvest(args)
    if args.command == "build":
        state = json.loads(Path(args.harvest).read_text(encoding="utf-8")) if args.harvest else None
        result = build(out=args.out, base_url=args.base_url, today=args.date, state=state)
        print(f"Built {len(result.pages)} pages into {result.out}.")
        for item in result.register.unpublished:
            print(f"Not published: {item.id} ({item.reason})")
        pending = load_config(base_url=args.base_url).pending_publication_inputs
        if pending:
            print("To be completed before publication (site.toml): " + ", ".join(pending))
        return 0
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


def _harvest(args: argparse.Namespace) -> int:
    config = load_config()
    fetcher = None if args.no_network else harvest.fetch
    previous, note = harvest.read_state(args.state or config.state_url, fetcher, config)
    now = dt.datetime.now(dt.UTC)
    state, results = harvest.run(ROOT, config, previous, now=now, fetcher=fetcher,
                                 only=set(args.only) if args.only else None)  # fmt: skip
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(note[0].upper() + note[1:] + ".")
    for result in results:
        where = " (from this repository)" if result.from_repository else ""
        print(f"{result.id}: {result.state}{where}")
        for finding in result.findings:
            print(f"    {_github(finding) if args.format == 'github' else finding}")
    print(f"Harvest state written to {args.out}.")
    # A failing source never stops the build: its last valid version stays published.
    return 0


def _github(finding: Finding) -> str:
    message = f"{finding.path}: {finding.message}" if finding.path else finding.message
    message = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    return f"::{finding.severity} file={finding.file},title={finding.rule}::{message}"


def _summary(result: Result) -> str:
    files = len(result.checked)
    errors, warnings = result.count("error"), result.count("warning")
    plural = lambda n, word: f"{n} {word}{'' if n == 1 else 's'}"  # noqa: E731
    return f"Checked {plural(files, 'file')}: {plural(errors, 'error')}, {plural(warnings, 'warning')}."
