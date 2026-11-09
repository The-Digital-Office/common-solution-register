"""Records for the JavaScript parity test, with what csr validate finds in each."""

import copy
import datetime as dt
from pathlib import Path

from csr.records import Record, read_register
from csr.rules import Context
from csr.schema import ROOT, load_yaml_file
from csr.taxonomy import load_all
from csr.validate import check_record

TODAY = dt.date(2026, 11, 2)
#: Rules both csr validate and the browser apply to a single file.
SHARED_RULES = {"R02", "R03", "R04", "R05", "R06", "R07", "R09", "R10", "R11", "R12", "R18"}


def _variants(minimal: dict) -> dict[str, dict]:
    def change(**changes):
        record = copy.deepcopy(minimal)
        for path, value in changes.items():
            target = record
            *parents, last = path.split("__")
            for part in parents:
                target = target[part]
            target[last] = value
        return record

    return {
        "R02 example outside range": change(id="csr-0100"),
        "R02 real record in example range": change(id="csr-9100", record_status="owner-confirmed",
                                                   name="Minimal Component"),  # fmt: skip
        "R03 unknown terms": change(service_areas=["parks", "housing"], owner__sector="local-govt"),
        "R03 audience as owner": change(owner__sector="scottish-public-sector",
                                         intended_adopters=["scottish-public-sector"]),
        "R05 unknown related": change(related_assets=[{"id": "csr-0404"}, {"id": "csr-0001"}]),
        "R06 future confirmation": change(confirmation__last_confirmed="2026-12-25"),
        "R07 personal contact": change(contact__value="jane.smith@example.gov.uk"),
        "R07 role contact": change(contact__value="digital.services@example.gov.uk"),
        "R09 placeholder": change(purpose="TODO: say what this solution does, for whom and why it matters."),
        "R10 sentinel": change(adoption_route__summary="not-publicly-stated"),
        "R11 example name": change(name="Minimal Component"),
        "R12 public codebase": change(codebases=[{"repository_url": "https://code.example.gov.uk/x",
                                                  "visibility": "public", "maintenance": "internal"}]),  # fmt: skip
        "R18 http": change(documentation_url="http://docs.example.gov.uk/",
                           open_data=[{"title": "Data", "url": "ftp://data.example.gov.uk/"}]),  # fmt: skip
    }


def corpus() -> dict:
    register, _ = read_register(ROOT / "records")
    known = sorted(r.id for r in register if r.id)
    context = Context(taxonomies=load_all(), today=TODAY, known_ids=frozenset(known))
    fixtures = Path(__file__).parent / "fixtures" / "schema"
    records = {f"fixture {p.relative_to(fixtures).as_posix()}": load_yaml_file(p) for p in sorted(fixtures.rglob("*.yaml"))}
    records.update({f"register {r.id}": r.data for r in register if r.data and not r.is_pointer})
    for hosted in sorted((ROOT / "examples" / "hosted").glob("*/solution.yml")):
        records[f"hosted {hosted.parent.name}"] = load_yaml_file(hosted)
    records.update(_variants(records["fixture pass/minimal.yaml"]))
    out = {}
    for name, data in records.items():
        findings = check_record(Record(name, data), context)
        out[name] = {
            "record": data,
            "schema_errors": any(f.rule == "SCHEMA" for f in findings),
            "rules": sorted({(f.rule, f.path, str(f.severity)) for f in findings if f.rule in SHARED_RULES}),
            "schema": sorted({(f.path, f.message) for f in findings if f.rule == "SCHEMA"}),
        }
    return {
        "today": TODAY.isoformat(),
        "known_ids": known,
        "taxonomies": {name: [{"id": t.id, "status": t.status, "replaced_by": t.replaced_by,
                               "intended_adopters_only": t.intended_adopters_only} for t in tax.terms]
                       for name, tax in load_all().items()},  # fmt: skip
        "shared_rules": sorted(SHARED_RULES),
        "records": out,
    }
