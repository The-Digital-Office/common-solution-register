"""Helpers shared by the tests."""

import datetime as dt
from pathlib import Path

from csr.records import Record

FIXTURES = Path(__file__).parent / "fixtures"
TODAY = dt.date(2026, 11, 2)


def as_record(data: dict, label: str = "records/test.yaml") -> Record:
    """Wrap a document as a record that is not in the register."""
    return Record(label=label, data=data, in_register=False, filename=Path(label).name)


def drop_demonstrations(root: Path) -> None:
    """Remove demonstration records from a copy of the register, so tests that
    allocate the next free id (csr-0003) do not change as they are added."""
    from csr.schema import load_yaml_file

    for path in (root / "records").glob("*.yaml"):
        if load_yaml_file(path).get("record_status") == "demonstration":
            path.unlink()


def demonstration_ids() -> list[str]:
    """The ids of the register's demonstration records, which S15 adds one at a time."""
    from csr.schema import ROOT, load_yaml_file

    return sorted(
        path.stem for path in (ROOT / "records").glob("*.yaml")
        if load_yaml_file(path).get("record_status") == "demonstration"
    )  # fmt: skip
