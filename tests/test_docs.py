"""The documentation: the files specification 6.3 lists exist, and links between them resolve."""

import re

import pytest

from csr.schema import ROOT

SPEC_DOCS = [
    "adopting-this-demonstrator.md", "decision-points.md", "editorial-model.md", "contributing-records.md",
    "hosting-your-solution-yml.md", "harvesting.md", "maintenance.md", "publiccode-mapping.md", "github-free.md",
]  # fmt: skip
MARKDOWN = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
LINK = re.compile(r"\]\(([^)\s]+)\)")


@pytest.mark.parametrize("name", SPEC_DOCS)
def test_the_documents_in_the_repository_layout_exist(name):
    assert (ROOT / "docs" / name).is_file()


@pytest.mark.parametrize("path", MARKDOWN, ids=lambda p: str(p.relative_to(ROOT)))
def test_relative_links_resolve(path):
    broken = []
    for target in LINK.findall(path.read_text(encoding="utf-8")):
        if re.match(r"[a-z]+:", target) or target.startswith("#"):
            continue
        if not (path.parent / target.split("#")[0]).exists():
            broken.append(target)
    assert not broken


def test_decision_points_are_numbered_in_order():
    numbers = [int(n) for n in re.findall(r"^\| DP-(\d+) \|", (ROOT / "docs/decision-points.md").read_text(), re.M)]
    assert numbers == list(range(1, len(numbers) + 1))


def test_the_contributing_guide_the_site_links_to_exists():
    assert "docs/contributing-records.md" in (ROOT / "src/csr/templates/contribute.html").read_text()
    assert (ROOT / "docs/contributing-records.md").is_file()
