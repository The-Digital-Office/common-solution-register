# UI test fixtures

`register/` is a fixed copy of the register for the UI tests, so that changes
to the real records (for example new demonstration entries) do not change the
screenshots. It holds the records, examples and descriptors as they were when
the visual baselines were approved, plus `csr-0100`, an invented demonstration
entry that shows how a record compiled from public sources is displayed. It
describes no real service and is never published.

`register/harvest-state.json` is a harvest state made at a fixed time
(`python ui/tests/fixtures/make-harvest-state.py`), with the official parser's
verdict on `csr-0001`'s publiccode.yml recorded as valid, so that the pages are
the same wherever the tests run.

The UI tests build this register as on 2 November 2026, without git history:

    csr build --root ui/tests/fixtures/register --harvest ui/tests/fixtures/register/harvest-state.json \
      --date 2026-11-02 --no-history --base-url http://localhost:4173/ --out ui/build
