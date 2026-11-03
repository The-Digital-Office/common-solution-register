# Maintenance

How maintainers look after the register's records and its code, and the
routine checks that keep it working (specification 6.12). How records are
reviewed is in [`editorial-model.md`](editorial-model.md); how owner-hosted
records are harvested is in [`harvesting.md`](harvesting.md).

Every change goes through a pull request: the ruleset blocks direct pushes to
`main`. The `Validate` and `UI tests` checks must pass before merging.

## Maintainer commands

Install with `pip install -e ".[dev]"`. Each command writes a file in
`records/` for you to review and propose in a pull request.

| Command | Does |
|---|---|
| `csr new --from-issue issue.md [--issue-url URL]` | Takes the `solution.yml` from a **Suggest a solution** issue (save the issue body to a file, or pass `-` and paste it), refuses an id already in the register, allocates the next free id (in the example range for fictional examples), and records the issue as the confirmation reference |
| `csr import-publiccode <url-or-path> --to csr-NNNN` | Adds a codebase to a local record from its `publiccode.yml`, or updates it (matched by repository address): repository, maintenance, version and maintainers |
| `csr import-publiccode <url-or-path> --new [--id csr-NNNN]` | Drafts a new record from a `publiccode.yml`, with suggestions to confirm and `TODO` wherever a person must decide (validation rejects `TODO`, rule R09) |
| `csr move-to-source csr-NNNN <url>` | Checks the owner's hosted file exactly as the harvester will, then replaces the local record with a pointer; nothing changes if it would not be published |
| `csr move-to-local csr-NNNN [--state PATH-OR-URL]` | Replaces a pointer with the last valid harvested version, as a local record |
| `csr validate [--base origin/main] [--check-links]` | Checks the register, or given files and addresses; `--check-links` also checks that addresses respond (warnings only) |
| `csr harvest`, `csr build` | See [`harvesting.md`](harvesting.md) and the README |
| `csr check-publiccode <path>` | Runs the official `publiccode.yml` parser on a file |

The mapping from `publiccode.yml` is in
[`publiccode-mapping.md`](publiccode-mapping.md).

## Handling issues

| Issue form (label) | What to do |
|---|---|
| Suggest a solution (`new record`) | Check the inclusion test ([`contributing-records.md`](contributing-records.md)); `csr new --from-issue`; open a pull request that says "Closes" the issue |
| Suggest a correction (`correction`) | Make the change in a pull request. For an owner-confirmed record, ask the owner first. For an owner-hosted record, ask the owner to change their file |
| Host our own solution.yml (`owner hosting`) | Check the person is from the owning organisation; `csr move-to-source`; open a pull request |
| Give feedback (`feedback`) | Reply, and record anything the working group should hear |

Email to the register's mailbox is handled the same way. An emailed draft
arrives as an attached `solution.yml`: save it, check it with `csr validate`,
and add it with a pull request.

## Maintaining records

| Action | Local record | Owner-hosted record |
|---|---|---|
| **Update** | Pull request to the file | The owner edits their file; it is published at the next harvest |
| **Retire the solution** | `status: deprecated` with `deprecation` (date and migration guidance); later `record_status: withdrawn` with `withdrawal` (date and reason) | The owner makes the same changes in their file |
| **Remove from the register** (no longer passes the inclusion test, or the owner asks) | Change it to a `withdrawn` record: its id and page stay, showing the reason | Replace the pointer with a local `withdrawn` record |
| **Delete** (fictional examples; demonstration records on request; anything published in error) | Delete the file | Delete the pointer |
| **Source lost** | — | The last valid version stays published and flagged; after 7 days, decide whether to withdraw it |
| **Move to the owner** | `csr move-to-source` | — |
| **Move back** | — | `csr move-to-local` |

During the demonstrator, a record about a real solution is **deleted** if its
owner asks. Once a register is operated, identifiers are never deleted: removed
records become withdrawn tombstones (decision point DP-11).

**Withdrawing a pointer at once.** If an owner-hosted file publishes something
inappropriate, open a pull request that replaces the pointer with a local
`withdrawn` record (or deletes it). It takes effect at the deployment after the
merge; to speed that up, run the Site workflow by hand.

### Removing content from history

