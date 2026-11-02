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
- The `Validate` job builds the site and uploads it as the `site-preview` artifact.

### Changed

- `.gitignore` extended for Python, the built site and UI test tooling.
- `publiccode.yml` completed: description, features, `softwareType: standalone/web` and categories.

### Removed

- `.github/workflows/template.yml`, which the template setup no longer needs.
