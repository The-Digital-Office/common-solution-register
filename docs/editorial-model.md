# Editorial model

How records get into the register, who checks them, and how an operated
register could make that checking enforceable (specification 6.7). The
demonstrator **documents** the model and **configures it lightly**: review is
requested, not enforced. Whether to enforce it, and who the editors are, is for
the body that runs a register (decision point DP-42).

## Two approvals

A record in an operated register would carry two approvals:

1. **Owner confirmation:** the owning organisation confirms the content is
   accurate. It is recorded in the record itself, in `confirmation`
   (`last_confirmed`, `method` and `reference`), and drives the record's
   currency: due after 11 months, stale after 12. An owner who hosts their own
   `solution.yml` confirms it by publishing it.
2. **Editorial approval:** an editor reviews the pull request that adds or
   changes the record, against the inclusion test and the contributing guide
   ([`contributing-records.md`](contributing-records.md)): is it a common
   solution, offered by an accountable owner, with a role-based contact, and
   classified sensibly? Editorial approval is the merged pull request.

Demonstration records have neither: they are compiled from public sources by
the register's maintainers, labelled "not confirmed by the owner", and the
owner receives a courtesy note instead.

## What the demonstrator does

- `CODEOWNERS` **requests** a review from the maintainers on every pull
  request, and on `records/`, `taxonomy/` and `schema/` in particular.
- The baseline ruleset ("DO baseline: main") requires a pull request for every
  change to `main`, with **no required approvals**, because a repository with
  one maintainer cannot approve its own pull requests. It requires the standards
  checks to pass on an up-to-date branch.
- The "CSR: required checks" ruleset requires `Validate` and `UI tests` to
  pass, so no record that fails validation can be merged, and a pull request
  that registers or changes a pointer fetches and checks the owner's file
  first.

So the checks are enforced, but the editorial judgement is not.

## Enforcing it in an operated register

1. Create an **editors team** of at least two people, because the author of a
   pull request cannot approve it.
2. Name the team in `CODEOWNERS` for `/records/`, `/taxonomy/` and `/schema/`.
3. Add a ruleset on the default branch that **requires one approval and
   code-owner review**.
4. **Do not dismiss stale approvals.** The baseline requires branches to be up
   to date before merging. Combined with dismissing stale approvals, every
   merge to `main` would force every open record pull request to be approved
   again. Instead, rely on a convention: an editor who approves a pull request
   checks it again before merging if the change has moved on substantially.
5. Record the editors and the convention in this document and in the
   repository's governance file.

## Owner-hosted records

Owners may change their hosted `solution.yml` **without maintainer review**
(decided 20 October 2026; decision point DP-37). Editorial review applies when
a pointer is **registered or changed**, because that is a pull request. After
that, the safeguards are automatic:

- full validation against the schema and rules, at every harvest;
- the **owner match** (R14): the harvested `id` and `owner.organisation` must
  match the pointer's `id` and `expected_owner`, so a compromised or repurposed
  address cannot take over a record;
- the **allowed statuses** (R16): only owner-confirmed or withdrawn records;
- the **last valid version** stays published if a new version fails, flagged on
  the record page and the harvest report.

This is the usual model for distributed publication. A maintainer can always
withdraw a pointer at once if an owner publishes something inappropriate
([`maintenance.md`](maintenance.md)).

## Corrections and removal

Anyone can suggest a correction (the "Suggest a correction" link on every
record, or the `suggest-correction` issue form). An editor decides whether to
make it, and for a confirmed record asks the owner. During the demonstrator,
a record about a real solution is deleted if its owner asks (decision point
DP-11).
