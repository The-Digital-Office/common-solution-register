This repository was created from the
[Digital Office repository template](https://github.com/The-Digital-Office/repository-template).
Its name, URL, date and code owner have been filled in automatically. The steps
below need a person. Close this issue when they are done.

### Settings (organisation owner)

- [ ] Apply the baseline settings by running
      `scripts/apply-baseline.sh {{REPO_NAME}}` from
      [The-Digital-Office/.github](https://github.com/The-Digital-Office/.github).
      This sets the branch rules, merge settings, security settings and labels.
- [ ] Add a description and topics in the repository's **About** panel.

### Files

- [ ] `README.md`: describe what this is, who it is for and how to get started.
- [ ] `.github/CODEOWNERS`: add the second maintainer, if there is one.
- [ ] If this repository contains **only documentation or content**, replace
      `LICENSE` with the
      [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
      text.

### publiccode.yml

Applies to **public software** repositories only. It is not checked while the
repository is private, so you can complete it any time before making the
repository public.

- [ ] Complete `description`: `shortDescription`, `longDescription` and `features`.
- [ ] Review `platforms`, `softwareType`, `categories` and `developmentStatus`.
- [ ] Check `maintenance.contacts` has your full name.
- If this repository is **documentation, not software**: add the
  `documentation` topic and delete `publiccode.yml`.

### Tidy up

- [ ] Delete `.github/workflows/template.yml`. It will not run again, but
      GitHub does not allow a workflow to delete itself.
