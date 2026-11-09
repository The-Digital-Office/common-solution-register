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

from csr import __version__, harvest, tools
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
    site.add_argument("--root", type=Path, help="build from the register in this folder (default: this repository)")
    site.add_argument("--no-history", action="store_true",
                      help="leave out dates and pull requests taken from git (for reproducible test builds)")  # fmt: skip

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
    reap.add_argument("--fail-on-problems", action="store_true",
                      help="exit 1 if an owner's source harvested in this run is not ok (for pull requests that "
                           "register one; sources in this repository are checked without it)")  # fmt: skip
    reap.add_argument("--summary", type=Path, metavar="PATH", help="also write the harvest report as Markdown")

    imp = commands.add_parser("import-publiccode", help="add a codebase to a record from a publiccode.yml, or draft a record",
                              description="Import a codebase's publiccode.yml (specification appendix A).")  # fmt: skip
    imp.add_argument("publiccode", metavar="url-or-path", help="the publiccode.yml to import")
    target = imp.add_mutually_exclusive_group(required=True)
    target.add_argument("--to", metavar="ID", help="add or update the codebase in this local record")
    target.add_argument("--new", action="store_true", help="draft a new record from the publiccode.yml")
    imp.add_argument("--id", help="with --new: the id to use (default: the next free id)")

    pcc = commands.add_parser("check-publiccode", help="check a publiccode.yml with the official parser",
                              description="Run the official publiccode.yml parser (installed by "
                              "tools/install-publiccode-parser.py) on a file, without the network.")  # fmt: skip
    pcc.add_argument("path")

    mts = commands.add_parser("move-to-source", help="replace a local record with a pointer to the owner's solution.yml",
                              description="Fetch and check the owner's solution.yml, then replace the local record "
                              "with a pointer to it (specification 6.12).")  # fmt: skip
    mts.add_argument("id")
    mts.add_argument("url", help="the HTTPS address of the owner's solution.yml")

    mtl = commands.add_parser("move-to-local", help="replace a pointer with the last valid harvested version",
                              description="Write the last valid version from the harvest state as a local record.")  # fmt: skip
    mtl.add_argument("id")
    mtl.add_argument("--state", metavar="PATH-OR-URL", help="the harvest state (default: state_url in site.toml)")

    new = commands.add_parser("new", help="add a record from a suggest-asset issue",
                              description="Write the solution.yml in a suggest-asset issue as a new record, "
                              "with the next free id.")  # fmt: skip
    new.add_argument("--from-issue", required=True, metavar="PATH",
                     help="a file with the issue's body, or - to read it from standard input")  # fmt: skip
    new.add_argument("--issue-url", help="the issue's address, recorded as the confirmation reference")
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
    if args.command == "check-publiccode":
        return _check_publiccode(Path(args.path))
    if args.command in ("import-publiccode", "move-to-source", "move-to-local", "new"):
        return _tool(args)
    if args.command == "build":
        state = json.loads(Path(args.harvest).read_text(encoding="utf-8")) if args.harvest else None
        result = build(root=args.root.resolve() if args.root else None, out=args.out, base_url=args.base_url,
                       today=args.date, state=state, history=not args.no_history)  # fmt: skip
        print(f"Built {len(result.pages)} pages into {result.out}.")
        for item in result.register.unpublished:
            print(f"Not published: {item.id} ({item.reason})")
        config = load_config(args.root, base_url=args.base_url)
        if config.preview:
            print("Preview: every page asks search engines not to index it (preview = true in site.toml).")
        pending = config.pending_publication_inputs
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


def _check_publiccode(path: Path) -> int:
    if not path.is_file():
        print(f"csr check-publiccode: {path}: no such file", file=sys.stderr)
        return 2
    found = harvest.run_parser(path)
    if found is None:
        print("csr check-publiccode: the official parser is not installed: run python tools/install-publiccode-parser.py",
              file=sys.stderr)  # fmt: skip
        return 2
    for f in found:
        kind = "error" if f.get("type", "error") == "error" else "warning"
        print(f"::{kind} file={path},line={f.get('line') or 1}::{f.get('key') + ': ' if f.get('key') else ''}{f.get('description', '')}")
    errors = sum(1 for f in found if f.get("type", "error") == "error")
    print(f"{path}: {errors} error{'' if errors == 1 else 's'} from publiccode-parser-go {harvest.PARSER_VERSION}.")
    return 1 if errors else 0


def _tool(args: argparse.Namespace) -> int:
    config = load_config()
    try:
        if args.command == "import-publiccode":
            if args.new:
                outcome = tools.import_new(ROOT, config, args.publiccode, fetcher=harvest.fetch, record_id=args.id)
            else:
                outcome = tools.import_to(ROOT, config, args.publiccode, args.to, fetcher=harvest.fetch)
        elif args.command == "move-to-source":
            outcome = tools.move_to_source(ROOT, config, args.id, args.url, fetcher=harvest.fetch)
        elif args.command == "move-to-local":
            state, note = harvest.read_state(args.state or config.state_url, harvest.fetch, config)
            outcome = tools.move_to_local(ROOT, config, args.id, state)
        else:
            body = sys.stdin.read() if args.from_issue == "-" else Path(args.from_issue).read_text(encoding="utf-8")
            outcome = tools.new_from_issue(ROOT, body, issue_url=args.issue_url)
    except (tools.ToolError, OSError) as exc:
        print(f"csr {args.command}: {exc}", file=sys.stderr)
        return 2
    for message in outcome.messages:
        print(message)
    for finding in outcome.findings:
        print(str(finding))
    errors = sum(1 for f in outcome.findings if f.severity == "error")
    print(f"{outcome.path.relative_to(ROOT).as_posix()}: {errors} error{'' if errors == 1 else 's'} to resolve before merging."
          if errors else f"{outcome.path.relative_to(ROOT).as_posix()} is valid.")  # fmt: skip
    return 0 if outcome.ok else 1


def _harvest(args: argparse.Namespace) -> int:
    config = load_config()
    fetcher = None if args.no_network else harvest.fetch
    previous, note = harvest.read_state(args.state or config.state_url, fetcher, config)
    now = dt.datetime.now(dt.UTC)
    state, results = harvest.run(ROOT, config, previous, now=now, fetcher=fetcher,
                                 only=set(args.only) if args.only else None)  # fmt: skip
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(note[0].upper() + note[1:] + ".")
    for result in results:
        where = " (from this repository)" if result.from_repository else ""
        print(f"{result.id}: {result.state}{where}")
        for finding in result.findings:
            print(f"    {_github(finding) if args.format == 'github' else finding}")
    print(f"Harvest state written to {args.out}.")
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        with args.summary.open("a", encoding="utf-8") as summary:
            summary.write(harvest.markdown_report(state, results))
    # A failing source never stops a scheduled build: its last valid version stays published.
    # For a pull request that registers a source, --fail-on-problems stops the merge.
    problems = [r for r in results if r.state != "ok" and not r.from_repository]  # owners' sources only
    if args.fail_on_problems and problems:
        print("Not ok: " + ", ".join(f"{r.id} ({r.state})" for r in problems), file=sys.stderr)
        return 1
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
