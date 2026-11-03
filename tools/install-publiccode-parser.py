"""Install the official publiccode.yml parser, at a pinned release with verified checksums.

Usage: python tools/install-publiccode-parser.py

Downloads publiccode-parser-go (EUPL-1.2, https://github.com/italia/publiccode-parser-go)
for this platform, checks the archive against the SHA-256 pinned below (taken from the
release's checksums.txt), and installs the binary at .tools/publiccode-parser/VERSION/,
where csr harvest finds it. The binary is not committed to this repository.
"""

from __future__ import annotations

import hashlib
import io
import platform
import stat
import sys
import tarfile
import urllib.request
from pathlib import Path

VERSION = "v5.4.3"  # released 6 August 2026
SHA256 = {
    "Linux_x86_64": "211847305611417ac0b76af5169086232ea6c75ff6ae686227b6972a41599dd7",
    "Linux_arm64": "33363da55ddf38457f6f9081cc8f3b833e833eb3a401d6c9c3feb8e5f2dc3fd7",
    "Darwin_x86_64": "38d6bb4be977a1b0ea723e1c4decece852d3c143d15ba98620956e8617354d1f",
    "Darwin_arm64": "61b3754455bfa5c04fe766d549e8b1d01fe804f7d914c93ee19e3ea28e6a46ae",
}
ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / ".tools" / "publiccode-parser" / VERSION / "publiccode-parser"


def platform_name() -> str:
    machine = {"amd64": "x86_64", "aarch64": "arm64"}.get(platform.machine().lower(), platform.machine().lower())
    return f"{platform.system()}_{machine}"


def main() -> None:
    name = platform_name()
    if name not in SHA256:
        sys.exit(f"No pinned build for {name}: run the harvester on Linux or macOS.")
    if TARGET.exists():
        print(f"Already installed: {TARGET.relative_to(ROOT)}")
        return
    url = f"https://github.com/italia/publiccode-parser-go/releases/download/{VERSION}/publiccode-parser-go_{name}.tar.gz"
    with urllib.request.urlopen(url, timeout=120) as response:  # noqa: S310 - fixed HTTPS release URL
        archive = response.read()
    if hashlib.sha256(archive).hexdigest() != SHA256[name]:
        sys.exit(f"Checksum mismatch for {url}: not installed.")
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        binary = tar.extractfile("publiccode-parser").read()
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(binary)
    TARGET.chmod(TARGET.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"Installed publiccode-parser {VERSION} at {TARGET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
