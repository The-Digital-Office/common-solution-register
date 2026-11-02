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
| S9 | Draft form, part 2: vendored Ajv (`js-yaml` was vendored in S8 for the preview); full validation; error summary and inline errors; copy, download, issue and email hand-off | 6.6, 6.9 | a) validation; b) hand-off | Parity rows for the form pass |
| S10 | Validate page: paste, upload and URL modes; results table | 6.8, 6.13 | a) modes; b) results | Matches wireframe, with real validation |
| S11 | Harvester: pointer records, fetch limits, owner match, last-valid state, harvest report; `publiccode-parser-go` for each codebase; R14–R17 | 6.11 | a) fetch and owner match; b) state; c) parser; d) report page | Harvest of `csr-0001` and the examples behaves as specified |
| S12 | Tools: `csr import-publiccode --to/--new`, `move-to-source`, `move-to-local`, `new --from-issue` | 6.6, 6.12, Appendix A | a) importer; b) move commands | Tests for each command |
| S13 | Workflows and community files: daily and on-demand harvest, deploy (disabled until `PAGES_ENABLED`), concurrency; reusable `validate-solution.yml`; issue forms (`suggest-asset.yml` must use the field ids the draft form pre-fills: `solution-yml`, `asset-name`, `organisation`, `contact`); pull request template | 6.10, 6.6 | a) workflows; b) forms and template | Workflows pass; deploy is skipped |
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
- 2026-11-02 — S3 merged. S4 inputs from the author: `csr-0002` passes inclusion test 1 (include it); contact for `csr-0001` and `csr-0002` is the repository's issues page (`web-form`) until a role mailbox is chosen (spec I3).
- 2026-11-02 — S4a done: root `solution.yml` (`csr-0001`, owner-confirmed, `service`, `in-development` because the site is not yet published, so condition 7 does not yet require `service_url`) and pointer `records/csr-0001.yaml`; `records/csr-0002.yaml` (pattern, two codebases), described only from the two repositories' own README and GOVERNANCE files. Neither codebase has a usable `publiccode.yml` (`.github` has none; `repository-template`'s is the template with placeholders), so `csr-0002` gives two R12 warnings.
- 2026-11-02 — S4b done: `records/csr-9001`–`csr-9005` (local examples), pointers `csr-9006` and `csr-9007`, and `examples/hosted/csr-9006/solution.yml` (valid) and `examples/hosted/csr-9007/solution.yml` (fails on purpose: schema, R03, R09, R10, R18). `tests/test_records.py` checks the record set, pointer id and owner match, what each example exercises, and the currency states.
- 2026-11-02 — **S4 ready for pull request.**
  - **Done:** S4a–b. `pytest -q`: 206 passed, 1 skipped (R13, nothing vendored). `csr validate --base origin/main`: 10 files, 0 errors, 2 warnings (R12 on `csr-0002`). `csr-9007`'s hosted file fails as intended.
  - **Next:** author opens and merges the pull request from `robbie/wizardly-dijkstra-2sjib7`. Then S5 (walking skeleton).
  - **Blockers:** none.
  - **For the author:**
    - **Currency drifts with time.** The fictional confirmation dates show `due` (`csr-9004`, 2025-12-01) and `stale` (`csr-9003`, 2025-09-02) as of 2 November 2026. `csr-9004` becomes stale after 1 December 2026, and the current examples become due 11 months after their dates. `test_example_currency_states` uses a fixed date, so it will not catch this. Before publication, move the dates forward, or decide in S6 to compute example currency against a fixed date in `site.toml`. Add to the S16 runbook either way.
    - **`csr-0002` intended adopters** are `local-government` only, as the Digital Office's own audience; widen if the offer is to the whole public sector.
    - **`csr-0002` R12 warnings** stay until `.github` and `repository-template` have their own `publiccode.yml` describing those repositories (the template's file describes the repositories created from it).
    - **`csr-0001` status** is `in-development` until the site is published; then change it to `beta` and add `service_url` and `service_page_url` (condition 7).
    - **Contact** for `csr-0001` and `csr-0002` is the issues page until a role mailbox is chosen (I3).
  - **Pull request title:** Add the owner and example records (S4)
  - **Pull request description:**

    > ## What this changes
    >
    > Adds the register's first records (slice S4 of `docs/build/PLAN.md`).
    >
    > - `solution.yml`: this demonstrator as a common solution (`csr-0001`, a service whose codebase is this repository), registered by the pointer `records/csr-0001.yaml`.
    > - `records/csr-0002.yaml`: the Digital Office repository baseline, a pattern with two codebases.
    > - Fictional examples `csr-9001` to `csr-9007`, each showing a condition or state from specification 5.2, including two owner-hosted examples under `examples/hosted/`. `csr-9007`'s file fails validation on purpose.
    > - Tests of the record set and what each example shows.
    >
    > ## Why
    >
    > Specification 5.1 and 5.2. The site, harvester and UI tests need records to work with.
    >
    > Points for the author's review (currency drift in the example dates, `csr-0002`'s intended adopters and warnings, `csr-0001`'s status, the contact) are in the S4 entry of the build plan's progress log.
    >
    > ## How it was tested
    >
    > `pytest -q` (206 passed, 1 skipped until files are vendored in S5) and `csr validate --base origin/main` (0 errors; 2 expected warnings on `csr-0002`) on Python 3.12.
    >
    > ## Checklist
    >
    > - [x] `CHANGELOG.md` updated under Unreleased
    > - [x] No secrets or personal data
- 2026-11-02 — S4 merged.
- 2026-11-02 — S5a done: `tools/vendor-sgds.py` downloads `@scottish-government/design-system@4.3.0` from npm, checks the npm integrity hash, and writes `design-system.min.css`, `design-system.js` (the package's `main`: an ES module bundle that sets `window.DS`), `LICENSE.txt`, `SOURCE.md` and `SHA256SUMS` to `src/csr/static/vendor/sgds/4.3.0/`; R13 now checks them. `.gitattributes` keeps vendored files byte for byte.
- 2026-11-02 — S5b–d done (one commit): `site.toml`; `src/csr/config.py`; `src/csr/register.py` (records with derived fields: hosting, currency and next due date, last changed and merged-in pull request from git, history URL; pointers whose source is a file in this repository are read from the working tree, other sources wait for the harvester; invalid or mismatched sources are not published); `src/csr/build.py` and `csr build [--out] [--base-url] [--date]`; templates `base.html`, `partials/` (header with the design system's mobile menu, banner, footer, tags, values), `index.html` (full list without JavaScript; filters and sort generated with counts but hidden until S7), `record.html`, `record-withdrawn.html`; `static/csr.css`; `static/js/init.js`; `docs/ui-requirements.md` (departures D1–D9); `tests/test_build.py`; `site.yml` builds the site and uploads the `site-preview` artifact. Checked in Chromium at 1280 and 375 pixels: no console errors, mobile menu opens and closes.
- 2026-11-02 — **S5 ready for pull request.**
  - **Done:** S5a–d. `pytest -q`: 223 passed. `csr validate --base origin/main`: 0 errors, 2 warnings. `csr build --base-url http://localhost:8000/`: 9 pages; `csr-9007` not published.
  - **Next:** author opens the pull request from `robbie/wizardly-dijkstra-2sjib7`, checks the `site-preview` artifact against the wireframes, decides D1–D9 in `docs/ui-requirements.md`, and merges. Then S6 (remaining static pages, API and CSV). S6 must build the pages the record page already links to (`sectors/`, `service-areas/`, `capabilities/<id>/`, `contribute/#corrections` and `#removal`, `reference/publiccode/`, `api/v0/assets/<id>.json`, `harvest/`), and decide how example currency avoids drift (S4 note).
  - **Blockers:** none.
  - **For the author:** the departures D1–D9 in `docs/ui-requirements.md`, especially D1 (banner wording: specification 6.8 and the wireframes disagree), D2 and D3 (the three record wireframes disagree with each other, so one template takes their union) and D5 (no web font: Roboto from Google Fonts would send visitors' addresses to a third party). The site must be served over HTTP to see it locally, because its scripts are JavaScript modules (README).
  - **Pull request title:** Add the site generator, layout, home and record pages (S5)
  - **Pull request description:**

    > ## What this changes
    >
    > Adds the walking skeleton of the site (slice S5 of `docs/build/PLAN.md`).
    >
    > - Vendors the Scottish Government Design System 4.3.0 (CSS, JavaScript and licence, unchanged from the npm package, with `SOURCE.md` and pinned hashes checked by R13), and the script that refreshes it.
    > - `csr build` generates the site from the register, configured by `site.toml`. Owner-hosted records whose `solution.yml` is in this repository are read at build time; a source that fails validation (`csr-9007`) is not published.
    > - Base layout: the design system's site header with its mobile menu, the demonstrator banner and the footer.
    > - Home page: the full list of records, which works without JavaScript. The filters and sort are generated with their counts and hidden until S7 makes them work.
    > - Record pages, one template for every provenance, hosting, status and currency, plus the withdrawn-record page and a downloadable `solution.yml` for each record.
    > - `docs/ui-requirements.md` records how the build applies the wireframes, and nine departures for the author to decide.
    > - The `Validate` job builds the site and uploads it as the `site-preview` artifact.
    >
    > ## Why
    >
    > Specification 6.2, 6.8 and 6.13: something to see early, on which the remaining pages are built.
    >
    > Points for review are the departures D1 to D9 in `docs/ui-requirements.md`: the banner wording, the record page sidebar and sections where the three record wireframes differ, and the font.
    >
    > ## How it was tested
    >
    > `pytest -q` (223 passed), `csr validate --base origin/main` and `csr build` on Python 3.12. The built site was checked in Chromium at 1280 and 375 pixels: no console errors, and the mobile menu opens and closes. Compare the `site-preview` artifact with `ui/baseline/`.
    >
    > ## Checklist
    >
    > - [x] `CHANGELOG.md` updated under Unreleased
    > - [x] No secrets or personal data
    > - [x] Actions pinned by SHA
- 2026-11-02 — S5 merged; author confirmed the site runs locally.
- 2026-11-02 — S6a–c done (one commit). Pages: `browse/`, every term page under `sectors/`, `service-areas/` and `capabilities/`, `contribute/`, `about/`, `accessibility/`, `privacy/`, `404.html` (root-relative links), `reference/` (generated from the schema, with all 19 rules from `csr.rules.RULES`), `reference/publiccode/` (the real files as the worked example), `data/`, `currency/`. `src/csr/api.py`: `api/v0/index.json`, `assets.json`, `assets/<id>.json`, `taxonomy/<name>.json`, `schema/*.schema.json`, `data/register.json`, `data/register.csv` (dotted columns, `; `-joined value lists, compact JSON for lists of objects). `site.toml` gains `currency.examples_as_of` (fixes the example currency drift noted in S4) and `[publication]` (inputs I3, I4, I8 and the statements' dates and contacts; pages show a highlighted placeholder until filled, and `csr build` lists them). `solution.yml` gains `open_data` (the register's own data page). Departures D10–D15 added to `docs/ui-requirements.md`. Checked in Chromium at 1280 and 375 pixels: no errors, no horizontal overflow; no broken internal links except to `draft/`, `validate/` and `harvest/` (later slices).
- 2026-11-02 — **S6 ready for pull request.**
  - **Done:** S6a–c. `pytest -q`: 255 passed. `csr validate --base origin/main`: 0 errors, 2 warnings. `csr build`: 55 pages, the API and the extracts.
  - **Next:** author opens and merges the pull request from `robbie/wizardly-dijkstra-2sjib7`. Then S7 (search, filters and sort).
  - **Blockers:** none.
  - **For the author:** D10–D15 in `docs/ui-requirements.md`, especially D10 (fictional examples judged as on a fixed date) and D11 (publication inputs: fill in `contact_mailbox` and `[publication]` in `site.toml` before publication; the site shows highlighted placeholders until then).
  - **Pull request title:** Add the remaining pages, the API and the extracts (S6)
  - **Pull request description:**

    > ## What this changes
    >
    > Builds every remaining page in the page-to-template map, the API and the bulk extracts (slice S6 of `docs/build/PLAN.md`).
    >
    > - Browse, and a page for every sector, service area and capability, with counts and related terms.
    > - Contribute, About, Accessibility, Privacy and Not found. Inputs not yet decided (the role mailbox, the feedback route, the Data Protection Officer's details and the statements' dates) come from a new `[publication]` section of `site.toml`; until they are filled in, the pages show a highlighted placeholder and `csr build` lists them.
    > - Field reference, generated from the schema; Solutions and codebases, with this demonstrator's own files as the worked example; Data and API, with file sizes and a real sample response; and Currency.
    > - `api/v0/` (index, all records, each record, taxonomies and schemas), `data/register.json` and `data/register.csv`.
    > - `examples_as_of` in `site.toml`, so the fictional examples keep showing the current, due and stale states they were written to show.
    > - `docs/ui-requirements.md` gains departures D10 to D15 for the author to decide.
    >
    > ## Why
    >
    > Specification 6.8 and 6.13: every page in the map, and the open data and API.
    >
    > ## How it was tested
    >
    > `pytest -q` (255 passed), `csr validate --base origin/main` and `csr build` on Python 3.12. Tests check that every page in the map is built, that internal links resolve, and that published records still match the schema. The site was checked in Chromium at 1280 and 375 pixels with no errors or horizontal overflow.
    >
    > ## Checklist
    >
    > - [x] `CHANGELOG.md` updated under Unreleased
    > - [x] No secrets or personal data
- 2026-11-02 — S6 merged. **Author:** UI decisions (the departures in `docs/ui-requirements.md`) are deferred until leaving them would make change harder. The build flags that point; expected before S14, whose visual baselines would lock the pages in.
- 2026-11-02 — S7a–c done (one commit): `static/js/search-core.js` (pure functions: URL state, word-prefix matching, faceted counts, sorting) and `static/js/search.js` (wires them to the page; announces the count through a status message after typing pauses); the home page renders every record with withdrawn ones hidden, embeds a search index, and hides search, filters and sort without JavaScript; `tests/js/search-core.test.mjs` run by `tests/test_js.py`. Parity rows 1 to 6 checked in Chromium with a scripted run (the committed Playwright tests come in S14). Departures D16–D18 added.
- 2026-11-02 — **S7 ready for pull request.**
  - **Done:** S7a–c. `pytest -q`: 256 passed (including the JavaScript tests). `csr validate --base origin/main`: 0 errors, 2 warnings. `csr build`: 55 pages.
  - **Next:** author opens and merges the pull request from `robbie/wizardly-dijkstra-2sjib7`. Then S8 (draft form, part 1).
  - **Blockers:** none.
  - **Pull request title:** Add search, filters and sorting to the home page (S7)
  - **Pull request description:**

    > ## What this changes
    >
    > Makes the home page's search, filters and sort work (slice S7 of `docs/build/PLAN.md`; parity rows 1 to 6 of specification 6.13).
    >
    > - Search as you type, matching the start of words in each record's name, summary, owner, purpose, ID and asset type, and the labels and synonyms of its taxonomy terms.
    > - Provenance, asset type, sector, service area, capability, currency and withdrawn filters, each with counts that reflect the query and the other filters.
    > - Sort by name, recently changed or recently confirmed.
    > - The query, filters and sort are kept in the address, so results can be shared; Clear all filters resets them; the result count is announced to screen readers once typing pauses.
    > - Without JavaScript the full list is shown, and search, filters and sort are hidden.
    > - The logic is in a small module of pure functions with unit tests, which `pytest` runs with Node's built-in test runner.
    > - `docs/ui-requirements.md` gains departures D16 to D18.
    >
    > ## Why
    >
    > Specification 6.13: the wireframe shows these controls, and the parity table requires them to work, with counts, and the page to work without JavaScript.
    >
    > ## How it was tested
    >
    > `pytest -q` (256 passed) and `csr build` on Python 3.12 and Node 22. Each of parity rows 1 to 6 was checked in Chromium against the built site, with JavaScript on and off; the committed browser tests come in S14.
    >
    > ## Checklist
    >
    > - [x] `CHANGELOG.md` updated under Unreleased
    > - [x] No secrets or personal data
- 2026-11-02 — S7 merged.
- 2026-11-02 — S8a–c done (one commit). `src/csr/form.py` (options and limits from the schema, with the wireframe's labels); `templates/draft.html` (generated from the schema and taxonomy: every option list, length limit and taxonomy term; conditional sections for conditions 1 and 3 to 8, condition 2 written automatically; repeaters for interfaces, sources, codebases and open data); `static/js/draft-core.js` (pure: answers to record in schema order, sections shown, record back to answers for "Suggest a correction", keeping fields the form does not show) and `static/js/draft.js` (repeaters, conditions, live preview, `?from=<id>` pre-fill); `js-yaml` 5.5.0 vendored for the preview (moved forward from S9; `tools/vendor-sgds.py` generalised to `tools/vendor.py`); the design system's character count initialised; `tests/js/draft-core.test.mjs` and `tests/test_draft.py`. Checked in Chromium: every condition, repeaters, start again, pre-fill from `csr-9003` and `csr-9005`, 375 pixels, no JavaScript. Departures D19–D22 added.
- 2026-11-02 — **S8 ready for pull request.**
  - **Done:** S8a–c. `pytest -q`: 270 passed. `csr validate --base origin/main`: 0 errors, 2 warnings. `csr build`: 56 pages.
  - **Next:** author opens and merges the pull request from `robbie/wizardly-dijkstra-2sjib7`. Then S9: Ajv, full validation with the error summary and inline errors (each control carries the field it fills, so schema errors can be placed), and the hand-off (copy, download, GitHub issue, email; Copy and Download are inert until then). S9 also decides how validation treats the `csr-NNNN` placeholder id.
  - **Blockers:** none.
  - **Pull request title:** Add the draft form with conditional sections and a live preview (S8)
  - **Pull request description:**

    > ## What this changes
    >
    > Adds the first part of the draft form at `draft/` (slice S8 of `docs/build/PLAN.md`).
    >
    > - The form is generated at build time from the schema and the taxonomy: every option list, length limit and taxonomy term comes from them, with the Draft wireframe's labels and layout.
    > - Conditional sections for the conditions in specification 6.4: sources and "not stated in public sources" for people who are not from the owning organisation, interfaces for APIs, support for live and beta services and platforms, charging details, deprecation, and withdrawal when correcting a withdrawn record. The owner's confirmation is written automatically.
    > - Add and remove codebases, open data links, interfaces and sources.
    > - A live, complete `solution.yml` preview, written with the vendored `js-yaml` 5.5.0 (moved forward from S9).
    > - "Suggest a correction" fills the form from the record, and keeps fields the form does not show.
    > - The logic is in a module of pure functions with unit tests, run by `pytest` through Node's test runner.
    > - Validation and the hand-off (copy, download, GitHub issue and email) follow in S9.
    >
    > ## Why
    >
    > Specification 6.2, 6.6 and 6.13: a friendly route to a valid record for people who do not use GitHub.
    >
    > ## How it was tested
    >
    > `pytest -q` (270 passed) and `csr build` on Python 3.12 and Node 22. Every condition, the repeaters, the preview and the pre-fill were checked in Chromium at 1280 and 375 pixels, and without JavaScript.
    >
    > ## Checklist
    >
    > - [x] `CHANGELOG.md` updated under Unreleased
    > - [x] No secrets or personal data
- 2026-11-02 — S8 merged; author confirmed the draft form runs locally.
- 2026-11-02 — S9a done: Ajv 8.17.1 vendored (`ajv-dist`, the Ajv project's browser bundle; `LICENSE` from `ajv@8.17.1`, as `ajv-dist` has none; `tools/vendor.py` can take a file from a second package); `static/js/record-check.js` (Ajv against the real schema, embedded in the page; plain messages, one per field; R06 and R09; `csr-NNNN` accepted as the draft id), checked against every schema fixture in `tests/js/record-check.test.mjs`; error summary and inline errors in `draft.js`, placed by schema path (`buildDraft` reports which form group each list entry came from). Schema fix: condition 1's `if` now requires `record_status`. `csr validate` accepts `csr-NNNN` outside `records/` with an R01 warning, so the browser and the command line agree.
- 2026-11-02 — S9b done: Copy YAML, Download (`solution.yml`), Open as a GitHub issue (new tab; pre-fills `solution-yml`, `asset-name`, `organisation` and `contact`; over about 8 KB the file is downloaded to attach instead), Send by email (downloads the file, then a `mailto:` with a subject and a two-line body; shown only when `contact_mailbox` is set). Every hand-off validates first. Checked in Chromium, including a build with a mailbox configured; the downloaded file passes `csr validate`. Departures D23–D27 added.
- 2026-11-02 — **S9 ready for pull request.**
  - **Done:** S9a–b. `pytest -q`: 273 passed. `csr validate --base origin/main`: 0 errors, 2 warnings. `csr build`: 56 pages.
  - **Next:** author opens and merges the pull request from `robbie/wizardly-dijkstra-2sjib7`. Then S10 (validate page), which can reuse `record-check.js` and the vendored Ajv and `js-yaml`.
  - **Blockers:** none.
  - **Pull request title:** Add validation and the hand-off to the draft form (S9)
  - **Pull request description:**

    > ## What this changes
    >
    > Completes the draft form (slice S9 of `docs/build/PLAN.md`).
    >
    > - Validation in the browser against the real schema, with the vendored Ajv 8.17.1 (JSON Schema 2020-12) runtime, plus rules R06 and R09. Problems are shown in the design system's error summary, in the order of the form, and inline on each field, with one plain message per field.
    > - Copy YAML and Download (`solution.yml`).
    > - Open as a GitHub issue: opens in a new tab, pre-filling the `suggest-asset.yml` form. A draft too long for GitHub's address limit is downloaded to attach instead.
    > - Send by email: downloads the file and opens an email with a subject and a two-line body asking for it to be attached. It appears once the role mailbox is set in `site.toml`.
    > - Every hand-off checks the draft first, so every route produces a validated record.
    > - `csr validate` accepts the draft's placeholder id `csr-NNNN` outside `records/`, with a warning, so a file that passes in the browser also passes on the command line.
    > - Fixes schema condition 1, which asked for sources when `record_status` was missing.
    > - `docs/ui-requirements.md` gains departures D23 to D27.
    >
    > ## Why
    >
    > Specification 6.6, 6.9 and 6.13: the form validates every field against the schema, with an error summary and inline errors, and its hand-off routes work.
    >
    > ## How it was tested
    >
    > `pytest -q` (273 passed), including JavaScript tests that check the browser validator agrees with the Python one on every schema fixture. In Chromium: the error summary and inline errors, focus, copy, download, the issue link (and the too-long case), and email on a build with a mailbox configured; the downloaded file passes `csr validate`.
    >
    > ## Checklist
    >
    > - [x] `CHANGELOG.md` updated under Unreleased
    > - [x] No secrets or personal data

