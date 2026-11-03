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
- 2026-11-02 — S9 merged. Author will check the build locally after the next couple of slices.
- 2026-11-02 — S10a–b done (one commit). `templates/validate.html` and `static/js/validate.js`: paste, upload and URL modes (HTTPS only, the harvest size limit, a plain message when a host refuses cross-site reads), `?url=` to open URL mode, YAML 1.1 parsing to match `csr validate` (dates kept as written), pointer records checked against the pointer schema; a results table of severity, rule, field and "problem and fix". `record-check.js` gains R02, R03, R04, R05, R07, R11, R12 and R18 with fix texts; `tests/js/record-check.test.mjs` now checks, against `tests/js_corpus.py`, that the browser finds exactly what `csr validate` finds, rule by rule and field by field, on every schema fixture, every record and each rule's trigger. R18 (Python and JavaScript) now skips the sentinel, which is R10's concern. Checked in Chromium: every mode, pass, warnings only, pointer, YAML errors, no JavaScript, 375 pixels. Departures D28–D30 added.
- 2026-11-02 — **S10 ready for pull request.**
  - **Done:** S10a–b. `pytest -q`: 276 passed. `csr validate --base origin/main`: 0 errors, 2 warnings. `csr build`: 57 pages.
  - **Next:** author opens and merges the pull request from `robbie/wizardly-dijkstra-2sjib7`. Then S11 (harvester), a larger slice with four checkpoints; it brings the harvest report page, the harvest state that record pages and the Data page already mention, and the official `publiccode-parser-go`.
  - **Blockers:** none.
  - **Pull request title:** Add the validate page (S10)
  - **Pull request description:**

    > ## What this changes
    >
    > Adds the validate page at `validate/` (slice S10 of `docs/build/PLAN.md`).
    >
    > - Paste a `solution.yml`, upload one, or give the URL of a hosted one (where the host allows cross-site reads, as raw GitHub files do). `?url=` opens the page in URL mode and checks that address.
    > - Checks run in the browser: the schema, with the vendored Ajv, and every validation rule that needs no network (R02 to R07, R09 to R12 and R18). Pointer records are checked against the pointer schema.
    > - Results in the wireframe's table: severity, rule, field, and the problem with its fix, errors first. A file with only warnings is shown as valid, with its warnings.
    > - A JavaScript test checks that the browser finds exactly what `csr validate` finds, rule by rule and field by field, on every schema fixture, every register record and a trigger for each rule.
    > - R18 no longer also reports "not stated in public sources" as a bad address; that is R10's finding.
    > - `docs/ui-requirements.md` gains departures D28 to D30.
    >
    > ## Why
    >
    > Specification 6.8 and 6.13: owners can check their own file before registering or hosting it, with real validation.
    >
    > ## How it was tested
    >
    > `pytest -q` (276 passed) on Python 3.12 and Node 22. In Chromium, each mode, a passing file, a file with only warnings, a pointer, broken YAML, a URL whose host refuses cross-site reads, without JavaScript, and at 375 pixels.
    >
    > ## Checklist
    >
    > - [x] `CHANGELOG.md` updated under Unreleased
    > - [x] No secrets or personal data
