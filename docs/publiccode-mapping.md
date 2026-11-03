# publiccode.yml mapping

How `csr import-publiccode` maps a codebase's `publiccode.yml` to a record. This is
appendix A of the specification, copied here so maintainers can find it; the
site shows the same mapping, with this repository's own files as a worked
example, at `reference/publiccode/`. Commands are described in
[`maintenance.md`](maintenance.md).

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
