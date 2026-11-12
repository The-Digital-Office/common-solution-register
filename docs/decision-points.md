# Decision points

The demonstrator makes many choices so that it can work at all. None of them
is a decision for the Scottish public sector: the short-life working group
(SLWG) decides whether a register is built, by whom and to what design. This
document lists each choice the SLWG, or a body adopting the demonstrator, may
want to revisit: what was built, the main alternatives, and what would need to
change (specification section 4, principle 7).

Each entry has an identifier (`DP-NN`) so that it can be referred to in
discussion. "Decided" means decided **for the demonstrator**, by the author,
on the date given.

User interface choices, where the build departs from the wireframes, are in
[`ui-requirements.md`](ui-requirements.md) (D1 to D34).

## A. Scope and model

| # | Choice | As built | Alternatives | What would change |
|---|---|---|---|---|
| DP-01 | What the register lists | **Common solutions**: capabilities an accountable owner offers to other public bodies, with a way to adopt them (specification 1.1). A public repository is not a solution unless someone offers it and takes responsibility for it | A catalogue of all public sector code, or of all digital services whether offered or not | The inclusion test, the schema's required fields (owner, contact, terms, adoption route), and the record set |
| DP-02 | Solutions and codebases | A solution's record **links** to the codebases that implement it (`codebases[]`); each public codebase is described by its own `publiccode.yml`, in its own repository, which the register validates but never replaces or extends | Describe software only with `publiccode.yml` (no `solution.yml`); or merge the two into one file | The schema, the importer (`csr import-publiccode`) and the harvester's parser step |
| DP-03 | Datasets | Out of scope: a solution links to the data it publishes through `open_data[]`, and the register does not list datasets (decided 20 October 2026) | List datasets as a record type; or link to a data catalogue's entries by identifier | The schema (a new asset type and fields), the taxonomy and the pages |
| DP-04 | Discovery | The harvester visits **registered endpoints only**: the `source` addresses in pointer records, each added through a reviewed pull request. There is no organisation scan or web crawl | Scan GitHub organisations or the web for `solution.yml` and `publiccode.yml` files, and propose records from what is found | A discovery job, a review queue for what it finds, and rules for whose files may be listed without asking |
| DP-05 | Federation | None: one register, one repository | Federate with other catalogues (for example the UK government's), exchanging records through the API | An exchange format and an identifier scheme shared with the other catalogues |
| DP-06 | Descriptor file name | `solution.yml`, for now (decided 20 October 2026). The name is generic, and other tools may use it for other things | A more specific name, such as `common-solution.yml` or `csr.yml` | The harvester's default, the reusable workflow's `path` default, the draft form's download name and the documentation; existing pointers name their files explicitly, so they would keep working |
| DP-07 | Record set size | 15 records: 2 owner-confirmed, 6 demonstration and 7 fictional examples. Specification 3.1 expected 10 to 13, and 5.2 limited demonstration records to 3 to 5; the author added a sixth, mygovscot myaccount, as a strong local government example (decided 3 November 2026) | Fewer demonstration records, or none, relying on examples | Only `records/`; nothing else depends on the number |

## B. Provenance, identifiers and removal

| # | Choice | As built | Alternatives | What would change |
|---|---|---|---|---|
| DP-08 | Provenance | Every record has a `record_status`: `owner-confirmed`, `demonstration` (compiled from cited public sources, not confirmed), `example` (fictional; the name begins "Example:") or `withdrawn` (specification 5.1) | In an operated register, only owner-confirmed records, with demonstration and example records removed | An adopting body may delete the example range and any demonstration records it does not keep |
| DP-09 | Unstated facts | In demonstration records only, six fields may say `not-publicly-stated` ("Not stated in public sources") instead of an inferred value: terms of use type, adoption route, charges, support, service address and service page | Leave the fields out (making them optional), or require owners' confirmation before listing | The schema's sentinel definition and condition 1 |
| DP-10 | Identifiers | `csr-` and four digits; `csr-0001` to `csr-8999` for real records and `csr-9000` to `csr-9999` for fictional examples; the next free id is the one after the highest in use | A scheme that carries meaning (sector or owner codes), or identifiers shared with other catalogues | The schema's pattern, rule R02 and `csr new` |
| DP-11 | Removal during the demonstrator | A record about a real solution is **deleted** if its owner asks; withdrawn tombstones are used only by an example. The rule that identifiers are never deleted takes effect only at adoption (specification 5.1) | Tombstone every removed record from the start | Nothing in the code: the choice is in the maintenance procedure ([`maintenance.md`](maintenance.md)) |
| DP-12 | The inclusion test | Six tests from the proposal (4.3): reuse by more than one body; owner accepts responsibility; role-based contact; can be classified; status and terms can be stated; no sensitive information. For demonstration records the owner's responsibility is replaced by a courtesy note | A stricter test (for example a minimum number of adopters), or a lighter one for early-stage solutions | The contributing guide and the editors' review |

## C. Descriptor schema v0.1

The specification fixed the fields and their eight conditions (6.4). Where it
left details open, the build chose as below (S2). The author asked for all of
them to be reviewed as part of the demonstrator.

| # | Field | As built | Alternatives |
|---|---|---|---|
| DP-13 | `terms_of_use` | `type` (`open-licence`, `service-terms`, `commercial-terms`, `other`) plus an SPDX `licence` expression or a `url`, and an optional `summary` | A licence only; or a controlled list of standard agreements (for example data sharing or memorandum of understanding templates) |
| DP-14 | `contact` | `type` (`role-mailbox`, `service-desk`, `web-form`) and `value`, which must be an email address for a role mailbox and an HTTPS address for a web form; never a named person (warned by R07) | Several contacts by purpose (adoption, support, security) |
| DP-15 | `sources[]` | `url`, `title`, `accessed` date and optional `publisher`; required in demonstration records | Quoted supporting words in the record itself, as kept outside it in [`demonstration-sources.md`](demonstration-sources.md) |
| DP-16 | `charging.model` | `recharge`, `subscription`, `per-transaction` or `other`, required when charges apply, with a summary or a link | Price fields; or no model, only text |
| DP-17 | `interfaces[].type` | `rest`, `soap`, `graphql`, `file`, `event` or `other`, each with a documentation address | Link to machine-readable descriptions (OpenAPI) and validate them |
| DP-18 | `related_assets[]` | `id` and an optional `relationship`: `replaced-by`, `replaces`, `uses`, `used-by`, `alternative` or `related` | A smaller set, or relationships to things outside the register |
| DP-19 | `adopters[]` | `organisation` (free text) and `evidence` (`self-reported` or `verified`) | Organisations from a controlled list, so adopters can be counted and searched |
| DP-20 | `confirmation` | `last_confirmed` date, and free-text `method` and `reference` | A controlled list of methods, or a signed attestation |
| DP-21 | Web addresses | Every address is HTTPS, enforced by the schema as well as rule R18 | Allow HTTP for legacy pages |
| DP-22 | `owner.organisation` | Free text, matched exactly against a pointer's `expected_owner` when harvesting | Organisations from a controlled list with identifiers, which would make the owner match robust to small differences in wording |
| DP-23 | Schema version | `schema_version: "0.1"`; a change that breaks existing files would need a new version and a migration | Version the schema by date, or not at all |

## D. Taxonomy

| # | Choice | As built | Alternatives | What would change |
|---|---|---|---|---|
| DP-24 | The vocabularies | Three drafts for the SLWG to critique: 8 sectors, 14 service areas and 14 capabilities, each with a definition and synonyms (`taxonomy/`) | Align with existing vocabularies, such as the LGA/ESD lists or a Scottish Government taxonomy (specification 6.5) | The taxonomy files; existing records would need their terms mapped. Deprecating a term (`status: deprecated`) keeps old records valid with a warning (R04) |
| DP-25 | Sectors | Seven Scottish sectors plus `uk-public-sector`, used for both the owner's sector and "Intended for"; and `scottish-public-sector`, an audience for "Intended for" only (`intended_adopters_only`; R03 rejects it as an owner's sector), added 9 November 2026 | Separate lists for owners and audiences; finer sectors (for example separate further and higher education) | The sector file and the records |