- 2026-11-03 — S10 merged.
- 2026-11-03 — S11a done: `src/csr/harvest.py` fetches each pointer's source over HTTPS within the size limit and timeout, refusing redirects to non-HTTPS addresses (R15); sources in this repository are read from the working tree; checks R14 (id and owner match), R16 (owner-hosted status) and the schema and rules; `tests/test_harvest.py` with a fake network.
- 2026-11-03 — S11b done: harvest state (`state_version` 1): per source its state (`ok`, `failing`, `unavailable`, `not-harvested`), `checked_at`, `harvested_at`, `content_hash`, `last_changed`, `last_valid` (the published copy), `failing_since`, `unavailable_since` and findings; a changed source or owner starts afresh. `csr harvest [--state PATH-OR-URL] [--out] [--only ID ...] [--no-network]` reads the previous state (default `state_url`; unreadable means starting fresh) and writes `.harvest/harvest-state.json` (ignored by git). `csr build --harvest PATH` publishes owner-hosted records from their last valid copy and writes `api/v0/harvest-state.json`; without a state it harvests this repository's sources without the network, as before. The API gains `source_state`, `harvested_at` and `content_hash`.
- 2026-11-03 — S11c done: `tools/install-publiccode-parser.py` installs publiccode-parser-go v5.4.3 (EUPL-1.2; released 6 August 2026) for Linux or macOS, checking the SHA-256 pinned from the release's `checksums.txt`, into `.tools/` (ignored by git; the binary is not committed). The harvester finds it there, through `CSR_PUBLICCODE_PARSER`, or on the path, and runs it with `-json -no-network` on every `publiccode.yml` linked from a local record or a harvested copy; verdicts (`valid`, `invalid`, `unavailable`, `not-checked`) are kept in the state under `publiccode`, and an invalid one gives an R17 warning on a harvested record. The parser was not run in this session (running a downloaded binary is not permitted here); its interface was taken from its source at v5.4.3, the tests use a stand-in, and one test uses the real parser where it is installed. The `Validate` job now installs it, harvests this repository's sources and builds from the state, so CI exercises the real parser.
- 2026-11-03 — S11d done: `templates/harvest.html` (last run, registered sources, a row per source with its state, problems per source with findings, sources unavailable for more than 7 days flagged for a maintainer, link to the state); record pages show the harvest state (passed, failing since, unavailable since; "Last harvested"), and every codebase's parser verdict; the Publiccode page's worked example and the Data page's state link use the state. `src/csr/messages.py` puts schema problems in plain words for `csr validate` and the report, word for word as the browser does (checked by the JavaScript parity test). Departures D6, D7 and D13 resolved; D31 and D32 added.
- 2026-11-03 — **S11 ready for pull request.**
  - **Done:** S11a–d. `pytest -q`: 310 passed, 1 skipped (the real-parser test, which runs where the parser is installed, as in CI). `csr harvest --no-network`: `csr-0001` ok, `csr-9006` ok, `csr-9007` failing (never published), as specified. `csr build --harvest .harvest/harvest-state.json`: 58 pages.
  - **Next:** author opens and merges the pull request from `robbie/wizardly-dijkstra-2sjib7`, and checks in the pull request's `Validate` run that the parser installs and the real-parser test passes. Then S12 (tools: import-publiccode, move-to-source, move-to-local, new --from-issue).
  - **Blockers:** none. The real parser was not run in the session (running a downloaded binary is not permitted there); the first run is in CI.
  - **For S13:** the daily and on-demand harvest workflow runs `python tools/install-publiccode-parser.py`, `csr harvest` (previous state from `state_url`, with the network), and `csr build --harvest .harvest/harvest-state.json`; pull requests run `csr harvest --only <added or changed pointers>` with the network to fetch and check a newly registered source (specification 6.12 step 3); the harvest report can also be written to the job summary.
  - **Pull request title:** Add the harvester and the harvest report (S11)
  - **Pull request description:**

    > ## What this changes
    >
    > Adds harvesting of owner-hosted records (slice S11 of `docs/build/PLAN.md`; specification 6.11).
    >
    > - `csr harvest` fetches each pointer's registered source over HTTPS only, within the size limit and timeout, refusing redirects to addresses that are not HTTPS (R15). Sources in this repository are read from the working tree, so a pull request is checked with its own changes.
    > - Each harvested file is checked for an id and owner that match the registration (R14), a status that may be owner-hosted (R16), and the schema and rules.
    > - Every linked `publiccode.yml` is checked with the official parser, publiccode-parser-go v5.4.3, installed by a new script at a pinned release with verified checksums (R17, a warning). The `Validate` job installs it.
    > - The harvest state keeps each source's last valid copy, content hash and dates. A failing or unavailable source keeps its last valid version published and is flagged; a source that has never passed is not published. The state is read from the live site, starts fresh if it cannot be read, and is published at `api/v0/harvest-state.json`.
    > - `csr build --harvest` publishes from the state. The harvest report page lists every source, its state and its problems, and flags sources unavailable for more than 7 days. Record pages show the harvest state and each codebase's parser verdict.
    > - `csr validate` and the harvest report now describe schema problems in plain words, one per field, word for word as the browser does.
    >
    > ## Why
    >
    > Specification 6.11: owners can publish their own records, protected by validation and the owner match, without maintainer review.
    >
    > ## How it was tested
    >
    > `pytest -q` (310 passed, 1 skipped) on Python 3.12 and Node 22, with a fake network and a stand-in parser for every rule and state transition. The skipped test runs the real parser and runs in CI. The harvest report and record pages were checked in Chromium at 1280 and 375 pixels.
    >
    > ## Checklist
    >
    > - [x] `CHANGELOG.md` updated under Unreleased
    > - [x] No secrets or personal data
    > - [x] Actions pinned by SHA
