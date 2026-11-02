"""Shared test helpers."""

import copy

import pytest
from helpers import FIXTURES, TODAY

from csr.rules import Context
from csr.schema import load_yaml_file
from csr.taxonomy import load_all


@pytest.fixture
def minimal() -> dict:
    """A fresh copy of the smallest valid record (an example)."""
    return copy.deepcopy(load_yaml_file(FIXTURES / "schema" / "pass" / "minimal.yaml"))


@pytest.fixture
def context() -> Context:
    return Context(taxonomies=load_all(), today=TODAY, known_ids=frozenset({"csr-9100", "csr-0001"}))
