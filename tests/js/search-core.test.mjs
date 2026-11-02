// Run with: node --test tests/js/  (pytest runs it through tests/test_js.py)
import assert from 'node:assert/strict';
import { test } from 'node:test';

import {
  counts, countText, emptyState, matches, normalise, queryFromState, results, stateFromQuery,
} from '../../src/csr/static/js/search-core.js';

const records = [
  { id: 'csr-0001', name: 'Register', text: 'register digital office content publishing csr 0001', provenance: 'owner-confirmed',
    type: 'service', sector: 'local-government', areas: ['corporate'], capabilities: ['content'], currency: 'current',
    withdrawn: false, changed: '2026-11-02', confirmed: '2026-11-02' },
  { id: 'csr-9001', name: 'Example: Payments', text: 'example payments card recharge', provenance: 'example',
    type: 'component', sector: 'local-government', areas: ['revenues'], capabilities: ['payments'], currency: 'current',
    withdrawn: false, changed: '2026-10-01', confirmed: '2026-09-15' },
  { id: 'csr-0100', name: 'ScotAccount', text: 'scotaccount sign in identity csr 0100', provenance: 'demonstration',
    type: 'service', sector: 'scottish-government', areas: ['corporate'], capabilities: ['identity'],
    currency: 'unconfirmed', withdrawn: false, changed: '2026-10-20', confirmed: null },
  { id: 'csr-9005', name: 'Example: Withdrawn', text: 'example withdrawn pilot', provenance: 'example',
    type: 'artefact', sector: 'local-government', areas: ['education'], capabilities: ['forms'], currency: null,
    withdrawn: true, changed: '2026-06-30', confirmed: null },
];

const state = (changes) => ({ ...emptyState(), ...changes, filters: { ...emptyState().filters, ...(changes.filters || {}) } });
const ids = (list) => list.map((r) => r.id);

test('everything except withdrawn records, by name, when nothing is chosen', () => {
  assert.deepEqual(ids(results(records, emptyState())), ['csr-9001', 'csr-0001', 'csr-0100']);
});

test('search matches every word, ignoring case and accents', () => {
  assert.deepEqual(ids(results(records, state({ q: 'PAYMENTS  card' }))), ['csr-9001']);
  assert.deepEqual(ids(results(records, state({ q: 'Sign-in' }))), ['csr-0100']);
  assert.deepEqual(ids(results(records, state({ q: 'payments identity' }))), []);
  assert.equal(normalise('  Café   Ölé '), 'cafe ole');
  assert.equal(normalise('csr-0001, solution.yml'), 'csr 0001 solution yml');
});

test('query words match the start of words, not the middle', () => {
  assert.deepEqual(ids(results(records, state({ q: 'pay' }))), ['csr-9001']);
  assert.deepEqual(ids(results(records, state({ q: 'gist' }))), []);
  assert.deepEqual(ids(results(records, state({ q: 'ister' }))), []);
  assert.deepEqual(ids(results(records, state({ q: 'csr-0100' }))), ['csr-0100']);
});

test('filters combine: any value within a group, every group across groups', () => {
  assert.deepEqual(ids(results(records, state({ filters: { provenance: ['example', 'demonstration'] } }))),
    ['csr-9001', 'csr-0100']);
  assert.deepEqual(ids(results(records, state({ filters: { provenance: ['example'], type: ['service'] } }))), []);
  assert.deepEqual(ids(results(records, state({ filters: { area: ['corporate'] } }))), ['csr-0001', 'csr-0100']);
  assert.deepEqual(ids(results(records, state({ filters: { currency: ['unconfirmed'] } }))), ['csr-0100']);
});

test('withdrawn records only when asked for', () => {
  assert.deepEqual(ids(results(records, state({ withdrawn: true, q: 'example' }))), ['csr-9001', 'csr-9005']);
  assert.equal(matches(records[3], emptyState()), false);
});

test('counts ignore their own group but respect the query and other groups', () => {
  const c = counts(records, state({ filters: { provenance: ['example'] } }));
  assert.deepEqual(c.provenance, { 'owner-confirmed': 1, example: 1, demonstration: 1 });
  assert.deepEqual(c.type, { component: 1 });
  assert.deepEqual(counts(records, state({ q: 'example', withdrawn: true })).type, { component: 1, artefact: 1 });
});

test('sort by recently changed and recently confirmed', () => {
  assert.deepEqual(ids(results(records, state({ sort: 'changed' }))), ['csr-0001', 'csr-0100', 'csr-9001']);
  assert.deepEqual(ids(results(records, state({ sort: 'confirmed' }))), ['csr-0001', 'csr-9001', 'csr-0100']);
});

test('state round-trips through the URL, and defaults are left out', () => {
  const s = state({ q: 'pay', filters: { provenance: ['example', 'owner-confirmed'], sector: ['local-government'] },
    withdrawn: true, sort: 'changed' });
  const query = queryFromState(s);
  assert.equal(query, '?q=pay&provenance=example&provenance=owner-confirmed&sector=local-government&withdrawn=1&sort=changed');
  assert.deepEqual(stateFromQuery(query), s);
  assert.equal(queryFromState(emptyState()), '');
});

test('unknown or repeated URL values are tidied', () => {
  const s = stateFromQuery('?sort=random&sector=a&sector=b&type=api&type=api&colour=red');
  assert.equal(s.sort, 'name');
  assert.deepEqual(s.filters.sector, ['a']);
  assert.deepEqual(s.filters.type, ['api']);
});

test('result count wording', () => {
  assert.equal(countText(1), '1 solution');
  assert.equal(countText(0), '0 solutions');
});
