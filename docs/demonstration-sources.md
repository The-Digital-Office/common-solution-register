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

Sources were accessed and rechecked on 3 November 2026. Current owner-operated pages are cited where available. Items confirmed manually by the register author are identified as author verification.

## csr-0003 ScotAccount

**Sources**

- [S1] [ScotAccount: transforming public services in Scotland](https://blogs.gov.scot/digital/2025/07/16/scotaccount-transforming-public-services-in-scotland/), Scottish Government Digital blog, 16 July 2025.
- [S2] [ScotAccount – helping more people to access public services online](https://blogs.gov.scot/digital/2024/09/23/scotaccount-helping-more-people-to-access-public-services-online/), Scottish Government Digital blog, 23 September 2024.
- [S3] [Join our beta](https://scotaccount.servicemanual.gov.scot/join-our-beta), Scottish Government, accessed 3 November 2026.
- [S4] [Create or sign in to ScotAccount](https://authn.scotaccount.service.gov.scot/sign-up/sign-in-or-create), Scottish Government, verified by the register author on 3 November 2026. Not listed in the record's `sources`: the page answers automated link checks with HTTP 401, so it would always warn (R08).
- [S5] [Contact](https://scotaccount.servicemanual.gov.scot/contact), Scottish Government, accessed 3 November 2026.
- [S6] [Help your users sign in to your service](https://scotaccount.servicemanual.gov.scot/), Scottish Government, accessed 3 November 2026.

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
| [ ] | `contact` | contact page https://scotaccount.servicemanual.gov.scot/contact | S3, S5 | S3: "get in touch with us" links to it; S5: "If you want to use ScotAccount you can get in touch with us via email" (scotaccount@gov.scot). The contact page is used, as demonstration contacts are public contact pages |
| [ ] | `service_areas` | corporate-and-cross-cutting | — | Classification by the register: a cross-cutting capability used by services in several areas |
| [ ] | `capabilities` | identity-and-access | S1 | "prove who they are"; "Sign in"; "Verify their identity" |
| [x] | `status` | beta | S3 | "ScotAccount is currently in beta." |
| [x] | `intended_adopters` | government teams and public services in Scotland | S3 | To use ScotAccount in beta, adopters need to "work in a government team or public service in Scotland". |
| [ ] | `terms_of_use.type` | not-publicly-stated | S1, S2 | Neither source states terms of use |
| [x] | `adoption_route.summary` | Join the beta; available to government teams and public services in Scotland with an alpha, beta or live service and the ability to integrate using OpenID Connect | S3 | The beta page states the eligibility criteria, integration requirement and that access to ScotAccount capabilities is at no charge. |
| [x] | `adoption_route.url` | [Join the beta](https://scotaccount.servicemanual.gov.scot/join-our-beta) | S3 | Current beta adoption page. |
| [x] | `charging.applies` | false for beta participants | S3 | Beta participants get "access to ScotAccount’s capabilities, at no charge". |
| [x] | `support.summary` | Support from the ScotAccount team throughout the beta; email answered in office hours, usually within 2 working days | S3, S5 | S3: the beta offer includes "support from our team throughout"; S5: "Our office hours are 09:30 to 16:30, Monday to Friday (excluding public holidays)"; "we'll try to reply within 2 working days" |
| [x] | `service_url` | [Create or sign in to ScotAccount](https://authn.scotaccount.service.gov.scot/sign-up/sign-in-or-create) | S4 | Standalone page for users to create a ScotAccount or sign in, verified by the register author. |
| [ ] | `service_page_url`, `roadmap_url` | https://scotaccount.servicemanual.gov.scot/ and its roadmap page | S6 | The address the ScotAccount website links in S1 and S2 now redirects here. S6: "We're inviting public services in Scotland to join ScotAccount"; "Check our roadmap for more details about the future of ScotAccount" |
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
| [x] | `status` | live | S3 | Stable releases are published and the Design System is in active public use; confirmed live by the register author. |
| [x] | `intended_adopters` | the wider Scottish public sector | S1, S3; author verification | S1 states "the Scottish Government and other Scottish public sector bodies"; scope confirmed by the register author. |
| [ ] | `terms_of_use` | open-licence, MIT, linking LICENSE.txt | S2, S3 | S2: "The MIT License (MIT)"; S3: licence `MIT`. The website's guidance text may be under another licence; not stated in these sources |
| [ ] | `adoption_route` | Install with npm, include the production files, follow the installation guidance | S1 | "Run the command `npm install @scottish-government/design-system`"; the link "installing the package using node package manager (npm)" goes to `https://designsystem.gov.scot/get-started/installation/` |
| [ ] | `charging.applies` | false | S2 | "Permission is hereby granted, free of charge" |
| [ ] | `support.summary` | Email the Design System team at designsystem@gov.scot for help or feedback | S1 | "If you need any help or want to give any feedback you can e-mail the Design System team at: designsystem@gov.scot" |
| [ ] | `service_page_url`, `documentation_url` | https://designsystem.gov.scot/ | S1 | Linked as "Scottish Government Design System" |
| [ ] | `current_version`, `codebases[0].version` | 4.3.0 | S3 | `latest` dist-tag 4.3.0. **Update** if a newer version has been released |
| [ ] | `codebases[0]` | public repository, maintenance `internal` | S1, S3 | S3: repository `github.com/scottish-government-design-system/design-system`, maintained by the "Scottish Government Digital Design system team". No `publiccode.yml` in the repository, so R12 warns |

## csr-0005 One Scotland Gazetteer

**Sources** (metadata records published by the Improvement Service in the
Scottish Government's spatial data catalogue, spatialdata.gov.scot)

- [S1] [One Scotland Gazetteer](https://spatialdata.gov.scot/geonetwork/srv/api/records/250ea276-48e2-4189-8a89-fcc4ca92d652) (dataset).
- [S2] [National Street Gazetteer for Scotland](https://spatialdata.gov.scot/geonetwork/srv/api/records/0454729b-6dda-49d3-bc18-ac73127345af) (dataset).
- [S3] [One Scotland Gazetteer REST Service](https://spatialdata.gov.scot/geonetwork/srv/api/records/0374e2cf-f0d4-4ae4-9b13-fc4b7df6588e) (service).
- [S4] [One Scotland Gazetteer SOAP Service](https://spatialdata.gov.scot/geonetwork/srv/api/records/1b74296b-cc69-4ede-bf48-380d3c6baa8c) (service).
- [S5] [One Scotland Gazetteer portal](https://osg.scot/portal/): behaviour, access routes and the [Terms and Conditions](https://osg.scot/portal/pages/terms-conditions), verified manually by the register author on 3 November 2026.

**Not used.** `onescotlandgazetteer.org.uk` describes itself as "an independent informational resource, not an official government service", so it is not used as a source. Portal behaviour and access routes were verified manually by the register author against the owner-operated OSG portal.

| Checked | Field | Value | Source | Supporting words |
|---|---|---|---|---|
| [ ] | `name` | One Scotland Gazetteer | S1 | Title "One Scotland Gazetteer" |
| [ ] | `summary`, `purpose` (database) | Address database made up of all 32 local authority gazetteers; BS7666:2006 and the Scottish Gazetteer Conventions; spatially referenced records and property lifecycle details | S1 | "The One Scotland Gazetteer is an address database made up of all 32 individual local authority gazetteers. All addresses are created in accordance with the national standard for addressing, BS7666:2006 and the Scottish Gazetteer Conventions. Key features include: Spatially referenced address records, Property lifecycle details" |
| [ ] | `purpose` (streets) | National Street Gazetteer for Scotland, every street, road, track or cycleway, with USRNs | S2 | "a line dataset depicting every street, road, track or cycleway in Scotland"; "Unique Street Reference Numbers (USRN)" |
| [ ] | `purpose` (services) | REST and SOAP services provide the data as an API for authorised organisations | S3, S4 | "provides the One Scotland Gazetteer data as an API that can be used by any authorised organisation within their address and street-based applications" |
| [ ] | `purpose` (daily) | Maintained daily | S1, S2 | Maintenance frequency "daily" |
| [ ] | `asset_type` | platform | — | Classification from specification 5.2 |
| [ ] | `owner` | Improvement Service, `local-government` | S1–S4 | Organisation "The Improvement Service" (the national improvement body for Scottish local government) |
| [ ] | `contact` | web form https://osg.scot/portal/pages/contact-Us | — | The portal's "Contact" link. The metadata gives the mailboxes gazcustomers@improvementservice.org.uk (S1, S2) and gazhelp@improvementservice.org.uk (S3, S4). **Check** the contact page works |
| [ ] | `service_areas` | corporate-and-cross-cutting | — | Classification by the register |
| [ ] | `capabilities` | data-and-analytics, mapping-and-location | — | Classification by the register: reference data; addresses and geographic data |
| [x] | `status` | live | S1–S4 | Maintained daily, with web services and public search in operation; confirmed live by the register author. |
| [x] | `intended_adopters` | PSGA members; commercial users through Ordnance Survey AddressBase products; limited public search | S1, S3, S5 | PSGA members can use the data; S3 states commercial availability through Ordnance Survey AddressBase products; limited public search was verified by the register author. |
| [x] | `terms_of_use` | PSGA use for public-sector applications; commercial access through Ordnance Survey AddressBase products; open UPRN and USRN components with attribution; portal terms for limited public search | S1, S3, S5 | The catalogue records distinguish PSGA and AddressBase routes. Open identifier components and portal search behaviour were verified by the register author. |
| [x] | `adoption_route` | PSGA members receive the data for public-sector use; commercial users obtain it through Ordnance Survey AddressBase products; the public portal provides limited address and map search after accepting its terms | S1, S3, S5 | Authoritative metadata supports the PSGA and AddressBase routes; portal behaviour was verified by the register author. |
| [x] | `charging.applies` | false for PSGA use and limited public search; commercial access is through Ordnance Survey AddressBase products | S1, S3, S5 | PSGA availability and the commercial AddressBase route are stated in the catalogue; free limited public use was verified by the register author. |
| [ ] | `support.summary` | not-publicly-stated | S1–S4 | Not stated (S3 and S4 give a "gazhelp" mailbox as the contact, without saying it is a support service) |
| [x] | `service_url` | https://osg.scot/portal/ | S1–S4 | Public portal supports limited address and map search after accepting its terms, returning UPRNs and USRNs; verified by the register author. |
| [x] | `service_page_url` | [One Scotland Gazetteer information](https://osg.scot/portal/pages/about-us) | S5 | Owner portal information page, verified by the register author. |
| [ ] | `interfaces` | REST (S3), SOAP (S4), each documented by its metadata record | S3, S4 | Titles "One Scotland Gazetteer REST Service", "One Scotland Gazetteer SOAP Service" |

## csr-0006 Spatial Hub

**Sources** (pages of the Spatial Hub itself, run by the Improvement Service)

- [S1] [About Us](https://data.spatialhub.scot/about).
- [S2] [Help Centre](https://data.spatialhub.scot/faq).
- [S3] [Terms and Conditions](https://data.spatialhub.scot/terms_and_condition).
- [S4] [Contact Us](https://data.spatialhub.scot/contact_us).

| Checked | Field | Value | Source | Supporting words |
|---|---|---|---|---|
| [ ] | `name` | Spatial Hub | S1 | "The Spatial Hub is a platform for hosting and publishing Scottish spatial data." |
| [ ] | `summary`, `purpose` (collects and publishes) | Combines datasets from local authorities and partners into Scotland-wide national datasets, published in various formats | S1 | "collects datasets from local authorities and other partner organisations to form Scotland-wide national datasets and publishes these in various formats to maximise their use" |
| [ ] | `purpose` (processing) | Every three months; some datasets daily; web services and file downloads | S2 | "Every three months, the collected data updates are quality assessed, cleaned, standardised, and amalgamated into national datasets"; "Certain datasets (e.g., Planning Applications and Building Standards) are updated daily"; "available as web services and a variety of file downloads" |
| [ ] | `purpose` (access) | Search and preview without an account; free account to download or connect | S2 | "You can search for datasets and display them on the preview map without registering. However, if you wish to download and/or connect to any data you'll need to register for a user account." |
| [ ] | `purpose` (open data portal) | Some local authorities use it as their open data portal | S2 | "Some local authorities have chosen to use the Spatial Hub as an Open Data Portal" |
| [ ] | `asset_type` | platform | S1, S3 | "a platform"; "an online platform for hosting and publishing Scottish spatial data" |
| [ ] | `owner` | Improvement Service, `local-government` | S1, S3 | "Developed and maintained by the Improvement Service (IS)"; "We are the Improvement Service, operator of the Spatial Hub service." |
| [ ] | `contact` | web form https://data.spatialhub.scot/contact_us | S4 | "For any other queries, please get in touch using the following form" |
| [ ] | `service_areas` | corporate-and-cross-cutting, planning-and-building-standards | S2 | Classification by the register; S2 names planning applications and building standards datasets |
| [ ] | `capabilities` | mapping-and-location, data-and-analytics | S1 | "Scottish spatial data"; national datasets |
| [x] | `status` | live | S1–S3 | The service is operating and taking registrations; confirmed live by the register author. |
| [ ] | `intended_adopters` | the six Scottish public sector sectors, and further and higher education | S2 | "Public Sector Organisations: These organisations and their members can access data once their Spatial Hub account is registered against the correct PSGA organisation"; "Academic Institutions within Scotland: These organisations and their members can access data via EDINA's DigiMap service" |
| [ ] | `terms_of_use` | service terms (the Terms and Conditions); OGL for open datasets; premium datasets by sector | S2, S3 | S2: "National Open Datasets: These datasets are shared under an Open Government Licence"; the premium access routes as above; "External Organisations/Users … can access data via our commercial partners" |
| [ ] | `adoption_route` | Free account; download or web service; ask to register the account against the PSGA organisation; data providers join an Organisation | S2, S3 | S3: "you must first have registered and logged in to a free Spatial Hub account. Then you can either download a copy of the data in a variety of formats or connect to a web service"; S2: "registered against the correct PSGA organisation. Please contact us to request this"; "If you think you may need to create an Organisation for providing data to the Spatial Hub, please contact us" |
| [x] | `charging` | applies: not-publicly-stated; free account and open datasets; premium access through a PSGA organisation or commercial licence agreement | S2, S3 | The sources state that accounts and open datasets are free, but do not publish charges for commercial or premium access. |
| [ ] | `support` | Help Centre; enquiry form; spatialhub@improvementservice.org.uk | S2, S4 | S4: "Please check our Help Centre before sending a message"; S2: "please contact us: spatialhub@improvementservice.org.uk" |
| [ ] | `service_url`, `service_page_url`, `documentation_url` | the home page, About Us and the Help Centre | S1, S2 | The service's own pages |
| [ ] | `open_data` | Spatial Hub datasets, https://data.spatialhub.scot/dataset/ | S2 | "National Open Datasets: These datasets are shared under an Open Government Licence" |

## csr-0007 GOV.UK Notify

The optional record in specification 5.2: the only real `api` record, with
publicly documented charges.

**Sources** (GOV.UK Notify's own pages, by the Government Digital Service)

- [S1] [GOV.UK Notify](https://www.notifications.service.gov.uk/) (home page).
- [S2] [Features](https://www.notifications.service.gov.uk/features).
- [S3] [Pricing](https://www.notifications.service.gov.uk/pricing).
- [S4] [Who can use Notify](https://www.notifications.service.gov.uk/features/who-can-use-notify).
- [S5] [Support](https://www.notifications.service.gov.uk/support).
- [S6] [Documentation](https://www.notifications.service.gov.uk/using-notify/api-documentation).
- [S7] [Terms of use](https://www.notifications.service.gov.uk/terms-of-use).

| Checked | Field | Value | Source | Supporting words |
|---|---|---|---|---|
| [ ] | `name` | GOV.UK Notify | S1 | Throughout |
| [ ] | `summary`, `purpose` (what) | Public sector service teams send emails, text messages and letters | S2 | "GOV.UK Notify makes it easy for public sector service teams to send emails, text messages and letters." |
| [ ] | `purpose` (no technical knowledge) | Templates, personalisation, bulk sending by spreadsheet, delivery tracking | S1, S2 | S2: "You do not need any technical knowledge to: create and send messages … add personalisation send messages in bulk see when your messages have been delivered"; S1: "Upload a spreadsheet of email addresses or phone numbers and Notify sends the messages." |
| [ ] | `purpose` (API) | A developer integrates the API with a web application or back office system; client libraries or REST directly | S2, S6 | S2: "To send messages automatically, you'll need a developer to integrate with the GOV.UK Notify API"; S6: "If you cannot use the client libraries, you can integrate directly with the API instead." |
| [ ] | `purpose` (letters) | Notify prints and posts letters | S2 | "GOV.UK Notify prints and posts your letters for you" |
| [ ] | `asset_type` | api | — | Classification from specification 5.2 |
| [ ] | `owner` | Government Digital Service, `uk-public-sector` | S1 | "GOV.UK Notify is built by the Government Digital Service" |
| [ ] | `contact` | web form https://www.notifications.service.gov.uk/support | S1 | "Contact us if you have a question or want to give feedback." (links to the support page) |
| [ ] | `service_areas` | corporate-and-cross-cutting | — | Classification by the register |
| [ ] | `capabilities` | notifications, integration-and-apis | S1, S2 | Emails, text messages and letters; "Integrate the GOV.UK Notify API" |
| [x] | `status` | live | S1 | The operational service publishes current usage figures and pricing; confirmed live by the register author. |
| [x] | `intended_adopters` | uk-public-sector, excluding universities | S4 | Only public sector organisations can accept the agreement. The eligibility page lists qualifying public-sector bodies and explicitly states that universities cannot use Notify. |
| [ ] | `terms_of_use` | service terms | S4, S7 | S7: "You accept our terms of use when you create an account."; S4 as above |
| [ ] | `adoption_route` | Free account; new services start in trial mode; suppliers are invited; API for automatic sending | S2, S3, S4 | S2: "Create an account for free and try it yourself"; S3: "When you add a new service it will start in trial mode"; S4: "Someone from the public sector organisation you're working with needs to create an account and add the service first. Then they can invite you to join as a team member." |
| [ ] | `charging` | applies, per-transaction, the prices | S1, S3 | S1: "Unlimited free emails"; "Up to 20,000 free text messages a year, then 2.4 pence per message"; "From 63.8 pence to print and post a one page letter"; S3: "no monthly charge, no setup fee and no procurement cost. You will only have to pay if you: send text messages after using all of your free allowance send letters". **Prices change**: check before publication |
| [ ] | `support` | 24/7 for emergencies, reply within 30 minutes; otherwise by the end of the next working day | S5 | "GOV.UK Notify provides 24/7 support for emergencies. If you have an emergency we'll reply within 30 minutes. If it's not an emergency we'll reply by the end of the next working day." |
| [ ] | `service_url`, `service_page_url`, `documentation_url` | home page, Features, Documentation | S1, S2, S6 | The service's own pages |
| [ ] | `interfaces` | REST, documented at docs.notifications.service.gov.uk/rest-api.html; client libraries for Java, .NET, Node JS, PHP, Python and Ruby | S6 | "Read the REST API documentation"; "Client libraries … Java .NET Node JS PHP Python Ruby" |
