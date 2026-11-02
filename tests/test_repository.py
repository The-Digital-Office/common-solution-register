"""Checks on the repository's own descriptor files."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def test_publiccode_is_complete():
    text = (ROOT / "publiccode.yml").read_text(encoding="utf-8")
    assert "TODO" not in text
    data = yaml.safe_load(text)
    description = data["description"]["en"]
    assert len(description["shortDescription"]) <= 150
    assert 150 <= len(description["longDescription"]) <= 10000
    assert description["features"]
    assert data["softwareType"] == "standalone/web"
    assert data["developmentStatus"] == "development"
