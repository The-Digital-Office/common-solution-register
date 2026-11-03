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
| [x] | `name` | ScotAccount | S1, S2 | Throughout |
| [x] | `summary` | A secure and simple way for people to prove who they are and that they are eligible… | S1 | "ScotAccount is the secure and simple way for people to prove who they are and that they are eligible" |
| [x] | `purpose` (sign in) | Sign in using two-factor authentication; available to public services as a stand-alone feature | S1 | "Sign in using two-factor authentication (which is available to public services as a stand-alone feature)" |
| [x] | `purpose` (verify) | Verify identity if required, by photo ID or security questions | S1 | "Verify their identity (if required) by photo ID or security questions"; "an alternative identity verification method, using security questions, for users without photographic ID" |
| [x] | `purpose` (reuse) | Save their digital identity to reuse with other public services | S1 | "Save their digital identity to reuse with other public services" |
| [x] | `purpose` (services) | Disclosure Scotland's online disclosure journey; COPFS Witness Gateway | S1, S2 | S1: "ScotAccount now supports the full online disclosure journey"; S2: "assisted the Crown Office and Procurator Fiscal Service (COPFS) to introduce their new Witness Gateway" |
| [x] | `asset_type` | service | S1 | A service run for others to use (classification by the register) |
| [x] | `owner.organisation` | Scottish Government | S1, S2 | S1: "the Scottish Government's ScotAccount programme"; S2: "Programme Director for the Scottish Government's digital identity programme" |
| [x] | `owner.sector` | scottish-government | S1 | As above |
| [x] | `contact` | contact page https://scotaccount.servicemanual.gov.scot/contact | S3, S5 | S3: "get in touch with us" links to it; S5: "If you want to use ScotAccount you can get in touch with us via email" (scotaccount@gov.scot). The contact page is used, as demonstration contacts are public contact pages |
| [x] | `service_areas` | corporate-and-cross-cutting | — | Classification by the register: a cross-cutting capability used by services in several areas |
| [x] | `capabilities` | identity-and-access | S1 | "prove who they are"; "Sign in"; "Verify their identity" |
| [x] | `status` | beta | S3 | "ScotAccount is currently in beta." |
| [x] | `intended_adopters` | government teams and public services in Scotland | S3 | To use ScotAccount in beta, adopters need to "work in a government team or public service in Scotland". |
| [x] | `terms_of_use.type` | not-publicly-stated | S1, S2 | Neither source states terms of use |
| [x] | `adoption_route.summary` | Join the beta; available to government teams and public services in Scotland with an alpha, beta or live service and the ability to integrate using OpenID Connect | S3 | The beta page states the eligibility criteria, integration requirement and that access to ScotAccount capabilities is at no charge. |
| [x] | `adoption_route.url` | [Join the beta](https://scotaccount.servicemanual.gov.scot/join-our-beta) | S3 | Current beta adoption page. |
| [x] | `charging.applies` | false for beta participants | S3 | Beta participants get "access to ScotAccount’s capabilities, at no charge". |
| [x] | `support.summary` | Support from the ScotAccount team throughout the beta; email answered in office hours, usually within 2 working days | S3, S5 | S3: the beta offer includes "support from our team throughout"; S5: "Our office hours are 09:30 to 16:30, Monday to Friday (excluding public holidays)"; "we'll try to reply within 2 working days" |
| [x] | `service_url` | [Create or sign in to ScotAccount](https://authn.scotaccount.service.gov.scot/sign-up/sign-in-or-create) | S4 | Standalone page for users to create a ScotAccount or sign in, verified by the register author. |
| [x] | `service_page_url`, `roadmap_url` | https://scotaccount.servicemanual.gov.scot/ and its roadmap page | S6 | The address the ScotAccount website links in S1 and S2 now redirects here. S6: "We're inviting public services in Scotland to join ScotAccount"; "Check our roadmap for more details about the future of ScotAccount" |
| [x] | `adopters` | Disclosure Scotland; Crown Office and Procurator Fiscal Service (both `self-reported`: stated by the owner, not by the adopter) | S1, S2 | S1: "Since launching with Disclosure Scotland in February 2023"; S2: "assisted the Crown Office and Procurator Fiscal Service (COPFS) to introduce their new Witness Gateway" |

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
| [x] | `name` | Scottish Government Design System | S1 | "# Scottish Government Design System" |
| [x] | `summary`, `purpose` (code) | Code for building websites and web applications for the Scottish Government and other Scottish public sector bodies | S1 | "This repository contains all the code needed to start building user interfaces for websites and web applications for the Scottish Government and other Scottish public sector bodies." |
| [x] | `summary`, `purpose` (guidance) | Live examples of components, with guidance on how and when to use them | S1 | "See live examples of the available components, alongside guidance on how and when to use them in the Scottish Government Design System" |
| [x] | `purpose` (install) | Installed from npm; compiled CSS and JavaScript included in projects | S1 | "We recommend installing the package using node package manager (npm)"; "optimised CSS, JavaScript files and static assets that should be included in your project" |
| [x] | `asset_type` | standard | — | Classification from specification 5.2 |
| [x] | `owner.organisation` | Scottish Government | S2, S3 | S2: "Copyright (c) Crown Copyright 2019"; S3: author "Scottish Government Digital Design system team" |
| [x] | `owner.sector` | scottish-government | S3 | As above |
| [x] | `contact` | web form: the repository's issues page | S3 | Package `bugs` address `https://github.com/scottish-government-design-system/design-system/issues`. S1 also gives the mailbox designsystem@gov.scot (used under `support`) |
| [x] | `service_areas` | corporate-and-cross-cutting | — | Classification by the register |
| [x] | `capabilities` | content-and-publishing | — | The taxonomy definition names design systems: "including design systems and content standards" |
| [x] | `status` | live | S3 | Stable releases are published and the Design System is in active public use; confirmed live by the register author. |
| [x] | `intended_adopters` | the wider Scottish public sector | S1, S3; author verification | S1 states "the Scottish Government and other Scottish public sector bodies"; scope confirmed by the register author. |
| [x] | `terms_of_use` | open-licence, MIT, linking LICENSE.txt | S2, S3 | S2: "The MIT License (MIT)"; S3: licence `MIT`. The website's guidance text may be under another licence; not stated in these sources |
| [x] | `adoption_route` | Install with npm, include the production files, follow the installation guidance | S1 | "Run the command `npm install @scottish-government/design-system`"; the link "installing the package using node package manager (npm)" goes to `https://designsystem.gov.scot/get-started/installation/` |
| [x] | `charging.applies` | false | S2 | "Permission is hereby granted, free of charge" |
| [x] | `support.summary` | Email the Design System team at designsystem@gov.scot for help or feedback | S1 | "If you need any help or want to give any feedback you can e-mail the Design System team at: designsystem@gov.scot" |
| [x] | `service_page_url`, `documentation_url` | https://designsystem.gov.scot/ | S1 | Linked as "Scottish Government Design System" |
| [x] | `current_version`, `codebases[0].version` | 4.3.0 | S3 | `latest` dist-tag 4.3.0. **Update** if a newer version has been released |
| [x] | `codebases[0]` | public repository, maintenance `internal` | S1, S3 | S3: repository `github.com/scottish-government-design-system/design-system`, maintained by the "Scottish Government Digital Design system team". No `publiccode.yml` in the repository, so R12 warns |

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
| [x] | `name` | One Scotland Gazetteer | S1 | Title "One Scotland Gazetteer" |
| [x] | `summary`, `purpose` (database) | Address database made up of all 32 local authority gazetteers; BS7666:2006 and the Scottish Gazetteer Conventions; spatially referenced records and property lifecycle details | S1 | "The One Scotland Gazetteer is an address database made up of all 32 individual local authority gazetteers. All addresses are created in accordance with the national standard for addressing, BS7666:2006 and the Scottish Gazetteer Conventions. Key features include: Spatially referenced address records, Property lifecycle details" |
| [x] | `purpose` (streets) | National Street Gazetteer for Scotland, every street, road, track or cycleway, with USRNs | S2 | "a line dataset depicting every street, road, track or cycleway in Scotland"; "Unique Street Reference Numbers (USRN)" |
| [x] | `purpose` (services) | REST and SOAP services provide the data as an API for authorised organisations | S3, S4 | "provides the One Scotland Gazetteer data as an API that can be used by any authorised organisation within their address and street-based applications" |
| [x] | `purpose` (daily) | Maintained daily | S1, S2 | Maintenance frequency "daily" |
| [x] | `asset_type` | platform | — | Classification from specification 5.2 |
| [x] | `owner` | Improvement Service, `local-government` | S1–S4 | Organisation "The Improvement Service" (the national improvement body for Scottish local government) |
| [x] | `contact` | web form https://osg.scot/portal/pages/contact-Us | — | The portal's "Contact" link. The metadata gives the mailboxes gazcustomers@improvementservice.org.uk (S1, S2) and gazhelp@improvementservice.org.uk (S3, S4). **Check** the contact page works |
| [x] | `service_areas` | corporate-and-cross-cutting | — | Classification by the register |
| [x] | `capabilities` | data-and-analytics, mapping-and-location | — | Classification by the register: reference data; addresses and geographic data |
| [x] | `status` | live | S1–S4 | Maintained daily, with web services and public search in operation; confirmed live by the register author. |
| [x] | `intended_adopters` | PSGA members; commercial users through Ordnance Survey AddressBase products; limited public search | S1, S3, S5 | PSGA members can use the data; S3 states commercial availability through Ordnance Survey AddressBase products; limited public search was verified by the register author. |
| [x] | `terms_of_use` | PSGA use for public-sector applications; commercial access through Ordnance Survey AddressBase products; open UPRN and USRN components with attribution; portal terms for limited public search | S1, S3, S5 | The catalogue records distinguish PSGA and AddressBase routes. Open identifier components and portal search behaviour were verified by the register author. |
| [x] | `adoption_route` | PSGA members receive the data for public-sector use; commercial users obtain it through Ordnance Survey AddressBase products; the public portal provides limited address and map search after accepting its terms | S1, S3, S5 | Authoritative metadata supports the PSGA and AddressBase routes; portal behaviour was verified by the register author. |
| [x] | `charging.applies` | false for PSGA use and limited public search; commercial access is through Ordnance Survey AddressBase products | S1, S3, S5 | PSGA availability and the commercial AddressBase route are stated in the catalogue; free limited public use was verified by the register author. |
| [x] | `support.summary` | not-publicly-stated | S1–S4 | Not stated (S3 and S4 give a "gazhelp" mailbox as the contact, without saying it is a support service) |
| [x] | `service_url` | https://osg.scot/portal/ | S1–S4 | Public portal supports limited address and map search after accepting its terms, returning UPRNs and USRNs; verified by the register author. |
| [x] | `service_page_url` | [One Scotland Gazetteer information](https://osg.scot/portal/pages/about-us) | S5 | Owner portal information page, verified by the register author. |
| [x] | `interfaces` | REST (S3), SOAP (S4), each documented by its metadata record | S3, S4 | Titles "One Scotland Gazetteer REST Service", "One Scotland Gazetteer SOAP Service" |

## csr-0006 Spatial Hub

**Sources** (pages of the Spatial Hub itself, run by the Improvement Service)

- [S1] [About Us](https://data.spatialhub.scot/about).
- [S2] [Help Centre](https://data.spatialhub.scot/faq).
- [S3] [Terms and Conditions](https://data.spatialhub.scot/terms_and_condition).
- [S4] [Contact Us](https://data.spatialhub.scot/contact_us).

| Checked | Field | Value | Source | Supporting words |
|---|---|---|---|---|
| [x] | `name` | Spatial Hub | S1 | "The Spatial Hub is a platform for hosting and publishing Scottish spatial data." |
| [x] | `summary`, `purpose` (collects and publishes) | Combines datasets from local authorities and partners into Scotland-wide national datasets, published in various formats | S1 | "collects datasets from local authorities and other partner organisations to form Scotland-wide national datasets and publishes these in various formats to maximise their use" |
| [x] | `purpose` (processing) | Every three months; some datasets daily; web services and file downloads | S2 | "Every three months, the collected data updates are quality assessed, cleaned, standardised, and amalgamated into national datasets"; "Certain datasets (e.g., Planning Applications and Building Standards) are updated daily"; "available as web services and a variety of file downloads" |
| [x] | `purpose` (access) | Search and preview without an account; free account to download or connect | S2 | "You can search for datasets and display them on the preview map without registering. However, if you wish to download and/or connect to any data you'll need to register for a user account." |
| [x] | `purpose` (open data portal) | Some local authorities use it as their open data portal | S2 | "Some local authorities have chosen to use the Spatial Hub as an Open Data Portal" |
| [x] | `asset_type` | platform | S1, S3 | "a platform"; "an online platform for hosting and publishing Scottish spatial data" |
| [x] | `owner` | Improvement Service, `local-government` | S1, S3 | "Developed and maintained by the Improvement Service (IS)"; "We are the Improvement Service, operator of the Spatial Hub service." |
| [x] | `contact` | web form https://data.spatialhub.scot/contact_us | S4 | "For any other queries, please get in touch using the following form" |
| [x] | `service_areas` | corporate-and-cross-cutting, planning-and-building-standards | S2 | Classification by the register; S2 names planning applications and building standards datasets |
| [x] | `capabilities` | mapping-and-location, data-and-analytics | S1 | "Scottish spatial data"; national datasets |
| [x] | `status` | live | S1–S3 | The service is operating and taking registrations; confirmed live by the register author. |
| [x] | `intended_adopters` | the six Scottish public sector sectors, and further and higher education | S2 | "Public Sector Organisations: These organisations and their members can access data once their Spatial Hub account is registered against the correct PSGA organisation"; "Academic Institutions within Scotland: These organisations and their members can access data via EDINA's DigiMap service" |
| [x] | `terms_of_use` | service terms (the Terms and Conditions); OGL for open datasets; premium datasets by sector | S2, S3 | S2: "National Open Datasets: These datasets are shared under an Open Government Licence"; the premium access routes as above; "External Organisations/Users … can access data via our commercial partners" |
| [x] | `adoption_route` | Free account; download or web service; ask to register the account against the PSGA organisation; data providers join an Organisation | S2, S3 | S3: "you must first have registered and logged in to a free Spatial Hub account. Then you can either download a copy of the data in a variety of formats or connect to a web service"; S2: "registered against the correct PSGA organisation. Please contact us to request this"; "If you think you may need to create an Organisation for providing data to the Spatial Hub, please contact us" |
| [x] | `charging` | applies: not-publicly-stated; free account and open datasets; premium access through a PSGA organisation or commercial licence agreement | S2, S3 | The sources state that accounts and open datasets are free, but do not publish charges for commercial or premium access. |
| [x] | `support` | Help Centre; enquiry form; spatialhub@improvementservice.org.uk | S2, S4 | S4: "Please check our Help Centre before sending a message"; S2: "please contact us: spatialhub@improvementservice.org.uk" |
| [x] | `service_url`, `service_page_url`, `documentation_url` | the home page, About Us and the Help Centre | S1, S2 | The service's own pages |
| [x] | `open_data` | Spatial Hub datasets, https://data.spatialhub.scot/dataset/ | S2 | "National Open Datasets: These datasets are shared under an Open Government Licence" |

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
| [x] | `name` | GOV.UK Notify | S1 | Throughout |
| [x] | `summary`, `purpose` (what) | Public sector service teams send emails, text messages and letters | S2 | "GOV.UK Notify makes it easy for public sector service teams to send emails, text messages and letters." |
| [x] | `purpose` (no technical knowledge) | Templates, personalisation, bulk sending by spreadsheet, delivery tracking | S1, S2 | S2: "You do not need any technical knowledge to: create and send messages … add personalisation send messages in bulk see when your messages have been delivered"; S1: "Upload a spreadsheet of email addresses or phone numbers and Notify sends the messages." |
| [x] | `purpose` (API) | A developer integrates the API with a web application or back office system; client libraries or REST directly | S2, S6 | S2: "To send messages automatically, you'll need a developer to integrate with the GOV.UK Notify API"; S6: "If you cannot use the client libraries, you can integrate directly with the API instead." |
| [x] | `purpose` (letters) | Notify prints and posts letters | S2 | "GOV.UK Notify prints and posts your letters for you" |
| [x] | `asset_type` | api | — | Classification from specification 5.2 |
| [x] | `owner` | Government Digital Service, `uk-public-sector` | S1 | "GOV.UK Notify is built by the Government Digital Service" |
| [x] | `contact` | web form https://www.notifications.service.gov.uk/support | S1 | "Contact us if you have a question or want to give feedback." (links to the support page) |
| [x] | `service_areas` | corporate-and-cross-cutting | — | Classification by the register |
| [x] | `capabilities` | notifications, integration-and-apis | S1, S2 | Emails, text messages and letters; "Integrate the GOV.UK Notify API" |
| [x] | `status` | live | S1 | The operational service publishes current usage figures and pricing; confirmed live by the register author. |
| [x] | `intended_adopters` | uk-public-sector, excluding universities | S4 | Only public sector organisations can accept the agreement. The eligibility page lists qualifying public-sector bodies and explicitly states that universities cannot use Notify. |
| [x] | `terms_of_use` | service terms | S4, S7 | S7: "You accept our terms of use when you create an account."; S4 as above |
| [x] | `adoption_route` | Free account; new services start in trial mode; suppliers are invited; API for automatic sending | S2, S3, S4 | S2: "Create an account for free and try it yourself"; S3: "When you add a new service it will start in trial mode"; S4: "Someone from the public sector organisation you're working with needs to create an account and add the service first. Then they can invite you to join as a team member." |
| [x] | `charging` | applies, per-transaction, the prices | S1, S3 | S1: "Unlimited free emails"; "Up to 20,000 free text messages a year, then 2.4 pence per message"; "From 63.8 pence to print and post a one page letter"; S3: "no monthly charge, no setup fee and no procurement cost. You will only have to pay if you: send text messages after using all of your free allowance send letters". **Prices change**: check before publication |
| [x] | `support` | 24/7 for emergencies, reply within 30 minutes; otherwise by the end of the next working day | S5 | "GOV.UK Notify provides 24/7 support for emergencies. If you have an emergency we'll reply within 30 minutes. If it's not an emergency we'll reply by the end of the next working day." |
| [x] | `service_url`, `service_page_url`, `documentation_url` | home page, Features, Documentation | S1, S2, S6 | The service's own pages |
| [x] | `interfaces` | REST, documented at docs.notifications.service.gov.uk/rest-api.html; client libraries for Java, .NET, Node JS, PHP, Python and Ruby | S6 | "Read the REST API documentation"; "Client libraries … Java .NET Node JS PHP Python Ruby" |

## csr-0008 mygovscot myaccount

Added at the author's request as a sixth demonstration record, beyond the 3–5
in specification 5.2 (see the build plan's log for the decision).

**Sources**

- [S1] [mygovscot myaccount](https://www.improvementservice.org.uk/products-and-services/digital-public-services/myaccount), Improvement Service. The page answers automated requests with HTTP 403, so its text was supplied by the register author on 3 November 2026; the author confirms the quotes below.
- [S2] [myaccount](https://www.mygov.scot/myaccount), mygov.scot (Scottish Government), last updated 10 June 2025.
- [S3] [mygovscot myaccount help](https://signin.mygovscot.org/portal/pages/help), Improvement Service; includes a link to the contact form (author verification).

**Not used.** A techUK guest article by Yoti (a supplier to the service) is not cited; everything it supports is also in S1 or S2. Services the author knows use myaccount but that the sources do not name (for example tellmescotland.gov.uk) are left out.

| Checked | Field | Value | Source | Supporting words |
|---|---|---|---|---|
| [x] | `name` | mygovscot myaccount | S1 | "About mygovscot myaccount" |
| [x] | `summary` | The simple and secure sign-in service for online public services in Scotland; one account across multiple organisations | S1 | "mygovscot myaccount is the simple and secure sign-in service for online public services in Scotland"; "an online account that can be used across multiple organisations" |
| [x] | `purpose` (services) | Council tax, parking permits, school meals, benefits, National Entitlement Card | S1 | "such as paying council tax or requesting a parking permit, paying for school meals, or applying for benefits or a National Entitlement Card" |
| [x] | `purpose` (providers) | Standards-based authentication and identity verification | S1 | "secure and trusted authentication and identity verification services that are standards-based, easy to integrate, and free to use" |
| [x] | `purpose` (four services) | Authentication, channel shift, identity verification, data integrity | S1 | "mygovscot myaccount is based around four services: Authentication … Channel shift … Identity verification … Data integrity" |
| [x] | `purpose` (GPG44 and GPG45) | Can meet GPG44 authentication levels and GPG45 identity profiles; missed bin versus NHS Lothian and My Diabetes My Way | S1 | "can provide tools that will enable the organisation to achieve Good Practice Guide 44 (GPG44) authentication levels and verified identities that meet Good Practice Guide 45 (GPG45) profiles, if required"; "a user wishing to access NHS Lothian or My Diabetes My Way, are required to have a verified mygovscot myaccount" |
| [x] | `purpose` (getyournec.scot, parentsportal.scot) | Used by all 32 and 23 councils respectively | S1 | "All 32 local authorities use getyournec.scot for National Entitlement Card applications"; "23 local authorities use parentsportal.scot" |
| [x] | `purpose` (age) | 12 or over | S1, S2 | S1: "provided exclusively to individuals who are at least 12 years of age"; S2: "You must be 12 or over." |
| [x] | `asset_type` | service | — | Classification by the register, as for ScotAccount |
| [x] | `owner` | Improvement Service, `local-government` | S2 | "Myaccount is run by the Improvement Service for local councils." |
| [x] | `contact` | web form: the help page | S3 | Help page with a link to the contact form (author verification) |
| [x] | `service_areas`, `capabilities` | corporate-and-cross-cutting; identity-and-access | — | Classification by the register |
| [x] | `status` | live | S1 | "41 organisations are live with mygovscot myaccount" |
| [x] | `intended_adopters` | the six Scottish public sector sectors | S1 | "For public service providers"; users include councils, NHS Lothian and Social Security Scotland. **Check** |
| [x] | `terms_of_use.type` | not-publicly-stated | S1 | Not stated |
| [x] | `adoption_route.summary` | Offered as a toolkit in a variety of configurations; easy to integrate | S1 | "offered to organisations as a toolkit, which can be deployed in a variety of configurations to meet their needs and requirements and is proportionate to the services they provide"; "easy to integrate" |
| [x] | `charging` | `applies: false`; free to use for public service providers | S1 | "For public service providers … free to use" |
| [x] | `support.summary` | not-publicly-stated | S1 | Support for organisations is not stated |
| [x] | `service_url` | https://signin.mygovscot.org/home/ | S2 | "Register on the myaccount website" links here |
| [x] | `service_page_url` | the Improvement Service's product page | S1 | The owner's page |
| [x] | `adopters` | All 32 Scottish councils; NHS Lothian; Social Security Scotland; Young Scot (all `self-reported`) | S1, S2 | S1: "all 32 councils across Scotland use it"; "NHS Lothian"; S2: "applying for Social Security Scotland benefits"; "applying for a Young Scot card" |