- 2026-11-03 — S11 merged.
- 2026-11-03 — S12a–b done (one commit; the commands share `src/csr/tools.py`). `csr import-publiccode <url-or-path> --to ID` adds or updates (by repository URL) a codebase from a publiccode.yml, copying `url`, `maintenance.type`, `softwareVersion` and `maintenance.contacts` (name, affiliation, email; never phone), and prints `categories` and `intendedAudience.scope` as hints; `--new [--id]` drafts a record with the next free id, suggesting name, summary, purpose, status, licence, owner, service page, documentation, interfaces (type left as TODO), roadmap, adopters (self-reported) and dependencies, with every unmapped mandatory field TODO (R09 rejects it until filled). `csr move-to-source ID URL` fetches the owner's file and checks it as the harvester does (HTTPS, R14, R16, schema and rules) before writing the pointer; nothing changes if it would not be published. `csr move-to-local ID [--state]` writes the last valid harvested version as a local record. `csr new --from-issue PATH|- [--issue-url]` takes the YAML block from a suggest-asset issue, refuses an id already in the register, allocates the next free id (example range for examples), and records the issue as the confirmation reference. Every command validates what it writes and exits 1 if a maintainer has errors to resolve, 2 if it could not act. `tests/test_tools.py`.
- 2026-11-03 — **S12 ready for pull request.**
  - **Done:** S12a–b. `pytest -q`: 329 passed, 1 skipped (the real-parser test). `csr validate --base origin/main`: 0 errors, 2 warnings.
  - **Next:** author opens and merges the pull request from `robbie/wizardly-dijkstra-2sjib7`. Then S13 (workflows and community files).
  - **Blockers:** none.
  - **For S13:** the `suggest-asset.yml` form's YAML text area should use `render: yaml`, so GitHub fences it and `csr new --from-issue` finds it; its field ids are `solution-yml`, `asset-name`, `organisation` and `contact` (S9). The `move-to-owner-hosting.yml` form asks for the record id and the owner's HTTPS address, which a maintainer passes to `csr move-to-source`. `docs/maintenance.md` (S16) should describe all five commands.
  - **Pull request title:** Add the maintainer tools (S12)
  - **Pull request description:**

    > ## What this changes
    >
    > Adds the maintainer tools (slice S12 of `docs/build/PLAN.md`; specification 6.6, 6.12 and appendix A). Each writes a file in `records/` for a maintainer to review and propose in a pull request, validates it, and says what to check.
    >
    > - `csr import-publiccode <url-or-path> --to csr-NNNN` adds the codebase a `publiccode.yml` describes to a record, or updates it if listed, following appendix A. Phone numbers are never imported.
    > - `csr import-publiccode <url-or-path> --new` drafts a new record with the next free id. Solution fields are suggestions from the codebase's description; anything a person must decide is `TODO`, which validation rejects until filled in.
    > - `csr move-to-source csr-NNNN <url>` fetches the owner's `solution.yml` and checks it as the harvester will (HTTPS, owner match, status, schema and rules) before replacing the local record with a pointer. If the file would not be published, nothing changes.
    > - `csr move-to-local csr-NNNN` replaces a pointer with the last valid version from the harvest state.
    > - `csr new --from-issue` adds the `solution.yml` from a suggest-asset issue as a new record with the next free id, and records the issue as the confirmation reference.
    > - The README lists the commands.
    >
    > ## Why
    >
    > Specification 6.6 (the assisted contribution route), 6.12 (moving records to and from owner hosting) and appendix A (the `publiccode.yml` mapping).
    >
    > ## How it was tested
    >
    > `pytest -q` (329 passed, 1 skipped) on Python 3.12: each command, what it writes and what it refuses, on a copy of the register, with a fake network.
    >
    > ## Checklist
    >
    > - [x] `CHANGELOG.md` updated under Unreleased
    > - [x] No secrets or personal data