## E. Validation rules

The rules are in [`schema/README.md`](../schema/README.md) (specification
appendix C). These interpretations were made in the build (S3 and later):

| # | Rule | Interpretation |
|---|---|---|
| DP-26 | R02 | `withdrawn` records may use either identifier range |
| DP-27 | R01 with `--base` | A record added on a branch whose identifier the base branch has since taken is reported, which catches two pull requests allocating the same identifier |
| DP-28 | R07 | A contact looks personal when its local part is two words joined by `.` or `_` and neither is a role word (`register`, `solutions`, `support`, `enquiries` and others); hyphenated local parts are not flagged. It is a warning, never an error |
| DP-29 | R08 | Checks codebase repository and `publiccode.yml` addresses, demonstration sources and pointer sources, only with `--check-links`, and never blocks a merge. Some hosts refuse automated requests (HTTP 403), so a warning is not proof that a link is broken |
| DP-30 | R09 | Values that **start** with `TODO` are rejected, not `TODO` inside text |
| DP-31 | R18 | Also enforced by the schema, so a non-HTTPS address gives two findings; the sentinel is left to R10 |
| DP-32 | Draft identifiers | `csr-NNNN` is accepted outside `records/` with a warning, so a draft that passes in the browser also passes `csr validate` |
| DP-33 | Messages | Schema problems are reworded in plain English, identically in the browser and in `csr validate` (`src/csr/messages.py`) |

