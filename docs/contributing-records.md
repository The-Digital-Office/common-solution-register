# Contributing records

How to suggest a common solution for the register, correct a record, or ask
for one to be removed. This is the register's own guide; for changes to the
code, see the
[Digital Office contributing guide](https://github.com/The-Digital-Office/.github/blob/main/CONTRIBUTING.md).

The register is a **demonstrator**: it shows how a register could work, for the
Scottish public sector short-life working group. Records added now help test
the approach; they are not a commitment that a register will exist.

## What belongs in the register

A **common solution** is a capability that an accountable owner offers to
other public bodies, with a way to adopt it: a service to use, a platform to
onboard to, a component, API, standard or pattern to take up, or software to
deploy, with terms and support behind it. A public repository on its own is a
codebase, not a solution, unless someone offers it for reuse and takes
responsibility for it.

A record should pass the **inclusion test**:

1. It is intended for reuse by more than one public body.
2. The owner accepts responsibility for the record's accuracy.
3. There is a role-based contact (a role mailbox, service desk or web form,
   never a named person).
4. It can be classified with the register's taxonomy.
5. Its status and terms can be stated.
6. It can be described without sensitive information.

## Ways to contribute

| Route | Best for | How |
|---|---|---|
| **Draft form** | Anyone; no GitHub skills needed | Fill in [Draft a record](https://the-digital-office.github.io/common-solution-register/draft/). It checks the record as you go. Then copy the YAML, download `solution.yml`, open it as a GitHub issue, or send it by email |
| **GitHub issue** | People with a GitHub account | The draft form's "Open as a GitHub issue" fills in the **Suggest a solution** form for you; or open that form and paste a `solution.yml` |
| **Email** | People without a GitHub account | The draft form's "Send by email" downloads the file and opens an email to the register's mailbox; attach the file |
| **Pull request** | People comfortable with git | Add `records/csr-NNNN.yaml` and open a pull request; the template asks for provenance and sources |
| **Assisted** | Owners who would rather talk it through | Email the register's mailbox; a maintainer drafts the record with you, or imports it from your codebase's `publiccode.yml` |
| **Host it yourself** | Owners who want to keep their record up to date themselves | See [Hosting your solution.yml](hosting-your-solution-yml.md) |

**GitHub issues are public.** By submitting a record by any route, you agree
it may be published under the
[Open Government Licence v3.0](../LICENCE-CONTENT.md).

## Writing a good record

- **Summary:** one sentence, under 200 characters, saying what it is in plain
  English. It is shown in search results.
- **Purpose:** what it does, the problem it solves and who it is for.
- **Terms of use, adoption route and charges:** say how another body would
  actually take it up. Link to the agreement or terms where there is one.
- **Contact:** a role mailbox, service desk or web form. A personal address
  gets a warning (rule R07) because it stops working when people move on.
- **Classification:** choose the asset type, service areas, capabilities and
  the sectors it is intended for from the
  [field reference](https://the-digital-office.github.io/common-solution-register/reference/).
- **Codebases:** if code implements it, list each repository. A public
  repository should have a `publiccode.yml`; link it, and the register checks
  it with the official parser.
- **Leave the `id` as `csr-NNNN`.** A maintainer allocates the identifier when
  the record is registered.

You can check a file at any time on the
[validate page](https://the-digital-office.github.io/common-solution-register/validate/),
or with `csr validate path/to/solution.yml`.

## Records about solutions you do not own

You may suggest a solution your organisation does not own, as a
**demonstration** record: `record_status: demonstration`. Then:

- every statement must come from a public source, listed under `sources`
  (address, title, date accessed);
- anything the sources do not state is `not-publicly-stated` (shown as "Not
  stated in public sources"), never a guess;
- the record is shown as "not confirmed by the owner", and the owner receives
  a courtesy note before it is published.

The draft form offers this when you say you are not from the owning
organisation.

## What happens next

1. A maintainer checks the record against the inclusion test and the schema,
   allocates its identifier, and proposes it in a pull request (for a
   suggestion by issue, with `csr new --from-issue`).
2. The pull request's checks validate it. Review by an editor is requested.
3. When it is merged, the record is published at the next build.
4. Owners are asked to confirm their records about once a year; a record is
   shown as **due** after 11 months and **stale** after 12.

## Corrections and removal

- **Correct a record:** use **Suggest a correction** on its page, which opens
  the draft form filled in from the record, or the **Suggest a correction**
  issue form. On a demonstration record, the owner can use **Confirm or
  correct** under "Is this your service?".
- **Remove a record:** if you are the owner, ask through **Is this your
  service?** on the record page, the issue form, or the register's mailbox.
  During the demonstrator, a record about a real solution is deleted if its
  owner asks.