- 2026-11-03 — S12 merged.
- 2026-11-03 — S13a done: `site.yml` rewritten for specification 6.10: triggers pull requests, pushes to `main`, `workflow_dispatch` and a daily schedule (05:23 UTC); concurrency per pull request (cancelling) and one queue for `main` (never cancelling a deployment). `Validate` installs the pinned parser, runs `pytest` and `csr validate` (`--base` on pull requests); on pull requests it harvests this repository's sources without the network, then fetches any pointer the pull request adds or changes with `--fail-on-problems` (specification 6.12 step 3); on other triggers it harvests every source from the live state and writes the report to the job summary; it builds from the harvest, uploads a preview on pull requests, and uploads the Pages artifact only when `PAGES_ENABLED` is `true`. `Deploy` (`actions/deploy-pages`) is skipped until then. `Reusable workflow` runs `validate-solution.yml` on this repository's own files at the commit being tested. `validate-solution.yml` (`on: workflow_call`; inputs `path`, `publiccode`, `register-repository`, `register-ref`, default `v0`) checks an owner's `solution.yml` with `csr validate` and any `publiccode.yml` with the official parser. New CLI: `csr harvest --fail-on-problems` (owners' sources only) and `--summary PATH` (Markdown), and `csr check-publiccode PATH`. All actions pinned by SHA.
- 2026-11-03 — S13b done: `.github/ISSUE_TEMPLATE/`: `suggest-asset.yml` (one YAML text area, `render: yaml`, plus `asset-name`, `organisation` and `contact`, the ids the draft form pre-fills), `suggest-correction.yml`, `move-to-owner-hosting.yml` (record id and HTTPS address, with the owner's confirmation), `feedback.yml`; the organisation's `bug_report.yml` and `change_request.yml` copied unchanged (a repository's own forms replace the organisation's); `config.yml` with links to the draft form, validate page and security policy. Every register form says issues are public and carries the OGL statement. `.github/pull_request_template.md` keeps the organisation's sections and checklist word for word and adds a Records section (provenance, sources, OGL and MIT agreement). `tests/test_community_files.py`, including an issue rendered from the form going through `csr new --from-issue`, and every action pinned by SHA.
- 2026-11-03 — **S13 ready for pull request.**
  - **Done:** S13a–b. `pytest -q`: 352 passed, 1 skipped (the real-parser test, which runs in CI).
  - **Next:** author opens the pull request from `robbie/wizardly-dijkstra-2sjib7` and checks it: `Validate` (with the harvest step) and `Reusable workflow / solution.yml` pass; `Deploy` does not run on a pull request. After merging, the push to `main` runs the full harvest and shows `Deploy` as skipped. Then S14 (UI tests). **Before S14 starts, the author should decide the UI departures in `docs/ui-requirements.md`** (D1–D32): S14 approves baselines from the built pages, so later UI changes also mean re-approving baselines.
  - **Blockers:** none.
  - **Author steps from this slice:**
    - Create the labels the register's forms apply (missing labels are not applied): `gh label create "new record" --color 0e8a16`, `gh label create correction --color fbca04`, `gh label create "owner hosting" --color 1d76db`, `gh label create feedback --color c5def5` (with `--repo The-Digital-Office/common-solution-register`).
    - After merging, tag `main` as `v0` (`git tag v0 && git push origin v0`), the version owners' workflows call; move the tag when the reusable workflow or rules change compatibly.
    - At publication (S16): set Settings → Pages → Source to "GitHub Actions" and the repository variable `PAGES_ENABLED` to `true`.
  - **Pull request title:** Add the workflows, issue forms and pull request template (S13)
  - **Pull request description (organisation template):**

    > ## What and why
    >
    > Adds the workflows and community files (slice S13 of `docs/build/PLAN.md`; specification 6.6 and 6.10).
    >
    > - `site.yml` runs on pull requests, pushes to `main`, on demand and daily, with one queue for `main` so a deployment is never cut off. Pull requests harvest the sources in this repository and fetch any pointer they add or change, which must pass before the pull request can merge. Other runs harvest every registered source from the state on the live site and write the harvest report to the job summary. Deployment to GitHub Pages is skipped until the repository variable `PAGES_ENABLED` is `true`.
    > - `validate-solution.yml` is a reusable workflow owners call from their own repositories to check their `solution.yml` and `publiccode.yml`. `site.yml` runs it on this repository's own files.
    > - Issue forms: suggest a solution (pre-filled by the draft form), suggest a correction, host our own solution.yml, and give feedback, each saying issues are public and carrying the Open Government Licence statement. The organisation's bug report and change request are kept, because a repository's own forms replace the organisation's.
    > - A pull request template that keeps the organisation's sections and checklist and adds provenance, sources and the licence agreement.
    > - `csr harvest --fail-on-problems` and `--summary`, and `csr check-publiccode`, for the workflows.
    >
    > ## How it was checked
    >
    > `pytest -q` (352 passed, 1 skipped) on Python 3.12, including tests that the suggest-asset form has exactly the fields the draft form fills in, that an issue rendered from it becomes a valid record, that the pull request template keeps the organisation's, and that every action is pinned by SHA. The workflows themselves run on this pull request.
    >
    > ## Checklist
    >
    > - [x] `CHANGELOG.md` updated under **Unreleased** (if users would notice the change)
    > - [x] Documentation updated (if behaviour or setup changed)
    > - [x] No secrets, credentials or personal data added
    > - [x] `publiccode.yml` still accurate (public software repositories only)
- 2026-11-03 — S13 merged; labels created and `v0` tagged by the author. **Author's decisions (3 November 2026):** UI departures D1–D5 and D19 as recommended (D5: serve Roboto from the site), all others accepted as built; input I3 is the role mailbox `solution-register@digitaloffice.scot` (requested, with an automatic reply), also the feedback route for people without GitHub (I4); reply time 10 working days.
- 2026-11-03 — S14 preparation (one commit): decisions recorded in `docs/ui-requirements.md`; Roboto (300, 400, 400 italic, 700) and Roboto Mono (400), Latin and Latin Extended, vendored from `@fontsource` 5.3.0 (OFL-1.1) with `static/fonts.css`, and used for code and YAML; `site.toml` `contact_mailbox` and `accessibility_reply_days = "10"`; `csr-0001`'s contact is the mailbox (`csr-0002`'s stays the issues page: the mailbox is the register's, not the baseline's). R07 now ignores hyphenated local parts and knows more role words (it flagged `solution-register@`), in Python and the browser alike.
- 2026-11-03 — S14a done: `package.json` and `package-lock.json` (test tooling only: `@playwright/test` 1.63.0, the version installed in the build sessions, and `@axe-core/playwright` 4.14.0; one `playwright-core` through `overrides`); the npm Dependabot entry is back. `ui/tests/fixtures/register/` is a fixed copy of the register plus `csr-0100`, an invented demonstration entry for the tests only, with a harvest state made at a fixed time; `csr build` gains `--root` and `--no-history` so the UI build is the same everywhere (as on 2 November 2026, no git dates). `ui/playwright.config.js` builds it and serves it; `ui/tests/visual.spec.js` compares the 21 wireframe screens (including the draft form's errors and the validate results) at 1280 and 375 pixels with `ui/baseline/`. As section 6.13 says, the baselines started as the approved wireframe images; this pull request replaces each with the built page, so the difference is visible in review, and adds the 375-pixel images (42 in all; repeat runs match). Contribute, About and Not found matched their wireframe images within the 1% tolerance, so `--update-snapshots` left them; they were then replaced too (`--update-snapshots=all`), so every baseline comes from the same renderer. `site.yml` gains the `UI tests` job (Python, Node 22, `npm ci --ignore-scripts`, Chromium, report uploaded on failure); `Deploy` needs it.
- 2026-11-03 — S14b done: `ui/tests/behaviour.spec.js`, one test per row of the parity table (14): search, the two kinds of filter with counts, sort, clear and announced count, without JavaScript, the draft form's conditions, validation, classification, preview and hand-off, the validate page's three modes, record page actions, and the mobile menu. All pass.
- 2026-11-03 — S14c done: `ui/tests/accessibility.spec.js` runs axe-core (WCAG 2.0 to 2.2 A and AA, and best practice) on every page and state, and with the mobile menu open, failing on serious or critical issues and reporting the rest. It found code examples that scroll sideways but could not be focused (serious; now `tabindex="0"` with a name), the phase banner outside any landmark, and unnamed sidebar asides on record pages (both moderate; fixed). No findings remain at any level. The visual baselines are unchanged by the fixes. Departures D33 and D34 added; README and `docs/ui-requirements.md` say how to run and update the tests.
- 2026-11-03 — **S14 ready for pull request.**
  - **Done:** S14 preparation and S14a–c. `npm run test:ui`: 78 passed (42 visual, 14 behaviour, 22 accessibility). `pytest -q`: 356 passed, 1 skipped.
  - **Next:** author opens the pull request from `robbie/wizardly-dijkstra-2sjib7` and checks that `UI tests` passes in CI; then **adds `UI tests` to the "CSR: required checks" ruleset** alongside `Validate`; reviews the baseline images in the pull request's files view (each wireframe image beside the built page); and merges. Then S15 (demonstration records).
  - **Blockers:** none.
  - **Pull request title:** Add the UI tests (S14)
  - **Pull request description (organisation template):**

    > ## What and why
    >
    > Adds the UI tests (slice S14 of `docs/build/PLAN.md`; specification 6.13) and puts the author's UI decisions into effect before the baselines are approved.
    >
    > - Records the author's decisions on the UI departures. Roboto and Roboto Mono are now served from the site itself (decision D5), so no visitor's browser contacts a font service.
    > - Adds the role mailbox `solution-register@digitaloffice.scot` (contact, emailed drafts and feedback without GitHub, 10 working day reply time) and makes it `csr-0001`'s contact. R07 no longer mistakes hyphenated role mailboxes for named people.
    > - Visual comparison of every page at 1280 and 375 pixels with `ui/baseline/`. As the specification describes, the baselines started as the approved wireframe images; this pull request replaces each with the built page, so each change can be reviewed side by side in the files view.
    > - A behaviour test for each of the 14 rows of the parity table, and axe-core on every page. Three accessibility findings were fixed: code examples that scroll sideways can now be reached by keyboard, the phase banner is a named region, and sidebar asides are named.
    > - The tests run on a fixed fixture register, built as on a fixed date, so new records do not change the screenshots. A new required `UI tests` job runs them and uploads the report and image differences on failure. Playwright and axe-core are test tooling only, pinned in `package.json`; Dependabot watches them.
    >
    > ## How it was checked
    >
    > `npm run test:ui`: 78 passed (42 visual, 14 behaviour, 22 accessibility), with no axe-core findings at any level. `pytest -q`: 356 passed, 1 skipped. The `UI tests` job runs on this pull request.
    >
    > ## Checklist
    >
    > - [x] `CHANGELOG.md` updated under **Unreleased** (if users would notice the change)
    > - [x] Documentation updated (if behaviour or setup changed)
    > - [x] No secrets, credentials or personal data added
    > - [x] `publiccode.yml` still accurate (public software repositories only)
- 2026-11-03 — S14 in CI: the first run's `UI tests` failed every visual comparison by about 4% (behaviour and accessibility passed): Chromium's font hinting measured text slightly differently on the runner, so some lines wrapped differently. The test browser now draws text without hinting or subpixel positioning (`ui/playwright.config.js`), the baselines were remade, and the second run passed: `Validate`, `UI tests` (78), `Reusable workflow` and the standards checks green, `Deploy` skipped. The Site workflow gained a manual `update-baselines` option that remakes the baselines in CI and uploads them as the `ui-baselines` artifact, for any future difference between machines.
- 2026-11-03 — S14 merged; author added `UI tests` to the "CSR: required checks" ruleset. Dependabot then proposed `@playwright/test` 1.64.1 (#18): every UI test failed, because `package.json` pins `playwright-core` 1.63.0 through `overrides` and a new Playwright also changes Chromium (and so the baselines). The author closed it. Follow-up (its own pull request, before S15): Dependabot now ignores minor and major Playwright updates; `docs/ui-requirements.md` says how to upgrade deliberately. S16's `docs/maintenance.md` should include it. **Next:** S15.
- 2026-11-03 — **S15a** (checkpoint). `csr-0003` ScotAccount (demonstration, service, `scottish-government`, identity capability, beta so the support condition applies) from two Scottish Government Digital blog posts; terms, charges, support and the service address are `not-publicly-stated`. `docs/demonstration-sources.md` gives field → value → source → supporting words, with rows marked **check** where the author should look at owner pages that answer automated requests with a bot check (`scotaccount.servicemanual.gov.scot`, `www.mygov.scot`). The tools tests now drop demonstration records from their copy of the register, so the next free id they expect stays `csr-0003`. **Done:** csr-0003. **Next:** S15b Scottish Government Design System. **Blockers:** none.
- 2026-11-03 — **S15b** (checkpoint). `csr-0004` Scottish Government Design System (demonstration, standard, open licence MIT, public codebase at version 4.3.0, charging false from the licence's "free of charge", support by the team's mailbox) from the repository's README and licence and the npm package's metadata; `designsystem.gov.scot` has a bot check, so it is linked but not cited. Its codebase has no `publiccode.yml`, so `csr validate` shows an R12 warning, as intended. The home-page test now expects demonstration records after the confirmed and example ones, whatever their number. **Done:** csr-0004. **Next:** S15c One Scotland Gazetteer. **Blockers:** none.
- 2026-11-03 — **S15c** (checkpoint). `csr-0005` One Scotland Gazetteer (demonstration, platform, Improvement Service as a `local-government` owner, data and mapping capabilities, REST and SOAP interfaces) from the Improvement Service's four metadata records on spatialdata.gov.scot. The dataset and service records disagree on commercial availability; the record says so. `onescotlandgazetteer.org.uk` now describes itself as an independent site, not an official service, so it is not used; the owner's portal builds its pages in the browser, so its contact, help and terms pages are for the author to read. **Done:** csr-0005. **Next:** S15d Spatial Hub. **Blockers:** none.
- 2026-11-03 — **S15d** (checkpoint). `csr-0006` Spatial Hub (demonstration, platform, Improvement Service, mapping and data capabilities, `open_data[]` linking its dataset catalogue, service terms with open and premium datasets, free accounts) from the Spatial Hub's About, Help Centre, Terms and Contact pages. **Done:** csr-0006. **Next:** S15e GOV.UK Notify (optional api record), then the S15 pull request. **Blockers:** none.
- 2026-11-03 — **S15e** (checkpoint). `csr-0007` GOV.UK Notify (demonstration, api, Government Digital Service as `uk-public-sector`, REST interface, per-transaction charging with the published prices, 24/7 emergency support) from seven of Notify's own pages. **Done:** S15's five demonstration records, each with a verification table in `docs/demonstration-sources.md`. **Next:** author verifies every row against its source (ticking it, or replacing a statement with the sentinel), opens the pull request and merges; then S16. Courtesy notes to the four owners (Scottish Government for ScotAccount and the Design System, Improvement Service, Government Digital Service) are sent before publication (S16). **Blockers:** none.
- 2026-11-03 — **S15 ready for pull request.** `pytest` 357 passed (1 skipped); `csr validate` 0 errors, 3 warnings (R12 on `csr-0002` twice and on `csr-0004`, as intended); `csr validate --check-links` on the new records: only `csr-0004`'s GitHub and npm addresses answered 403 from the build session (its proxy, and npm refusing automated requests), which R08 reports as warnings and never blocks on. The UI tests use the fixture register, so their baselines are unchanged.
  - **Pull request title:** Add the demonstration records (S15)
  - **Next:** author works through `docs/demonstration-sources.md`, opens the pull request and merges; then S16.
- 2026-11-03 — **S15f** (checkpoint). Author's verification applied: ScotAccount now cites its service manual (join the beta, contact, home page), with the beta's adoption route, no charge for beta participants, support and office hours, the sign-in page as its service address and the roadmap; One Scotland Gazetteer has the PSGA, AddressBase and open UPRN/USRN terms, no charge for PSGA use or public search, the portal's About page and terms, and the author's check of the portal as a source; Spatial Hub's charges are now not stated (with the free-account summary kept). Record pages now show a charging summary after "No charge" and "Not stated in public sources". Next: a proposed record for mygovscot myaccount (author's request).
