# User interface requirements

The wireframes in [`ui/wireframes/`](../ui/wireframes/) and the approved images
in [`ui/baseline/`](../ui/baseline/) are the user interface requirements for the
build (specification section 6.13, which this document carries). This document
records how the build applies them, and every departure from them. Update it
whenever the wireframes or the templates change.

## What is normative

Page inventory and navigation; page layout (the design system's layout
patterns); the components used and their order; headings, labels, hint and
error text, button text, link text and banner wording; tags and their colours;
which fields appear on each record page and in which section; and the
interactions in the behaviour-parity table of section 6.13.

Not normative: values in `[square brackets]`, counts and dates, and the sample
records, which come from the real record set.

## Design system

The Scottish Government Design System 4.3.0 is vendored under
`src/csr/static/vendor/sgds/4.3.0/` (see `SOURCE.md` there). `static/js/init.js`
initialises the components the site uses: the mobile site navigation, skip
links and details. The header follows the design system's site header with
its mobile menu control; its icons are inline SVG paths, because the design
system's graphic assets are not vendored. Above the title it shows
`header_line` from `site.toml` ("Scottish public sector"), and its look
follows decision D37.

Local styles are in `src/csr/static/csr.css`, limited to the cases section
6.13 allows: tag rows, the fictional-example panel, unstated values, the
actions column, the results heading row, filters and wide tables; and the
header, page band and button colours of decision D37. Wireframe
`wf-` classes are renamed `csr-`.

## Tests

`npm run test:ui` (after `pip install -e .`, `npm ci` and `npx playwright install chromium`) builds
the fixture register in `ui/tests/fixtures/` and runs, in Chromium:

- `ui/tests/visual.spec.js`: every page below, at 1280 and 375 pixels, compared with its approved
  image in `ui/baseline/` (at most 1% of pixels may differ). The browser draws text without font
  hinting or subpixel positioning, so screenshots match across Linux machines. After a deliberate
  design change, run `npm run test:ui:update` and commit the new images in the same pull request,
  so the change is visible in review. If CI's images still differ from yours, run the Site workflow
  by hand on the branch (**Actions → Site → Run workflow**, with **update-baselines** ticked),
  download the `ui-baselines` artifact, review the images and commit them instead.
- `ui/tests/behaviour.spec.js`: one test per row of the behaviour-parity table.
- `ui/tests/accessibility.spec.js`: axe-core on every page, failing on any serious or critical issue.

The `UI tests` job in `site.yml` runs them on every pull request and uploads the report and image
differences if they fail.

