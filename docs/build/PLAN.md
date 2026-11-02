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
| S14 | UI tests: fixtures reproducing the wireframes; visual comparison at 1280 and 375 pixels; behaviour tests; `axe-core`; required `UI tests` job; `npm` entry in `dependabot.yml` (removed after S1 because there was no `package.json` to read) | 6.13 | a) visual; b) behaviour; c) accessibility | `UI tests` passes in CI |
| S15 | Demonstration records: research, cited sources, sentinels where facts are not public | 5.2 | a) one record per checkpoint | Author verifies every statement against its source |
| S16 | Documentation and readiness: adopting guide, decision points, editorial model, maintenance, runbook; manual accessibility pass | 8, 9 | a) documents; b) checklist | Ready for courtesy notes, sign-off and enabling Pages (author steps) |

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
