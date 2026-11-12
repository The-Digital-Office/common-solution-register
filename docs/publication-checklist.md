# Publication checklist

What the author does, in order, between the end of the build and sharing the
site with the short-life working group (specification 9, author steps; inputs
in 10.2). Nothing here needs code changes beyond small pull requests to
`site.toml` and `solution.yml`.

Tick each item in a pull request that edits this file, or keep the record
elsewhere and note where.

**Preview first (decided 9 November 2026).** The author publishes the site as a
preview before the courtesy notes, the manual accessibility check and sign-off:
`preview = true` in `site.toml` asks search engines not to index any page
(decision point DP-54), and `csr-0001` stays `in-development`. Step 6 can
therefore come before steps 1 to 5; step 2 ends the preview.

## 1. Inputs

- [ ] **Mailbox live (I3).** `solution-register@digitaloffice.scot` receives
      mail, and its automatic reply is on. Send a test message and check the
      reply: the 10-working-day response time, and working links to the site,
      the [privacy notice](https://the-digital-office.github.io/common-solution-register/privacy/)
      and the
      [accessibility statement](https://the-digital-office.github.io/common-solution-register/accessibility/).
      The links work only once the site is published (step 6); recheck them then.
- [ ] **Publication inputs** in `site.toml` `[publication]`, each agreed with the
      person responsible. `csr build` lists any still empty, and the pages show
      "[To be completed before publication: …]" until they are filled:
  - [ ] `data_controller_address`: the Digital Office's address as data
        controller
  - [ ] `dpo_contact`: how to contact the Data Protection Officer
  - [ ] `lawful_basis` (I8): as agreed with the Data Protection Officer
  - [ ] `retention`: how long emails to the mailbox and feedback are kept
  - [ ] `feedback_form` (I4): who owns the feedback route and how long its
        responses are kept (the mailbox, decided 3 November 2026)
  - [ ] `accessibility_assessment`: how the site was assessed (the automated
        tests and the manual check in step 4)
  - [ ] `accessibility_tested_on`: the date of the manual check
  - [ ] `statements_prepared_on`: the date the accessibility statement and
        privacy notice were prepared
- [ ] **DPO reference (I8).** Add the date and form of the Data Protection
      Officer's agreement to importing maintainer names and emails (given on
      19 October 2026, specification 6.9) where the Digital Office records
      such agreements, and note it here: ……
- [ ] **`csr-0002` intended adopters.** Currently `local-government` only, as
      the Digital Office's own audience. Widen it if the baseline is offered to
      the whole public sector.

## 2. The register's own record

When the site goes to beta, end the preview: set `preview = false` in
`site.toml`, so search engines may list it. `csr-0001` stops being in
development. In `solution.yml`:

```yaml
status: beta
support:
  summary: >-
    Questions and feedback to the register's mailbox, answered within 10
    working days. Not an operated service: no service level applies.
service_url: https://the-digital-office.github.io/common-solution-register/
service_page_url: https://the-digital-office.github.io/common-solution-register/about/
```

(`beta` services must give support and both addresses: condition 7.) Update
`confirmation.last_confirmed` to the date. Check with `csr validate`, and merge
it with or just before enabling Pages.

## 3. Courtesy notes to owners

Before publication, write to the owner of every real solution described by a
demonstration record (specification 5.2). Use the contact routes the records
themselves cite:

| Owner | Records | Contact route |
|---|---|---|
| Scottish Government (ScotAccount team) | `csr-0003` ScotAccount | scotaccount@gov.scot, or the [contact page](https://scotaccount.servicemanual.gov.scot/contact) |
| Scottish Government (Design System team) | `csr-0004` Scottish Government Design System | designsystem@gov.scot |
| Improvement Service | `csr-0005` One Scotland Gazetteer, `csr-0006` Spatial Hub, `csr-0008` mygovscot myaccount | One note covering all three, to a named contact if the Digital Office has one; otherwise gazcustomers@improvementservice.org.uk (Gazetteer), spatialhub@improvementservice.org.uk (Spatial Hub) and the [myaccount help page](https://signin.mygovscot.org/portal/pages/help) |
| Government Digital Service | `csr-0007` GOV.UK Notify | The [Notify support page](https://www.notifications.service.gov.uk/support) |

A suggested note, to adapt:

> Subject: Your service in the common solution register demonstrator
>
> The Digital Office for Scottish Local Government has built a demonstrator of
> a common solution register for the short-life working
> group on a common solution register. It is not an official register, and
> inclusion does not mean endorsement.
>
> To show how real solutions could be described, it includes a short entry
> about ‹solution›, compiled only from your public pages, which it cites. The
> entry is clearly marked as compiled from public sources and not confirmed by
> you, and anything your pages do not say is shown as "Not stated in public
> sources". You can see it here: ‹link to the record page, or the attached
> solution.yml before publication›.
>
> We plan to publish the demonstrator on ‹date›. If anything is wrong, or you
> would rather your service were not included, reply to this email and we will
> correct or remove it. If you would like to confirm the entry, or publish and
> maintain it yourselves, we would be glad to help.
>
> ‹name›, The Digital Office for Scottish Local Government
> solution-register@digitaloffice.scot

- [ ] Notes sent (dates): ……
- [ ] Replies handled: corrections made, or records removed on request (delete
      the file: `maintenance.md`, "Maintaining records")

Before publication the record pages are not online. Attach each record's
`solution.yml`, or the record page from the `site-preview` artifact of the
latest pull request.

## 4. Manual accessibility check

The automated tests (axe-core on every page and state, and the behaviour tests)
pass, but they do not replace a person (specification 6.9: WCAG 2.2 AA, with a
manual keyboard and screen-reader pass). Use the `site-preview` artifact or a
local build (README). Check at least: the home page, a record page of each kind
(owner-hosted `csr-0001`, demonstration `csr-0003`, example `csr-9003`,
withdrawn `csr-9005`), Browse, a term page, Contribute, the draft form and the
validate page.

**Keyboard only** (no mouse), in a desktop browser:

- [ ] "Skip to main content" is the first thing Tab reaches, and works.
- [ ] Every link, button and form control can be reached with Tab, in a
      sensible order, and its focus is clearly visible.
- [ ] The mobile menu (narrow the window to phone width) opens and closes with
      the keyboard.
- [ ] Home page: type a search, choose filters and a sort order, and clear
      them, all from the keyboard.
- [ ] Draft form: complete a record, submit it with errors, use the error
      summary links to reach each field, fix them, and use Copy YAML and
      Download.
- [ ] Validate page: paste a file, check it, and read the results table.
- [ ] Nothing traps focus, and nothing moves or appears without warning.

**Screen reader** (NVDA with Firefox or Chrome on Windows, or VoiceOver with
Safari on a Mac or iPhone):

- [ ] Each page's title and main heading say where you are; headings make
      sense when listed (NVDA: Insert+F7; VoiceOver: the rotor).
- [ ] Landmarks are announced: header, navigation, the demonstrator notice,
      main and footer.
- [ ] Home page: the result count is announced after a search or filter.
- [ ] Record page: tags (provenance, status, currency) and "Not stated in
      public sources" are read meaningfully.
- [ ] Draft form: labels, hints and errors are read with each field, and the
      error summary is announced when it appears.
- [ ] Tables (record codebases, validate results, harvest report) are read
      with their headers.

**Other:**

- [ ] At 200% and 400% zoom (or 320 pixels wide), nothing is cut off and
      there is no scrolling sideways except in code examples.
- [ ] With JavaScript turned off, the home page lists every record, and the
      draft and validate pages say they need JavaScript.

Record what you found, and fix or list each problem in the accessibility
statement before publication. Then fill in `accessibility_tested_on` and
`accessibility_assessment` (step 1).

- [ ] Manual check done (date and who): ……

## 5. Sign-off (I7)

- [ ] Show the Digital Office signatories (for example the CTO and the
      communications lead) the site preview, the About page, the banner and
      this checklist, and record their sign-off: ……

## 6. Publish

- [ ] **Settings → Pages → Source: GitHub Actions.**
- [ ] **Settings → Secrets and variables → Actions → Variables:** create
      `PAGES_ENABLED` with the value `true`.
- [ ] Run the Site workflow on `main` (**Actions → Site → Run workflow**), or
      merge any pull request. `Deploy` now runs.
- [ ] Open https://the-digital-office.github.io/common-solution-register/ and
      check: the banner, a record page of each kind, `harvest/` (the
      register's own record and `csr-9006` harvested, `csr-9007` failing, as
      intended), `data/` and its downloads, and the 404 page (any missing
      address).
- [ ] The next day, check that the scheduled run harvested from the published
      state: the `Harvest (every registered source)` step's log says "Previous
      state read from …", not "starting fresh".
- [ ] Recheck the mailbox's automatic reply links (step 1).
- [ ] Add the site's address to the repository's About panel.

## 7. Share (I6)

- [ ] Share the address with the working group, after sign-off, and in time
      for its next meeting; point members to the About page and
      [`decision-points.md`](decision-points.md).
