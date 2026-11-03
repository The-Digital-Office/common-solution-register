# GitHub Free, as it applies to this repository

What the GitHub Free plan offers a public repository, and how the demonstrator
uses it. This is appendix B of the specification, copied here for adopting
bodies ([`adopting-this-demonstrator.md`](adopting-this-demonstrator.md)).
Section references are to the specification.

| Capability | Availability | Approach |
|---|---|---|
| Rulesets and branch protection | Public repositories | Available |
| Organisation rulesets and required workflows | Not on Free | Per-repository `apply-baseline.sh` |
| Push rulesets (file-path restrictions) | Not on Free (Team and Enterprise, for private and internal repositories) | Not needed |
| Required approvals and code-owner review | Public repositories; authors cannot approve their own pull requests | Requested, not enforced, in the demonstrator (6.7) |
| GitHub Pages | Public repositories; private Pages needs Enterprise Cloud | Public site; preview artifact on pull requests |
| Pages limits | 1 GB site; soft limits of 100 GB/month and 10 builds/hour; 10-minute deploy timeout | Far above need |
| Pages on repository transfer | Not redirected | Section 8 |
| Secret scanning with push protection, private vulnerability reporting, Dependabot, CodeQL | Free for public repositories | Enabled |
| Actions minutes | Free on standard runners for public repositories | None needed |
| Scheduled workflows | Disabled after about 60 days without repository activity | Daily harvest; monthly runbook check (6.11) |
| SAML SSO, audit-log streaming | Not on Free | Require two-factor authentication for organisation members |
