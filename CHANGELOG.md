# Changelog

All notable changes to this project are recorded here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Repository created from the Digital Office repository template on 2026-11-02.
- README describing the demonstrator, how to get started and its licences.
- `LICENCE-CONTENT.md`: Open Government Licence v3.0 for records and documentation.
- `CODEOWNERS` review requests for `/records/`, `/taxonomy/` and `/schema/`.
- Specification v1.2, build plan, wireframes, baseline images and the wireframe rendering script.
- Python package skeleton for the `csr` command-line tool, with `pytest` tests.
- `Site` workflow with a `Validate` job that runs the tests.
- Dependabot updates for `pip`.
- Descriptor schema v0.1 (`schema/asset.schema.json`) with its eight conditions, the pointer record schema and `schema/README.md`.
- Draft taxonomy: 8 sectors, 14 service areas and 14 capabilities, with definitions and synonyms.
- Passing and failing schema fixtures for each of the eight conditions.
- `csr validate`: checks records, files or HTTPS URLs against the schema and validation rules R01 to R12 and R18 (R08 and R19 with `--check-links`), with `--base` to catch ids already taken on the base branch, and text, JSON or GitHub output.
- R13 test for vendored file hashes.
- The `Validate` job runs `csr validate`.
- Owner records: `csr-0001` (this demonstrator, owner-hosted in `solution.yml`) and `csr-0002` (the Digital Office repository baseline).
- Fictional example records `csr-9001` to `csr-9007`, with owner-hosted examples in `examples/hosted/`.
- Scottish Government Design System 4.3.0 (CSS and JavaScript), vendored with its licence, source and pinned hashes, and a script to refresh it.
- `csr build`: generates the static site from the register, with `site.toml` for the site's configuration. This slice builds the base layout (header with the design system's mobile menu, banner and footer), the home page (the full list without JavaScript) and the record pages, including the withdrawn-record page and a downloadable `solution.yml` for each record.
- `docs/ui-requirements.md`: how the build applies the wireframes, and its departures from them.
- Remaining static pages: Browse, a page for every sector, service area and capability, Contribute, About, Accessibility, Privacy, Not found, Field reference (generated from the schema), Solutions and codebases, Data and API, and Currency.
- API and extracts: `api/v0/` (index, all records, each record, taxonomies and schemas) and `data/register.json` and `data/register.csv`.
- `site.toml`: `examples_as_of`, so fictional examples keep their currency states, and a `[publication]` section for the inputs the author completes before publication.
- `csr-0001` links to the register's own open data.
- Home page search, filters and sorting: search by name, summary, owner, purpose, record ID and taxonomy synonyms; provenance, asset type, sector, service area, capability, currency and withdrawn filters with counts; sort by name, recently changed or recently confirmed; the state kept in the URL; the result count announced to screen readers. Without JavaScript the full list is shown.
- JavaScript unit tests, run by `pytest` with Node's built-in test runner when Node is installed.
- Draft form (`draft/`), part 1: generated from the schema and taxonomy, with conditional sections for every condition, repeating codebases, open data, interfaces and sources, a live `solution.yml` preview, and "Suggest a correction" filling the form from a record.
- `js-yaml` 5.5.0, vendored with its licence and pinned hashes; `tools/vendor.py` refreshes any vendored package.
- Draft form, part 2: validation against the schema in the browser with the vendored Ajv 8.17.1 (2020-12) runtime, plus rules R06 and R09, with an error summary and inline errors; Copy YAML, Download, Open as a GitHub issue (pre-filled, or download-and-attach when too long) and Send by email.
- `csr validate` accepts the draft placeholder id `csr-NNNN` in files outside `records/`, with a warning.
- Harvester (`csr harvest`): fetches each owner-hosted record's registered source over HTTPS within limits (R15), checks the owner match (R14), the allowed statuses (R16), the schema and rules, and each linked `publiccode.yml` with the official parser (R17), keeping the last valid copy, content hash and dates in a harvest state published at `api/v0/harvest-state.json`. `csr build --harvest` publishes from that state.
- Harvest report page (`harvest/`), and harvest states on owner-hosted record pages.
- `tools/install-publiccode-parser.py`: installs publiccode-parser-go v5.4.3 with verified checksums; the `Validate` job uses it.
- Roboto and Roboto Mono, served from the site itself (decision D5), with their licences and pinned hashes.
- The role mailbox `solution-register@digitaloffice.scot` for the site, emailed drafts and feedback, with a 10 working day reply time; it is also `csr-0001`'s contact.
- UI tests (`npm run test:ui`, required `UI tests` job): every page compared with its approved image in `ui/baseline/` at 1280 and 375 pixels, a behaviour test for each row of the parity table, and axe-core on every page; a fixed fixture register for them; `csr build --root` and `--no-history`.
- Workflows: `site.yml` runs on pull requests, pushes to `main`, on demand and daily; pull requests fetch and check any pointer they add or change; other runs harvest every source and report it in the job summary; deployment to GitHub Pages is skipped until the `PAGES_ENABLED` variable is `true`. `validate-solution.yml` is a reusable workflow owners call to check their `solution.yml` and `publiccode.yml`.
- `csr harvest --fail-on-problems` and `--summary`, and `csr check-publiccode`.
- Issue forms: suggest a solution, suggest a correction, host our own solution.yml, and give feedback, alongside the organisation's bug report and change request; and a pull request template that keeps the organisation's and adds provenance, sources and the licence agreement.
- Maintainer tools: `csr import-publiccode` (add or update a codebase from its `publiccode.yml`, or draft a new record, following specification appendix A), `csr move-to-source` and `csr move-to-local` (move a record to and from owner hosting, checking the owner's file first), and `csr new --from-issue` (add a record from a suggest-asset issue with the next free id).
- Validate page (`validate/`): check a `solution.yml` or pointer by pasting it, uploading it or giving its URL, in the browser, against the schema and every rule that needs no network, with a results table giving the severity, rule, field, problem and fix for each finding.
- The `Validate` job builds the site and uploads it as the `site-preview` artifact.
- Demonstration records `csr-0003` ScotAccount , `csr-0004` Scottish Government Design System , `csr-0005` One Scotland Gazetteer , `csr-0006` Spatial Hub , `csr-0007` GOV.UK Notify and `csr-0008` mygovscot myaccount, compiled from cited public sources, and `docs/demonstration-sources.md`, which ties each statement to its source for the author to verify.
- `docs/decision-points.md`: every choice the working group may revisit (DP-01 to DP-53), including the schema v0.1 choices and the rule interpretations, with alternatives and what would change; `docs/editorial-model.md`: the two-approval model and how to enforce it.
- Guides: `docs/adopting-this-demonstrator.md` (transfer or fork, files and settings to change), `docs/contributing-records.md` (the inclusion test and every contribution route, linked from the Contribute page), `docs/hosting-your-solution-yml.md` (owner hosting and the reusable workflow) and `docs/harvesting.md`.
- `docs/maintenance.md`: maintainer commands, handling issues, maintaining records, removing content from history, dependency and vendored-file updates, and the runbook (monthly, on rule changes, on failures, yearly); `docs/publiccode-mapping.md` and `docs/github-free.md` (specification appendices A and B).

### Changed

- `.gitignore` extended for Python, the built site and UI test tooling.
- `publiccode.yml` completed: description, features, `softwareType: standalone/web` and categories.
- The visual baselines in `ui/baseline/` are now screenshots of the built pages (they were the wireframe images), with 375-pixel images added.
- The phase banner is a named region, sidebar asides are named by their headings, and scrolling code examples can be reached with the keyboard.
- Dependabot proposes only patch releases of Playwright; minor and major upgrades are made deliberately, with the UI baselines remade.
- R07 treats hyphenated addresses (such as `solution-register@`) as role mailboxes, and knows more role words.
- `csr validate` and the harvest report describe schema problems in plain words, one per field, with the same wording as the draft form and validate page.
- Record pages show a charging summary after "No charge" and "Not stated in public sources", not only when charges apply.

### Fixed

- Schema condition 1 required `sources` when `record_status` was missing; it now applies only to demonstration records.
- R18 no longer also reports "not stated in public sources" as a bad address; that is R10's finding.

### Removed

- `.github/workflows/template.yml`, which the template setup no longer needs.
