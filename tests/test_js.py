"""Runs the JavaScript unit tests with Node's built-in test runner, if Node is installed."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from js_corpus import corpus

from csr.schema import load_yaml_file

TESTS = sorted((Path(__file__).parent / "js").glob("*.test.mjs"))


@pytest.mark.skipif(shutil.which("node") is None, reason="Node is not installed")
@pytest.mark.parametrize("path", TESTS, ids=lambda p: p.name)
def test_javascript(path, tmp_path):
    # The schema fixtures, as JSON, so the browser validator can be checked against the Python one.
    fixtures = tmp_path / "fixtures.json"
    root = Path(__file__).parent / "fixtures" / "schema"
    fixtures.write_text(json.dumps({p.relative_to(root).as_posix(): load_yaml_file(p) for p in sorted(root.rglob("*.yaml"))}))
    parity = tmp_path / "corpus.json"
    parity.write_text(json.dumps(corpus()))
    env = {**os.environ, "CSR_FIXTURES": str(fixtures), "CSR_CORPUS": str(parity)}
    result = subprocess.run(["node", "--test", str(path)], capture_output=True, text=True, check=False, env=env)
    assert result.returncode == 0, result.stdout + result.stderr
