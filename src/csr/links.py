"""Rules that need the network, run only with ``--check-links``: R08 and R19.

They never block a merge, so they only produce warnings.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from collections.abc import Callable
from urllib.parse import urlsplit

import yaml

from csr.findings import Finding, warning
from csr.records import MAX_REMOTE_BYTES, REMOTE_TIMEOUT, Record
from csr.rules import list_items
from csr.schema import load_yaml

#: Fetches a URL and returns (status, body). Status 0 means no response.
Fetch = Callable[[str], tuple[int, bytes]]


def fetch(url: str) -> tuple[int, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": "csr-validate"})
    try:
        with urllib.request.urlopen(request, timeout=REMOTE_TIMEOUT) as response:  # noqa: S310 - HTTPS URLs only
            return response.status, response.read(MAX_REMOTE_BYTES)
    except urllib.error.HTTPError as exc:
        return exc.code, b""
    except (OSError, ValueError):
        return 0, b""


def _normalise(url: str) -> str:
    parts = urlsplit(url.strip())
    path = parts.path.rstrip("/").removesuffix(".git")
    return f"{parts.scheme.lower()}://{parts.netloc.lower()}{path}"


def check_links(record: Record, get: Fetch = fetch) -> list[Finding]:
    """R08: repository, publiccode.yml and source URLs respond.
    R19: a codebase's publiccode.yml agrees with the record."""
    data = record.data
    findings: list[Finding] = []
    urls: list[tuple[str, str]] = []
    if record.is_pointer:
        urls.append(("source", data.get("source")))
    for i, source in list_items(data, "sources"):
        urls.append((f"sources[{i}].url", source.get("url")))
    publiccode: list[tuple[int, dict]] = []
    for i, codebase in list_items(data, "codebases"):
        urls.append((f"codebases[{i}].repository_url", codebase.get("repository_url")))
        if codebase.get("publiccode_url"):
            publiccode.append((i, codebase))

    for path, url in urls:
        if isinstance(url, str) and url.startswith("https://"):
            status, _ = get(url)
            if not 200 <= status < 400:
                findings.append(_no_response(record, path, url, status))

    for i, codebase in publiccode:
        url = codebase["publiccode_url"]
        if not isinstance(url, str) or not url.startswith("https://"):
            continue
        status, body = get(url)
        if not 200 <= status < 400:
            findings.append(_no_response(record, f"codebases[{i}].publiccode_url", url, status))
            continue
        try:
            document = load_yaml(body.decode("utf-8"))
        except (UnicodeDecodeError, yaml.YAMLError):
            document = None
        if not isinstance(document, dict):
            findings.append(warning(record.label, "R19", f"codebases[{i}].publiccode_url",
                                    "publiccode.yml cannot be read as YAML", "Check the file with the official parser."))  # fmt: skip
            continue
        repository = codebase.get("repository_url")
        if isinstance(repository, str) and isinstance(document.get("url"), str):
            if _normalise(document["url"]) != _normalise(repository):
                findings.append(warning(record.label, "R19", f"codebases[{i}].repository_url",
                                        f"publiccode.yml gives url {document['url']}",
                                        "Make repository_url and the publiccode.yml url the same."))  # fmt: skip
        maintenance = document.get("maintenance")
        stated = maintenance.get("type") if isinstance(maintenance, dict) else None
        if stated and stated != codebase.get("maintenance"):
            findings.append(warning(record.label, "R19", f"codebases[{i}].maintenance",
                                    f"publiccode.yml gives maintenance type '{stated}'",
                                    "Make maintenance match publiccode.yml maintenance.type."))  # fmt: skip
    return findings


def _no_response(record: Record, path: str, url: str, status: int) -> Finding:
    detail = f"returned HTTP {status}" if status else "did not respond"
    return warning(record.label, "R08", path, f"{url} {detail}", "Check the address is right and publicly reachable.")
