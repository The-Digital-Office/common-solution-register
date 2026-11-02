# common-solution-register

A demonstrator of a common solution register for the Scottish public sector,
built for the Scottish Government short-life working group (SLWG) on a common
solution register. It shows, with a working example, how public bodies could
describe the solutions they offer to each other for reuse, how those
descriptions are validated and published, and how owners can keep them current.
It is hosted by The Digital Office for Scottish Local Government. **It is not an
official register**: every record is labelled by its provenance, and the SLWG
decides whether a register is built, by whom and to what design.

A *common solution* is a capability that an accountable owner offers to other
public bodies, described by a `solution.yml` file. A *codebase* is source code
that implements a solution, described by its own `publiccode.yml`. The
specification in
[`docs/spec/`](docs/spec/Common-Solution-Register-Demonstrator-Specification.md)
sets out the scope, design and build.

> **Status:** under construction. The build is done in slices, recorded in
> [`docs/build/PLAN.md`](docs/build/PLAN.md). The site is not yet published.

## Getting started

Prerequisites: Python 3.12 and Git.

```bash
git clone https://github.com/The-Digital-Office/common-solution-register.git
cd common-solution-register
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest -q
csr --version
```

To check the register's records, or any `solution.yml` file or HTTPS URL:

```bash
csr validate
csr validate path/to/solution.yml
csr validate --check-links
```

`--check-links` also checks that linked addresses respond and that each
codebase's `publiccode.yml` agrees with the record. The checks are listed in
[`schema/README.md`](schema/README.md). Harvesting owner-hosted descriptors
(`csr harvest`) and building the site (`csr build`) are added in later build
slices.

A failed build or deployment notifies the person whose commit triggered it,
through GitHub. Maintainers watch the repository.

## Contributing

Contributions are welcome. See the
[Digital Office contributing guide](https://github.com/The-Digital-Office/.github/blob/main/CONTRIBUTING.md).
To report a security problem, follow the
[security policy](https://github.com/The-Digital-Office/.github/blob/main/SECURITY.md)
rather than opening an issue.

## Licence

Unless stated otherwise, the code in this repository is licensed under the
[MIT licence](LICENSE), and the records and documentation are © The Digital
Office for Scottish Local Government and licensed under the
[Open Government Licence v3.0](LICENCE-CONTENT.md).

## Maintainers

Maintained by The Digital Office for Scottish Local Government. See
[CODEOWNERS](.github/CODEOWNERS) for the current maintainers.
