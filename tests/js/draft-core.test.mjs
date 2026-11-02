// Run with: node --test tests/js/draft-core.test.mjs  (pytest runs it through tests/test_js.py)
import assert from 'node:assert/strict';
import { test } from 'node:test';

import {
  SENTINEL, answersFromRecord, buildDraft, buildRecord, contactType, emptyAnswers, isoDate, sections, ukDate,
} from '../../src/csr/static/js/draft-core.js';

const order = ['schema_version', 'id', 'record_status', 'name', 'summary', 'purpose', 'asset_type', 'owner', 'contact',
  'service_areas', 'capabilities', 'status', 'intended_adopters', 'terms_of_use', 'adoption_route', 'charging',
  'support', 'service_url', 'service_page_url', 'documentation_url', 'sources', 'confirmation', 'withdrawal',
  'deprecation', 'interfaces', 'codebases', 'open_data', 'related_assets', 'adopters'];
const build = (changes, base) => buildRecord({ ...emptyAnswers(), ...changes }, { base, order, today: '2026-11-02' });

test('an empty form gives the skeleton, with a placeholder id', () => {
  const record = build({});
  assert.deepEqual(Object.keys(record), ['schema_version', 'id', 'asset_type', 'owner', 'status', 'terms_of_use', 'charging']);
  assert.equal(record.id, 'csr-NNNN');
  assert.deepEqual(record.charging, { applies: false });
});

test('fields follow the schema order and blanks are left out', () => {
  const record = build({ name: ' Booking ', owner: 'Example Council', contact: 'booking@example.gov.uk',
    service_areas: ['housing'], terms_ref: 'MIT', adoption: 'Deploy it.' });
  assert.equal(record.name, 'Booking');
  assert.deepEqual(record.contact, { type: 'role-mailbox', value: 'booking@example.gov.uk' });
  assert.deepEqual(record.terms_of_use, { type: 'open-licence', licence: 'MIT' });
  const keys = Object.keys(record);
  assert.ok(keys.indexOf('name') < keys.indexOf('owner') && keys.indexOf('owner') < keys.indexOf('terms_of_use'));
});

test('condition 1 and 2: owners confirm; others cite sources and may leave things unstated', () => {
  const owner = build({ own: 'yes' });
  assert.equal(owner.record_status, 'owner-confirmed');
  assert.deepEqual(owner.confirmation, { last_confirmed: '2026-11-02', method: 'draft form', reference: 'Submitted with the draft form' });
  const other = build({ own: 'no', charges: 'unstated', terms_type: SENTINEL,
    sources: [{ url: 'https://example.gov.uk/', title: 'Home', publisher: '', accessed: '01/11/2026' }] });
  assert.equal(other.record_status, 'demonstration');
  assert.deepEqual(other.sources, [{ url: 'https://example.gov.uk/', title: 'Home', accessed: '2026-11-01' }]);
  assert.equal(other.adoption_route.summary, SENTINEL);
  assert.deepEqual(other.charging, { applies: SENTINEL });
  assert.deepEqual(other.terms_of_use, { type: SENTINEL });
  assert.equal(other.confirmation, undefined);
  assert.equal(build({ own: 'yes', charges: 'unstated' }).charging, undefined); // the sentinel only for demonstration
});

test('sections follow the conditions', () => {
  const s = (changes, base) => sections({ ...emptyAnswers(), ...changes }, base);
  assert.equal(s({ asset_type: 'service', status: 'live' }).support, true);
  assert.equal(s({ asset_type: 'platform', status: 'beta' }).support, true);
  assert.equal(s({ asset_type: 'service', status: 'concept' }).support, false);
  assert.equal(s({ asset_type: 'component', status: 'live' }).support, false);
  assert.equal(s({ asset_type: 'api' }).interfaces, true);
  assert.equal(s({ asset_type: 'component' }, { interfaces: [{}] }).interfaces, true);
  assert.equal(s({ asset_type: 'software' }).software, true);
  assert.equal(s({ charges: 'yes' }).charging, true);
  assert.equal(s({ status: 'deprecated' }).deprecation, true);
  assert.equal(s({}, { record_status: 'withdrawn' }).withdrawal, true);
  assert.equal(s({ own: 'no' }).sources, true);
});

