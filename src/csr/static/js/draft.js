// The draft form page (specification 6.6 and 6.13): repeating groups,
// conditional sections, and a live solution.yml preview. Validation and the
// hand-off (copy, download, GitHub issue, email) are added in slice S9.
import { dump } from '../vendor/js-yaml/5.5.0/js-yaml.mjs';
import { answersFromRecord, buildRecord, emptyAnswers, sections } from './draft-core.js';

const form = document.getElementById('draft-form');
const config = JSON.parse(document.getElementById('csr-draft-config').textContent);
const preview = document.getElementById('draft-yaml');
let base = {};

const today = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
};

// Repeating groups

const REPEATERS = {
  interfaces: { read: (n) => ({ type: value(`itype-${n}`), documentation_url: value(`idoc-${n}`) }),
    write: (n, i) => { set(`itype-${n}`, i.type); set(`idoc-${n}`, i.documentation_url); } },
  sources: { read: (n) => ({ url: value(`srcurl-${n}`), title: value(`srctitle-${n}`),
    publisher: value(`srcpub-${n}`), accessed: value(`srcdate-${n}`) }),
    write: (n, s) => { set(`srcurl-${n}`, s.url); set(`srctitle-${n}`, s.title); set(`srcpub-${n}`, s.publisher);
      set(`srcdate-${n}`, s.accessed); } },
  codebases: { read: (n) => ({ repository_url: value(`repo-${n}`), visibility: radio(`vis-${n}`),
    publiccode_url: value(`pc-${n}`), maintenance: value(`maint-${n}`) }),
    write: (n, c) => { set(`repo-${n}`, c.repository_url); setRadio(`vis-${n}`, c.visibility);
      set(`pc-${n}`, c.publiccode_url); set(`maint-${n}`, c.maintenance); } },
  open_data: { read: (n) => ({ title: value(`odtitle-${n}`), url: value(`odurl-${n}`) }),
    write: (n, d) => { set(`odtitle-${n}`, d.title); set(`odurl-${n}`, d.url); } },
};
const counters = {};

function value(id) {
  const element = document.getElementById(id);
  return element ? element.value : '';
}
function set(id, text) {
  const element = document.getElementById(id);
  if (element) element.value = text ?? '';
}
function radio(name) {
  const checked = form.querySelector(`input[name="${name}"]:checked`);
  return checked ? checked.value : '';
}
function setRadio(name, choice) {
  form.querySelectorAll(`input[name="${name}"]`).forEach((input) => { input.checked = input.value === choice; });
}
function checked(name) {
  return [...form.querySelectorAll(`input[name="${name}"]:checked`)].map((input) => input.value);
}
function setChecked(name, values) {
  form.querySelectorAll(`input[name="${name}"]`).forEach((input) => { input.checked = values.includes(input.value); });
}

function items(group) {
  return [...document.querySelectorAll(`[data-repeater="${group}"] > [data-item]`)];
}

function addItem(group, { focus = false } = {}) {
  counters[group] = (counters[group] || 0) + 1;
  const n = counters[group];
  const html = document.getElementById(`tpl-${group}`).innerHTML.replaceAll('__N__', String(n));
  const holder = document.createElement('div');
  holder.innerHTML = html.trim();
  const item = holder.firstElementChild;
  item.dataset.n = String(n);
  document.querySelector(`[data-repeater="${group}"]`).append(item);
  renumber(group);
  if (focus) item.querySelector('input, select, textarea')?.focus();
  return n;
}

/** Keep visible numbering consecutive, and hide "Remove" when a group has a single item. */
function renumber(group) {
  const list = items(group);
  list.forEach((item, index) => {
    const legend = item.querySelector('legend');
    if (legend && /\d+$/.test(legend.textContent)) legend.textContent = legend.textContent.replace(/\d+$/, String(index + 1));
    const remove = item.querySelector('[data-remove]');
    if (remove) remove.textContent = remove.textContent.replace(/\d+$/, String(index + 1));
    const row = item.querySelector('[data-remove-row]');
    if (row) row.hidden = list.length === 1;
  });
}

function clearGroup(group) {
  items(group).forEach((item) => item.remove());
  counters[group] = 0;
}

// Reading and writing the whole form

