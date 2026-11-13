# UK Cross-Government Metadata Exchange Model

`uk_cross_government_metadata_exchange_model.yaml` is an unmodified copy of the
model's LinkML schema, downloaded on 13 November 2026 from
<https://github.com/co-cddo/ukgov-metadata-exchange-model/blob/main/src/model/uk_cross_government_metadata_exchange_model.yaml>.
It is published under the Open Government Licence v3.0.

`tests/test_metadata.py` reads it to check `api/v0/metadata.json` against the
model's required properties, allowed values and patterns (decision point DP-57).
The model's list of GOV.UK organisations (`uk-gov-orgs.yaml`) is not copied: the
register's host is not on it, which DP-57 records as a departure.
