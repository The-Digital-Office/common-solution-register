"""Write the UI fixtures' harvest state, at a fixed time, with the parser's verdicts as valid."""

import datetime as dt
import json
from pathlib import Path

from csr import harvest
from csr.config import load_config

ROOT = Path(__file__).parent / "register"
NOW = dt.datetime(2026, 11, 2, 5, 23, tzinfo=dt.UTC)

state, _ = harvest.run(ROOT, load_config(ROOT), harvest.empty_state(), now=NOW, parser=lambda path: [])
(ROOT / "harvest-state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({record: entry["state"] for record, entry in state["sources"].items()})