## F. Currency

| # | Choice | As built | Alternatives | What would change |
|---|---|---|---|---|
| DP-34 | Thresholds | A record is **due** 11 months and **stale** 12 months after `last_confirmed` (`site.toml`); demonstration records are always "Not confirmed by owner" | Different periods by asset type or status; reminders sent to owners | `site.toml`; reminders would need a notification route |
| DP-35 | Fictional examples | Judged as on a fixed date (`examples_as_of`, 2 November 2026), so they keep showing the states they were written to show | Move their dates forward periodically | `site.toml` |
| DP-36 | Owner-hosted records | Currency comes from the owner's own `last_confirmed`; the harvest shows whether the file is reachable and valid, which is not the same as confirmation | Treat a successful harvest as a confirmation | The currency calculation in `src/csr/register.py` |

## G. Distributed publication

| # | Choice | As built | Alternatives | What would change |
|---|---|---|---|---|
| DP-37 | Changes to owner-hosted records | Published at the next harvest **without maintainer review**; review applies when a pointer is registered or changed. Safeguards: full validation, the owner match (R14), the allowed statuses (R16), and keeping the last valid version if a new one fails (decided 20 October 2026) | Hold changed files for review before publication | A review queue, and the harvest would publish only approved hashes |
| DP-38 | Harvest frequency | Daily, on demand, and on every push to `main` (decided 20 October 2026) | Hourly; or only on demand | The `schedule` in `.github/workflows/site.yml` |
| DP-39 | Harvest state | Kept on the live site (`api/v0/harvest-state.json`), not committed, because the baseline blocks direct pushes to `main` and pull requests opened by the workflow's token do not run required checks (specification 6.11) | Commit snapshots through pull requests opened by a GitHub App | A GitHub App and its credentials |
| DP-40 | Lost sources | The last valid version stays published and is flagged; after 7 days the harvest report flags it for a maintainer. Nothing is withdrawn automatically | Withdraw automatically after a period | The harvester and the maintenance procedure |
| DP-41 | Who may host | Only `owner-confirmed` and `withdrawn` records (and fictional examples) may be owner-hosted; demonstration records are always local | Allow third parties to host descriptions of others' solutions | Rule R16 and the provenance model |

## H. Editorial model and contribution

| # | Choice | As built | Alternatives | What would change |
|---|---|---|---|---|
| DP-42 | Editorial review | Review is **requested** (`CODEOWNERS`), not enforced; see [`editorial-model.md`](editorial-model.md) for the two-approval model an operated register could adopt | Enforce code-owner review for `records/`, `taxonomy/` and `schema/` | An editors team of at least two and a ruleset |
| DP-43 | Contribution routes | Pull request; the draft form (copy, download, GitHub issue or email); assisted drafting by a maintainer; import from `publiccode.yml`; owner hosting | A web form backed by a service, so contributors need neither GitHub nor email | A server-side component, which the demonstrator avoids |
| DP-44 | Issues are public | GitHub issue forms say so, and carry the Open Government Licence statement | A private route for submissions that are not yet ready to publish | The email route already gives one; a form service would be another |
| DP-45 | Feedback without GitHub | The role mailbox `solution-register@digitaloffice.scot` (input I4, decided 3 November 2026) | A Microsoft Form owned by the Digital Office | `feedback_url` and `[publication]` in `site.toml`, and the privacy notice |

