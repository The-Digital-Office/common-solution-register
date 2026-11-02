"""Loading the record schemas and checking documents against them."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

#: Repository root: schema/ and taxonomy/ live here.
ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "schema"
SENTINEL = "not-publicly-stated"


class _Loader(yaml.SafeLoader):
    """Safe YAML loader that keeps dates as strings, as JSON Schema expects."""


_Loader.yaml_implicit_resolvers = {
    first: [(tag, regexp) for tag, regexp in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for first, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load_yaml(text: str) -> Any:
    """Parse YAML text safely, leaving dates as ISO strings."""
    return yaml.load(text, Loader=_Loader)  # noqa: S506 - _Loader is a SafeLoader


def load_yaml_file(path: Path) -> Any:
    """Parse a YAML file safely, leaving dates as ISO strings."""
    return load_yaml(path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class SchemaError:
    """One schema validation error, with the location of the failing value."""

    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path or '(record)'}: {self.message}"


@cache
def load_schema(name: str) -> dict[str, Any]:
    """Load ``schema/<name>.schema.json``."""
    return json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))


@cache
def validator(name: str) -> Draft202012Validator:
    """Return a validator for ``schema/<name>.schema.json``, with format checks."""
    schema = load_schema(name)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _path(error) -> str:
    return "".join(f"[{part}]" if isinstance(part, int) else f".{part}" for part in error.absolute_path).lstrip(".")


def check(document: Any, name: str = "asset") -> list[SchemaError]:
    """Validate a document against a schema and return its errors, in path order."""
    errors = validator(name).iter_errors(document)
    return sorted((SchemaError(_path(e), e.message) for e in errors), key=lambda e: (e.path, e.message))


def is_pointer(document: Any) -> bool:
    """A record is a pointer if it has a ``source`` and no ``schema_version``."""
    return isinstance(document, dict) and "source" in document and "schema_version" not in document
