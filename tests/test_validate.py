"""The validate command: the register as a whole (R01), --base, reading files, and the CLI."""

import json
import shutil
import subprocess

import pytest
import yaml
from helpers import FIXTURES, TODAY

from csr.cli import main
from csr.validate import BaseError, validate

MINIMAL = FIXTURES / "schema" / "pass" / "minimal.yaml"


@pytest.fixture
def repo(tmp_path, minimal):
    """A register with one valid record, and helpers to add more."""
    (tmp_path / "records").mkdir()

    def add(record_id, filename=None, **changes):
        record = dict(minimal)
        record.update(id=record_id, **changes)
        (tmp_path / "records" / (filename or f"{record_id}.yaml")).write_text(yaml.safe_dump(record), encoding="utf-8")

    add("csr-9100")
    return tmp_path, add


def findings(result):
    return [(f.file, f.rule, f.path) for f in result.findings]


def test_valid_register(repo):
    root, _ = repo
    result = validate(root=root, today=TODAY)
    assert result.ok and result.findings == []
    assert result.checked == ["records/csr-9100.yaml"]


def test_empty_or_missing_register(tmp_path):
    result = validate(root=tmp_path, today=TODAY)
    assert result.ok and result.checked == []


def test_root_solution_yml_is_checked(repo):
    root, _ = repo
    shutil.copy(MINIMAL, root / "solution.yml")
    assert validate(root=root, today=TODAY).checked == ["records/csr-9100.yaml", "solution.yml"]


# R01


def test_r01_id_must_match_file_name(repo):
    root, add = repo
    add("csr-9101", filename="csr-9102.yaml")
    assert ("records/csr-9102.yaml", "R01", "id") in findings(validate(root=root, today=TODAY))


def test_r01_file_name_format(repo):
    root, add = repo
    add("csr-9101", filename="csr-9101.yml")
    result = validate(root=root, today=TODAY)
    assert findings(result) == [("records/csr-9101.yml", "R01", "")]
    assert not result.ok


def test_r01_ids_are_unique(repo):
    root, add = repo
    add("csr-9100", filename="csr-9101.yaml")
    rules = [(f, r) for f, r, _ in findings(validate(root=root, today=TODAY))]
    assert ("records/csr-9101.yaml", "R01") in rules
    assert any(f.message.endswith("records/csr-9100.yaml") for f in validate(root=root, today=TODAY).findings)


def _git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


@pytest.fixture
def git_repo(repo):
    root, add = repo
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "test@example.gov.uk")
    _git(root, "config", "user.name", "Test")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "Start")
    return root, add


def test_r01_base_detects_an_id_taken_on_the_base_branch(git_repo):
    root, add = git_repo
    _git(root, "checkout", "-q", "-b", "feature")
    add("csr-9101")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "Add csr-9101 on the branch")
    _git(root, "checkout", "-q", "main")
    add("csr-9101", summary="Another fictional component, added on main by someone else.")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "Add csr-9101 on main")
    _git(root, "checkout", "-q", "feature")

    result = validate(root=root, base="main", today=TODAY)
    assert ("records/csr-9101.yaml", "R01", "id") in findings(result)
    assert "csr-9102" in next(f.fix for f in result.findings if f.rule == "R01")
    assert validate(root=root, today=TODAY).ok  # without --base, nothing is wrong


def test_r01_base_ignores_records_that_already_existed(git_repo):
    root, add = git_repo
    _git(root, "checkout", "-q", "-b", "feature")
    add("csr-9100", summary="An edit to an existing fictional component's summary.")
    assert validate(root=root, base="main", today=TODAY).ok


def test_r01_base_must_exist(git_repo):
    root, _ = git_repo
    with pytest.raises(BaseError):
        validate(root=root, base="no-such-branch", today=TODAY)


# Reading files


def test_yaml_errors_are_reported(repo):
    root, _ = repo
    (root / "records" / "csr-9101.yaml").write_text("id: [unclosed\n", encoding="utf-8")
    (root / "records" / "csr-9102.yaml").write_text("- a list\n", encoding="utf-8")
    result = findings(validate(root=root, today=TODAY))
    assert ("records/csr-9101.yaml", "YAML", "") in result
    assert ("records/csr-9102.yaml", "YAML", "") in result


def test_repeated_keys_are_reported(repo):
    root, _ = repo
    text = MINIMAL.read_text(encoding="utf-8").replace("id: csr-9100", "id: csr-9101\nname: Again")
    (root / "records" / "csr-9101.yaml").write_text(text, encoding="utf-8")
    result = validate(root=root, today=TODAY)
    assert any(f.rule == "YAML" and "repeated key 'name'" in f.message for f in result.findings)


