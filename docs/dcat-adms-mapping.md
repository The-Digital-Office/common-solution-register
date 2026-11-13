# solution.yml and DCAT, ADMS and SKOS

How each field of a `solution.yml` record relates to the W3C Data Catalog
Vocabulary (DCAT) and the EU's Asset Description Metadata Schema (ADMS), and
how the register's taxonomies are published in SKOS. Decision point DP-58
records why `solution.yml` stays the register's own format, with these
standards used to publish and exchange what it says.

Nothing here changes a record. The register does not export records in DCAT or
ADMS today (DP-56); this mapping shows where the format already lines up with
recognised standards, where it deliberately goes further, and what an export
would involve if one were needed.

## The standards

| Standard | Version | What it describes | Used here |
|---|---|---|---|
| [DCAT](https://www.w3.org/TR/vocab-dcat-3/) | 3, W3C Recommendation, 2024 | Catalogues, datasets and data services; since version 3, any catalogued resource (`dcat:Resource`) | The vocabulary this mapping uses for catalogue-level properties |
| [ADMS](https://semic.pages.code.europa.eu/ADMS/releases/2.00/) | 2.00, SEMIC Recommendation, 1 February 2024 | Reusable "semantic assets" (data models, specifications, reference data, open source software) and repositories of them | Adds status, version notes, identifiers with their managing body, and samples. SEMIC advises using it inside a DCAT profile |
| [SKOS](https://www.w3.org/TR/skos-reference/) | W3C Recommendation, 2009 | Concept schemes: taxonomies, thesauri, code lists | **Published**: the three taxonomies, at `api/v0/taxonomy/<name>.ttl` |
| [UK Cross-Government Metadata Exchange Model](https://co-cddo.github.io/ukgov-metadata-exchange-model/) | Based on a DCAT 3 working draft | Data assets shared between UK government organisations | **Published**: the register's own open data, at `api/v0/metadata.json` (DP-57) |

## Layers

- **Authoring and validation:** `solution.yml`, checked against
  `schema/asset.schema.json` and the validation rules. Owners write it, by hand
  or with the draft form, and may host it themselves.
- **Publication:** the site, `data/register.json` and `.csv`, and the API.
- **Description for other catalogues:** the UK model for the register's data
  (DP-57); SKOS for the taxonomies (DP-58); DCAT and ADMS for individual records
  only if a register to exchange them with appears (DP-56).

In DCAT and ADMS terms, the register is a catalogue (`dcat:Catalog`, or an ADMS
asset repository), each record page is a catalogue record
(`dcat:CatalogRecord`), and each solution is a catalogued resource. ADMS calls
it an asset (`adms:Asset`); a solution whose `asset_type` is `api` and that
serves data is also a data service (`dcat:DataService`), and one whose type is
`standard` is a `dct:Standard`.

## Field by field

**Fit:** *Direct*: an equivalent term with the same meaning. *Partial*: a term
that covers some of the meaning, or needs the value converted. *None*: no
equivalent in DCAT or ADMS.

### Identity and description

| `solution.yml` | DCAT, ADMS or Dublin Core | Fit | Notes |
|---|---|---|---|
| `id` | `dct:identifier`; `adms:identifier` (an `adms:Identifier` naming the register as the scheme's managing agency) | Direct | |
| `schema_version` | `dct:conformsTo` on the catalogue record, pointing at the schema | Partial | Describes the record, not the solution |
| `name` | `dct:title` | Direct | |
| `summary` | `dct:description`; the UK model's `summary` (up to 250 characters) | Direct | |
| `purpose` | `dct:description` | Partial | DCAT has one description; the register has a short summary and a longer purpose |
| `asset_type` | `dct:type`, with the register's own values | Partial | ADMS's asset types were defined for semantic assets, so types such as `service`, `platform` and `component` would need the register's own values. `api` maps to `dcat:DataService` when the API serves data |
| `current_version` | `dcat:version` | Direct | |
| `standards_alignment` | `dct:conformsTo` | Direct | |

### Owner, contact and classification

| `solution.yml` | DCAT, ADMS or Dublin Core | Fit | Notes |
|---|---|---|---|
| `owner.organisation` | `dct:publisher` | Partial | The owner is accountable for the offer of reuse, which is more than publishing a description |
| `owner.sector` | None | None | Some profiles type the publisher; the value would be a concept from the sectors scheme |
| `contact` | `dcat:contactPoint` (a vCard with an email address or web address) | Direct | `contact.type` (role mailbox, service desk, web form) has no equivalent |
| `service_areas` | `dcat:theme`, with concepts from `api/v0/taxonomy/service-areas.ttl` | Direct | Needs the SKOS export (DP-58) |
| `capabilities` | `dcat:theme`, with concepts from `api/v0/taxonomy/capabilities.ttl` | Direct | Needs the SKOS export (DP-58) |
| `intended_adopters` | `dct:audience`, with concepts from `api/v0/taxonomy/sectors.ttl` | Direct | Dublin Core's term for who a resource is intended for |

### Using the solution

| `solution.yml` | DCAT, ADMS or Dublin Core | Fit | Notes |
|---|---|---|---|
| `service_page_url` | `dcat:landingPage` | Direct | |
| `service_url` | `dcat:endpointURL` for a data service | Partial | For other kinds of solution (a service people use, a platform) there is no equivalent |
| `documentation_url` | `foaf:page`, as DCAT-AP uses for documentation; `dcat:endpointDescription` for an API | Direct | |
| `interfaces` | A `dcat:DataService` for each, with `dcat:endpointDescription`; the interface type as `dct:conformsTo` | Partial | The UK model's `serviceType` covers REST, SOAP and events, not GraphQL or files |
| `terms_of_use` | `dct:license` for a licence; `dct:rights` for service terms | Partial | The register uses SPDX expressions such as `MIT AND OGL-UK-3.0`; DCAT expects one licence document per resource |
| `access_restriction` | `dct:accessRights` | Partial | DCAT profiles expect a value from a list (public, restricted, non-public); the register has free text |
| `adoption_route` | None | **None** | How another body can adopt it. The heart of an offer of reuse |
| `charging` | None | **None** | Whether adopters pay, and how |
| `support` | None | **None** | Support for adopters; `dcat:contactPoint` covers only who to contact |
| `adopters` | None | **None** | Who already uses it, and the evidence |
| `roadmap_url`, `accessibility_statement_url` | `foaf:page` | Partial | A page, without saying what kind |
| `funding_model` | None | **None** | |

### Lifecycle and relationships

| `solution.yml` | DCAT, ADMS or Dublin Core | Fit | Notes |
|---|---|---|---|
| `status` | `adms:status`, a SKOS concept | Partial | Values need matching: `concept` and `in-development` to "under development", `deprecated` to "deprecated"; `beta` and `live` have no separate equivalents |
| `deprecation` | `adms:status` deprecated; the replacement as `dct:isReplacedBy` | Partial | The date and the migration guidance have no equivalent |
| `record_status: withdrawn` and `withdrawal` | `adms:status` withdrawn | Partial | The date and reason have no equivalent |
| `related_assets` | `dct:relation`; `replaced-by` and `replaces` as `dct:isReplacedBy` and `dct:replaces`; `uses` and `used-by` as `dct:requires` and `dct:isRequiredBy` | Direct | `alternative` has no equivalent |
| `dependencies` | `dct:requires` | Direct | |
| `codebases` | None | **None, by design** | Each codebase is described by its own `publiccode.yml` (DP-02, `docs/publiccode-mapping.md`). An export would link to them, not restate them |
| `open_data` | `dct:relation`, pointing at the dataset's catalogue entry | Partial | Datasets stay out of scope (DP-03) |

### Provenance and currency

These are what most separate the register from a catalogue that only describes
things: they say how far a record can be relied on.

| `solution.yml` or derived field | DCAT, ADMS or Dublin Core | Fit | Notes |
|---|---|---|---|
| `record_status` (owner-confirmed, demonstration, example) | `dct:provenance`, as a statement | Partial | Free text in DCAT; the register's three values drive its tags, filters and rules |
| `sources` | `dct:source` | Partial | For demonstration entries; the date each source was accessed has no equivalent |
| `confirmation` | None | **None** | That the owner confirmed the record is still accurate, when and how. Not the same as a change (`dct:modified`) |
| Currency (derived: current, due, stale) | None | **None** | Derived from the confirmation date and the register's thresholds |
| Hosting and source (derived) | `dct:source` on the catalogue record: the owner's own `solution.yml` | Direct | For owner-hosted records |
| Last changed (derived) | `dct:modified` on the catalogue record | Direct | |
| Merged in (derived) | None | None | The pull request that registered it |

## Summary

Of the 40 rows above, 15 have a direct equivalent, mostly identity,
description, classification, links and relationships. 15 map partly. 10 have
none, and they are the ones that make the register more than a list: how to adopt a solution, what it costs, what support there is,
who uses it, and whether the owner has confirmed the record recently. A DCAT or
ADMS export would carry the first two groups and could only point to the
record page for the rest.

**Field names.** None need renaming for this mapping: the names are for the
people who write records, and an export would translate them. Two pairs are
worth knowing for discussion: `intended_adopters` is Dublin Core's
`dct:audience`, and `standards_alignment` is `dct:conformsTo`.

**Controlled values that could be reused rather than defined here:**

- `status`: the status scheme a partner catalogue uses, through a mapping, if
  records are ever exchanged.
- `terms_of_use.licence`: already SPDX identifiers, which licence lists such as
  the EU's can be matched to.
- `interfaces[].type`: the UK model's service types (REST, SOAP, events) cover
  three of the six.

**Public services.** SEMIC's Core Public Service Vocabulary (CPSV-AP)
describes public services to citizens and businesses. It overlaps with records
of `asset_type: service` (name, description, owner, channels), but describes
the service people use, not the offer of reuse to other public bodies.

## The taxonomies in SKOS

`api/v0/taxonomy/sectors.ttl`, `service-areas.ttl` and `capabilities.ttl`
publish each taxonomy as a SKOS concept scheme in Turtle, alongside the JSON
files. `api/v0/index.json` links to them.

| Taxonomy file | SKOS |
|---|---|
| The taxonomy | `skos:ConceptScheme`, at the address of its column on the Browse page (`browse/#h-<name>`), with `owl:versionInfo`, licence and publisher |
| A term | `skos:Concept`, at the address of its page on the site (`<name>/<id>/`) |
| `id` | `skos:notation` |
| `label` | `skos:prefLabel` |
| `synonyms` | `skos:altLabel` |
| `definition` | `skos:definition` |
| `intended_adopters_only` | `skos:scopeNote`: an audience only, never the owning sector |
| `status: deprecated` and `replaced_by` | `owl:deprecated true` and `dct:isReplacedBy`; a deprecated term is not a top concept |

`tests/test_skos.py` parses each file with `rdflib` and checks it against the
taxonomy.
