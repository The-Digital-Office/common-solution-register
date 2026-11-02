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
system's graphic assets are not vendored.

Local styles are in `src/csr/static/csr.css`, limited to the cases section
6.13 allows: tag rows, the fictional-example panel, unstated values, the
actions column, the results heading row, filters and wide tables. Wireframe
`wf-` classes are renamed `csr-`.

## Page-to-template map

| Wireframe | Template | Built path | Slice |
|---|---|---|---|
| Main | `index.html` | `./` | S5 (list), S7 (search, filters, sort) |
| Record-Hosted, Record-Demonstration, Record-Example | `record.html` | `assets/<id>/` | S5 |
| Record-Withdrawn | `record-withdrawn.html` | `assets/<id>/` | S5 |
| Browse | `browse.html` | `browse/` | S6 |
| Term | `term.html` | `sectors/<id>/`, `service-areas/<id>/`, `capabilities/<id>/` (every term) | S6 |
| Contribute, About, Accessibility, Privacy | `contribute.html`, `about.html`, `accessibility.html`, `privacy.html` | `contribute/`, `about/`, `accessibility/`, `privacy/` | S6 |
| Reference, Publiccode | `reference.html`, `publiccode.html` | `reference/`, `reference/publiccode/` | S6 |
| Data, Currency | `data.html`, `currency.html` | `data/`, `currency/` | S6 |
| NotFound | `404.html` | `404.html` (links from the site root, because GitHub Pages serves it at any missing address) | S6 |
| Draft | `draft.html` | `draft/` | S8, S9 |
| Validate | `validate.html` | `validate/` | S10 |
| Harvest | `harvest.html` | `harvest/` | S11 |

## Departures and open questions for the author

Raised rather than resolved silently (section 6.13). Each is the build's
current choice until the author decides.

| # | Where | Wireframe or specification | Build | Why |
|---|---|---|---|---|
| D1 | Banner, every page | Specification 6.8 gives one long banner text for every page. The wireframes use it only on Main; the other 18 pages say "This is not an official register. Inclusion does not mean endorsement." | Follows the wireframes: long text on the home page, short text elsewhere | The wireframes are normative for banner wording; the author to confirm |
| D2 | Record page sidebar | The three record wireframes differ. Record-Hosted has "Actions" (buttons and links), Contents and Record history. Record-Demonstration has "Service links", "Is this your service?", "Use this record" and Contents. Record-Example has "Service links", "Use this record" and "Other states shown by examples". | One template with: "Service links" (when the record has service addresses); "Is this your service?" (demonstration records); "Use this record"; Contents; "Other states shown by examples" (examples, generated from the example records); Record history | Section 6.13 requires one template; this is the union, using the headings two of the three wireframes share |
| D3 | Record page sections | Record-Example omits Classification, the owning sector, Record ID and Hosting, and lists codebases as a summary list. | Every record shows every section of Record-Hosted, and codebases as a table | One template; the fullest wireframe is followed |
| D4 | Fictional-example panel | Explains the specific state, for example "It shows how the register displays a deprecated service whose record has not been confirmed for over 12 months." | "This record does not describe a real ‹type›. It shows how the register displays a record like this." | The schema has no field for the explanation; the tags and notices on the page show the state. A field could be added if the author wants the specific wording |
| D5 | Font | The wireframes load Roboto from Google Fonts | No web font is loaded; the design system's font stack falls back to Helvetica or Arial | Loading fonts from Google would send visitors' addresses to a third party, against the privacy notice (section 6.9). Vendoring Roboto (Apache 2.0) is an option for S14, where it matters for visual comparison |
| D6 | "Hosted by its owner" panel | "It was last harvested on [harvest date] and passed validation." | "…which passed validation when the site was built." | Until the harvester (S11) records harvests, owner-hosted files in this repository are read at build time |
| D7 | publiccode.yml column | "Valid (official parser)" | "Not yet checked" | The official parser runs in the harvester (S11) |
| D8 | Home page without JavaScript | Not shown | Filters and sorting are hidden; the full list of current (not withdrawn) records is shown, sorted by name | Section 6.13 parity table; withdrawn records stay reachable at their address |
| D9 | "Due for confirmation" notice | No wireframe | An information message, "This record is due for confirmation", in the same place as the stale warning | So that the due state is visible on the record page as well as in its tag |
| D10 | Example currency | Not shown | Fictional examples are judged as on `examples_as_of` in `site.toml` (2 November 2026), so they keep showing current, due and stale; real records are judged on the build date. The Currency page says so | Otherwise the examples drift: `csr-9004` would turn stale after 1 December 2026, and the current examples would become due (S4 note) |
| D11 | Inputs not yet decided | `[role mailbox]`, `[Data Protection Officer]`, `[date]` and similar placeholders on Contribute, About, Accessibility and Privacy | Filled from `site.toml`; until then a highlighted "[To be completed before publication: …]" is shown, and `csr build` lists what is outstanding. Without a mailbox, Contribute leaves out the "Email us" route, and corrections and removal point to GitHub | Nothing is invented; the author completes inputs I3, I4 and I8 before publication |
| D12 | Term page "Related terms" | Shown, with no source for the relation | Terms of the same taxonomy that appear on the same records, most frequent first; the section is left out when there are none | The taxonomy has no "related" field |
| D13 | Data page | The harvest state row links to the file | The row is shown without a link until the harvester publishes `api/v0/harvest-state.json` (S11) | So that no link leads nowhere |
| D14 | Reference page | Optional fields as a paragraph; "17 rules (R01 to R17)" | Mandatory and optional fields as tables generated from the schema (sub-fields of required objects listed separately); all 19 rules listed with severity | The specification's appendix C has 19 rules; generating from the schema keeps the page true to it |
| D15 | Contribute "Contributing guide", About "ask for your record to be moved", feedback on GitHub | Links | Link to `docs/contributing-records.md` and the `move-to-owner-hosting` and `feedback` issue forms | Those files arrive in S13 and S16; the links work once they exist |

