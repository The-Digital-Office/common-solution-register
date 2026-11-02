# Build plan: Common Solution Register Demonstrator

The build is done in small sessions, one **slice** per session. Each slice is one branch and one pull request, and leaves `main` working.

## Briefing

- **What:** a demonstrator of a common solution register for the Scottish public sector, built for the Scottish Government short-life working group. Not an official register. Hosted by The Digital Office for Scottish Local Government.
- **Specification:** `docs/spec/Common-Solution-Register-Demonstrator-Specification.md` (v1.2). Section 1.1 defines solutions and codebases; 9.1 sets the authorship rules.
- **Wireframes:** `ui/wireframes/` (normative UI requirements, spec 6.13); baseline images in `ui/baseline/`.
- **Concepts:** a common solution is an owned offer of reuse, described by `solution.yml`; a codebase is source code, described by its own `publiccode.yml` and listed in a solution's `codebases`; datasets are linked through `open_data`, never listed.
- **Stack:** Python 3.12 (`src/csr/`), Jinja2 templates, plain JavaScript (no framework, no build step), Scottish Government Design System 4.3.0 vendored under `src/csr/static/vendor/sgds/4.3.0/`. Node 22 for tests only.
- **Fast checks (every session):** `pip install -e .[dev]`, `pytest -q`, `csr validate --base origin/main`, `csr build --base-url http://localhost:8000/`. Heavy UI tests run in CI only.
- **Conventions:** Digital Office baseline (`The-Digital-Office/.github`); British English; code MIT, content OGL v3.0; every slice updates `CHANGELOG.md` under Unreleased and the progress log below; actions pinned by SHA; never invent facts about real organisations.
- **Authorship (spec 9.1):** commit as `Robbie Harris <robbie.harris@digitaloffice.scot>`; no co-author or session trailers; no tool or AI attribution in any file, commit or pull request text; no GitHub comments; push the slice branch and the author opens the pull request.

## Resume protocol (every session)

1. Read this briefing, then the **Progress log** below: the last entry says which slice and checkpoint is next.
2. Check `git config user.name` and `user.email` match the authorship rule (set them if not). `git fetch`. If the slice's branch (`build/sNN-short-name`) exists, check it out and continue; otherwise branch from `main`.
3. Read **only** the spec sections and wireframes the slice names.
4. Work in checkpoint order. **Commit and push at every checkpoint**, then add a log line.
5. Before stopping, for any reason: run the fast checks (`pytest -q`, `csr validate`), push, and write a log entry with **Done**, **Next** and **Blockers**.
6. When the slice's acceptance checks pass, push the branch, write the pull request title and description (organisation template, no tool footer) into the log entry, and mark the slice ready. The author opens and merges the pull request.

Rules: never push to `main`; never rewrite pushed history; do not start the next slice in the same pull request; leave heavy UI tests to CI; if a slice turns out too big, split it here before continuing.

## Slices

