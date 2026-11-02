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

### Changed

- `.gitignore` extended for Python, the built site and UI test tooling.
- `publiccode.yml` completed: description, features, `softwareType: standalone/web` and categories.

### Removed

- `.github/workflows/template.yml`, which the template setup no longer needs.
