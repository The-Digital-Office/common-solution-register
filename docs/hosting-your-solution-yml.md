# Hosting your solution.yml

An owner can publish their solution's record themselves, as a `solution.yml`
file at an address they control. The register then holds only a **pointer**
to it, and publishes the owner's file at every harvest: daily, on demand, and
whenever the register changes. Owners keep their record current by editing
their own file, without asking anyone.

This guide is for owners. How the harvester works is in
[`harvesting.md`](harvesting.md).

## Who can host

The owning organisation of a solution, for an `owner-confirmed` (or
`withdrawn`) record. Demonstration records, which describe someone else's
solution, are always held in the register.

## Moving your record to your own hosting

1. **Get the file.** On your record's page, choose **Download solution.yml**
   (it downloads as `csr-NNNN.yml`; save it as `solution.yml`).
   For a new solution, use the
   [draft form](https://the-digital-office.github.io/common-solution-register/draft/).
2. **Check and adjust it.** Set `record_status: owner-confirmed` and fill in
   `confirmation` (`last_confirmed`, how you confirmed it, and where). Keep the
   `id` the register gave you, and make `owner.organisation` your
   organisation's name exactly as the register has it.
3. **Publish it** at an HTTPS address that returns the file itself. The
   recommended place is the root of the solution's own repository, beside its
   `publiccode.yml`; any HTTPS address works. On GitHub, use the file's raw
   address (`https://github.com/<owner>/<repo>/raw/main/solution.yml`).
4. **Check it** on the
   [validate page](https://the-digital-office.github.io/common-solution-register/validate/)
   (give it the address), or with `csr validate <address>`.
5. **Ask for the move** with the **Host our own solution.yml** issue form
   (the record ID and the file's address). A maintainer runs
   `csr move-to-source csr-NNNN <address>`, which checks the file exactly as
   the harvester will and, if it passes, replaces the local record with a
   pointer in a single pull request.
6. The pull request's checks fetch and validate your file again, including the
   owner match, and it cannot merge unless they pass. Once it is merged, your
   record shows "Hosted by ‹owner›", and your edits are published at each
   harvest.

A pointer looks like this (`records/csr-0001.yaml`):

```yaml
id: csr-0001
source: https://github.com/The-Digital-Office/common-solution-register/raw/main/solution.yml
expected_owner: The Digital Office for Scottish Local Government
```

## Checking your file on every change

If your file is in a GitHub repository, call the register's reusable workflow,
so every pull request that changes it is checked against the register's schema
and rules, and any `publiccode.yml` against the official parser. Add
`.github/workflows/common-solution-register.yml`:

```yaml
name: Common solution register
on: [pull_request]
permissions:
  contents: read
jobs:
  solution:
    uses: The-Digital-Office/common-solution-register/.github/workflows/validate-solution.yml@v0
```

Optional inputs: `path` (default `solution.yml`) and `publiccode` (default
`publiccode.yml`; skipped if there is none). `v0` is moved forward when the
rules change in ways that keep existing files valid.

## What the register checks at every harvest

- The address is HTTPS, answers within 10 seconds, returns at most 256 KB, and
  does not redirect to an address that is not HTTPS.
- The file's `id` and `owner.organisation` match the pointer's `id` and
  `expected_owner`. If you rename your organisation, ask for the pointer to be
  updated first.
- `record_status` is `owner-confirmed` or `withdrawn`.
- The file passes the schema and every rule.

If a new version fails, **the last valid version stays published**, and your
record says "Source failing validation since ‹date›"; the problems are listed
on the [harvest report](https://the-digital-office.github.io/common-solution-register/harvest/).
If your address stops answering, the record says "Source unavailable since
‹date›"; after 7 days a maintainer is asked to decide what to do. Records are
never withdrawn automatically.

## Keeping it current

- Change your file whenever the solution changes. It is published at the next
  harvest, without review.
- Confirm it about once a year by updating `confirmation.last_confirmed`. The
  record is shown as **due** after 11 months and **stale** after 12.
- To retire the solution, set `status: deprecated` with a `deprecation` date
  and migration guidance; later, `record_status: withdrawn` with a
  `withdrawal` date and reason.
- To stop hosting, ask a maintainer to run `csr move-to-local csr-NNNN`, which
  turns the last valid version back into a record held by the register.
