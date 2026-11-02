// The validate page (specification 6.8 and 6.13): check a solution.yml from
// pasted text, an uploaded file or a URL, in the browser, against the schema
// and the rules that need no network, and show a results table with the
// rule, field and fix for each problem.
import { YAML11_SCHEMA, load } from '../vendor/js-yaml/5.5.0/js-yaml.mjs';
import { check, compile } from './record-check.js';

const config = JSON.parse(document.getElementById('csr-validate-config').textContent);
const AjvClass = window.ajv2020 && (window.ajv2020.default || window.ajv2020);
const validators = AjvClass ? { asset: compile(AjvClass, config.schemas.asset), pointer: compile(AjvClass, config.schemas.pointer) } : null;
const context = { taxonomies: config.taxonomies, knownIds: config.known_ids };
let mode = 'paste';

const $ = (id) => document.getElementById(id);
const today = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
};

/** Parse YAML as csr validate does: YAML 1.1, repeated keys refused, dates kept as the text written. */
export function parse(text) {
  const plain = (value) => {
    if (value instanceof Date) {
      const iso = value.toISOString();
      return iso.endsWith('T00:00:00.000Z') ? iso.slice(0, 10) : iso.replace('.000Z', 'Z');
    }
    if (Array.isArray(value)) return value.map(plain);
    if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, plain(v)]));
    return value;
  };
  return plain(load(text, { schema: YAML11_SCHEMA }));
}

