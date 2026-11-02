"""Helpers shared by the tests."""

import datetime as dt
from pathlib import Path

from csr.records import Record

FIXTURES = Path(__file__).parent / "fixtures"
TODAY = dt.date(2026, 11, 2)


def as_record(data: dict, label: str = "records/test.yaml") -> Record:
    """Wrap a document as a record that is not in the register."""
    return Record(label=label, data=data, in_register=False, filename=Path(label).name)
