// Run with: node --test tests/js/record-check.test.mjs  (pytest runs it through tests/test_js.py)
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import { test } from 'node:test';

import { check, compile, dotted, isDate } from '../../src/csr/static/js/record-check.js';

const require = createRequire(import.meta.url);
const Ajv = require('../../src/csr/static/vendor/ajv/8.17.1/ajv2020.min.js');
const schema = JSON.parse(readFileSync(new URL('../../schema/asset.schema.json', import.meta.url)));
const validate = compile(Ajv.default || Ajv, schema);

const minimal = {
  schema_version: '0.1', id: 'csr-NNNN', record_status: 'owner-confirmed', name: 'Booking component',
  summary: 'A reusable booking component for council services.',
  purpose: 'Lets council services take bookings for collections, appointments and rooms through one component.',
  asset_type: 'component', owner: { organisation: 'Example Council', sector: 'local-government' },
  contact: { type: 'role-mailbox', value: 'booking@example.gov.uk' }, service_areas: ['housing'],
  capabilities: ['booking-and-scheduling'], status: 'live', intended_adopters: ['local-government'],
  terms_of_use: { type: 'open-licence', licence: 'MIT' }, adoption_route: { summary: 'Deploy it from the repository.' },
  charging: { applies: false },
  confirmation: { last_confirmed: '2026-11-02', method: 'draft form', reference: 'Submitted with the draft form' },
};
const problems = (record, today = '2026-11-02') => check(validate, record, { today });
const paths = (record) => problems(record).map((p) => p.path).sort();

test('a complete record, with the placeholder id, has no problems', () => {
  assert.deepEqual(problems(minimal), []);
});

test('agrees with the Python validator on every schema fixture', () => {
  // The fixtures, as JSON, are written by tests/test_js.py before this runs.
  const fixtures = JSON.parse(readFileSync(process.env.CSR_FIXTURES, 'utf8'));
  for (const [path, record] of Object.entries(fixtures)) {
    assert.equal(problems(record, '2027-01-01').length === 0, path.startsWith('pass/'), path);
  }
});

test('one plain message per missing field', () => {
  const { name, summary, contact, service_areas, ...rest } = minimal;
  const found = problems({ ...rest, owner: { sector: 'local-government' } });
  assert.deepEqual(found.map((p) => [p.path, p.message]).sort(), [
    ['contact', 'Enter a contact'],
    ['name', "Enter the solution's name"],
    ['owner.organisation', 'Enter the owning organisation'],
    ['service_areas', 'Choose at least one service area'],
    ['summary', 'Enter a summary'],
  ]);
});

test('lengths, addresses and dates are explained', () => {
  const found = Object.fromEntries(problems({ ...minimal, summary: 'Too short',
    documentation_url: 'http://docs.example.gov.uk', status: 'deprecated',
    deprecation: { date: '2026-02-30', migration_guidance: 'Use the new one.' } }).map((p) => [p.path, p.message]));
  assert.equal(found.summary, 'Summary must be at least 20 characters');
  assert.equal(found.documentation_url, 'Documentation address must be a full web address starting https://');
  assert.equal(found['deprecation.date'], 'Deprecation date must be a real date, for example 31/03/2026');
});

test('conditions report the field that is missing', () => {
  assert.deepEqual(paths({ ...minimal, asset_type: 'service' }), ['service_page_url', 'service_url', 'support']);
  assert.deepEqual(paths({ ...minimal, asset_type: 'software' }), ['codebases']);
  assert.deepEqual(paths({ ...minimal, charging: { applies: true } }), ['charging', 'charging.model']);
  assert.deepEqual(paths({ ...minimal, terms_of_use: { type: 'service-terms' } }), ['terms_of_use']);
  const { confirmation, ...unconfirmed } = minimal;
  assert.deepEqual(paths({ ...unconfirmed, record_status: 'demonstration' }), ['sources']);
  assert.deepEqual(paths({ ...minimal, codebases: [{ visibility: 'public', maintenance: 'none' }] }),
    ['codebases[0].repository_url']);
});

test('the sentinel outside a demonstration entry is explained once', () => {
  const found = problems({ ...minimal, adoption_route: { summary: 'not-publicly-stated' } });
  assert.equal(found.length, 1);
  assert.equal(found[0].path, 'adoption_route.summary');
  assert.match(found[0].message, /Not stated in public sources/);
});

test('R09 placeholders and R06 future confirmation dates', () => {
  assert.deepEqual(problems({ ...minimal, purpose: 'TODO: describe what the component does and who it is for.' })
    .map((p) => [p.path, p.rule]), [['purpose', 'R09']]);
  assert.deepEqual(problems(minimal, '2026-11-01').map((p) => [p.path, p.rule]), [['confirmation.last_confirmed', 'R06']]);
});

test('helpers', () => {
  assert.equal(dotted('/codebases/0/repository_url'), 'codebases[0].repository_url');
  assert.equal(dotted(''), '');
  assert.equal(isDate('2026-02-28'), true);
  assert.equal(isDate('2026-02-29'), false);
  assert.equal(isDate('31/03/2026'), false);
});