def test_targets_instead_of_register(repo, tmp_path):
    root, _ = repo
    result = validate([str(MINIMAL), str(FIXTURES / "schema" / "fail" / "c8-deprecated-without-deprecation.yaml")],
                      root=root, today=TODAY)  # fmt: skip
    assert len(result.checked) == 2
    assert [f.rule for f in result.findings] == ["SCHEMA"]


def test_pointer_target(tmp_path, repo):
    root, _ = repo
    pointer = tmp_path / "csr-0001.yaml"
    pointer.write_text("id: csr-0001\nsource: http://example.gov.uk/solution.yml\nexpected_owner: Example\n")
    result = validate([str(pointer)], root=root, today=TODAY)
    assert [(f.rule, f.path) for f in result.findings] == [("SCHEMA", "source")]


def test_url_target_must_be_https(repo):
    root, _ = repo
    result = validate(["http://example.gov.uk/solution.yml"], root=root, today=TODAY)
    assert [f.rule for f in result.findings] == ["R18"]


# --check-links (R08 and R19), with a fake network


PUBLICCODE = b"""
publiccodeYmlVersion: "0"
url: https://github.com/example/booking
maintenance:
  type: community
"""


def test_check_links(repo, minimal):
    root, add = repo
    add("csr-9101", codebases=[
        {"repository_url": "https://github.com/example/booking.git", "visibility": "public", "maintenance": "internal",
         "publiccode_url": "https://github.com/example/booking/raw/main/publiccode.yml"},
        {"repository_url": "https://github.com/example/gone", "visibility": "public", "maintenance": "none",
         "publiccode_url": "https://github.com/example/gone/raw/main/publiccode.yml"},
    ])  # fmt: skip
    responses = {
        "https://github.com/example/booking.git": (200, b""),
        "https://github.com/example/booking/raw/main/publiccode.yml": (200, PUBLICCODE),
    }
    result = validate(root=root, today=TODAY, check_links=True, fetch=lambda url: responses.get(url, (404, b"")))
    assert findings(result) == [
        ("records/csr-9101.yaml", "R08", "codebases[1].publiccode_url"),
        ("records/csr-9101.yaml", "R08", "codebases[1].repository_url"),
        ("records/csr-9101.yaml", "R19", "codebases[0].maintenance"),
    ]
    assert result.ok  # network rules only warn


def test_check_links_publiccode_url_mismatch(repo):
    root, add = repo
    add("csr-9101", codebases=[
        {"repository_url": "https://github.com/example/other", "visibility": "public", "maintenance": "community",
         "publiccode_url": "https://github.com/example/booking/raw/main/publiccode.yml"},
    ])  # fmt: skip
    result = validate(root=root, today=TODAY, check_links=True, fetch=lambda url: (200, PUBLICCODE))
    assert findings(result) == [("records/csr-9101.yaml", "R19", "codebases[0].repository_url")]


def test_links_not_checked_by_default(repo):
    root, add = repo
    add("csr-9101", codebases=[{"repository_url": "https://github.com/example/a", "visibility": "public",
                                "maintenance": "internal"}])  # fmt: skip

    def fail(url):
        raise AssertionError("network used without --check-links")

    validate(root=root, today=TODAY, fetch=fail)


# The command line


def test_cli_text(repo, capsys, monkeypatch):
    root, add = repo
    add("csr-9101", name="Not an example")
    monkeypatch.setattr("csr.validate.ROOT", root)
    monkeypatch.chdir(root)
    assert main(["validate", "--today", "2026-11-02"]) == 1
    out = capsys.readouterr().out
    assert "records/csr-9101.yaml: error R11 name:" in out
    assert '    Fix: Rename it "Example: Not an example".' in out
    assert out.strip().endswith("Checked 2 files: 1 error, 0 warnings.")


def test_cli_json_and_github(capsys):
    target = str(FIXTURES / "schema" / "fail" / "c3-withdrawn-without-withdrawal.yaml")
    assert main(["validate", "--format", "json", target]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["ok"] is False and report["findings"][0]["rule"] == "SCHEMA"
    assert main(["validate", "--format", "github", target]) == 1
    assert capsys.readouterr().out.startswith("::error file=")


def test_cli_valid_file(capsys):
    assert main(["validate", str(MINIMAL)]) == 0
    assert "Checked 1 file: 0 errors, 0 warnings." in capsys.readouterr().out


def test_cli_bad_base(capsys):
    assert main(["validate", "--base", "refs/heads/no-such-branch-anywhere"]) == 2
    assert "csr validate:" in capsys.readouterr().err
