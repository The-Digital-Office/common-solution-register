"""Each of the eight schema conditions (specification 6.4) has passing and failing fixtures.

A failing fixture declares where its error is expected, in header comments:

    # expect-error-at: charging          (a field path, or "(record)" for the record itself)
    # expect-message: ...                (optional: text the error message must contain)

Every error a failing fixture produces must be at that path, so each fixture
fails for its stated reason only.
"""

import re
from pathlib import Path

import pytest

from csr.schema import check, load_yaml_file
from csr.taxonomy import load_all

FIXTURES = Path(__file__).parent / "fixtures" / "schema"
PASSING = sorted((FIXTURES / "pass").glob("*.yaml"))
FAILING = sorted((FIXTURES / "fail").glob("*.yaml"))
CONDITIONS = range(1, 9)


def _header(path: Path, key: str) -> str | None:
    match = re.search(rf"^# {key}: (.+)$", path.read_text(encoding="utf-8"), re.MULTILINE)
    return match.group(1).strip() if match else None


def _condition(path: Path) -> int | None:
    match = re.match(r"c(\d)-", path.name)
    return int(match.group(1)) if match else None


@pytest.mark.parametrize("condition", CONDITIONS)
def test_every_condition_has_passing_and_failing_fixtures(condition):
    assert any(_condition(p) == condition for p in PASSING), f"no passing fixture for condition {condition}"
    assert any(_condition(p) == condition for p in FAILING), f"no failing fixture for condition {condition}"


@pytest.mark.parametrize("path", PASSING, ids=lambda p: p.stem)
def test_passing_fixture_is_valid(path):
    assert [str(e) for e in check(load_yaml_file(path))] == []


@pytest.mark.parametrize("path", FAILING, ids=lambda p: p.stem)
def test_failing_fixture_fails_for_its_stated_reason(path):
    expected_path = _header(path, "expect-error-at")
    assert expected_path, "failing fixture has no 'expect-error-at' header"
    expected_path = "" if expected_path == "(record)" else expected_path
    errors = check(load_yaml_file(path))
    assert errors, "fixture unexpectedly passes"
    assert {e.path for e in errors} == {expected_path}, [str(e) for e in errors]
    expected_message = _header(path, "expect-message")
    if expected_message:
        assert any(expected_message in e.message for e in errors), [str(e) for e in errors]


@pytest.mark.parametrize("path", PASSING + FAILING, ids=lambda p: p.stem)
def test_fixture_taxonomy_terms_exist(path):
    record = load_yaml_file(path)
    taxonomies = load_all()
    assert record["owner"]["sector"] in taxonomies["sectors"]
    assert all(term in taxonomies["sectors"] for term in record["intended_adopters"])
    assert all(term in taxonomies["service-areas"] for term in record["service_areas"])
    assert all(term in taxonomies["capabilities"] for term in record["capabilities"])
