"""The ``csr`` command-line tool.

Commands are added slice by slice (see ``docs/build/PLAN.md``): ``validate``
in S3, ``build`` in S5, ``harvest`` in S11 and the record tools in S12.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from csr import __version__


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser for the ``csr`` command."""
    parser = argparse.ArgumentParser(
        prog="csr",
        description="Validate, harvest and publish the Common Solution Register Demonstrator.",
    )
    parser.add_argument("--version", action="version", version=f"csr {__version__}")
    parser.add_subparsers(dest="command", metavar="command")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ``csr`` command and return its exit status."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
    return 0
