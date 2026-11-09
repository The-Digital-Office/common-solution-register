"""Site configuration from site.toml."""

from __future__ import annotations

import datetime as dt
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from csr.schema import ROOT


@dataclass(frozen=True)
class Config:
    title: str
    base_url: str
    state_url: str
    repository_url: str
    default_branch: str
    host_organisation: str
    contact_mailbox: str
    feedback_url: str
    due_after_months: int = 11
    stale_after_months: int = 12
    harvest_max_bytes: int = 262144
    harvest_timeout_seconds: int = 10
    examples_as_of: dt.date | None = None
    host_logo: str = ""
    publication: dict[str, str] = field(default_factory=dict)

    @property
    def pending_publication_inputs(self) -> list[str]:
        """Inputs still to be completed before publication (contact mailbox and [publication])."""
        pending = [] if self.contact_mailbox else ["contact_mailbox"]
        return pending + [key for key, value in self.publication.items() if not value]

    @property
    def raw_prefix(self) -> str:
        """URLs under this prefix are files in this repository's default branch."""
        return f"{self.repository_url}/raw/{self.default_branch}/"


def load_config(root: Path | None = None, base_url: str | None = None) -> Config:
    """Read ``site.toml``. ``base_url`` overrides the configured value (for previews)."""
    data = tomllib.loads(((root or ROOT) / "site.toml").read_text(encoding="utf-8"))
    currency = data.get("currency", {})
    harvest = data.get("harvest", {})
    base = base_url or data["base_url"]
    return Config(
        title=data["title"],
        base_url=base if base.endswith("/") else base + "/",
        state_url=data.get("state_url") or f"{base.rstrip('/')}/api/v0/harvest-state.json",
        repository_url=data["repository_url"].rstrip("/"),
        default_branch=data.get("default_branch", "main"),
        host_organisation=data["host_organisation"],
        host_logo=data.get("host_logo", ""),
        contact_mailbox=data.get("contact_mailbox", ""),
        feedback_url=data.get("feedback_url", ""),
        due_after_months=currency.get("due_after_months", 11),
        stale_after_months=currency.get("stale_after_months", 12),
        harvest_max_bytes=harvest.get("max_bytes", 262144),
        harvest_timeout_seconds=harvest.get("timeout_seconds", 10),
        examples_as_of=dt.date.fromisoformat(currency["examples_as_of"]) if currency.get("examples_as_of") else None,
        publication={k: str(v) for k, v in data.get("publication", {}).items()},
    )
