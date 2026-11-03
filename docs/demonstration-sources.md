# Demonstration records: sources and verification

Demonstration records describe real solutions **only from cited public
sources** (specification 5.1 and 5.2). They are not confirmed by their owners.
This document lets the author check every statement before the records are
merged: each row gives a field, the value in the record, the source it comes
from, and the words in that source that support it.

Where a source does not state a fact, the record uses the sentinel
`not-publicly-stated` (shown as "Not stated in public sources"), never an
inferred value.

**How to verify.** Open each source, find the supporting words, and tick the
row. If a statement cannot be found, replace the value with the sentinel (in
the four sentinel fields, `service_url` or `service_page_url`) or remove it,
and note the change here. If a record cannot be sourced adequately, drop it.

Sources were accessed on 3 November 2026. Some owner pages (for example
`scotaccount.servicemanual.gov.scot` and `www.mygov.scot`) answer automated
requests with a bot check, so they could not be read while compiling the
records; they are not cited as sources, and the author should look at them by
hand during verification.

## csr-0003 ScotAccount

**Sources**

- [S1] [ScotAccount: transforming public services in Scotland](https://blogs.gov.scot/digital/2025/07/16/scotaccount-transforming-public-services-in-scotland/), Scottish Government Digital blog, 16 July 2025.
- [S2] [ScotAccount – helping more people to access public services online](https://blogs.gov.scot/digital/2024/09/23/scotaccount-helping-more-people-to-access-public-services-online/), Scottish Government Digital blog, 23 September 2024.

| Checked | Field | Value | Source | Supporting words |
|---|---|---|---|---|
| [ ] | `name` | ScotAccount | S1, S2 | Throughout |
| [ ] | `summary` | A secure and simple way for people to prove who they are and that they are eligible… | S1 | "ScotAccount is the secure and simple way for people to prove who they are and that they are eligible" |
| [ ] | `purpose` (sign in) | Sign in using two-factor authentication; available to public services as a stand-alone feature | S1 | "Sign in using two-factor authentication (which is available to public services as a stand-alone feature)" |
| [ ] | `purpose` (verify) | Verify identity if required, by photo ID or security questions | S1 | "Verify their identity (if required) by photo ID or security questions"; "an alternative identity verification method, using security questions, for users without photographic ID" |
| [ ] | `purpose` (reuse) | Save their digital identity to reuse with other public services | S1 | "Save their digital identity to reuse with other public services" |
| [ ] | `purpose` (services) | Disclosure Scotland's online disclosure journey; COPFS Witness Gateway | S1, S2 | S1: "ScotAccount now supports the full online disclosure journey"; S2: "assisted the Crown Office and Procurator Fiscal Service (COPFS) to introduce their new Witness Gateway" |
| [ ] | `asset_type` | service | S1 | A service run for others to use (classification by the register) |
| [ ] | `owner.organisation` | Scottish Government | S1, S2 | S1: "the Scottish Government's ScotAccount programme"; S2: "Programme Director for the Scottish Government's digital identity programme" |
| [ ] | `owner.sector` | scottish-government | S1 | As above |
| [ ] | `contact` | web form https://scotaccount.campaign.gov.scot/contact | S1 | Link text "Contact us to find out more and join our test environment". S2 gives the mailbox scotaccount@gov.scot; the newer web form is used, as demonstration contacts are public contact pages |
| [ ] | `service_areas` | corporate-and-cross-cutting | — | Classification by the register: a cross-cutting capability used by services in several areas |
| [ ] | `capabilities` | identity-and-access | S1 | "prove who they are"; "Sign in"; "Verify their identity" |
| [ ] | `status` | beta | S1 | "and now into public beta" (July 2025). **Check whether it has since gone live** |
| [ ] | `intended_adopters` | the six Scottish public sector sectors (not further and higher education, not UK public sector) | S1 | "We invite public sector organisations in Scotland to get in touch with us". **Check** whether colleges and universities are included |
| [ ] | `terms_of_use.type` | not-publicly-stated | S1, S2 | Neither source states terms of use |
| [ ] | `adoption_route.summary` | Contact the team to find out more and join the test environment; live or in-development services; including simple sign-in | S1, S2 | S1: "Whether your service is already live or in development, you can see how ScotAccount works by joining our test environment"; S2: "To access our test environment, even if your requirement is a simple sign in/login" |
| [ ] | `adoption_route.url` | https://scotaccount.campaign.gov.scot/contact | S1 | Contact link, as above |
| [ ] | `charging.applies` | not-publicly-stated | S1, S2 | Neither source mentions charges |
| [ ] | `support.summary` | not-publicly-stated | S1, S2 | Neither source describes support for adopting services |
| [ ] | `service_url` | not-publicly-stated | S1 | People reach ScotAccount through the services that use it; S1 points to a list on mygov.scot ("For a full list of services currently using ScotAccount visit mygov.scot") but gives no start page. **Check** `https://www.mygov.scot/scotaccount` by hand |
| [ ] | `service_page_url` | https://scotaccount.campaign.gov.scot/ | S1, S2 | Linked as the ScotAccount website in both. It now redirects to `https://scotaccount.servicemanual.gov.scot/` (HTTPS); **check** which address to keep |
| [ ] | `adopters` | Disclosure Scotland; Crown Office and Procurator Fiscal Service (both `self-reported`: stated by the owner, not by the adopter) | S1, S2 | S1: "Since launching with Disclosure Scotland in February 2023"; S2: "assisted the Crown Office and Procurator Fiscal Service (COPFS) to introduce their new Witness Gateway" |

## csr-0004 Scottish Government Design System

**Sources**

- [S1] [Repository README](https://github.com/scottish-government-design-system/design-system/blob/main/README.md), Scottish Government.
- [S2] [LICENSE.txt](https://github.com/scottish-government-design-system/design-system/blob/main/LICENSE.txt), Scottish Government.
- [S3] [`@scottish-government/design-system` on npm](https://www.npmjs.com/package/@scottish-government/design-system) (read from the registry's public metadata, `https://registry.npmjs.org/@scottish-government/design-system`).

`designsystem.gov.scot` answers automated requests with a bot check, so the
design system's own website is linked from the record but not cited; the
author should look at it by hand.

| Checked | Field | Value | Source | Supporting words |
|---|---|---|---|---|
| [ ] | `name` | Scottish Government Design System | S1 | "# Scottish Government Design System" |
| [ ] | `summary`, `purpose` (code) | Code for building websites and web applications for the Scottish Government and other Scottish public sector bodies | S1 | "This repository contains all the code needed to start building user interfaces for websites and web applications for the Scottish Government and other Scottish public sector bodies." |
| [ ] | `summary`, `purpose` (guidance) | Live examples of components, with guidance on how and when to use them | S1 | "See live examples of the available components, alongside guidance on how and when to use them in the Scottish Government Design System" |
| [ ] | `purpose` (install) | Installed from npm; compiled CSS and JavaScript included in projects | S1 | "We recommend installing the package using node package manager (npm)"; "optimised CSS, JavaScript files and static assets that should be included in your project" |
| [ ] | `asset_type` | standard | — | Classification from specification 5.2 |
| [ ] | `owner.organisation` | Scottish Government | S2, S3 | S2: "Copyright (c) Crown Copyright 2019"; S3: author "Scottish Government Digital Design system team" |
| [ ] | `owner.sector` | scottish-government | S3 | As above |
| [ ] | `contact` | web form: the repository's issues page | S3 | Package `bugs` address `https://github.com/scottish-government-design-system/design-system/issues`. S1 also gives the mailbox designsystem@gov.scot (used under `support`) |
| [ ] | `service_areas` | corporate-and-cross-cutting | — | Classification by the register |
| [ ] | `capabilities` | content-and-publishing | — | The taxonomy definition names design systems: "including design systems and content standards" |
| [ ] | `status` | live | S3 | Stable releases published; the `latest` version is 4.3.0 (29 September 2026). **Check** the website does not describe it as beta |
| [ ] | `intended_adopters` | the six Scottish public sector sectors | S1, S3 | S1: "the Scottish Government and other Scottish public sector bodies"; S3: "Design System for Scottish public sector websites". **Check** whether colleges and universities are included |
| [ ] | `terms_of_use` | open-licence, MIT, linking LICENSE.txt | S2, S3 | S2: "The MIT License (MIT)"; S3: licence `MIT`. The website's guidance text may be under another licence; not stated in these sources |
| [ ] | `adoption_route` | Install with npm, include the production files, follow the installation guidance | S1 | "Run the command `npm install @scottish-government/design-system`"; the link "installing the package using node package manager (npm)" goes to `https://designsystem.gov.scot/get-started/installation/` |
| [ ] | `charging.applies` | false | S2 | "Permission is hereby granted, free of charge" |
| [ ] | `support.summary` | Email the Design System team at designsystem@gov.scot for help or feedback | S1 | "If you need any help or want to give any feedback you can e-mail the Design System team at: designsystem@gov.scot" |
| [ ] | `service_page_url`, `documentation_url` | https://designsystem.gov.scot/ | S1 | Linked as "Scottish Government Design System" |
| [ ] | `current_version`, `codebases[0].version` | 4.3.0 | S3 | `latest` dist-tag 4.3.0. **Update** if a newer version has been released |
| [ ] | `codebases[0]` | public repository, maintenance `internal` | S1, S3 | S3: repository `github.com/scottish-government-design-system/design-system`, maintained by the "Scottish Government Digital Design system team". No `publiccode.yml` in the repository, so R12 warns |
