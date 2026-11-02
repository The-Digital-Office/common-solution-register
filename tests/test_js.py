"""Runs the JavaScript unit tests with Node's built-in test runner, if Node is installed."""

import shutil
import subprocess
from pathlib import Path

import pytest

TESTS = sorted((Path(__file__).parent / "js").glob("*.test.mjs"))


@pytest.mark.skipif(shutil.which("node") is None, reason="Node is not installed")
@pytest.mark.parametrize("path", TESTS, ids=lambda p: p.name)
def test_javascript(path):
    result = subprocess.run(["node", "--test", str(path)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