| # | Slice | Spec | Checkpoints | Acceptance |
|---|---|---|---|---|
| S0 | **Author:** create the repository from `repository-template` and apply the baseline | 7.1 steps 1–5 | — | Setup commit and setup issue exist; baseline ruleset applied; repository attached to the build environment, whose setup script sets the git identity and a global ignore file for tool working folders (spec 9.1) |
| S1 | Setup and scaffolding: complete the setup issue (README, `publiccode.yml`, delete `template.yml`); commit the handover pack (spec, wireframes, baseline images, this plan); extend `.gitignore` and `dependabot.yml`; Python package skeleton (`pyproject.toml`, `src/csr/`, `tests/`); `site.yml` with the `Validate` job running `pytest` | 5, 6.3, 7.1 | a) setup-issue files; b) handover pack; c) skeleton and CI | Baseline checks and `Validate` pass; setup issue closable |
| S2 | Schema and taxonomy: `asset.schema.json` (all fields and 8 conditions), pointer schema, sectors, service areas and capabilities with definitions; fixtures; schema tests | 6.4, 6.5 | a) schema; b) taxonomy; c) pass/fail fixture per condition | Every condition has a passing and a failing fixture |
| S3 | Validator: `csr validate` with R01–R13, R18, R19 (network rules behind `--check-links`), `--base` | Appendix C | a) loader and CLI; b) rules; c) tests | `pytest` covers each rule, pass and fail |
| S4 | Owner and example records: `csr-0001` (`solution.yml` at the repository root plus a pointer), `csr-0002`, `csr-9001`–`9007`, `examples/hosted/` | 5.1, 5.2 | a) csr-0001 and 0002; b) examples | `csr validate` passes; `csr-9007` fails as intended |
| S5 | Walking skeleton: generator, vendored Scottish Government Design System 4.3.0, base layout and partials (header, banner, footer), home page (list without JavaScript), record page | 6.2, 6.8, 6.13 | a) vendoring and hashes; b) layout; c) home; d) record | Built site opens; record page matches wireframe structure; preview artifact uploaded by CI |
| S6 | Remaining static pages, API and CSV: browse, term, contribute, about, accessibility, privacy, 404, withdrawn, field reference, solutions-and-codebases, data, currency | 6.8, 6.13 | a) pages, part 1; b) part 2; c) API and CSV | Every page in the 6.13 map is built; `api/v0/` and extracts are generated |
| S7 | Search, filter and sort script; query in URL; result count announced | 6.13 parity rows 1–6 | a) search; b) filters and counts; c) sort | Behaves as the parity table; works without JavaScript |
| S8 | Draft form, part 1: form generated from schema and taxonomy; conditional sections; codebases and open data repeaters; live YAML preview | 6.6, 6.13 | a) template; b) conditions; c) preview | Matches the Draft wireframe |
| S9 | Draft form, part 2: vendored Ajv and `js-yaml`; full validation; error summary and inline errors; copy, download, issue and email hand-off | 6.6, 6.9 | a) validation; b) hand-off | Parity rows for the form pass |
| S10 | Validate page: paste, upload and URL modes; results table | 6.8, 6.13 | a) modes; b) results | Matches wireframe, with real validation |
| S11 | Harvester: pointer records, fetch limits, owner match, last-valid state, harvest report; `publiccode-parser-go` for each codebase; R14–R17 | 6.11 | a) fetch and owner match; b) state; c) parser; d) report page | Harvest of `csr-0001` and the examples behaves as specified |
| S12 | Tools: `csr import-publiccode --to/--new`, `move-to-source`, `move-to-local`, `new --from-issue` | 6.6, 6.12, Appendix A | a) importer; b) move commands | Tests for each command |
| S13 | Workflows and community files: daily and on-demand harvest, deploy (disabled until `PAGES_ENABLED`), concurrency; reusable `validate-solution.yml`; issue forms; pull request template | 6.10, 6.6 | a) workflows; b) forms and template | Workflows pass; deploy is skipped |
| S14 | UI tests: fixtures reproducing the wireframes; visual comparison at 1280 and 375 pixels; behaviour tests; `axe-core`; required `UI tests` job; `npm` entry in `dependabot.yml` (removed after S1 because there was no `package.json` to read); **author** adds `UI tests` to the "CSR: required checks" ruleset | 6.13 | a) visual; b) behaviour; c) accessibility | `UI tests` passes in CI |
| S15 | Demonstration records: research, cited sources, sentinels where facts are not public | 5.2 | a) one record per checkpoint | Author verifies every statement against its source |
| S16 | Documentation and readiness: adopting guide, decision points (including the S2 schema choices, which the author wants reviewed as part of the demonstrator), editorial model, maintenance, runbook; manual accessibility pass | 8, 9 | a) documents; b) checklist | Ready for courtesy notes, sign-off and enabling Pages (author steps) |

## Progress log

Newest last. One line per checkpoint; a fuller entry when a session ends.

