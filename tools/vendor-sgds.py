"""Vendor the Scottish Government Design System's compiled CSS and JavaScript.

Usage: python tools/vendor-sgds.py VERSION

Downloads @scottish-government/design-system@VERSION from the npm registry,
checks the tarball against the registry's integrity hash, and writes
design-system.min.css, design-system.js and LICENSE.txt to
src/csr/static/vendor/sgds/VERSION/, with SOURCE.md and SHA256SUMS (checked by
the R13 test). No npm install is needed. Graphic assets are not vendored.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import sys
import tarfile
import urllib.request
from pathlib import Path

PACKAGE = "@scottish-government/design-system"
FILES = {
    "package/dist/css/design-system.min.css": "design-system.min.css",
    "package/dist/scripts/design-system.js": "design-system.js",
    "package/LICENSE.txt": "LICENSE.txt",
}
ROOT = Path(__file__).resolve().parents[1]


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as response:  # noqa: S310 - fixed HTTPS registry URL
        return response.read()


def main(version: str) -> None:
    meta = json.loads(fetch(f"https://registry.npmjs.org/{PACKAGE.replace('/', '%2F')}/{version}"))
    tarball_url, integrity = meta["dist"]["tarball"], meta["dist"]["integrity"]
    tarball = fetch(tarball_url)
    algorithm, expected = integrity.split("-", 1)
    actual = base64.b64encode(hashlib.new(algorithm, tarball).digest()).decode()
    if actual != expected:
        sys.exit(f"integrity mismatch for {tarball_url}")

    target = ROOT / "src" / "csr" / "static" / "vendor" / "sgds" / version
    target.mkdir(parents=True, exist_ok=True)
    sums = []
    with tarfile.open(fileobj=io.BytesIO(tarball), mode="r:gz") as archive:
        for member, name in FILES.items():
            data = archive.extractfile(member).read()
            (target / name).write_bytes(data)
            sums.append(f"{hashlib.sha256(data).hexdigest()}  {name}")
    (target / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    (target / "SOURCE.md").write_text(
        f"""# Scottish Government Design System {version}

| | |
|---|---|
| Package | [`{PACKAGE}@{version}`](https://www.npmjs.com/package/{PACKAGE}/v/{version}) |
| Tarball | {tarball_url} |
| npm integrity | `{integrity}` |
| Licence | MIT ([`LICENSE.txt`](LICENSE.txt)) |

Files taken unchanged from the package: `dist/css/design-system.min.css`,
`dist/scripts/design-system.js` and `LICENSE.txt`. Their SHA-256 hashes are in
[`SHA256SUMS`](SHA256SUMS), checked by the R13 test. No graphic assets are
vendored, and no Scottish Government logo or brand asset is used.

Refresh with `python tools/vendor-sgds.py {version}`.
""",
        encoding="utf-8",
    )
    print(f"Vendored {PACKAGE}@{version} into {target.relative_to(ROOT)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
