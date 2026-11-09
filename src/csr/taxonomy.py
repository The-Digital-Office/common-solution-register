"""Loading the taxonomy: sectors, service areas and capabilities (specification 6.5)."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cache
from pathlib import Path

from csr.schema import ROOT, check, load_yaml_file

TAXONOMY_DIR = ROOT / "taxonomy"

#: Taxonomy name, and the record fields whose values it supplies.
TAXONOMIES: dict[str, tuple[str, ...]] = {
    "sectors": ("owner.sector", "intended_adopters"),
    "service-areas": ("service_areas",),
    "capabilities": ("capabilities",),
}


@dataclass(frozen=True)
class Term:
    """One taxonomy term."""

    id: str
    label: str
    definition: str
    synonyms: tuple[str, ...] = ()
    status: str = "active"
    replaced_by: str | None = None
    #: An audience for intended_adopters only, never an owning sector (owner.sector).
    intended_adopters_only: bool = False

    @property
    def deprecated(self) -> bool:
        return self.status == "deprecated"


@dataclass(frozen=True)
class Taxonomy:
    """The terms of one taxonomy file, in file order."""

    name: str
    version: str
    terms: tuple[Term, ...] = field(default_factory=tuple)

    def __contains__(self, term_id: object) -> bool:
        return any(term.id == term_id for term in self.terms)

    def get(self, term_id: str) -> Term | None:
        return next((term for term in self.terms if term.id == term_id), None)

    @property
    def ids(self) -> list[str]:
        return [term.id for term in self.terms]


class TaxonomyError(ValueError):
    """A taxonomy file does not match its schema."""


def load_taxonomy(name: str, directory: Path = TAXONOMY_DIR) -> Taxonomy:
    """Load and check ``taxonomy/<name>.yaml``."""
    data = load_yaml_file(directory / f"{name}.yaml")
    errors = check(data, "taxonomy")
    if errors:
        raise TaxonomyError(f"taxonomy/{name}.yaml: " + "; ".join(map(str, errors)))
    terms = tuple(
        Term(
            id=t["id"],
            label=t["label"],
            definition=t["definition"],
            synonyms=tuple(t["synonyms"]),
            status=t["status"],
            replaced_by=t.get("replaced_by"),
            intended_adopters_only=t.get("intended_adopters_only", False),
        )
        for t in data["terms"]
    )
    return Taxonomy(name=data["taxonomy"], version=data["version"], terms=terms)


@cache
def load_all() -> dict[str, Taxonomy]:
    """Load every taxonomy from the repository's ``taxonomy/`` folder."""
    return {name: load_taxonomy(name) for name in TAXONOMIES}