Deleting a file removes it from the site but **not from git history**, and
GitHub keeps cached views of old commits. If content that should never have
been published (for example personal or sensitive data) is committed, it needs
an exceptional procedure, not a routine one:

1. Remove it from the current files in a pull request, and deploy.
2. Agree the rest with the repository's administrators and the Data
   Protection Officer: it means rewriting history, which the ruleset forbids
   and every clone and open pull request would have to follow.
3. Rewrite history to remove the file (for example with `git filter-repo`), with
   the ruleset temporarily relaxed by an administrator, then restore the
   ruleset.
4. Ask GitHub Support to remove cached views and pull request references of
   the old commits, and ask anyone with a clone to delete it and clone afresh.
5. If the content was a credential, revoke it first: rewriting history does not
   make it safe again.

## Dependencies

| Dependency | How it is updated |
|---|---|
| GitHub Actions, Python packages | Dependabot pull requests (weekly). Actions are pinned by SHA with the version in a comment; Python packages are pinned exactly in `pyproject.toml` |
| npm test tooling | Dependabot proposes patch releases only. **Playwright** minor and major versions are upgraded by hand: see "Upgrading Playwright" in [`ui-requirements.md`](ui-requirements.md), because a new Playwright brings a new Chromium and so new baseline images |
| Vendored browser files | `python tools/vendor.py NAME VERSION` (`sgds`, `js-yaml`, `ajv`, `roboto`, `roboto-mono`) downloads the package, checks its integrity hash and writes the files with `SOURCE.md` and `SHA256SUMS` (checked by the R13 test). The version is part of the path, so also change the references: `SGDS_VERSION` in `src/csr/build.py` and the import in `static/js/init.js` (design system); the imports in `static/js/draft.js` and `validate.js` (js-yaml); the script tags in `templates/draft.html` and `validate.html` and `tests/js/record-check.test.mjs` (Ajv); `static/fonts.css` (fonts). Delete the old folder. A design system or font change needs new baselines |
| The official `publiccode.yml` parser | Change `VERSION` and the `SHA256` values (from the release's `checksums.txt`) in `tools/install-publiccode-parser.py` |

A pull request that changes how pages look must update the UI baselines in the
same pull request (`npm run test:ui:update`, or the Site workflow's
**update-baselines** option), so reviewers see the difference.

## Runbook

### Monthly

- [ ] **The daily harvest is still running.** Open **Actions → Site** and check
      there is a scheduled run in the last day. GitHub disables scheduled
      workflows after about 60 days without activity in the repository; if it
      is disabled, choose **Enable workflow**. Pushes and on-demand runs keep
      harvesting regardless.
- [ ] **The harvest report** (`harvest/` on the site, or the latest run's job
      summary). For each source flagged as unavailable for more than 7 days,
      contact the owner and decide whether to withdraw it. For each failing
      source, tell the owner what fails.
- [ ] **Currency** (`currency/` on the site). Ask the owners of records that
      are due or stale to confirm them.
- [ ] **Open pull requests and issues**, including Dependabot's. Merge security
      updates promptly.
- [ ] **Links** (optional): `csr validate --check-links`. Warnings about hosts
      that refuse automated requests (HTTP 403) can be ignored once checked by
      hand.

### When the rules or the reusable workflow change

Owners call `validate-solution.yml@v0`. When a change keeps existing files
valid, move the tag after merging:

```bash
git fetch origin
git tag -f v0 origin/main
git push -f origin v0
```

A change that would make existing files invalid needs a new schema version and
a new tag (`v1`), announced to owners first.

### Fictional examples

The examples are judged as on `examples_as_of` in `site.toml`, so they keep
showing the current, due and stale states without their dates being moved.
Leave it unchanged unless the examples are rewritten.

### When a build or deployment fails

GitHub notifies the person whose commit triggered the run. Open the run, read
the failing step, and fix it in a pull request. A failed deployment leaves the
previous site in place. If the failure is in `UI tests` and the images differ
only slightly, see "Tests" in [`ui-requirements.md`](ui-requirements.md).

### Yearly

- [ ] Review the accessibility statement and privacy notice, and their dates
      in `[publication]` in `site.toml`.
- [ ] Confirm the register's own record (`solution.yml`, `csr-0001`) by
      updating `confirmation.last_confirmed`.
- [ ] Review [`decision-points.md`](decision-points.md) against what the
      working group has decided.