- 2026-11-02 — Plan created. **Next:** S0 (author), then S1a.
- 2026-11-02 — S1a done: setup-issue files (README, `publiccode.yml` completed, `LICENCE-CONTENT.md`, `CODEOWNERS` review paths, `template.yml` deleted). S1 works on branch `robbie/wizardly-dijkstra-2sjib7`, the branch the build environment assigned, instead of `build/s01-…`.
- 2026-11-02 — S1b done: handover pack committed (spec, wireframes, baseline images, this plan, `tools/render-wireframes.js`, `ui/README.md`).
- 2026-11-02 — S1c done: `pyproject.toml` (dependencies pinned exactly), `src/csr/` with a `csr` entry point (`--version` only), `tests/`, `.gitignore` and `dependabot.yml` (pip, npm) extended, `site.yml` with the `Validate` job running `pytest` (actions pinned by SHA).
- 2026-11-02 — **S1 ready for pull request.**
  - **Done:** S1a–c. `pytest -q` passes (5 tests). `csr validate` and `csr build` do not exist yet (S3 and S5); until then the fast checks are `pip install -e .[dev]` and `pytest -q`.
  - **Next:** author opens the pull request from `robbie/wizardly-dijkstra-2sjib7`, confirms `Validate` and the baseline checks pass, merges, completes the **About** panel (description and topics) and closes the setup issue (#1). Then S2 on `build/s02-schema-taxonomy`.
  - **Blockers:** none. Notes for the author: no second maintainer was named, so `CODEOWNERS` has one; the npm Dependabot entry has no `package.json` to read until S14; the pull request may need `Validate` added as a required check if the ruleset is to enforce it.
  - **Pull request title:** Set up the repository and scaffold the `csr` package (S1)
  - **Pull request description:**

    > ## What this changes
    >
    > Completes the template setup and lays the foundations for the build (slice S1 of `docs/build/PLAN.md`).
    >
    > - Writes the README, completes `publiccode.yml`, adds `LICENCE-CONTENT.md` (OGL v3.0), adds `CODEOWNERS` review paths for `/records/`, `/taxonomy/` and `/schema/`, and deletes `.github/workflows/template.yml`.
    > - Commits the specification (v1.2), the build plan, the wireframes, the baseline images and the rendering script.
    > - Adds the Python package skeleton (`pyproject.toml`, `src/csr/`, `tests/`) and the `Site` workflow, whose `Validate` job runs `pytest`.
    > - Extends `.gitignore` and `dependabot.yml` (pip and npm).
    >
    > ## Why
    >
    > Specification sections 6.3 and 7.1: the first pull request completes the setup issue, and every later slice builds on the package and the `Validate` check.
    >
    > Closes #1 once the About panel description and topics are added.
    >
    > ## How it was tested
    >
    > `pip install -e .[dev]` and `pytest -q` (5 passed) on Python 3.12.
    >
    > ## Checklist
    >
    > - [x] `CHANGELOG.md` updated under Unreleased
    > - [x] No secrets or personal data
    > - [x] Actions pinned by SHA
- 2026-11-02 — S1 merged; setup issue closed and About panel completed. Follow-up: `npm` entry removed from `dependabot.yml` (its weekly run failed with no `package.json`); S14 adds it back. **Next:** S2.
- 2026-11-02 — Author created the "CSR: required checks" ruleset (default branch, requires `Validate`), alongside "DO baseline: main".
- 2026-11-02 — S2a done: `schema/asset.schema.json` (all 6.4 fields, eight conditions, sentinel only in demonstration records, derived fields rejected), `schema/pointer.schema.json`, `schema/README.md`, `src/csr/schema.py` (YAML loader that keeps dates as strings; `check()`), schema tests. Branch `robbie/wizardly-dijkstra-2sjib7` (environment-assigned).
- 2026-11-02 — S2b done: `taxonomy/` (8 sectors, 14 service areas, 14 capabilities, each with label, definition, synonyms and status), `schema/taxonomy.schema.json`, `src/csr/taxonomy.py`, taxonomy tests.
- 2026-11-02 — S2c done: `tests/fixtures/schema/` with 26 fixtures (`pass/` and `fail/`, named `cN-…` by condition; each failing fixture declares `expect-error-at` and must fail only there) and `tests/test_schema_conditions.py`.
- 2026-11-02 — **S2 ready for pull request.**
  - **Done:** S2a–c. `pytest -q` passes (127 tests). Every condition has passing and failing fixtures.
  - **Next:** author opens and merges the pull request from `robbie/wizardly-dijkstra-2sjib7`. Then S3 (validator). S3 should build on `src/csr/schema.py` (`load_yaml_file`, `check`, `is_pointer`) and `src/csr/taxonomy.py` (`load_all`), and can reuse the fixtures in `tests/fixtures/schema/`.
  - **Blockers:** none.
  - **Decisions for the author to confirm** (not fixed by the spec; taken from the Draft and Reference wireframes where possible): `terms_of_use` has `type` (`open-licence`, `service-terms`, `commercial-terms`, `other`) plus `licence` (SPDX) or `url`, and an optional `summary`; `contact.value` must be an email for `role-mailbox` and an HTTPS URL for `web-form`; `sources[]` items have `url`, `title`, `accessed` and optional `publisher`; `charging.model` is `recharge`, `subscription`, `per-transaction` or `other`; `interfaces[].type` is `rest`, `soap`, `graphql`, `file`, `event` or `other`; `related_assets[]` items have `id` and an optional `relationship` (`replaced-by`, `replaces`, `uses`, `used-by`, `alternative`, `related`); `adopters[]` items have `organisation` and `evidence`; `confirmation.method` and `.reference` are free text; URLs must be HTTPS in the schema as well as in R18. Taxonomy definitions and synonyms are drafts for the working group.
  - **Pull request title:** Add the descriptor schema and draft taxonomy (S2)
  - **Pull request description:**

    > ## What this changes
    >
    > Adds schema version 0.1 of `solution.yml` and the draft taxonomy (slice S2 of `docs/build/PLAN.md`).
    >
    > - `schema/asset.schema.json`: every field in specification 6.4 and its eight conditions. The sentinel `not-publicly-stated` is accepted only in demonstration records, and fields the register derives at build time are rejected.
    > - `schema/pointer.schema.json` for owner-hosted records, `schema/taxonomy.schema.json`, and `schema/README.md` listing the conditions and validation rules.
    > - `taxonomy/`: 8 sectors, 14 service areas and 14 capabilities, each with a label, definition, synonyms and status.
    > - `src/csr/schema.py` and `src/csr/taxonomy.py`: loaders that the validator (S3) builds on.
    > - Tests, with a passing and a failing fixture for every condition.
    >
    > ## Why
    >
    > Specification 6.4 and 6.5. The validator, the site and the draft form all depend on the schema and taxonomy.
    >
    > Field details the specification leaves open are listed under "Decisions for the author to confirm" in the S2 entry of the build plan's progress log.
    >
    > ## How it was tested
    >
    > `pip install -e .[dev]` and `pytest -q` (127 passed) on Python 3.12.
    >
    > ## Checklist
    >
    > - [x] `CHANGELOG.md` updated under Unreleased
    > - [x] No secrets or personal data
- 2026-11-02 — S2 merged. Author: the S2 schema choices should all be reviewed as part of the demonstrator; S16 lists them in `docs/decision-points.md`.
- 2026-11-02 — S3a and S3b done: `csr validate [path-or-url ...] [--base REF] [--check-links] [--format text|json|github]`. `src/csr/records.py` (reading files, URLs and `records/`; YAML errors and repeated keys reported), `findings.py` (rule, severity, field, message, fix), `rules.py` (R02–R07, R09–R12, R18), `links.py` (R08, R19, warnings only, behind `--check-links`), `validate.py` (schema, R01 file name and uniqueness, `--base`). With no targets it checks `records/` and the root `solution.yml`. R13 is a `pytest` test (S3c).
- 2026-11-02 — S3c done: `tests/test_rules.py` (each rule, pass and fail), `tests/test_validate.py` (R01 in the register, `--base` against a temporary git repository, YAML errors and repeated keys, pointer and URL targets, R08 and R19 with a fake network, CLI formats and exit codes), `tests/test_vendor.py` (R13: `SHA256SUMS` beside each vendored package; nothing vendored yet, so its hash check is skipped until S5). `site.yml` `Validate` job now also runs `csr validate --base origin/<base>` on pull requests (full history checked out).
- 2026-11-02 — **S3 ready for pull request.**
  - **Done:** S3a–c. `pytest -q`: 186 passed, 1 skipped (R13 hash check, nothing vendored). `csr validate --base origin/main` passes (no records yet).
  - **Next:** author opens and merges the pull request from `robbie/wizardly-dijkstra-2sjib7`. Then S4 (owner and example records). S5 must write `src/csr/static/vendor/sgds/4.3.0/SHA256SUMS` (format of `sha256sum`) so R13 covers the design system; S9 does the same for Ajv and `js-yaml`.
  - **Blockers:** none.
  - **Interpretations for the decision-points review (S16):** R02 lets `withdrawn` records use either ID range (spec 5.1); `--base` reports a record added on the branch whose id the base branch has since taken (the concurrent-pull-request case); R07 flags `firstname.lastname@` addresses unless either part is a role word; R08 checks codebase repository and `publiccode.yml` URLs, demonstration `sources[]` URLs and pointer sources; R09 checks values that start with `TODO`, not `TODO` inside text; R18 is also enforced by the schema, so a non-HTTPS URL gives two findings; schema messages are those of the `jsonschema` library and may need plainer wording for the validate page (S10). With no targets, `csr validate` checks `records/` and the root `solution.yml`; `examples/hosted/` is left to the harvester, because `csr-9007` fails on purpose.
  - **Pull request title:** Add the csr validate command (S3)
  - **Pull request description:**

    > ## What this changes
    >
    > Adds the validator (slice S3 of `docs/build/PLAN.md`).
    >
    > - `csr validate [path-or-url ...]` checks the register's records, or given files and HTTPS URLs, against the schema and the rules in appendix C: R01 to R07, R09 to R12 and R18, with R08 and R19 behind `--check-links` (warnings only).
    > - `--base REF` reports a new record whose id the base branch has already taken.
    > - Each finding gives the rule, field, message and a fix, as text, JSON or GitHub annotations. The exit status is 1 when there are errors.
    > - R13 is a `pytest` test of the hashes of vendored files, ready for S5 and S9.
    > - The `Validate` job now also runs `csr validate`, with `--base` on pull requests.
    >
    > ## Why
    >
    > Appendix C. Every later slice (records, harvester, site, validate page) relies on the validator.
    >
    > Interpretations of the rules are listed in the S3 entry of the build plan's progress log, for the decision-points review.
    >
    > ## How it was tested
    >
    > `pytest -q` (186 passed, 1 skipped until files are vendored in S5) and `csr validate --base origin/main` on Python 3.12. Each rule has passing and failing tests; `--base` is tested against a temporary git repository, and the network rules with a fake network.
    >
    > ## Checklist
    >
    > - [x] `CHANGELOG.md` updated under Unreleased
    > - [x] No secrets or personal data
    > - [x] Actions pinned by SHA