test('hidden sections are not written', () => {
  const record = build({ asset_type: 'component', status: 'live', support: 'Service desk',
    interfaces: [{ type: 'rest', documentation_url: 'https://x' }], migration_guidance: 'Move', charges: 'no',
    charging_detail: 'ignored' });
  assert.equal(record.support, undefined);
  assert.equal(record.interfaces, undefined);
  assert.equal(record.deprecation, undefined);
  assert.deepEqual(record.charging, { applies: false });
});

test('charging details: a URL or a summary', () => {
  assert.deepEqual(build({ charges: 'yes', charging_model: 'subscription', charging_detail: 'https://x/charges' }).charging,
    { applies: true, model: 'subscription', url: 'https://x/charges' });
  assert.deepEqual(build({ charges: 'yes', charging_detail: 'Annual fee' }).charging,
    { applies: true, model: 'recharge', summary: 'Annual fee' });
});

test('rows say which form group each list entry came from', () => {
  const { rows } = buildDraft({ ...emptyAnswers(), codebases: [
    { repository_url: '', visibility: '', publiccode_url: '', maintenance: 'internal' },
    { repository_url: 'https://code/x', visibility: '', publiccode_url: '', maintenance: 'internal' }] }, { order });
  assert.deepEqual(rows.codebases, [1]);
});

test('repeaters drop empty rows', () => {
  const record = build({ codebases: [{ repository_url: '', visibility: '', publiccode_url: '', maintenance: 'internal' },
    { repository_url: 'https://code/x', visibility: 'public', publiccode_url: '', maintenance: 'none' }],
  open_data: [{ title: '', url: '' }] });
  assert.deepEqual(record.codebases, [{ repository_url: 'https://code/x', visibility: 'public', maintenance: 'none' }]);
  assert.equal(record.open_data, undefined);
});

test('correcting a record keeps its id, status, confirmation and fields the form does not show', () => {
  const base = { schema_version: '0.1', id: 'csr-9003', record_status: 'example', name: 'Example: X', summary: 's',
    purpose: 'p', asset_type: 'service', owner: { organisation: 'Example Council', sector: 'local-government' },
    contact: { type: 'role-mailbox', value: 'a@example.gov.uk' }, service_areas: ['housing'], capabilities: ['payments'],
    status: 'deprecated', intended_adopters: ['local-government'], terms_of_use: { type: 'service-terms', url: 'https://t' },
    adoption_route: { summary: 'Ask', url: 'https://adopt' }, charging: { applies: false },
    deprecation: { date: '2026-03-31', migration_guidance: 'https://m' },
    confirmation: { last_confirmed: '2025-09-02', method: 'email', reference: 'r' },
    adopters: [{ organisation: 'Example Council', evidence: 'verified' }], related_assets: [{ id: 'csr-9006' }],
    codebases: [{ visibility: 'private', maintenance: 'none', role: 'Front end' }],
    currency: 'stale', record_url: 'assets/csr-9003/', hosting: 'local' };
  const answers = answersFromRecord(base);
  assert.equal(answers.own, '');
  assert.equal(answers.deprecation_date, '31/03/2026');
  const record = buildRecord(answers, { base, order, today: '2026-11-02' });
  assert.equal(record.id, 'csr-9003');
  assert.equal(record.record_status, 'example');
  assert.deepEqual(record.confirmation, base.confirmation);
  assert.deepEqual(record.adopters, base.adopters);
  assert.deepEqual(record.related_assets, base.related_assets);
  assert.deepEqual(record.adoption_route, base.adoption_route); // url kept although the form shows only the summary
  assert.deepEqual(record.codebases, base.codebases); // role kept
  assert.equal(record.currency, undefined);
  assert.equal(record.record_url, undefined);
  const { currency, record_url, hosting, ...descriptor } = base;
  assert.deepEqual(record, Object.fromEntries(order.filter((k) => k in descriptor).map((k) => [k, descriptor[k]])));
});

test('dates and contact types', () => {
  assert.equal(isoDate('1/3/2026'), '2026-03-01');
  assert.equal(isoDate('2026-03-01'), '2026-03-01');
  assert.equal(isoDate('next week'), 'next week');
  assert.equal(ukDate('2026-03-01'), '01/03/2026');
  assert.equal(contactType('team@example.gov.uk'), 'role-mailbox');
  assert.equal(contactType('https://example.gov.uk/contact'), 'web-form');
  assert.equal(contactType('0300 123 4567'), 'service-desk');
});