function setMode(next) {
  mode = next;
  document.querySelectorAll('[data-mode]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.mode === mode)));
  document.querySelectorAll('[data-panel]').forEach((p) => { p.hidden = p.dataset.panel !== mode; });
  clearResults();
}

function clearResults() {
  ['result-fail', 'result-pass', 'result-table', 'result-pointer'].forEach((id) => { $(id).hidden = true; });
  $('result-rows').replaceChildren();
}

async function readInput() {
  if (mode === 'paste') return $('yaml').value;
  if (mode === 'upload') {
    const file = $('file').files[0];
    if (!file) throw new Error('Choose a file to check.');
    if (file.size > config.max_bytes) throw new Error(`The file is larger than ${Math.round(config.max_bytes / 1024)} KB, the register's limit.`);
    return file.text();
  }
  const url = $('url').value.trim();
  if (!/^https:\/\//.test(url)) throw new Error('Enter an address starting https://.');
  let response;
  try {
    response = await fetch(url, { credentials: 'omit', redirect: 'follow' });
  } catch {
    throw new Error('The file could not be fetched. Its host may not allow other sites to read it: open the address, copy the file, and paste it instead.');
  }
  if (!response.ok) throw new Error(`The address returned HTTP ${response.status}. Check it is right and public.`);
  if (!response.url.startsWith('https://')) throw new Error('The address redirected to one that is not HTTPS.');
  const text = await response.text();
  if (text.length > config.max_bytes) throw new Error(`The file is larger than ${Math.round(config.max_bytes / 1024)} KB, the register's limit.`);
  return text;
}

/** Findings for a document, as the table shows them. */
export function findings(text) {
  if (!text.trim()) return [{ rule: 'YAML', severity: 'error', path: '', message: 'There is nothing to check', fix: 'Paste, upload or fetch a solution.yml.' }];
  let data;
  try {
    data = parse(text);
  } catch (error) {
    const line = error.mark ? ` on line ${error.mark.line + 1}` : '';
    return [{ rule: 'YAML', severity: 'error', path: '', message: `The file cannot be read as YAML${line}: ${error.reason || error.message}`, fix: 'Correct the YAML syntax.' }];
  }
  if (!data || typeof data !== 'object' || Array.isArray(data)) {
    return [{ rule: 'YAML', severity: 'error', path: '', message: 'The file is not a list of field names and values', fix: 'Start it with fields such as schema_version: "0.1".' }];
  }
  if ('source' in data && !('schema_version' in data)) {
    const valid = validators.pointer(data);
    const problems = valid ? [] : validators.pointer.errors.map((e) => ({ rule: 'SCHEMA', severity: 'error',
      path: (e.instancePath.slice(1) || e.params.missingProperty || ''), message: e.keyword === 'required'
        ? `A pointer record needs ${e.params.missingProperty}` : `This value ${e.message}`, fix: 'A pointer has exactly three fields: id, source (an HTTPS address) and expected_owner.' }));
    return [{ pointer: data.source }, ...problems];
  }
  const found = check(validators.asset, data, { today: today(), context });
  if (data.id === 'csr-NNNN') {
    found.push({ rule: 'R01', severity: 'warning', path: 'id', message: 'The id is allocated when the record is registered', fix: 'Nothing to do: a maintainer gives the record its id.' });
  }
  return found;
}

function cell(row, content) {
  const td = document.createElement('td');
  if (content instanceof Node) td.append(content); else td.textContent = content;
  row.append(td);
}

function show(found) {
  clearResults();
  const pointer = found.find((f) => f.pointer)?.pointer;
  const list = found.filter((f) => !f.pointer)
    .sort((a, b) => (a.severity === b.severity ? 0 : a.severity === 'error' ? -1 : 1));
  const errors = list.filter((f) => f.severity === 'error').length;
  for (const f of list) {
    const tr = document.createElement('tr');
    const tag = document.createElement('strong');
    tag.className = `ds_tag ds_tag--${f.severity === 'error' ? 'red' : 'orange'}`;
    tag.textContent = f.severity === 'error' ? 'Error' : 'Warning';
    cell(tr, tag);
    cell(tr, f.rule === 'SCHEMA' ? 'Schema' : f.rule);
    const code = document.createElement('code');
    code.textContent = f.path || '(whole file)';
    cell(tr, code);
    cell(tr, f.fix ? `${f.message}. ${f.fix}` : `${f.message}.`);
    $('result-rows').append(tr);
  }
  $('result-table').hidden = list.length === 0;
  if (errors) {
    $('result-fail-title').textContent = list.length === 1 ? '1 problem found' : `${list.length} problems found`;
    $('result-fail').hidden = false;
    $('result-fail').focus();
  } else {
    const warnings = list.length;
    $('result-pass-text').textContent = pointer
      ? 'This pointer record is valid. The file it points to is checked when it is harvested: you can check it here too.'
      : `This solution.yml meets schema version ${config.schemas.asset.properties.schema_version.const} and all rules${
        warnings ? `, with ${warnings === 1 ? 'a warning' : `${warnings} warnings`} below. Warnings do not stop registration.` : '.'}`;
    $('result-pass').hidden = false;
    $('result-pass').focus();
  }
  if (pointer && /^https:\/\//.test(pointer)) {
    const p = $('result-pointer');
    p.replaceChildren('This is a pointer record. ');
    const a = document.createElement('a');
    a.href = `?url=${encodeURIComponent(pointer)}`;
    a.textContent = 'Check the file it points to';
    p.append(a, '.');
    p.hidden = false;
  }
}

async function run() {
  let text;
  try {
    text = await readInput();
  } catch (error) {
    show([{ rule: 'Input', severity: 'error', path: '', message: error.message.replace(/\.$/, ''), fix: '' }]);
    return;
  }
  if (!validators) {
    show([{ rule: 'Input', severity: 'error', path: '', message: 'The validator could not load', fix: 'Reload the page, or use csr validate.' }]);
    return;
  }
  show(findings(text));
}

if ($('run')) {
  document.querySelectorAll('[data-mode]').forEach((button) => button.addEventListener('click', () => setMode(button.dataset.mode)));
  $('run').addEventListener('click', run);
  ['yaml', 'file', 'url'].forEach((id) => $(id).addEventListener('input', clearResults));
  const url = new URLSearchParams(window.location.search).get('url');
  if (url) {
    setMode('url');
    $('url').value = url;
    run();
  }
}