**Upgrading Playwright.** Dependabot proposes only patch releases of Playwright. To move to a new
minor or major version, change `@playwright/test` in `package.json` and the `playwright-core`
override to the same version, run `npm install --package-lock-only --ignore-scripts`, then remake
the baselines (the Site workflow's `update-baselines` option), review the images and commit them
in the same pull request. A new Playwright brings a new Chromium, which draws text slightly
differently.

## Page-to-template map

| Wireframe | Template | Built path | Slice |
|---|---|---|---|
| Main | `index.html` | `./` | S5 (list), S7 (search, filters, sort: `static/js/search-core.js` and `search.js`) |
| Record-Hosted, Record-Demonstration, Record-Example | `record.html` | `assets/<id>/` | S5 |
| Record-Withdrawn | `record-withdrawn.html` | `assets/<id>/` | S5 |
| Browse | `browse.html` | `browse/` | S6 |
| Term | `term.html` | `sectors/<id>/`, `service-areas/<id>/`, `capabilities/<id>/` (every term) | S6 |
| Contribute, About, Accessibility, Privacy | `contribute.html`, `about.html`, `accessibility.html`, `privacy.html` | `contribute/`, `about/`, `accessibility/`, `privacy/` | S6 |
| Reference, Publiccode | `reference.html`, `publiccode.html` | `reference/`, `reference/publiccode/` | S6 |
| Data, Currency | `data.html`, `currency.html` | `data/`, `currency/` | S6 |
| NotFound | `404.html` | `404.html` (links from the site root, because GitHub Pages serves it at any missing address) | S6 |
| Draft | `draft.html` | `draft/` | S8 (form, conditions, preview: `static/js/draft-core.js` and `draft.js`), S9 (validation with `static/js/record-check.js` and the vendored Ajv; hand-off) |
| Validate | `validate.html` | `validate/` | S10 (`static/js/validate.js`, with `record-check.js`, Ajv and `js-yaml`) |
| Harvest | `harvest.html` | `harvest/` | S11 (from the harvest state; `src/csr/harvest.py`) |

## Departures and the author's decisions

Raised rather than resolved silently (section 6.13). **Decided by the author
on 3 November 2026**, before the visual baselines were approved (slice S14):

| # | Decision |
|---|---|
| D1 | As built: the long banner on the home page and the short banner on every other page, as the wireframes show. Section 6.8 of the specification was corrected to match in version 1.3. |
| D2, D3 | As built: one record template with the union of the three record wireframes' sections and sidebar. |
| D4 | As built: generic wording in the fictional-example panel. |
| D5 | Changed: Roboto, the design system's typeface, and Roboto Mono for code are served from the site itself (`static/fonts.css`, `vendor/roboto/`, `vendor/roboto-mono/`); no font service is contacted. |
| D19 | As built: all eight sectors under "Intended for". |
| All others | Accepted as built. |

**Decided by the author on 12 November 2026**, after the site was published as
a preview, to give each page a clearer start (the first of three stages of a
redesign; the record page and the home page follow):

| # | Decision |
|---|---|
| D37 | Changed: the header, page band and buttons, as described in the table below. Specification 6.13 was updated to allow these local styles in version 1.4. |

The table below records each departure as raised.

| # | Where | Wireframe or specification | Build | Why |
|---|---|---|---|---|
| D1 | Banner, every page | Specification 6.8 gives one long banner text for every page. The wireframes use it only on Main; the other 18 pages say "This is not an official register. Inclusion does not mean endorsement." | Follows the wireframes: long text on the home page, short text elsewhere | The wireframes are normative for banner wording; the author to confirm |
| D2 | Record page sidebar | The three record wireframes differ. Record-Hosted has "Actions" (buttons and links), Contents and Record history. Record-Demonstration has "Service links", "Is this your service?", "Use this record" and Contents. Record-Example has "Service links", "Use this record" and "Other states shown by examples". | One template with: "Service links" (when the record has service addresses); "Is this your service?" (demonstration records); "Use this record"; Contents; "Other states shown by examples" (examples, generated from the example records); Record history | Section 6.13 requires one template; this is the union, using the headings two of the three wireframes share |
| D3 | Record page sections | Record-Example omits Classification, the owning sector, Record ID and Hosting, and lists codebases as a summary list. | Every record shows every section of Record-Hosted, and codebases as a table | One template; the fullest wireframe is followed |
| D4 | Fictional-example panel | Explains the specific state, for example "It shows how the register displays a deprecated service whose record has not been confirmed for over 12 months." | "This record does not describe a real ‹type›. It shows how the register displays a record like this." | The schema has no field for the explanation; the tags and notices on the page show the state. A field could be added if the author wants the specific wording |
| D5 | Font | The wireframes load Roboto from Google Fonts | Decided: Roboto (and Roboto Mono for code) served from the site itself | Loading fonts from Google would send visitors' addresses to a third party, against the privacy notice (section 6.9) |
| D6 | "Hosted by its owner" panel | "It was last harvested on [harvest date] and passed validation." | Resolved in S11: as the wireframe, with the harvest date and time; a failing or unavailable source shows a warning, "Source failing validation since ‹date›" or "Source unavailable since ‹date›", in place of the panel | — |
| D7 | publiccode.yml column | "Valid (official parser)" | Resolved in S11: the parser's verdict from the harvest state: "Valid (official parser)", "Fails the official parser" (with its messages), "Unavailable" or "Not yet checked" | — |
| D8 | Home page without JavaScript | Not shown | Filters and sorting are hidden; the full list of current (not withdrawn) records is shown, sorted by name | Section 6.13 parity table; withdrawn records stay reachable at their address |
| D9 | "Due for confirmation" notice | No wireframe | An information message, "This record is due for confirmation", in the same place as the stale warning | So that the due state is visible on the record page as well as in its tag |
| D10 | Example currency | Not shown | Fictional examples are judged as on `examples_as_of` in `site.toml` (2 November 2026), so they keep showing current, due and stale; real records are judged on the build date. The Currency page says so | Otherwise the examples drift: `csr-9004` would turn stale after 1 December 2026, and the current examples would become due (S4 note) |
| D11 | Inputs not yet decided | `[role mailbox]`, `[Data Protection Officer]`, `[date]` and similar placeholders on Contribute, About, Accessibility and Privacy | Filled from `site.toml`; until then a highlighted "[To be completed before publication: …]" is shown, and `csr build` lists what is outstanding. Without a mailbox, Contribute leaves out the "Email us" route, and corrections and removal point to GitHub | Nothing is invented; the author completes inputs I3, I4 and I8 before publication |
| D12 | Term page "Related terms" | Shown, with no source for the relation | Terms of the same taxonomy that appear on the same records, most frequent first; the section is left out when there are none | The taxonomy has no "related" field |
| D13 | Data page | The harvest state row links to the file | Resolved in S11: the row links to the published `api/v0/harvest-state.json` | — |
| D14 | Reference page | Optional fields as a paragraph; "17 rules (R01 to R17)" | Mandatory and optional fields as tables generated from the schema (sub-fields of required objects listed separately); all 19 rules listed with severity | The specification's appendix C has 19 rules; generating from the schema keeps the page true to it |
| D15 | Contribute "Contributing guide", About "ask for your record to be moved", feedback on GitHub | Links | Link to `docs/contributing-records.md` and the `move-to-owner-hosting` and `feedback` issue forms | Those files arrive in S13 and S16; the links work once they exist |
| D16 | Home page without JavaScript | Not shown | The search box is hidden as well as the filters and sort, because a static site cannot search without the script; the full list is shown, as the parity table requires | A search box that silently did nothing would mislead |
| D17 | Filter counts | Provenance and asset-type counts reflect the search query only | Every count (provenance, type, sector, service area, capability, currency) is faceted: the number of results that option would give, with the query and the other filter groups applied | With several working filter groups, counts that ignored the other groups would promise results that are not there |
| D18 | Search matching | Substring of name, summary and owner | Every query word must start a word in the name, summary, owner, purpose, record ID, asset type, or the labels and synonyms of the record's terms; accents and punctuation are ignored | Substring matching let short words match inside others ("gis" in "register") |
| D19 | Draft "Intended for" | Four groupings: Local government; Scottish Government and agencies; NHS Scotland; Other Scottish public bodies | All eight sector terms | The parity table requires all terms, generated from the taxonomy; a grouping would map to several sectors without saying so |
| D20 | Draft preview | Shows every field, with empty values (`name: ""`) | Shows only what has been entered, in schema order, plus `id: csr-NNNN  # allocated when registered` | The preview is the file people submit; S9's validation lists what is still missing |
| D21 | Draft summary count | "0 of 200 characters" | The design system's character count component and its wording | Section 6.13 asks for the design system's components |
| D22 | Draft conditions not in the wireframe | Not shown | Sources, and a "Not stated in public sources" choice for terms, adoption, support and charges, when the person is not from the owning organisation (condition 1); withdrawal date and reason when correcting a withdrawn record (condition 3); interfaces as a repeater | The parity table requires every condition in 6.4 |
| D23 | Draft hand-off | Copy, download, issue and email are always available | Each first checks the draft; if there are problems, the error summary is shown instead, so every route produces a validated record | Specification 2: "every route produces the same validated record" |
| D24 | "Open as a GitHub issue" | Opens in the same tab | Opens in a new tab, and says so in the link text | Leaving the page would lose the draft, which is kept only in the page |
| D25 | Downloaded file name | "Download .yaml" | The file is `solution.yml`, the descriptor's name; the button keeps the wireframe's wording | The same file can be submitted or hosted by the owner |
| D26 | The draft's record ID | `id: csr-NNNN  # allocated when registered` | Kept. The browser and `csr validate` both accept `csr-NNNN` in a draft outside `records/`, with a warning that the id is allocated when registered; in `records/` a real id is required (R01) | So a draft that passes in the browser also passes `csr validate` |
| D27 | Draft preview position | Sticky beside the form | Sticky from the large breakpoint up; S14's full-page screenshots should hold it at the top (for example by scrolling to the top first) | Full-page screenshots draw sticky elements where the page was last scrolled |
| D28 | Validate page without JavaScript | Not shown | A note that the page needs JavaScript, pointing to `csr validate` and the workflow; the modes and button are hidden | Specification 6.8: the page "needs JavaScript, and the page says so" |
| D29 | Validate results | A simulated pass or three sample problems | Real results: the schema and every rule that needs no network (R02 to R07, R09 to R12, R18), errors before warnings; with only warnings the "Valid" panel is shown with the warnings below; a pointer record is checked against the pointer schema, with a link to check the file it points to; `?url=` opens URL mode and checks that address | The parity table requires real validation with rule, field and fix |
| D30 | Validate page sample text | The paste box starts with an example | It starts empty | The wireframe's sample is illustration, not content |
| D31 | Harvest report times | "[date and time]", "[date]" | Dates with times in UTC ("3 November 2026 at 08:36 UTC"); "Never" for a source never harvested; a source that has never passed is named from its file but not linked | Harvests run several times a day in CI; UTC avoids ambiguity |
| D32 | Harvest report problems | One entry per failing source | Every source with findings, including R17 warnings on published records; a source unavailable for more than 7 days is flagged for a maintainer's decision | Specification 6.11 |
| D33 | Visual baselines | The approved wireframe images | As section 6.13 describes: the baselines started as the wireframe images, and slice S14 replaced each with the built page's screenshot in the same pull request, so the difference was visible in review; 375-pixel images were added. The wireframe images remain in git history and can be regenerated with `tools/render-wireframes.js` | A built page never matches a drawing pixel for pixel; the review of each difference is the approval |
| D34 | Landmarks and focus | Not shown | The phase banner is a named region ("Demonstrator notice"); each sidebar aside is named by its heading; code examples that scroll sideways can be focused with the keyboard | Found by axe-core in S14 |
| D35 | Footer organisation | "Hosted for demonstration by [host organisation]." as text | The host's logo (`host_logo` in `site.toml`), using the design system's footer logo pattern, linked to the host's website (`host_url`); its alt text is that sentence, so screen readers still hear who hosts it. With `host_logo` empty, the text is shown | Author's feedback, 9 November 2026 |
| D36 | Draft form after "Check my answers" | A green "valid" panel: "Copy or download it below, then submit it or host it yourself" | The panel scrolls fully into view and is followed by "Send it to the register", with the GitHub issue, email and download options themselves (the sidebar keeps them too), and says nothing has been sent yet. Filled in from a record ("Suggest a correction"), it says "Your correction is ready to send", the issue opens the correction form with the record ID and the corrected YAML, and the email subject names the record; for an owner-hosted record it tells the owner to update their own file. "Start again" is "Clear and start again" on a new draft; on a correction it is replaced by "Discard edits", a link back to the record. On a correction, "Are you from the owning organisation?" must be answered: Yes confirms the record today (and makes a demonstration entry owner-confirmed); No suggests a change without altering its provenance or confirmation. Choices keep the record's order | Author's feedback, 9 November 2026: after checking a correction, nothing seemed to happen, and nothing was sent |
| D37 | Header, page band and buttons, every page | The design system's site header with the title "Common Solution Register: Demonstrator" in regular weight; a grey phase banner; the page header on white; the design system's blue buttons | A small line, "Scottish public sector" (`header_line` in `site.toml`), above the title "Common Solution Register" in large bold navy; bold navy navigation with a thicker bar under the current page; a compact white phase banner with the same wording, so "Demonstrator" is still on every page; a full-width tinted band behind the breadcrumbs and the page header, with navy page titles; navy primary buttons and navy-outlined secondary buttons | Three thin grey strips of similar weight came before each page and nothing marked where it began. The line above the title says who the register is for without naming a body that runs it. Decided by the author on 12 November 2026 |