## I. Presentation, technology and hosting

| # | Choice | As built | Alternatives | What would change |
|---|---|---|---|---|
| DP-46 | Design system | The Scottish Government Design System 4.3.0, vendored, with a text-only header and no Scottish Government logo or brand assets; the About page says who hosts the demonstrator, and the footer shows the host's logo (decided 20 October 2026; logo added 9 November 2026). Using it could be read as Scottish Government branding | GOV.UK Frontend, or the adopting body's own design system | The templates and the vendored files; the UI baselines would be remade |
| DP-47 | Banner | One short notice on every page, home included, as a warning notification message: "This is a demonstrator, not an official register. Inclusion does not mean endorsement." (decided 12 November 2026, wireframe change W4; until then, the long notice on the home page and a short one elsewhere in a phase banner, D1) | The long notice on the home page; a phase banner with a "Demonstrator" tag; the design system's warning text (with the triangle icon), which is kept for warnings about a record | `src/csr/templates/partials/banner.html`, `csr.css` and the baselines |
| DP-48 | Fonts | Roboto and Roboto Mono served from the site itself; no font service is contacted (D5) | System fonts only | `static/fonts.css` and the baselines |
| DP-49 | Architecture | A static site built by Python and published on GitHub Pages; JavaScript only for search, the draft form and the validate page; no server, cookies or analytics | A hosted application with a database, sign-in and editing | Almost everything; the record files, schema and taxonomy could be kept |
| DP-50 | API | Static JSON under `api/v0/`, plus JSON and CSV extracts; `v0` signals no promise of stability | A versioned API with a change policy | The API's path and a published policy |
| DP-51 | Hosting | Hosted by the Digital Office on GitHub Pages in the US, on GitHub Free | Another host, or the adopting body's own | `site.toml` and the steps in [`adopting-this-demonstrator.md`](adopting-this-demonstrator.md) |
| DP-52 | Maintainer data | Names and emails of codebase maintainers are imported from owner-published `publiccode.yml` files, with the Digital Office Data Protection Officer's agreement for the demonstrator (specification 6.9) | Do not import personal data at all | `csr import-publiccode` and the privacy notice. **An adopting body must revisit this** |
| DP-53 | Reusable workflow version | Owners call `validate-solution.yml@v0`; the `v0` tag is moved when the rules change compatibly | Pin to a release, or to a commit | The tag and owners' workflow files |
| DP-54 | Publishing as a preview | Published on GitHub Pages on 9 November 2026 as a preview, before the courtesy notes, the manual accessibility check and sign-off. Anyone with the address can see it; every page asks search engines not to index it (`preview` in `site.toml`, a robots meta tag) | Wait until all of them are done; or publish privately, which GitHub Pages offers only on Enterprise Cloud | `preview = false` when the site goes to beta (`publication-checklist.md`). The tag is honoured by the main search engines, not by every crawler, and does not cover downloads such as the JSON and CSV extracts |
| DP-55 | Home page and finder length | The home page introduces the register and shows only the three records most recently changed or confirmed (whichever is later), leaving out withdrawn records and including fictional examples, so it stays short however many records there are (decided 12 November 2026, wireframe change W3). The finder at `solutions/` lists every current record on one page, with no pagination (decided 9 November 2026). Search and filters narrow the list, and without JavaScript the full list is the fallback. Comfortable up to a few hundred records; beyond about 300 to 500 the finder gets long and heavier on phones | For the finder: "Show more" (the first 25 or 50 results, then more on request), or numbered pages kept in the address like the filters. For the home page: more or fewer recent records (`RECENT_COUNT` in `build.py`) | `static/js/search.js` and `templates/solutions.html` for the finder; `recently_updated()` in `build.py` and `templates/index.html` for the home page; the full list would stay as the finder's no-JavaScript fallback |
