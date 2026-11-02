"""Tests for the ``csr`` command-line entry point."""

import subprocess
import sys

import pytest

from csr import __version__
from csr.cli import main


def test_version(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])
    assert exit_info.value.code == 0
    assert capsys.readouterr().out.strip() == f"csr {__version__}"


def test_no_command_prints_help(capsys):
    assert main([]) == 0
    assert "usage: csr" in capsys.readouterr().out


def test_unknown_command_fails():
    with pytest.raises(SystemExit) as exit_info:
        main(["no-such-command"])
    assert exit_info.value.code == 2


def test_runs_as_module():
    result = subprocess.run(
        [sys.executable, "-m", "csr", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == f"csr {__version__}"
