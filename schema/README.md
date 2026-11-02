# Schemas

| File | Describes |
|---|---|
| [`asset.schema.json`](asset.schema.json) | A full record: the `solution.yml` descriptor, schema version 0.1 (specification 6.4) |
| [`pointer.schema.json`](pointer.schema.json) | A pointer record, which registers an owner-hosted `solution.yml` (`id`, `source`, `expected_owner`) |
| [`taxonomy.schema.json`](taxonomy.schema.json) | A taxonomy file in [`taxonomy/`](../taxonomy/) |

All are JSON Schema draft 2020-12. Records are written in YAML. Dates are
written as `YYYY-MM-DD` and checked as strings.

## Conditions

Beyond the mandatory fields, the asset schema enforces eight conditions:

| # | When | Then required |
|---|---|---|
| 1 | `record_status = demonstration` | `sources[]` (public URLs). The sentinel `not-publicly-stated` is allowed in `terms_of_use.type`, `adoption_route.summary`, `support.summary`, `charging.applies`, `service_url` and `service_page_url`, and **only** in demonstration records |
| 2 | `record_status` is `owner-confirmed` or `example` | `confirmation.last_confirmed`, `.method`, `.reference` |
| 3 | `record_status = withdrawn` | `withdrawal.date`, `withdrawal.reason` |
| 4 | `asset_type = software` | At least one entry in `codebases[]` |
| 5 | `asset_type = api`, or `interfaces` present | `interfaces[]`, each with `type` and `documentation_url` |
| 6 | `charging.applies = true` | `charging.model`, plus `charging.url` or `charging.summary` |
| 7 | `asset_type` is `service` or `platform`, and `status` is `beta` or `live` | `support`, `service_url` and `service_page_url` |
| 8 | `status = deprecated` | `deprecation.date`, `deprecation.migration_guidance` |

Each condition has a passing and a failing fixture in
[`tests/fixtures/schema/`](../tests/fixtures/schema/).

Fields the register derives at build time (`last_changed`, `history_url`,
`merged_in`, `currency`, `hosting`, `source`, `harvested_at`, `content_hash`,
`source_state`) are never written in a record, and the schema rejects them.

## Validation rules

`csr validate` applies the schema, then these rules (specification appendix C).

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
| R12 | A codebase with `visibility: public` has no `publiccode_url` | Warning |
| R13 | Vendored files match their pinned hashes (`pytest`) | Test failure |
| R14 | A harvested `id` and `owner.organisation` match the pointer's `id` and `expected_owner` | Error (not published) |
| R15 | A source is not HTTPS, exceeds the size limit, times out, or redirects to a non-HTTPS address | Error (last valid version kept) |
| R16 | A pointer resolves to a record whose status is not `owner-confirmed` or `withdrawn` (or `example`, within `csr-9000`–`9999`) | Error |
| R17 | A codebase's `publiccode.yml` fails the official parser | Warning |
| R18 | `service_url`, `service_page_url`, `documentation_url`, a codebase `repository_url` or an `open_data` URL is not an HTTPS URL | Error |
| R19 | A codebase's `publiccode.yml` names a different `url` from its `repository_url`, or a different `maintenance.type` | Warning |

The schema already rejects some of what the rules check (sentinels outside
demonstration records, and URLs that are not HTTPS). The rules give the
clearer message and also apply to harvested files.
