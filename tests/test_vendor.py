"""R13: vendored files match their pinned hashes.

Each vendored package under src/csr/static/vendor/ has a SHA256SUMS file
(``<sha256>  <file>`` per line, as written by ``sha256sum``). Every CSS and
JavaScript file must be listed, and every listed file must match. Vendored
packages arrive in S5 (design system) and S9 (Ajv, js-yaml).
"""

import hashlib
from pathlib import Path

import pytest

VENDOR = Path(__file__).resolve().parents[1] / "src" / "csr" / "static" / "vendor"
MANIFESTS = sorted(VENDOR.rglob("SHA256SUMS")) if VENDOR.is_dir() else []


def _entries(manifest: Path) -> dict[str, str]:
    entries = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, name = line.split(maxsplit=1)
            entries[name.lstrip("*")] = digest
    return entries


@pytest.mark.parametrize("manifest", MANIFESTS, ids=lambda p: str(p.parent.relative_to(VENDOR)))
def test_vendored_files_match_their_hashes(manifest):
    for name, digest in _entries(manifest).items():
        path = manifest.parent / name
        assert path.is_file(), f"{name} is listed but missing"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, f"{name} does not match its pinned hash"


def test_every_vendored_script_and_stylesheet_is_pinned():
    if not VENDOR.is_dir():
        return
    listed = {(m.parent / name).resolve() for m in MANIFESTS for name in _entries(m)}
    unlisted = [p for p in VENDOR.rglob("*") if p.suffix in {".js", ".mjs", ".css"} and p.resolve() not in listed]
    assert unlisted == [], f"vendored files without a pinned hash: {unlisted}"


def test_manifest_format(tmp_path):
    manifest = tmp_path / "SHA256SUMS"
    manifest.write_text("abc  design-system.min.css\ndef *design-system.js\n", encoding="utf-8")
    assert _entries(manifest) == {"design-system.min.css": "abc", "design-system.js": "def"}
