"""Vendor a pinned npm package's browser files, without npm.

Usage: python tools/vendor.py NAME VERSION     (NAME: sgds, js-yaml, ajv, roboto or roboto-mono)

Downloads the package from the npm registry, checks the tarball against the
registry's integrity hash, and writes the listed files to
src/csr/static/vendor/NAME/VERSION/, with SOURCE.md and SHA256SUMS (checked by
the R13 test). Files are taken unchanged.
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

ROOT = Path(__file__).resolve().parents[1]

#: Folder name: the npm package, the files to take (path in the package: file name), and a note.
PACKAGES = {
    "sgds": (
        "@scottish-government/design-system",
        {
            "package/dist/css/design-system.min.css": "design-system.min.css",
            "package/dist/scripts/design-system.js": "design-system.js",
            "package/LICENSE.txt": "LICENSE.txt",
        },
        "No graphic assets are vendored, and no Scottish Government logo or brand asset is used.",
    ),
    "js-yaml": (
        "js-yaml",
        {
            "package/dist/browser/js-yaml.esm.min.mjs": "js-yaml.mjs",
            "package/LICENSE": "LICENSE",
        },
        "Used by the draft form to write solution.yml. The browser ES module build is renamed "
        "js-yaml.mjs.",
    ),
    "roboto": (
        "@fontsource/roboto",
        {
            **{f"package/files/roboto-{subset}-{face}.woff2": f"roboto-{subset}-{face}.woff2"
               for subset in ("latin", "latin-ext") for face in ("300-normal", "400-normal", "400-italic", "700-normal")},
            "package/LICENSE": "LICENSE",
        },
        "Roboto, the design system's typeface, served from the site itself so that no visitor's browser "
        "contacts a font service (decision D5 in docs/ui-requirements.md). Latin and Latin Extended "
        "subsets, in the weights the design system uses. The @font-face rules are in static/fonts.css.",
    ),
    "roboto-mono": (
        "@fontsource/roboto-mono",
        {
            **{f"package/files/roboto-mono-{subset}-400-normal.woff2": f"roboto-mono-{subset}-400-normal.woff2"
               for subset in ("latin", "latin-ext")},
            "package/LICENSE": "LICENSE",
        },
        "Roboto Mono, for code and YAML, so that they look the same on every computer. Served from the site itself.",
    ),
    "ajv": (
        "ajv-dist",
        {
            "package/dist/ajv2020.min.js": "ajv2020.min.js",
            "ajv@{version}:package/LICENSE": "LICENSE",
        },
        "The browser bundle of Ajv's JSON Schema 2020-12 validator, published by the Ajv project as "
        "ajv-dist. That package has no licence file, so `LICENSE` is taken from the same version of the "
        "ajv package. Used by the draft and validate pages to check records in the browser.",
    ),
}


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as response:  # noqa: S310 - fixed HTTPS registry URL
        return response.read()


def download(package: str, version: str) -> tuple[dict, bytes]:
    """The registry's metadata and the tarball, checked against its integrity hash."""
    meta = json.loads(fetch(f"https://registry.npmjs.org/{package.replace('/', '%2F')}/{version}"))
    tarball = fetch(meta["dist"]["tarball"])
    algorithm, expected = meta["dist"]["integrity"].split("-", 1)
    if base64.b64encode(hashlib.new(algorithm, tarball).digest()).decode() != expected:
        sys.exit(f"integrity mismatch for {meta['dist']['tarball']}")
    return meta, tarball


def main(name: str, version: str) -> None:
    package, files, note = PACKAGES[name]
    meta, tarball = download(package, version)
    tarball_url, integrity = meta["dist"]["tarball"], meta["dist"]["integrity"]

    target = ROOT / "src" / "csr" / "static" / "vendor" / name / version
    target.mkdir(parents=True, exist_ok=True)
    sums = []
    for member, file_name in files.items():
        source = tarball
        if ":" in member:  # a file from another package: "name@version:path"
            other, member = member.format(version=version).split(":", 1)
            source = download(*other.rsplit("@", 1))[1]
        with tarfile.open(fileobj=io.BytesIO(source), mode="r:gz") as archive:
            data = archive.extractfile(member).read()
        (target / file_name).write_bytes(data)
        sums.append(f"{hashlib.sha256(data).hexdigest()}  {file_name}")
    (target / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    taken = ", ".join(f"`{m.format(version=version).replace(':package/', ':').removeprefix('package/')}`" for m in files)
    licence = next(f for f in files.values() if f.startswith("LICENSE"))
    (target / "SOURCE.md").write_text(
        f"""# {package} {version}

| | |
|---|---|
| Package | [`{package}@{version}`](https://www.npmjs.com/package/{package}/v/{version}) |
| Tarball | {tarball_url} |
| npm integrity | `{integrity}` |
| Licence | {meta.get("license", "see the licence file")} ([`{licence}`]({licence})) |

Files taken unchanged from the package: {taken}. Their SHA-256 hashes are in
[`SHA256SUMS`](SHA256SUMS), checked by the R13 test. {note}

Refresh with `python tools/vendor.py {name} {version}`.
""",
        encoding="utf-8",
    )
    print(f"Vendored {package}@{version} into {target.relative_to(ROOT)}")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in PACKAGES:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