function readAnswers() {
  const answers = emptyAnswers();
  Object.assign(answers, {
    name: value('name'), summary: value('summary'), purpose: value('purpose'), asset_type: value('type'),
    status: value('status'), service_url: value('svcurl'), service_page_url: value('svcpage'),
    deprecation_date: value('depdate'), migration_guidance: value('mig'), support: value('support'),
    owner: value('owner'), sector: value('sector'), contact: value('contact'), own: radio('own'),
    withdrawal_date: value('wddate'), withdrawal_reason: value('wdreason'),
    service_areas: checked('service_areas'), capabilities: checked('capabilities'),
    intended_adopters: checked('intended_adopters'), terms_type: value('terms'), terms_ref: value('licence'),
    adoption: value('adopt'), charges: radio('ch'), charging_model: value('chmodel'), charging_detail: value('chdetail'),
  });
  for (const [group, repeater] of Object.entries(REPEATERS)) {
    answers[group] = items(group).map((item) => repeater.read(item.dataset.n));
  }
  return answers;
}

function writeAnswers(answers) {
  set('name', answers.name); set('summary', answers.summary); set('purpose', answers.purpose);
  set('type', answers.asset_type); set('status', answers.status); set('svcurl', answers.service_url);
  set('svcpage', answers.service_page_url); set('depdate', answers.deprecation_date);
  set('mig', answers.migration_guidance); set('support', answers.support); set('owner', answers.owner);
  set('sector', answers.sector); set('contact', answers.contact); setRadio('own', answers.own);
  set('wddate', answers.withdrawal_date); set('wdreason', answers.withdrawal_reason);
  setChecked('service_areas', answers.service_areas); setChecked('capabilities', answers.capabilities);
  setChecked('intended_adopters', answers.intended_adopters); set('terms', answers.terms_type);
  set('licence', answers.terms_ref); set('adopt', answers.adoption); setRadio('ch', answers.charges);
  set('chmodel', answers.charging_model); set('chdetail', answers.charging_detail);
  for (const [group, repeater] of Object.entries(REPEATERS)) {
    clearGroup(group);
    const list = answers[group].length ? answers[group] : [];
    list.forEach((entry) => repeater.write(addItem(group), entry));
    if (!list.length) addItem(group);
  }
  form.querySelectorAll('textarea').forEach((area) => area.dispatchEvent(new Event('input')));
}

// Conditional sections and the preview

function update() {
  const answers = readAnswers();
  const show = sections(answers, base);
  document.querySelectorAll('[data-section]').forEach((section) => {
    section.hidden = !show[section.dataset.section];
  });
  document.querySelectorAll('[data-show-when="unstated"]').forEach((element) => {
    element.hidden = !show.unstated;
    if (element.tagName === 'OPTION') element.disabled = !show.unstated;
  });
  const record = buildRecord(answers, { base, order: config.order, today: today(), schemaVersion: config.schema_version });
  let yaml = dump(record, { lineWidth: 80, noRefs: true });
  if (record.id === 'csr-NNNN') yaml = yaml.replace(/^id: csr-NNNN$/m, 'id: csr-NNNN  # allocated when registered');
  preview.textContent = yaml;
  return { answers, record, yaml };
}

function reset() {
  base = {};
  form.reset();
  document.getElementById('draft-loaded').hidden = true;
  writeAnswers(emptyAnswers());
  update();
}

async function loadFrom(id) {
  if (!/^csr-\d{4}$/.test(id)) return;
  try {
    const response = await fetch(`../api/v0/assets/${id}.json`);
    if (!response.ok) return;
    base = await response.json();
  } catch {
    return;
  }
  writeAnswers(answersFromRecord(base));
  const link = document.getElementById('draft-loaded-link');
  link.textContent = `${base.name} (${id})`;
  link.href = `../assets/${id}/`;
  document.getElementById('draft-loaded').hidden = false;
  update();
}

if (form) {
  form.addEventListener('input', update);
  form.addEventListener('change', update);
  form.addEventListener('submit', (event) => { event.preventDefault(); update(); });
  form.addEventListener('click', (event) => {
    const add = event.target.closest('[data-add]');
    if (add) { addItem(add.dataset.add, { focus: true }); update(); return; }
    const remove = event.target.closest('[data-remove]');
    if (remove) {
      const item = remove.closest('[data-item]');
      const group = item.dataset.item;
      const index = items(group).indexOf(item);
      item.remove();
      renumber(group);
      const next = items(group)[Math.min(index, items(group).length - 1)];
      next?.querySelector('input, select, textarea')?.focus();
      update();
    }
  });
  document.getElementById('draft-reset').addEventListener('click', reset);
  writeAnswers(emptyAnswers());
  update();
  const from = new URLSearchParams(window.location.search).get('from');
  if (from) loadFrom(from);
}

export { update, readAnswers, writeAnswers };
