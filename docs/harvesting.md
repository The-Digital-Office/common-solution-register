# Harvesting

How the register publishes records that their owners host themselves
(specification 6.11). For owners, the practical steps are in
[Hosting your solution.yml](hosting-your-solution-yml.md).

## What is harvested

Only **registered endpoints**: the `source` address in each pointer record in
`records/`. Every pointer got there through a reviewed pull request. The
harvester never searches for files that have not been registered (decision
point DP-04).

Sources that are files in this repository (the register's own `solution.yml`
and the fictional `examples/hosted/`) are read from the working tree, so they
can be checked without the network.

## When it runs

The `Validate` job of the Site workflow (`.github/workflows/site.yml`):

| Trigger | What it harvests |
|---|---|
| Daily, at 05:23 UTC | Every registered source, starting from the published state |
| Every push to `main` | The same |
| On demand (**Actions → Site → Run workflow**) | The same |
| A pull request | This repository's sources without the network; then any pointer the pull request adds or changes, fetched from the network with `--fail-on-problems`, so a pointer cannot be registered unless its file passes |

The harvest report is written to the job summary of every run, and published
on the site at `harvest/` with each deployment.

**GitHub disables scheduled workflows** after about 60 days without activity
in the repository, and harvests do not commit, so they do not count as
activity. The monthly check in [`maintenance.md`](maintenance.md) covers this.
Pushes and on-demand runs keep working regardless.

## For each source

1. **Fetch** over HTTPS only, within the limits in `site.toml` (`[harvest]`:
   256 KB and 10 seconds), refusing redirects to addresses that are not HTTPS,
   and parse it as data only (rule R15).
2. **Match the owner:** the file's `id` and `owner.organisation` must equal the
   pointer's `id` and `expected_owner` (R14). A mismatch is rejected, so an
   address that is compromised or reused cannot take over a record.
3. **Check the status:** `owner-confirmed` or `withdrawn`, or `example` in the
   example range (R16).
4. **Validate** against the schema and every rule, and check each codebase's
   `publiccode.yml` with the official parser (R17, a warning).
5. **Publish** the result:

| Result | State | What is published |
|---|---|---|
| Passes | `ok` | The new version; its `content_hash`, `harvested_at` and `last_changed` are updated |
| Fails validation | `failing` | The **last valid version**, marked "Source failing validation since ‹date›"; the problems are listed on `harvest/` |
| Cannot be fetched | `unavailable` | The last valid version, marked "Source unavailable since ‹date›"; after 7 days it is flagged on `harvest/` for a maintainer |
| Has never passed | `failing` or `unavailable` | Nothing; the source appears only on `harvest/` (the fictional `csr-9007` shows this) |

Records are never withdrawn automatically. A changed `source` or
`expected_owner` starts the source's state afresh.

## The harvest state

The state is a JSON file (`state_version` 1) holding, for each source, its
state, the last valid copy, its hash, and the dates it was checked, harvested,
changed, and started failing or became unavailable, with the findings and the
parser's verdict on each `publiccode.yml`.

It is **not committed**. Each run reads the previous state from the live site
(`state_url` in `site.toml`; empty means `<base_url>api/v0/harvest-state.json`)
and the deployment publishes the new one there (decision point DP-39). Before
the site is first published there is no state, so the first harvest starts
fresh. If the state cannot be read, the harvest also starts fresh: harmless,
except that a failing source has no last valid version to fall back on until
it passes again.

## The official publiccode.yml parser

`tools/install-publiccode-parser.py` installs `publiccode-parser-go` at a
pinned release (v5.4.3), checking its SHA-256 against the value pinned from
the release's checksums, into `.tools/` (not committed). The harvester finds it
there, through the `CSR_PUBLICCODE_PARSER` environment variable, or on the
path, and runs it without network access on every linked `publiccode.yml`. If
it is not installed, files are marked "Not yet checked". To upgrade it, change
the version and checksums in the script, in a pull request.

## Running it yourself

```bash
csr harvest                          # every source, from the published state
csr harvest --no-network             # only the sources in this repository
csr harvest --only csr-0001          # one source, keeping the others' state
csr harvest --state path/or/url      # start from another state
csr build --harvest .harvest/harvest-state.json --base-url http://localhost:8000/
```

`csr harvest` writes `.harvest/harvest-state.json` (ignored by git). `--format
github` writes annotations, `--summary PATH` writes the report as Markdown, and
`--fail-on-problems` exits with an error if any source has problems.
