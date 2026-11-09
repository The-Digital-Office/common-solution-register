# Adopting this demonstrator

For a body the short-life working group asks to take the work forward, or
anyone who wants to build on it (specification section 8). The code is under
the MIT licence and the content under the Open Government Licence v3.0, so the
repository can be **transferred** or **forked**.

Read [`decision-points.md`](decision-points.md) first: it lists the choices
the demonstrator made that a register may want to make differently.

## What you get

- The descriptor schema (`schema/`), the draft taxonomy (`taxonomy/`) and the
  records (`records/`, `examples/hosted/`).
- The `csr` command (`src/csr/`): validator, harvester, site generator and
  maintainer tools ([`maintenance.md`](maintenance.md)).
- A static site published on GitHub Pages, with a JSON API and extracts.
- Workflows (`.github/workflows/`): `site.yml` (validate, harvest, build, UI
  tests, deploy), `validate-solution.yml` (reusable, for owners), and
  `standards.yml` (the Digital Office baseline checks).
- Issue forms, a pull request template, and this documentation.

## Transfer or fork

**Transferring** the repository to your organisation keeps its history,
issues, pull requests, stars and watchers, and GitHub redirects links to the
repository. **GitHub does not redirect the Pages site**: the old address,
`https://the-digital-office.github.io/common-solution-register/`, stops working
the moment the repository moves. So:

1. Before transferring, publish a notice of the new address (for example in
   the banner and on the About page), and tell the working group and any
   owners who host their own records.
2. Transfer (**Settings → General → Danger Zone → Transfer**).
3. Set `base_url` (and `repository_url`) in `site.toml`, and redeploy.

**Forking** leaves the demonstrator where it is and starts a new repository
from a copy. Make the same changes below in the fork.

## Files to change first

| File | Change |
|---|---|
| `site.toml` | `preview` (true asks search engines not to index the site), `title`, `base_url`, `state_url` (usually left empty), `repository_url`, `default_branch`, `host_organisation`, `contact_mailbox`, `feedback_url`, the currency thresholds, and every value under `[publication]` (data controller, Data Protection Officer, lawful basis, retention, feedback form, accessibility assessment and dates) |
| `publiccode.yml` | Organisation, maintainers and URLs |
| `solution.yml` | The register's own record (`csr-0001`): owner, contact, `service_url`, `service_page_url`, documentation, codebase and `open_data` addresses, and `confirmation` |
| `records/csr-0001.yaml` | The pointer's `source` and `expected_owner` |
| `.github/CODEOWNERS` | Your maintainers, or an editors team ([`editorial-model.md`](editorial-model.md)) |
| `src/csr/templates/partials/banner.html`, `about.html` | The banner and About wording: who hosts it, its status, and the working group context |
| `src/csr/static/host/`, `host_logo` in `site.toml` | The footer logo is the Digital Office's, and not openly licensed: put your own logo there and set `host_logo` to its path and `host_url` to the address it links to, or set `host_logo = ""` to show "Hosted for demonstration by ‹host_organisation›" as text. The UI baselines then need remaking |
| `schema/*.schema.json` | The `$id` addresses, which name the Pages site |
| `.github/ISSUE_TEMPLATE/*.yml` | Links to the draft and validate pages, which name the Pages site |
| `.github/workflows/validate-solution.yml` | The default `register-repository`, and the usage example in its comment |
| `pyproject.toml`, `README.md` | The repository address and the description |
| `LICENCE-CONTENT.md`, `README.md` | The copyright holder for content |
| `records/` | Delete the example range (`csr-9000` to `csr-9999`, with `examples/hosted/`) and any demonstration records you do not keep; confirm the rest with their owners, or withdraw them |

The tests in `tests/` use the real records, including the examples, to check
every condition and state. If you delete the examples, update the tests that
name them, or keep the examples as test fixtures elsewhere. The UI tests use
their own fixed copy (`ui/tests/fixtures/register/`), so they are unaffected.

Then run the checks:

```bash
pip install -e ".[dev]"
pytest -q
csr validate
csr build --base-url http://localhost:8000/
```

## Repository settings to recreate or check

Repository settings do not travel with a fork, and should be checked after a
transfer.

| Setting | Value |
|---|---|
| Rulesets | **"DO baseline: main"**: pull request required (squash merge only, no required approvals), up-to-date branches, required checks `standards / Required files` and `standards / publiccode.yml`, no force-pushes or deletion. **"CSR: required checks"**: required checks `Validate` and `UI tests`. The Digital Office applies the first with its `apply-baseline.sh` script |
| Merge settings | Squash merge only, pull request title as the commit title, head branches deleted after merge |
| Pages | **Settings → Pages → Source: GitHub Actions**, and the repository variable `PAGES_ENABLED` set to `true` (**Settings → Secrets and variables → Actions → Variables**). Until then, `Deploy` is skipped |
| Security | Dependabot alerts and security updates; secret scanning with push protection; private vulnerability reporting |
| Labels | `new record`, `correction`, `owner hosting` and `feedback`, which the issue forms apply; the baseline's standard labels |
| Tag | `v0`, which owners' workflows call; create it on the new repository (`git tag v0 && git push origin v0`) |
| Editors | An editors team and an enforced ruleset, if you adopt the editorial model |
| Scheduled harvest | Check the Site workflow is enabled (**Actions → Site**); GitHub disables schedules after about 60 days without activity |

`standards.yml` calls the Digital Office's public reusable workflow
(`The-Digital-Office/.github`, at `@v1`). It keeps working after a transfer or
fork, or can be replaced by your own.

## Harvest state after a move

The harvest reads its previous state from the live site. After a transfer the
old address no longer serves it, so the first harvest at the new address starts
fresh. That is harmless, except that a failing source has no last valid
version to fall back on until it passes again ([`harvesting.md`](harvesting.md)).

## Owners' references

- **Pointers** in `records/` name the owners' files, so they are unaffected by
  a move.
- **Owners who call the reusable workflow** should change their `uses:` line to
  the new repository, and the new repository needs the `v0` tag.
- **Owners' own copies** of the schema refer to it by its `$id`, which changes
  with `base_url`.

## Before publishing

Work through [`publication-checklist.md`](publication-checklist.md): the
inputs, courtesy notes to owners, sign-off, the manual accessibility check and
enabling Pages.
