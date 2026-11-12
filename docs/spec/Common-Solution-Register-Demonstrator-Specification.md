---
title: "Common Solution Register Demonstrator: Scope, Design and Build Specification"
author: "Robbie Harris, Enterprise Architect"
organisation: "The Digital Office for Scottish Local Government"
status: "Draft: built as a demonstrator (see docs/build/PLAN.md)"
version: "1.3"
date: "3 November 2026"
classification: "OFFICIAL"
based_on:
  - "Common Solution Register: Proposed Approach and Operating Model, v0.2 (19 October 2026)"
  - "Model handover: Common Solution Register proposed approach v0.2"
  - "Review notes on specification v0.2 and v0.4 (19 October 2026)"
  - "The-Digital-Office/.github baseline (GOVERNANCE.md, repository-standards workflow v1, apply-baseline.sh) and repository-template"
---

# Common Solution Register Demonstrator: Scope, Design and Build Specification

| Document control | Detail |
|---|---|
| Status | Draft. Built as a demonstrator; the build is recorded in `docs/build/PLAN.md`. |
| Version | 1.3 |
| Date | 3 November 2026 |
| Owner | Robbie Harris, Enterprise Architect, The Digital Office |
| Classification | OFFICIAL |

## Version history

| Version | Date | Summary of change |
|---|---|---|
| 0.1–0.3 | 19 October 2026 | Proof-of-concept drafts and response to the review of v0.2. |
| 0.4 | 19 October 2026 | Reframed as a demonstrator for the short-life working group (SLWG), covering the whole Scottish public sector, designed to be built on and handed over. |
| 0.5 | 19 October 2026 | Responds to the review of v0.4 (appendix D). Adds clearly fictional **example** records, so every condition and currency state is shown truthfully. Reduces **demonstration** records about real services to 3–5 well-documented assets, with courtesy notes to their owners before publication. Allows "not stated in public sources". Adds Digital Office sign-off before publication. Fixes the form architecture (built in Python, validated in the browser by vendored libraries) and re-estimates it. Simplifies hand-off and the issue form. Renames `approved_in` to `merged_in`. Makes the document self-contained: the `publiccode.yml` mapping, the GitHub Free analysis and the validation rules are now appendices. Adds an ID policy, repository-settings transfer steps (GitHub does not redirect Pages sites on transfer), privacy and accessibility detail, and observability. Written in the third person. |
| 0.6 | 20 October 2026 | Adds **distributed publication for registered endpoints**. `solution.yml` is a portable descriptor that owners can host themselves. Each register entry is either a local record or a **pointer** to an owner-hosted file. A **harvester** runs daily and on demand, for registered endpoints only, and validates every harvested `solution.yml` and linked `publiccode.yml` (the latter with the official parser). Owners can edit their hosted files without maintainer review, protected by validation and an owner-match check. Adds a validate page, a reusable validation workflow for owners' repositories, a one-step move from local to owner-hosted, and a register maintenance model (update, retire, withdraw, delete, source lost). Discovery crawling (an organisation scan) is excluded. Decisions are recorded in 10.1. |
| 0.7 | 20 October 2026 | Adds `service_url` (the live service itself) and `service_page_url` (the owner's page describing it), both required for live and beta services and platforms. `publiccode.yml` `landingURL` now maps to `service_page_url`, and `description.*.documentation` to `documentation_url`. Adds the pages the wireframes showed were missing: Browse, Contribute, a withdrawn-record view and a not-found page, plus "Report a problem" on every record and sorting of search results. Adopts the **Scottish Government Design System** (v4.3.0, MIT) for the user interface, without Scottish Government branding. |
| 0.8 | 2 November 2026 | Makes the **wireframes normative**: they are the user interface requirements for the build (new section 6.13), with a page-to-template map, a behaviour-parity table, the known differences, and acceptance by automated visual comparison and browser behaviour tests (new required `UI tests` check). States the build languages (section 6.2). Specifies how the Scottish Government Design System is vendored, initialised and checked against its reference markup. |
| 0.9 | 2 November 2026 | Adds 7.1: the step-by-step creation of the repository from `The-Digital-Office/repository-template`, who does each step, and what the build keeps, extends or replaces from the template. |
| 1.0 | 2 November 2026 | Separates **common solutions** from **codebases** (new 1.1). `solution.yml` describes the offer; `publiccode.yml` describes a codebase and stays in that code's repository. Replaces the top-level repository fields with a `codebases[]` list, carrying each codebase's `publiccode_url`, `maintenance` (mapped from `publiccode.yml`), version and maintainers. Adds `open_data[]` links, so a solution can point to the data it publishes without the register cataloguing datasets. `csr-0001` becomes a **service** whose codebase is this repository. The `publiccode.yml` importer now adds a codebase to a solution. Records two decision points: datasets are out of scope, and a codebase on its own is not a common solution. |
| 1.1 | 2 November 2026 | Adds reference implementations as a kind of codebase (1.1, `codebases[].kind`). Replaces the build plan in section 9 with an incremental, multi-session build strategy, with the slices and resume protocol in `docs/build/PLAN.md`. |
| 1.2 | 2 November 2026 | Removes all tool attribution from the repository: no tool-specific instruction file, build sessions brief from `docs/build/PLAN.md`, and commits, pull requests and files carry the author's identity only (9.1). |
| 1.3 | 3 November 2026 | Corrections after the build. 6.8: the banner wording follows the wireframes, a long notice on the home page and a short one elsewhere (UI decision D1). 5.2: a sixth demonstration record, mygovscot myaccount (decision point DP-07). |
| 1.4 | 12 November 2026 | 6.13: a deliberate departure from the wireframes' look, decided by the author (UI decision D37). The header has a small "Scottish public sector" line above the title, which no longer includes "Demonstrator" (the banner still says it on every page); the main navigation is bold; a tinted band runs behind the breadcrumbs and page header; buttons are navy. `csr.css` may style these as well as the cases already listed. |
| 1.5 | 12 November 2026 | 6.13: the wireframes now show the header, page band and buttons of version 1.4, so they are part of the requirements rather than a departure (wireframe change W1, which replaces UI decision D37). A deliberate design change updates the wireframes first. |
| 1.6 | 12 November 2026 | 6.13: the record wireframes show the record page as a summary card, with one main action in the page band, a grid of key facts, "On this page" in place of the sidebar, and a band asking for corrections (wireframe change W2). |
| 1.7 | 12 November 2026 | 6.8 and 6.13: the home page introduces the register, and the finder moves to `solutions/` as "Find solutions" (new Solutions wireframe); "Home" joins the main navigation (wireframe change W3, decision point DP-55). |


## 1. Purpose and context

The Scottish Government has set up a **short-life working group (SLWG)** on a common solution register for the **Scottish public sector**. The Digital Office is a member. This demonstrator is built **ahead of** that group's process, to:

- **show what is possible:** a working, interactive example of the approach in the *Proposed Approach* paper, so SLWG members can react to something concrete;
- **inform the SLWG's decisions:** on scope, information model, taxonomy, contribution routes, currency and operating model; and
- **provide a foundation to build on:** whichever body the SLWG asks to take the work forward can adopt this repository, by transfer or fork, and continue from it.

The demonstrator is **not a register**. Its content is labelled by provenance (section 5). The SLWG, not the Digital Office, decides whether a register is built, by whom and to what design. Before the site is published, the owners of any real services it describes receive a courtesy note (section 9).

### 1.1 Common solutions and codebases

| Term | Meaning | Described by |
|---|---|---|
| **Common solution** | A capability that an accountable owner deliberately offers to other public bodies, with a way to adopt it: a service to use, a platform to onboard to, a component, API, standard or pattern to take up, or software to deploy, with terms and support behind it. What makes it a common solution is the **offer and the ownership**, not the existence of code. | `solution.yml` (this register's descriptor) |
| **Codebase** | Source code that implements all or part of a solution, or a **reference implementation** of it (for example of a standard or an API). A solution may have none (a standard, a pattern, a procured service), one, or several, and they may be public or private. ScotAccount, for example, is a common solution with a `solution.yml` whether or not any of its code is public; an open-source or reference implementation, if one existed, would be a codebase with its own `publiccode.yml`. | `publiccode.yml` (the European standard), in the codebase's own repository |
| **Dataset** | Published data. A solution may publish data, which the register links to but does not catalogue. | Open data catalogues (for example data.gov.uk or Spatial Hub) |

So:
- A public repository is **not** a common solution unless someone offers it for reuse and takes responsibility for it. Most public sector repositories are codebases only, and do not belong in the register.
- `publiccode.yml` stays in the codebase's repository and is never replaced by `solution.yml`. A solution's record **links** to the codebases that implement it, and the register validates their `publiccode.yml` files.
- **This demonstrator is both.** The `common-solution-register` repository is a codebase, with a `publiccode.yml`. The register it implements is a common solution, of type `service`, with a `solution.yml` (record `csr-0001`) that lists that repository among its codebases. For convenience its `solution.yml` is hosted in the same repository; an owner can host it anywhere.

## 2. What SLWG members can do with it

| Journey | What it demonstrates |
|---|---|
| **Find solutions:** search and filter by service area, capability, asset type, status, sector and provenance | Discovery through a controlled taxonomy (proposal 9) |
| **Assess a solution:** a record page showing purpose, owner, contact, terms, adoption route, currency and provenance | The minimum information for initial assessment (proposal 3.2, 8.2) |
| **Browse the taxonomy:** assets by service area, capability or sector, with term definitions | The taxonomy as the common join point |
| **Read the field reference:** generated from the schema, showing each field, its requirement level, conditions and an example | The descriptor, in a form non-technical members can critique |
| **Draft a record in the browser:** a form with live validation that produces a YAML record to copy, download, attach to a GitHub issue, or email | That contribution can be easy without GitHub skills, and that every route produces the same validated record |
| **Use the data:** a data page listing API URLs with sample responses, and JSON and CSV downloads | An open API and bulk extract from one master record |
| **See a solution and its codebase:** the register (a service) beside the `publiccode.yml` of the repository that implements it | The difference between a common solution and its code; reusing a standard without forking it |
| **See currency in action:** current, due, stale and unconfirmed badges, and a currency summary page | Visible currency and attestation (proposal 10.4) |
| **Validate a `solution.yml`:** paste, upload or give the URL of a descriptor and see the validation result | That owners can check their own file before registering it |
| **See an owner-hosted record:** a record harvested from its owner's own repository, with its source, last harvest and validation state | That curated and distributed publication can coexist, and that a record can move to its owner in one step |
| **See the harvest report:** every registered endpoint, when it was last harvested, and whether it passed validation | That the harvester validates every source and never publishes a failing file |
| **Give feedback:** a link on every page | Input to the SLWG |

## 3. Scope

### 3.1 In scope

- A public repository, `The-Digital-Office/common-solution-register`.
- The schema, a taxonomy covering the Scottish public sector, and 10–13 records (section 5).
- A Python validator and static site generator.
- The pages in section 2, deployed to GitHub Pages.
- `solution.yml`: the descriptor as a portable file that owners can host themselves, alongside `publiccode.yml` for software.
- A **harvester for registered endpoints only**, running daily and on demand (6.11).
- A validate page, `csr validate <path-or-url>`, and a **reusable GitHub workflow** that owners can call from their own repositories.
- A one-step move from a local record to an owner-hosted one, and the maintenance model in 6.12.
- Issue forms for "suggest an asset", "suggest a correction", "move to owner hosting" and "feedback".
- Documentation for adopting and extending the demonstrator.

### 3.2 Out of scope

- Operating a register: no service levels, no formal editorial process, no attestation cycle, and no promise that records are current.
- Discovery crawling: searching GitHub organisations or the web for unregistered `solution.yml` or `publiccode.yml` files (an "organisation scan"). The harvester visits only endpoints registered through a reviewed pointer. Discovery is recorded as a future option in `decision-points.md`.
- Federation with other catalogues.
- Server-side components.
- Analytics and cookies.
- A formal accessibility audit (a self-assessment and an accessibility statement are in scope).
- Anything the SLWG has yet to decide.

## 4. Design principles for building on it

1. **Portable:** everything needed is in the repository. A new host changes `site.toml` (base URL, host organisation, contact mailbox, feedback URL) and the repository settings listed in section 8.
2. **Neutral:** presented as a Scottish public sector demonstration *hosted by* the Digital Office, not as a Digital Office service. Organisation-specific values live in configuration, not templates.
3. **Standards first:** JSON Schema; `publiccode.yml` used unchanged for codebases and linked from solutions, never forked; SPDX licence identifiers; MIT for code and OGL v3.0 for content.
4. **Simple to understand:** YAML files, a small Python generator, static HTML, and JavaScript only where interaction needs it.
5. **Honest labelling:** every record states its provenance; nothing is presented as confirmed, approved or current unless it is.
6. **Ready to distribute:** any record can be held locally or by its owner, using the same file format and the same validation, so a body adopting the demonstrator can move from curated to distributed publication without changing the model.
7. **Open decisions stay visible:** `docs/decision-points.md` records each choice the SLWG may revisit, the alternative, and what would need to change.

## 5. Demonstration content

### 5.1 Provenance

| `record_status` | Meaning | Shown as | ID range |
|---|---|---|---|
| `owner-confirmed` | The owning organisation has confirmed the content (`confirmation.*` required) | "Confirmed by owner on ‹date›" | `csr-0001`–`csr-8999` |
| `demonstration` | A real asset, described **only from cited public sources** (`sources[]` required). **Not confirmed by the owner.** | "Demonstration entry, compiled from public sources and not confirmed by the owner" | `csr-0001`–`csr-8999` |
| `example` | **Fictional.** The name always begins "Example:". Used to show conditions and states that cannot be shown truthfully with real records. | A distinct "Fictional example" banner and styling | `csr-9000`–`csr-9999` |
| `withdrawn` | Retained as a tombstone. During the demonstrator, used only by an example record. | "Withdrawn" | either |

**Not stated in public sources.** In `demonstration` records, these fields may take the sentinel value `not-publicly-stated` instead of inferred text:

- `terms_of_use.type`
- `adoption_route.summary`
- `support.summary`
- `charging.applies`

The site renders the sentinel as *"Not stated in public sources"* in a distinct style. The schema allows it only when `record_status = demonstration`.

**Hosting.** Separately from provenance, each record is either **local** (the full record is in `records/`) or **owner-hosted** (`records/` holds a pointer to the owner's `solution.yml`; see 6.11). An owner-hosted record must be `owner-confirmed` or `withdrawn`, because publishing the file is the owner's own assertion. The one exception is fictional `example` records (`csr-9006`, `csr-9007`), which show the mechanism. `demonstration` records are always local.

**API and extracts.** All records are included, each carrying `record_status`. The site's provenance facet, and the `record_status` column in the API and CSV, let users and consumers filter. Example names always begin "Example:", so they cannot be mistaken for real assets even out of context.

**Removal and identifiers.** During the demonstrator, a record about a real asset is **deleted** if its owner asks; it is not tombstoned. The "IDs are never deleted" rule of the register model **takes effect only at adoption**. An adopting body may delete the whole `csr-9000`–`csr-9999` range, and any `demonstration` records it does not keep.

### 5.2 Record set

The **inclusion test** is from proposal 4.3: (1) intended for reuse by more than one public body; (2) the owner accepts responsibility for accuracy; (3) a role-based contact exists; (4) the asset can be classified; (5) status and terms can be stated; (6) it can be described without sensitive information. For `demonstration` records, test 2 is replaced by the courtesy note, and tests 3 and 5 by what is publicly stated.

| Provenance | Record | Type | Exercises | Inclusion test |
|---|---|---|---|---|
| owner-confirmed, **owner-hosted** | `csr-0001` Common Solution Register Demonstrator | service | **Solution and codebase separated**: the register (service) lists its codebase, the `common-solution-register` repository, with that repository's `publiccode.yml` validated by the official parser and its maintenance type. **Owner-hosted**: its `solution.yml` is in the same repository. Also `current` currency, `MIT AND OGL-UK-3.0`. | Passes |
| owner-confirmed | `csr-0002` Digital Office repository baseline | pattern | A solution with **two codebases** (`.github` and `repository-template`) | Test 1 to be confirmed by the author: is it offered to other public bodies? If not, drop it. |
| demonstration | ScotAccount (Scottish Government) | service | `scottish-government` owner, identity capability, support condition | 1, 4, 6 pass; 3 and 5 as publicly stated |
| demonstration | Scottish Government Design System | standard | Standard type, open licence, public codebase (from sources) | 1, 4, 5, 6 pass |
| demonstration | One Scotland Gazetteer (Improvement Service) | platform | Local government owner, data capability | 1, 4, 6 pass; 5 as publicly stated |
| demonstration | Spatial Hub (Improvement Service) | platform | Mapping capability; `open_data[]` link to its catalogue | 1, 4, 6 pass; 5 as publicly stated |
| demonstration (optional) | GOV.UK Notify or GOV.UK Pay | api | `uk-public-sector`, interfaces, publicly documented charging | 1, 3, 4, 5, 6 pass from public documentation |
| demonstration (added in 1.3) | mygovscot myaccount (Improvement Service) | service | A live sign-in service used by all 32 councils; local government owner, identity capability | 1, 3, 4, 6 pass; 5 as publicly stated |
| example | `csr-9001` Example: Council Payments Gateway | component | `charging.applies = true`, `support` | n/a (fictional) |
| example | `csr-9002` Example: Benefits Case Management API | api | `interfaces[]`, related assets | n/a |
| example | `csr-9003` Example: Legacy Waste Booking Service | service | `deprecated` with migration guidance; `stale` currency | n/a |
| example | `csr-9004` Example: Pilot Notifications Component | component | `beta`; `due` currency | n/a |
| example | `csr-9005` Example: Withdrawn Pilot | artefact | `withdrawn` tombstone | n/a |
| example, owner-hosted | `csr-9006` Example: Hosted Booking Component | component | Owner-hosted fictional record; its `solution.yml` lives under `examples/hosted/` and is harvested like any other source | n/a |
| example, owner-hosted | `csr-9007` Example: Failing Hosted Source | component | A pointer to a deliberately invalid `solution.yml`. It is never published; it appears in the harvest report with its validation errors. | n/a |

Every `demonstration` record is verified against its sources during the build. Any statement that cannot be sourced is replaced by the sentinel, and any record that cannot be sourced adequately is dropped. Example records carry fictional `confirmation` dates, which is how the `due` and `stale` states are shown truthfully. Contacts in demonstration records are public contact pages (`contact.type: web-form`). Using `csr-0001` as the first owner-hosted record keeps the real demonstration inside Digital Office-owned repositories. No other organisation's repository is touched.

## 6. Design

### 6.1 Architecture

```
  records/*.yaml ──────────────┐   (local records, and pointers to owner-hosted files)
  schema/ taxonomy/ site.toml ─┤
                               ▼
  owner-hosted solution.yml ◄─ csr harvest ─► csr validate ─► csr build ─► site/ ─► GitHub Pages
  (+ linked publiccode.yml)    (registered      (schema, rules,              (HTML, API, CSV, reports,
                                endpoints only)  publiccode parser)           draft and validate pages)
                               ▲
  previous published state ────┘   (last-good copies and content hashes, read from the live site)

  visitors ──► issue / email + attached .yaml ──► pull request ──► records/
  owners   ──► edit their hosted solution.yml ──► next harvest (daily or on demand)
```

- **Backup:** the repository is the master record and the backup. The site regenerates from any clone.
- **Determinism:** the build is deterministic for a given record set, set of harvested inputs, build date and configuration. Network access happens only in the harvest step, and only to registered endpoints.
- **Hosting location:** GitHub Pages content and request logs are hosted by GitHub, primarily in the United States. All content is intended for publication.
- **Observability:** a failed build or deployment notifies the person whose commit triggered it, through GitHub. Maintainers watch the repository. That is sufficient for a demonstrator, and the README says so.

### 6.2 Technology

| Concern | Choice |
|---|---|
| Records, schema | YAML; JSON Schema draft 2020-12 |
| **Languages** | **Python 3.12**: validator, harvester, generator and `csr` command-line tool. **Jinja2** HTML templates: every page. **JavaScript** (plain ES2020 modules, no framework, no build step): search, filtering and sorting, the draft form, the validate page, copy and download. **CSS**: the vendored design system, plus one small extension file. **YAML and JSON Schema**: records, taxonomy and schema. **GitHub Actions YAML**: workflows. **JavaScript on Node 22**: test tooling only (Playwright and `axe-core`), never part of the published site or the build. The official `publiccode-parser-go` is used as a prebuilt, checksummed binary; no Go is written. |
| Validator and generator | Python 3.12 with `PyYAML`, `jsonschema` and `Jinja2`; `pytest` for tests; versions pinned exactly; Dependabot |
| User interface | The **Scottish Government Design System** (`@scottish-government/design-system`, v4.3.0, MIT licence), whose repository describes it as for "the Scottish Government and other Scottish public sector bodies". Its compiled CSS and JavaScript are vendored at a pinned version, with hashes checked by R13, and are not loaded from a CDN. Components used: site header and navigation, phase banner, site search, search filters and results, metadata, tags, page header, summary list, notification panel and messages, warning and inset text, error summary, form questions, details, contents navigation, breadcrumbs, tables and site footer. **No Scottish Government logo or other brand assets are used**, because the design system's graphic assets are excluded from its Open Government Licence. The header carries a text title only. **How it is included:** `design-system.min.css` and `design-system.js` from the npm package `@scottish-government/design-system@4.3.0` are committed under `src/csr/static/vendor/sgds/4.3.0/`, with the package's licence and a `SOURCE.md` recording the package URL and its npm `integrity` hash. A script refreshes them on version upgrade, so no npm install is needed to build. The design system's JavaScript is loaded on every page and initialised for the components that need it (mobile site navigation, details and other interactive components), as its documentation describes. **Markup follows the design system's reference examples** for each component used, checked against its published examples during the build (slice S5). Any departure is listed in `docs/ui-requirements.md`. |
| Site | Static HTML and CSS. JavaScript is used for search, filtering and sorting (pages still work without it) and for the draft form. All links are relative, so the site works under `/common-solution-register/` and on any future domain. |
| Draft form | **The form HTML is generated at build time by Python** from the schema and taxonomy, through one Jinja2 template. **The conditional show/hide behaviour is hand-written** for the eight conditions in 6.4. **Validation runs in the browser** with the vendored, pinned **Ajv 2020 runtime** (the schema is compiled in the browser, so Node is not needed). **YAML is produced** by vendored, pinned **`js-yaml`**. A `pytest` test checks the hashes of the vendored files. |
| `publiccode.yml` validation | The official **`publiccode-parser-go`** binary, at a pinned release with a verified checksum. It runs in the harvest step and in pull request checks for any linked `publiccode.yml`. The demonstrator's own file is also validated by the baseline standards workflow. |
| UI and accessibility testing | Playwright (Node 22) and `axe-core`: visual comparison with the wireframes, browser behaviour tests and accessibility checks (6.13). Runs in the required `UI tests` job against the locally built site, with no network access. |
| Hosting | GitHub Pages through `actions/deploy-pages` |

### 6.3 Repository layout

```
common-solution-register/
├── README.md, LICENSE (MIT), LICENCE-CONTENT.md (OGL v3.0), CHANGELOG.md
├── publiccode.yml, solution.yml  (the demonstrator's own descriptors; records/csr-0001.yaml points at solution.yml)
├── site.toml                    (base_url, state_url, host organisation, contact mailbox, feedback URL, currency thresholds, harvest limits)
├── .github/
│   ├── CODEOWNERS               (records/, taxonomy/, schema/ → maintainers; review requested, not enforced)
│   ├── dependabot.yml           (github-actions, pip)
│   ├── ISSUE_TEMPLATE/  suggest-asset.yml, suggest-correction.yml, move-to-owner-hosting.yml, feedback.yml
│   ├── pull_request_template.md (provenance, sources, OGL contribution grant)
│   └── workflows/  standards.yml (baseline), site.yml (jobs: Validate, UI tests, deploy),
│                   validate-solution.yml (reusable: on: workflow_call, for owners' repositories)
├── schema/      asset.schema.json, README.md (validation rules: appendix C)
├── taxonomy/    sectors.yaml, service-areas.yaml, capabilities.yaml
├── records/     csr-0001.yaml … csr-9007.yaml   (full records or pointers)
├── examples/hosted/  fictional owner-hosted solution.yml files for csr-9006 and csr-9007
├── src/csr/     cli.py (validate | harvest | build | import-publiccode | move-to-source),
│                templates/ (one Jinja2 template per wireframe page, plus shared header, footer and banner partials),
│                static/csr.css (small extension), static/js/ (search.js, draft.js, validate.js, actions.js),
│                static/vendor/sgds/4.3.0/, static/vendor/ajv/, static/vendor/js-yaml/
├── ui/          wireframes/*.dc.html (normative source), baseline/*.png (approved screenshots), tests/*.spec.js (Playwright)
├── tests/
└── docs/        adopting-this-demonstrator.md, decision-points.md, editorial-model.md,
                 contributing-records.md, hosting-your-solution-yml.md, harvesting.md, maintenance.md,
                 publiccode-mapping.md (appendix A), github-free.md (appendix B)
```

### 6.4 Descriptor schema v0.1

**Mandatory for all records:**

- `schema_version`, `id`, `record_status`.
- `name`, `summary` (at most 200 characters), `purpose`, `asset_type` (`service` \| `platform` \| `component` \| `api` \| `standard` \| `pattern` \| `software` \| `artefact`).
- `owner.organisation`, `owner.sector`.
- `contact` (`role-mailbox` \| `service-desk` \| `web-form`).
- `service_areas[]`, `capabilities[]`, `status` (`concept` \| `in-development` \| `beta` \| `live` \| `deprecated`), `intended_adopters[]` (sector IDs).
- `terms_of_use`, `adoption_route.summary`, `charging.applies`.

**Conditional:**

| # | Condition | Required |
|---|---|---|
| 1 | `record_status = demonstration` | `sources[]` (public URLs); sentinel values permitted (5.1) |
| 2 | `record_status ∈ {owner-confirmed, example}` | `confirmation.last_confirmed`, `.method`, `.reference` |
| 3 | `record_status = withdrawn` | `withdrawal.date`, `withdrawal.reason` |
| 4 | `asset_type = software` (software offered for other bodies to deploy themselves) | At least one entry in `codebases[]` |
| 5 | `asset_type = api`, or `interfaces` present | `interfaces[]` (`type`, `documentation_url`) |
| 6 | `charging.applies = true` | `charging.model`, plus `charging.url` or `charging.summary` |
| 7 | `asset_type ∈ {service, platform}` and `status ∈ {beta, live}` | `support`, `service_url` and `service_page_url` (for `demonstration` records, either may be `not-publicly-stated`) |
| 8 | `status = deprecated` | `deprecation.date`, `deprecation.migration_guidance` |

**Pointer records** (owner-hosted) contain only these fields, validated by a separate small schema:

```yaml
id: csr-0007
source: https://github.com/owner-org/their-repo/raw/main/solution.yml   # HTTPS only
expected_owner: Owner Organisation                                         # must match the harvested owner.organisation
```

The harvested `solution.yml` must contain the full descriptor above, including the same `id`.

**Two web addresses, with distinct meanings:**

| Field | Meaning | Example |
|---|---|---|
| `service_url` | The address of the live service itself: where a user or adopter starts using it (start page, sign-in, application, or base API address for an API) | `https://service.example.gov.scot/` |
| `service_page_url` | The owner's own public page **describing** the service: what it is, who it is for, how to get it | `https://www.example.gov.scot/our-services/booking/` |
| `documentation_url` | Technical or implementation documentation | `https://docs.example.gov.scot/booking/` |

Both are recommended for every record, and required as in condition 7. Record pages show them as the first two actions: **"Go to the service"** and **"More information from the owner"**.

**Codebases and open data (optional for every type):**

```yaml
codebases:                       # the code that implements this solution, if any
  - repository_url: https://github.com/The-Digital-Office/common-solution-register
    visibility: public           # public | private
    publiccode_url: https://github.com/The-Digital-Office/common-solution-register/raw/main/publiccode.yml
    maintenance: internal        # internal | contract | community | none (as in publiccode.yml maintenance.type)
    version: "0.1.0"             # optional; from publiccode.yml softwareVersion
    kind: implementation         # implementation | reference-implementation
    role: Register site, API and tools   # optional, when there are several codebases
    maintainers:                 # optional; from publiccode.yml maintenance.contacts
      - name: [Name]
        affiliation: The Digital Office for Scottish Local Government
        email: [work email]
open_data:                       # data this solution publishes; links only
  - title: Spatial Hub datasets
    url: https://data.spatialhub.scot/
    catalogue: Spatial Hub       # optional
```

- A public codebase without a `publiccode_url` raises a warning (R12).
- `maintenance` is given per codebase. It is how the register shows whether code is actively maintained, which status (concept to deprecated) cannot express. A record whose codebases are all `maintenance: none`, and which has no `support`, shows **"No active maintenance"**.
- A private codebase is listed with `visibility: private` and no URL is required; `access_restriction` explains how to obtain access.

**Optional:** `access_restriction` (who may access a private codebase or restricted service, and how), `documentation_url`, `current_version`, `roadmap_url`, `dependencies[]`, `related_assets[]`, `adopters[]` (self-reported or verified), `standards_alignment[]`, `accessibility_statement_url`, `funding_model`.

**Derived at build time, from git, configuration and harvest results:**

- `last_changed` and `history_url` for local records. For owner-hosted records, `last_changed` is the date the harvested content hash last changed.
- `hosting` (`local` \| `owner-hosted`) and, for owner-hosted records, `source`, `harvested_at`, `content_hash` and `source_state` (`ok` \| `failing` \| `unavailable`).
- **`merged_in`:** rendered as "Merged in pull request #N", taken from the squash-merge commit subject. For owner-hosted records it refers to the pull request that registered the pointer; later content changes show "Harvested from owner source on ‹date›". In the demonstrator this is a merge reference, **not** an editorial approval; `docs/editorial-model.md` explains what an enforced approval would add.
- `currency`: `current`, `due` or `stale` for records with `confirmation`, using `site.toml` thresholds (default 11 and 12 months); `unconfirmed` for `demonstration` records.

The validation rules are listed in appendix C and in `schema/README.md`. The field-reference page is generated from the schema.

### 6.5 Taxonomy (draft for the SLWG to critique)

- **Sectors:** `scottish-government`, `executive-agencies`, `local-government`, `nhs-scotland`, `police-and-fire`, `non-departmental-public-bodies`, `further-and-higher-education`, `uk-public-sector`.
- **Service areas (14):** `health-and-care`, `social-care-and-social-work`, `children-and-families`, `education-and-skills`, `housing`, `social-security-and-benefits`, `revenues-and-tax`, `justice-and-community-safety`, `environment-and-waste`, `planning-and-building-standards`, `transport-and-roads`, `economy-and-business`, `culture-and-communities`, `corporate-and-cross-cutting`.
- **Capabilities (14):** `identity-and-access`, `payments`, `booking-and-scheduling`, `case-management`, `forms-and-transactions`, `notifications`, `document-and-records-management`, `integration-and-apis`, `data-and-analytics`, `mapping-and-location`, `content-and-publishing`, `cyber-security`, `information-governance`, `collaboration-and-productivity`.

Each term has an `id`, `label`, `definition`, `synonyms[]` and `status`. `decision-points.md` notes the option of aligning with existing vocabularies, such as the LGA/ESD lists or any Scottish Government taxonomy.

### 6.6 Contribution and feedback

| Route | Demonstrated by |
|---|---|
| Direct | Pull request; the template asks for provenance, sources and the OGL grant |
| Structured | **Draft form**, with these actions: **Copy YAML** and **Download .yaml** (primary); **Open as GitHub issue** (pre-fills the single YAML text area of `suggest-asset.yml`, within GitHub's URL length limit, about 8 KB; longer drafts are told to attach the file); **Send by email** (a `mailto:` with a subject line and a two-line body asking the sender to attach the downloaded file, because mail clients truncate long `mailto:` bodies) |
| Assisted | Documented: a maintainer drafts a record, or imports one from `publiccode.yml` with `csr import-publiccode` |
| Move to owner hosting | `move-to-owner-hosting.yml` issue form (record ID and the URL of the owner's published `solution.yml`), or a maintainer runs `csr move-to-source` (6.12) |
| Feedback | `feedback.yml` issue form, plus a configurable link for people without GitHub accounts (input I4) |

`suggest-asset.yml` has **one YAML text area plus three free-text fields** (asset name, organisation, contact). The draft form is the friendly front end, so the issue form does not duplicate the taxonomy.

Every form says that GitHub issues are public, and carries: *"By submitting, you agree your submission may be published under the Open Government Licence v3.0."*

### 6.7 Editorial model: documented, lightly configured

`docs/editorial-model.md` sets out the two-approval model for the SLWG to adopt or change:

- **Owner confirmation:** recorded in the record.
- **Editorial approval:** a review by an editors team, which would be enforced by a separate ruleset requiring code-owner review on `records/`, `taxonomy/` and `schema/`. It needs at least two editors, because authors cannot approve their own pull requests.
- **The lesson learned:** the baseline requires branches to be up to date before merging. Combined with dismissing stale approvals, that would force record pull requests to be re-approved after every merge to `main`. An enforced model should therefore not dismiss stale approvals, and should rely on a merge convention instead.

In the demonstrator, `CODEOWNERS` **requests** a review but nothing **enforces** it.

**Owner-hosted records (decided).** Owners may change their hosted `solution.yml` **without maintainer review**. Editorial review applies when a pointer is **registered or changed**, because that is a pull request. After that, the safeguards are automatic: full validation, an owner-match check (the harvested `id` and `owner.organisation` must match the pointer), and keeping the last valid version if a new one fails. This is the normal model for distributed publication, and `decision-points.md` records it as a choice the SLWG may revisit.

### 6.8 Pages

| Page | Path | Needs JavaScript |
|---|---|---|
| Home: an introduction to the register, a search box that opens Find solutions, the three records most recently changed or confirmed (DP-55), and ways into the rest of the site | `./` | No |
| Find solutions: search, facets, sorting (name, recently changed, recently confirmed), and the full list without JavaScript | `solutions/` | No (enhanced by it) |
| Record: **Go to the service**, **More information from the owner**, **Download solution.yml**, provenance, hosting, source and harvest state, and **Suggest a correction** | `assets/<id>/` | No |
| Withdrawn record: tombstone with withdrawal date, reason and any replacement; the ID and URL stay | `assets/<id>/` | No |
| Browse: index of sectors, service areas and capabilities, with counts | `browse/` | No |
| Taxonomy term | `service-areas/<id>/`, `capabilities/<id>/`, `sectors/<id>/` | No |
| Contribute: the routes (form, GitHub, email, self-hosting), what happens next, corrections and removal | `contribute/` | No |
| Not found (404), with search and links to Browse and Contribute | `404.html` | No |
| Field reference | `reference/` | No |
| `publiccode.yml` mapping | `reference/publiccode/` | No |
| Draft a record | `draft/` | **Yes**, and the page says so |
| Data and API: URLs with sample responses generated at build time; downloads | `data/` | No |
| Currency summary | `currency/` | No |
| Validate a `solution.yml` (paste, upload, or URL where the host allows cross-site fetches; raw GitHub files do) | `validate/` | **Yes**, and the page says so |
| Harvest report: each registered endpoint, last harvest, state, errors | `harvest/` | No |
| About: purpose, demonstrator status, SLWG context, provenance, not-endorsement, how to adopt | `about/` | No |
| Accessibility statement, Privacy notice | `accessibility/`, `privacy/` | No |
| API and extracts | `api/v0/…`, `data/register.json`, `data/register.csv` | n/a |

Every page carries a "Demonstrator" banner with a link to give feedback, as the wireframes show. On the home page it says: *"Built for the Scottish public sector common solution register short-life working group. This is not an official register. Records are confirmed by their owner, compiled from public sources, or fictional examples. Inclusion does not mean endorsement."* Every other page says: *"This is not an official register. Inclusion does not mean endorsement."*

**CSV:** nested objects use dotted column names; arrays of values are joined with `; `; arrays of objects are stored as compact JSON; UTF-8 with a header row.

### 6.9 Privacy and accessibility

- **Privacy notice** covers:
  - `maintainers[]`, imported from owner-published `publiccode.yml`;
  - GitHub issues, which are public and processed by GitHub;
  - the email hand-off, received by the Digital Office mailbox in `site.toml`;
  - the non-GitHub feedback route, with the Digital Office as controller where it owns the form;
  - content harvested from owner-hosted files, including `maintainers[]`, which is published as the owner published it;
  - GitHub Pages request logging and US hosting;
  - no cookies or analytics.
- **Maintainer data:** the Digital Office DPO's agreement to importing maintainer names and emails for the demonstrator was given to the author on 19 October 2026 (*reference to be added by the author*). **An adopting body must revisit it.**
- **Accessibility:** target WCAG 2.2 AA. The draft form uses an error summary at the top, inline errors linked to fields, and `aria-live` announcements. The accessibility statement names `draft/` and `validate/` as the only pages that need JavaScript. A manual keyboard and screen-reader pass is done before publication.

### 6.10 Workflows

| Workflow | Required? | Does |
|---|---|---|
| `standards.yml` | Yes (baseline) | Required files; `publiccode.yml` validation |
| `site.yml` | `Validate` job: Yes | **Triggers:** pull requests, pushes to `main`, `workflow_dispatch` (on demand), and a **daily** `schedule`. **Pull requests:** validate (fetching and validating only pointers added or changed in the pull request), run `pytest`, build, and upload a preview artifact. **Other triggers:** harvest, validate, build, and deploy (deploy is skipped until `PAGES_ENABLED` is `true`; the harvest report is still produced as a job summary). Uses a concurrency group. |
| `validate-solution.yml` | n/a (reusable) | `on: workflow_call`. Owners call it from their own repositories (`uses: The-Digital-Office/common-solution-register/.github/workflows/validate-solution.yml@v0`) to validate their `solution.yml`, and any `publiccode.yml`, on every pull request. |
| `site.yml`, job `UI tests` | **Yes** | Builds the site from the test fixtures, serves it locally, and runs the Playwright suite: visual comparison against `ui/baseline/`, behaviour tests, and `axe-core` (no serious or critical issues). Uploads a diff report on failure. |

Actions are pinned by SHA. Least-privilege permissions; no secrets; `persist-credentials: false`.

### 6.11 Harvesting registered endpoints

The harvester runs **daily and on demand**, and on every push to `main`, for **registered endpoints only**: the `source` URLs in pointer records. Each of those got there through a reviewed pull request. For each pointer it:

1. **Fetches** the file over HTTPS only, with a size limit (default 256 KB), a timeout (default 10 s), no redirects to non-HTTPS addresses, and safe YAML parsing. Content is treated purely as data, and rendered with auto-escaping and sanitised Markdown.
2. **Checks the owner match:** the harvested `id` must equal the pointer's `id`, and `owner.organisation` must equal `expected_owner`. A mismatch is rejected, so a compromised or repurposed URL cannot take over a record.
3. **Validates** against the schema and rules (appendix C), and validates each codebase's `publiccode_url` with the official parser.
4. **Publishes** the result:
   - **On success**, the harvested record is published and its `content_hash` and `harvested_at` are updated.
   - **On a validation failure**, the **last valid version** is kept and the record shows "Source failing validation since ‹date›". The errors are listed on `harvest/`.
   - **On a fetch failure** (404, timeout), the last valid version is kept and the record shows "Source unavailable since ‹date›". After 7 days it is listed on `harvest/` for a maintainer to decide whether to withdraw it. Records are never withdrawn automatically.
   - **A source that has never passed** (such as `csr-9007`) is not published. It appears only on `harvest/`.

**State without commits.** Last-valid copies and hashes are read from the live site (`state_url`, default `<base_url>/api/v0/harvest-state.json`) and written back with each deployment. This avoids two problems with committing snapshots: the baseline blocks direct pushes to `main`, and pull requests opened by the workflow's own token do not trigger required checks. The audit trail is the published harvest state and report, plus the workflow run logs. Before the first publication there is no state, and the harvester starts fresh.

**Scheduled-run caveat.** GitHub disables scheduled workflows after about 60 days without repository activity, and harvest runs do not commit. The runbook includes a monthly check. On-demand runs and pushes to `main` keep working regardless.

### 6.12 Register maintenance

| Action | Local record | Owner-hosted record |
|---|---|---|
| **Update** | Pull request to the file | Owner edits their `solution.yml`; published at the next harvest (daily, or on demand) |
| **Retire the asset** | `status: deprecated` with date and migration guidance; later `record_status: withdrawn` | The owner makes the same changes in their own file |
| **Remove from the register** (no longer meets the inclusion test, or the owner asks) | Change to a `withdrawn` record: ID and page kept, showing the reason | Replace the pointer with a local `withdrawn` record |
| **Delete** (example records; demonstration records on request; anything published in error) | Delete the file | Delete the pointer |
| **Source lost** | n/a | Last valid version kept and flagged; a maintainer decides (6.11) |
| **Move local → owner-hosted** | See below | n/a |
| **Move owner-hosted → local** | n/a | `csr move-to-local csr-NNNN` writes the last valid version as a local record, in one pull request |

**Moving a record to its owner, in one step:**

1. The owner downloads `solution.yml` from the record page, adjusts it if needed, and publishes it at their location. The recommended location is the root of the asset's own repository, beside `publiccode.yml`; otherwise any HTTPS URL. They can check it first with the validate page or the reusable workflow.
2. The owner raises a `move-to-owner-hosting` issue, or a maintainer runs `csr move-to-source csr-NNNN <url>`. Either way, a single pull request replaces the local record with a pointer.
3. The pull request check fetches and validates the remote file immediately, including the owner match, and the pull request cannot merge unless it passes.
4. On merge, the build harvests the file and the record shows "Hosted by ‹owner›". From then on, the owner's edits are published at each harvest.

**Deletion and history.** Deleting a file removes it from the site but **not from git history**. Removing content that should never have been published (for example personal or sensitive data) needs an exceptional procedure: rewriting history and asking GitHub to purge cached copies. `docs/maintenance.md` sets this out, and it is not a routine action.

### 6.13 User interface requirements (from the wireframes)

The wireframes (the sources in `ui/wireframes/` and the 22 approved images in `ui/baseline/`) are the **user interface requirements** for the build. Their files are committed to `ui/wireframes/`, and their approved screenshots to `ui/baseline/`. Where this specification and a wireframe disagree, the difference is raised with the author, not resolved silently.

**What is normative:** page inventory and navigation; page layout (the design system's layout patterns); the components used and their order; headings, labels, hint and error text, button text, link text and banner wording; tags and their colours; which fields appear on each record page and in which section; and the interactions listed below.

**What is not:** values in `[square brackets]` (filled from records, configuration or sources); counts and dates; and the sample records, which come from the real record set.

**Page-to-template map:**

| Wireframe | Template | Built path |
|---|---|---|
| Main | `index.html` | `./` |
| Solutions | `solutions.html` | `solutions/` |
| Browse | `browse.html` | `browse/` |
| Term | `term.html` | `sectors/`, `service-areas/`, `capabilities/<id>/` |
| Record-Hosted, Record-Demonstration, Record-Example | `record.html` (one template; sections and notices vary by provenance, hosting, status and currency) | `assets/<id>/` |
| Record-Withdrawn | `record-withdrawn.html` | `assets/<id>/` |
| Contribute | `contribute.html` | `contribute/` |
| Draft | `draft.html` | `draft/` |
| Validate | `validate.html` | `validate/` |
| Reference | `reference.html` | `reference/` |
| Publiccode | `publiccode.html` | `reference/publiccode/` |
| Data | `data.html` | `data/` |
| Currency | `currency.html` | `currency/` |
| Harvest | `harvest.html` | `harvest/` |
| About, Accessibility, Privacy | `about.html`, `accessibility.html`, `privacy.html` | `about/`, `accessibility/`, `privacy/` |
| NotFound | `404.html` | `404.html` |

**Behaviour parity.** The wireframes simulate some behaviour. The build must do at least what each wireframe shows, and in places more:

| Behaviour | In the wireframe | In the build |
|---|---|---|
| Search box | Filters by name, summary and owner as you type | Same, plus purpose and taxonomy synonyms; query kept in the URL so results can be shared |
| Provenance and asset-type filters, with counts | Working | Same |
| Sector, service area, capability, currency and withdrawn filters | Shown, not working | **Working**, with counts |
| Sort | Shown, not working | **Working**: name, recently changed, recently confirmed |
| Clear all filters; result count announced | Working | Same |
| Without JavaScript | Not shown | Full list shown; filters hidden |
| Draft form conditional sections | Software, API, deprecated, support, charges | Same, plus every condition in 6.4 |
| Draft form validation | Three fields checked; error summary and inline errors | **Every field**, against the real schema (Ajv), with the same error summary and inline error pattern |
| Draft form classification | Four sample terms, plus "[all 14 listed]" | **All terms**, generated from the taxonomy |
| solution.yml preview | Partial, updates live | **Complete**, updates live |
| Copy YAML, Download .yaml, open as GitHub issue, send by email | Buttons and links, inert | **Working**, as in 6.6 |
| Validate page | Paste mode with a simulated result | **Real validation** in paste, upload and URL modes, with the results table showing rule, field and fix |
| Record page actions | Links only | Working links; Download solution.yml produces the record's file |
| Mobile navigation | Not shown | The design system's mobile menu |

**Known differences, deliberately:** the wireframes use a few local styles (`wf-` classes) for layout details the design system does not provide: tag rows, the fictional-example panel, the YAML preview and the statistics tiles on the currency page. The build keeps these in `csr.css`, which uses design system spacing, colour and type values, and is limited to those cases. Since change W1 (version 1.5), the wireframes also style the header, the page band behind the breadcrumbs and page header, and the button colours; since change W2 (version 1.6), the record page's summary card (the actions in the page band, the key facts grid, the owner's panel, "On this page" and the band asking for corrections). The build keeps those in `csr.css` too. A deliberate change to the design changes the wireframes first, and is listed under "Changes to the wireframes" in `docs/ui-requirements.md`. The wireframes were drawn at 1280 pixels wide. The build must also work at 375 pixels (design system breakpoints), and is checked at both widths.

**Acceptance.**
1. **Visual comparison.** Playwright screenshots each built page, at 1280 and 375 pixels wide, using the test fixture records that reproduce the wireframe content, and compares them with `ui/baseline/`. The 1280-pixel baselines start as the approved wireframe images. Differences above a small threshold fail the check, with a diff image. A deliberate change to the design updates the baseline in the same pull request, so the change is visible and reviewed.
2. **Behaviour tests.** One Playwright test per row of the parity table.
3. **Accessibility.** `axe-core` on every page, with no serious or critical issues; plus the manual keyboard and screen-reader pass before publication.
4. **Author review.** The author compares the built preview with the wireframes before publication (slice S16).

`docs/ui-requirements.md` carries this section, and is updated whenever the wireframes change.

## 7. Baseline

- The repository is created from `repository-template`. Template setup writes `CODEOWNERS` as `* @<creator>` (extended as in 7.1) and fills in `publiccode.yml`, including the maintainer name from the creator's GitHub profile.
- An organisation owner runs `apply-baseline.sh`. That script changes only its own named ruleset, merge and security settings, and labels.
- The repository is public, which makes rulesets, secret scanning and Pages available on GitHub Free (appendix B).

### 7.1 Creating the repository from the template

The repository **must** be created from `The-Digital-Office/repository-template`. It is not created empty, and template files are not copied by hand. The sequence is:

| Step | Who | Action |
|---|---|---|
| 1 | Author, or another organisation member | On `repository-template`, choose **Use this template → Create a new repository**: owner `The-Digital-Office`, name `common-solution-register`, **public**, description "Demonstrator of a common solution register for the Scottish public sector". Do not include other branches. |
| 2 | Automatic | The template's setup workflow runs on the first push. It fills in the name, URL, date and code owner; sets the `publiccode.yml` maintainer from the creator's GitHub profile; removes the template-only README note and `.github/template/`; commits to `main`; opens the **Complete repository setup** issue; and runs the standards checks. |
| 3 | Author | Confirm the setup commit and issue exist (if not, run **Actions → Template setup → Run workflow**). |
| 4 | Organisation owner | Run `scripts/apply-baseline.sh common-solution-register` from `The-Digital-Office/.github`. This must come **after** step 2, because the setup workflow commits directly to `main`, which the baseline ruleset then blocks. |
| 5 | Author | Add topics in the **About** panel (for example `common-solutions`, `public-sector`, `scotland`, `publiccode`). |
| 6 | Build sessions, on branches `build/sNN-…`, by pull request | Every build change from here on, starting with the first pull request below. Nothing is pushed to `main` directly. |

**The first pull request completes the setup issue.** It:
- writes `README.md` in the template's structure (purpose, getting started, contributing, licence, maintainers);
- completes `publiccode.yml` (description, features, `softwareType: standalone/web`, categories, `developmentStatus: development`), and **removes every `TODO`** before any release tag, because the shared standards check then treats them as errors;
- deletes `.github/workflows/template.yml`, as the setup issue asks;
- adds the second maintainer to `CODEOWNERS` when named.

**What the build keeps, extends or replaces from the template:**

| Template file | Treatment |
|---|---|
| `.github/workflows/standards.yml` (calls the shared standards workflow `@v1`) | **Kept unchanged**; its two checks stay required by the baseline ruleset |
| `LICENSE` (MIT) | **Kept** for code; `LICENCE-CONTENT.md` (OGL v3.0) added for records and documentation, and the README licence section states both, as the template's wording already does |
| `CHANGELOG.md` (Keep a Changelog, Semantic Versioning) | **Kept and used**; each pull request adds to **Unreleased** |
| `.editorconfig` | **Kept** (it already sets four-space indentation for Python) |
| `.gitattributes` | **Kept** |
| `.gitignore` | **Extended** under its "language-specific entries" line: Python (`__pycache__/`, `.venv/`, `*.egg-info/`), build output (`site/`), test tooling (`node_modules/`, `test-results/`, `playwright-report/`) |
| `.github/dependabot.yml` (GitHub Actions, weekly, grouped) | **Extended** with `pip` (the `csr` tool) and `npm` (the UI test tooling) entries, in the same style |
| `.github/CODEOWNERS` (`* @<creator>`) | **Extended**: the `*` line is kept and gains the second maintainer, and `/records/`, `/taxonomy/` and `/schema/` lines are added to request review (6.7) |
| `publiccode.yml` | **Completed**, never replaced; it is the source of record `csr-0001` |
| `README.md` | **Completed** in the template's structure |
| Organisation-wide files (security policy, contributing guide, code of conduct, support, issue and pull request templates) | **Inherited** from `The-Digital-Office/.github`. The register adds its own issue forms (6.6) and its own `pull_request_template.md`, which **keeps the organisation template's sections and checklist** and adds the provenance, sources and OGL items. |

## 8. Handover and transfer

`docs/adopting-this-demonstrator.md` covers the following.

**Transfer or fork.** Transferring the repository keeps history, issues, pull requests, wiki, stars and watchers, and redirects repository links. **GitHub does not redirect the GitHub Pages site**, so the old Pages address stops working at the moment of transfer. Before transferring, publish a notice of the new address. Afterwards, set `base_url` and redeploy. Forking is the alternative; code is MIT and content OGL v3.0.

**Files to change first:**
- `site.toml`;
- `publiccode.yml` (organisation and maintainers);
- `CODEOWNERS`;
- banner and About wording;
- records: delete the example range and any demonstration records not kept, and confirm the rest with their owners.

**Repository settings to recreate or check:**
- the branch ruleset and its required check names (`standards / Required files`, `standards / publiccode.yml`, `Validate`);
- Pages source ("GitHub Actions") and `PAGES_ENABLED`;
- Dependabot alerts and security updates;
- secret scanning with push protection, and private vulnerability reporting;
- any editors team and the enforced editorial ruleset, if adopted;
- the standards workflow, which calls the Digital Office's public reusable workflow (`@v1`). It keeps working after transfer, or can be replaced;
- the daily harvest schedule, which needs re-enabling if GitHub has disabled it;
- `state_url` in `site.toml`. After transfer the old Pages address no longer serves harvest state, so the first harvest at the new address starts fresh; this is harmless, but failing sources lose their "last valid version" until they pass again.

**Owners' references.** Pointers in `records/` are unaffected by a transfer. Owners calling `validate-solution.yml` should update their `uses:` reference to the new repository location.

**Decision points:** listed in `decision-points.md`.

## 9. Build plan

The build is incremental, over many short sessions, because build capacity is limited and each session starts with no memory of the last.

- **All state lives in the repository.** The specification, wireframes, plan, progress log, code and tests are committed and pushed; nothing is kept only in a session.
- **`docs/build/PLAN.md`** opens with a short briefing (the project, the stack and the checks) and the resume protocol. It lists 17 slices (S0 for the author, S1 to S16 for the build). Each names the spec sections to read, its checkpoints and its acceptance checks, and ends with a progress log that records what was done, what is next and any blockers.
- **One slice per session, one pull request per slice.** Work is pushed at every checkpoint, so a session that runs out part-way loses nothing. The author merges each pull request, so `main` always works.
- **Fast checks in the session, heavy checks in CI.** Sessions run unit tests and record validation; visual, behaviour and accessibility tests run in GitHub Actions.
- **Order:** setup and scaffolding (S1), schema (S2) and validator (S3) first, because everything depends on them, then a walking skeleton (S5) so there is something to see early.
- **Starting a session:** the author's prompt, in 9.1.

### 9.1 Authorship and attribution

The repository, its history and its GitHub activity carry the author's identity only. No build tool is named or credited anywhere:

- **Commits** are authored as the author (`Robbie Harris <robbie.harris@digitaloffice.scot>`), set in the build environment's setup script, and carry no co-author or session trailers.
- **Pull requests** are opened by the author from pushed `build/sNN-…` branches, so they are authored by the author's account. Their titles and descriptions follow the organisation's pull request template, with no tool footer.
- **No comments** are posted on GitHub by build sessions; the author posts any that are needed.
- **No tool-specific files** are committed: there is no tool instruction file, and the build environment's setup script excludes tool working folders through a global git ignore file, so the repository's own `.gitignore` does not name them.
- **Documents** in the repository carry no tool acknowledgement. Any AI-use statement the Digital Office's documentation policy requires is the author's to add, in the author's words.
- **The session prompt** states these rules every time:

  > Continue the CSR demonstrator build: read `docs/build/PLAN.md` and follow its resume protocol. Commit as Robbie Harris <robbie.harris@digitaloffice.scot>. Do not add any AI or tool attribution anywhere: no Co-Authored-By or session trailers in commits, no generated-by lines in files or pull request text, and do not post comments or open pull requests on GitHub; push the slice branch and I will open the pull request.

Author steps outside the slices: creating the repository and applying the baseline (S0, section 7.1), verifying demonstration records (S15), courtesy notes, Digital Office sign-off, and enabling Pages.

## 10. Decisions and inputs

### 10.1 Decisions recorded (20 October 2026)

| Decision | Outcome |
|---|---|
| Descriptor file name | `solution.yml`, for now (listed in `decision-points.md`) |
| Harvest frequency | Daily, plus on demand |
| Changes to owner-hosted records | Published without maintainer review, with validation and owner match as the safeguards |
| Harvesting scope | Registered and known endpoints only; no discovery crawling or organisation scan |
| Service addresses | Add `service_url` (the live service) and `service_page_url` (the owner's description page) |
| User interface | Scottish Government Design System v4.3.0, with no Scottish Government branding, included in the build (vendored) |
| Solutions and codebases | A common solution is an owned offer of reuse; a codebase is not a solution on its own (1.1). `solution.yml` describes solutions; `publiccode.yml` describes codebases and is linked, not replaced. |
| Datasets | Out of scope: the register links to data catalogues through `open_data[]` but does not list datasets. Recorded in `decision-points.md` for the working group. |
| UI requirements | The wireframes are normative for the build's user interface, and are verified by automated visual and behaviour tests (6.13) |

### 10.2 Inputs needed from the author

| ID | Input | Recommendation |
|---|---|---|
| I1 | Repository name | `common-solution-register` (agreed); titled "Demonstrator" |
| I2 | Record set | Approve or amend 5.2, including whether `csr-0002` passes test 1 and whether to include the GOV.UK record |
| I3 | Contact mailbox for the site and emailed drafts | A Digital Office role mailbox |
| I4 | Feedback route for people without GitHub accounts | A Microsoft Form owned by the Digital Office, or the I3 mailbox |
| I5 | Visual identity | Scottish Government Design System components with a text-only header; "hosted by the Digital Office" in the footer |
| I6 | When to share with the SLWG | After the author's review and the I7 sign-off; confirm against the SLWG's first meeting date |
| I7 | Digital Office sign-off before publication | Named by the author (for example the CTO and communications lead) |
| I8 | DPO reference | The date and form of the DPO's agreement (6.9) |

## 11. Risks

| Risk | Control |
|---|---|
| The demonstrator is mistaken for a register, or for a Digital Office bid to run one | Banner; neutral styling; About page on the SLWG context; Digital Office sign-off |
| Owners are surprised or object to their service being described | Only 3–5 well-documented assets; courtesy notes before publication; deletion on request |
| Demonstration records are inaccurate or inferred | Sourced statements only; "not stated in public sources" sentinel; correction link |
| Example records are mistaken for real ones | "Example:" name prefix; distinct banner and styling; separate ID range; provenance facet |
| The draft form overruns | Architecture fixed (6.2); 3 days allocated; core journeys do not depend on it |
| Pages address lost on transfer | Transfer steps in section 8 |
| An owner publishes inaccurate or inappropriate content in their hosted file | Validation; owner match; the "suggest a correction" route; a maintainer can withdraw the pointer at once |
| A registered URL is compromised or repurposed | Owner-match check; HTTPS only; size and time limits; content treated as data and escaped |
| The daily harvest silently stops | Monthly runbook check; on-demand and push-triggered harvests are unaffected |
| `solution.yml` collides with other uses of that file name | Accepted for now; recorded in `decision-points.md` |
| The demonstrator hardens into a design by default | `decision-points.md` |
| Using the Scottish Government Design System is read as Scottish Government branding or ownership | No Scottish Government logo or brand assets; text-only header; About page states who hosts the demonstrator; recorded in `decision-points.md` as a choice an adopting body can change |

---

## Appendix A: `publiccode.yml` mapping

`publiccode.yml` describes a **codebase**, so importing one **adds or updates an entry in a solution's `codebases[]`**: `csr import-publiccode <url-or-path> --to csr-NNNN`. When the codebase belongs to a solution that has no record yet, `--new` also drafts the solution's record, pre-filling the solution fields marked "suggested" below for the owner to confirm or change, because a codebase's description is not necessarily the solution's. It parses the YAML and writes the draft. Unmapped mandatory fields are set to `TODO`, which validation rejects. Full validation against the standard is done by the official parser in the baseline workflow.

| `publiccode.yml` | Record field | Treatment |
|---|---|---|
| `url` | `codebases[].repository_url` | Copied; `visibility: public`; `publiccode_url` set to the file's location |
| `maintenance.type` | `codebases[].maintenance` | Copied |
| `softwareVersion` | `codebases[].version` | Copied |
| `name` | `name` | Suggested (new solution only) |
| `description.en.shortDescription` (at most 150 characters) | `summary` | Suggested (new solution only) |
| `description.en.longDescription` | `purpose` | Suggested (new solution only); editor shortens it |
| `developmentStatus` | `status` | Suggested (new solution only): `concept→concept`, `development→in-development`, `beta→beta`, `stable→live`, `obsolete→deprecated` |
| `legal.license` | `terms_of_use.licence` | Suggested where the solution is offered as the software itself; content licence added where relevant |
| `organisation.name`, else `legal.mainCopyrightOwner` | `owner.organisation` | Suggested; must match the solution owner |
| `landingURL` | `service_page_url` | Suggested (new solution only) |
| `description.en.documentation` | `documentation_url` | Copied |
| `description.en.apiDocumentation` | `interfaces[].documentation_url` | Copied, with `type` left for the editor |
| `roadmap` | `roadmap_url` | Suggested |
| `usedBy[]` | `adopters[]` with `evidence: self-reported` | Copied |
| `dependsOn` | `dependencies[]` | Summarised |
| `maintenance.contacts[]` | `codebases[].maintainers[]` (`name`, `affiliation`, `email`) | Copied; `phone` is not imported |
| `categories`, `intendedAudience.scope` | — | Printed as hints only |
| — | `contact` | Never derived from maintainers; must be role-based |

The register never writes to, extends or redefines `publiccode.yml`.

## Appendix B: GitHub Free, as it applies to a public repository

| Capability | Availability | Approach |
|---|---|---|
| Rulesets and branch protection | Public repositories | Available |
| Organisation rulesets and required workflows | Not on Free | Per-repository `apply-baseline.sh` |
| Push rulesets (file-path restrictions) | Not on Free (Team and Enterprise, for private and internal repositories) | Not needed |
| Required approvals and code-owner review | Public repositories; authors cannot approve their own pull requests | Requested, not enforced, in the demonstrator (6.7) |
| GitHub Pages | Public repositories; private Pages needs Enterprise Cloud | Public site; preview artifact on pull requests |
| Pages limits | 1 GB site; soft limits of 100 GB/month and 10 builds/hour; 10-minute deploy timeout | Far above need |
| Pages on repository transfer | Not redirected | Section 8 |
| Secret scanning with push protection, private vulnerability reporting, Dependabot, CodeQL | Free for public repositories | Enabled |
| Actions minutes | Free on standard runners for public repositories | None needed |
| Scheduled workflows | Disabled after about 60 days without repository activity | Daily harvest; monthly runbook check (6.11) |
| SAML SSO, audit-log streaming | Not on Free | Require two-factor authentication for organisation members |

## Appendix C: Validation rules

| Rule | Check | Severity |
|---|---|---|
| R01 | `id` matches the filename and is unique (including against the base branch, with `--base`) | Error |
| R02 | ID range matches provenance: `example` uses `csr-9000`–`9999`, and only `example` does | Error |
| R03 | Taxonomy references exist | Error |
| R04 | A referenced taxonomy term is deprecated | Warning |
| R05 | `related_assets` IDs exist | Error |
| R06 | `last_confirmed` is not in the future | Error |
| R07 | A `contact.value` that looks personal | Warning |
| R08 | Repository and source URLs respond (`--check-links`; never blocks a merge) | Warning |
| R09 | No value starts with `TODO` | Error |
| R10 | A sentinel value is used outside a `demonstration` record | Error |
| R11 | An `example` record's name does not begin "Example:" | Error |
| R12 | A codebase with `visibility: public` has no `publiccode_url` | Warning (counted for H6) |
| R13 | Vendored files (design system CSS and JavaScript, Ajv, `js-yaml`) match their pinned hashes (`pytest`) | Test failure |
| R14 | A harvested `id` and `owner.organisation` match the pointer's `id` and `expected_owner` | Error (not published) |
| R15 | A source is not HTTPS, exceeds the size limit, times out, or redirects to a non-HTTPS address | Error (last valid version kept) |
| R16 | A pointer resolves to a record whose status is not `owner-confirmed` or `withdrawn` (or `example`, within the `csr-9000`–`9999` range) | Error |
| R17 | A codebase's `publiccode.yml` fails the official parser | Warning, shown on the record page and on `harvest/` |
| R18 | `service_url`, `service_page_url`, `documentation_url`, a codebase `repository_url` or an `open_data` URL is not an HTTPS URL | Error |
| R19 | A codebase's `publiccode.yml` names a different `url` from its `repository_url`, or a `maintenance.type` that differs from `maintenance` | Warning |

## Appendix D: Disposition of the v0.4 review

| Finding | Disposition |
|---|---|
| F1 Unconfirmed descriptions of real services | **Accepted.** Reduced to 3–5 well-documented assets; courtesy notes (step 5); sentinel for unstated facts; Digital Office sign-off (step 8) |
| F2 Currency not demonstrable | **Accepted.** Example records with fictional confirmation dates show `due` and `stale` |
| F3 Conditional branches without honest records | **Accepted.** Example records `csr-9001`–`9005` |
| F4 Form architecture and estimate | **Accepted.** Built in Python, validated in the browser with vendored Ajv 2020 runtime and `js-yaml`; hand-written conditions; 3 days; API explorer replaced by build-time sample responses |
| F5 Hand-off limits | **Accepted.** Copy and download first; issue pre-fill within the URL limit; short `mailto:` asking for an attachment |
| F6 Duplicate field definitions | **Accepted.** Issue form reduced to a YAML text area plus three fields; options-match check dropped |
| F7 `approved_in` | **Accepted.** Renamed `merged_in` and labelled as a merge reference |
| F8 Dependence on v0.3 | **Accepted.** Appendices A and B; references to v0.3 removed |
| F9 Identifier policy and removal vs tombstone | **Accepted.** Example ID range; never-delete applies from adoption; deletion on request during the demonstrator |
| F10 Transfer leaves settings behind | **Accepted, verified.** GitHub does not redirect Pages on transfer; settings checklist added |
| F11 Privacy notice scope | **Accepted** (6.9) |
| F12 Accessibility of JavaScript pages | **Accepted.** Only `draft/` needs JavaScript; error summary and `aria-live` |
| F13 Internal sign-off | **Accepted.** Step 8; I7 |
| F14 Step 4 estimate | **Accepted.** 2.5 days |
| F15 "You" and "I" | **Accepted.** Third person throughout |
| DPO wording | **Accepted.** Date recorded; reference to be added (I8); adopters must revisit |
| Non-functional gaps | **Accepted.** Observability and hosting location (6.1) |
