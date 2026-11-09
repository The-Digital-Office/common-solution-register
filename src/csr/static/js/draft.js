// The draft form page (specification 6.6, 6.9 and 6.13): repeating groups,
// conditional sections, a live solution.yml preview, validation against the
// schema with an error summary and inline errors, and the hand-off: copy,
// download, GitHub issue and email.
import { dump } from '../vendor/js-yaml/5.5.0/js-yaml.mjs';
import { answersFromRecord, buildDraft, emptyAnswers, sections } from './draft-core.js';
import { check, compile } from './record-check.js';

const form = document.getElementById('draft-form');
const config = JSON.parse(document.getElementById('csr-draft-config').textContent);
const preview = document.getElementById('draft-yaml');
const AjvClass = window.ajv2020 && (window.ajv2020.default || window.ajv2020);
const validator = AjvClass ? compile(AjvClass, config.schema) : null;
const ISSUE_URL_LIMIT = 8000; // GitHub's address length limit is about 8 KB (specification 6.6)
let base = {};
let current = { record: {}, rows: {}, yaml: '' };

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
  const { record, rows } = buildDraft(answers, { base, order: config.order, today: today(), schemaVersion: config.schema_version });
  let yaml = dump(record, { lineWidth: 80, noRefs: true });
  if (record.id === 'csr-NNNN') yaml = yaml.replace(/^id: csr-NNNN$/m, 'id: csr-NNNN  # allocated when registered');
  preview.textContent = yaml;
  current = { answers, record, rows, yaml };
  updateIssueLink();
  return current;
}

// Validation: the error summary and inline errors (design system pattern)

const FIELDS = {
  name: 'name', summary: 'summary', purpose: 'purpose', asset_type: 'type', status: 'status',
  service_url: 'svcurl', service_page_url: 'svcpage', documentation_url: null, support: 'support',
  'support.summary': 'support', deprecation: 'depdate', 'deprecation.date': 'depdate', 'deprecation.migration_guidance': 'mig',
  owner: 'owner', 'owner.organisation': 'owner', 'owner.sector': 'sector', contact: 'contact', 'contact.value': 'contact',
  'contact.type': 'contact', record_status: 'own-yes', confirmation: 'own-yes', 'confirmation.last_confirmed': 'own-yes',
  withdrawal: 'wddate', 'withdrawal.date': 'wddate', 'withdrawal.reason': 'wdreason',
  service_areas: () => firstOf('service_areas'), capabilities: () => firstOf('capabilities'),
  intended_adopters: () => firstOf('intended_adopters'),
  terms_of_use: 'licence', 'terms_of_use.type': 'terms', 'terms_of_use.licence': 'licence', 'terms_of_use.url': 'licence',
  adoption_route: 'adopt', 'adoption_route.summary': 'adopt', charging: 'chdetail', 'charging.applies': 'ch-yes',
  'charging.model': 'chmodel', 'charging.url': 'chdetail', 'charging.summary': 'chdetail',
  sources: () => firstIn('sources', 'srcurl'), interfaces: () => firstIn('interfaces', 'idoc'),
  codebases: () => firstIn('codebases', 'repo'), open_data: () => firstIn('open_data', 'odtitle'),
};
const ITEM_FIELDS = {
  interfaces: { type: 'itype', documentation_url: 'idoc' },
  sources: { url: 'srcurl', title: 'srctitle', publisher: 'srcpub', accessed: 'srcdate' },
  codebases: { repository_url: 'repo', visibility: 'vis', publiccode_url: 'pc', maintenance: 'maint' },
  open_data: { title: 'odtitle', url: 'odurl' },
};

function firstOf(name) {
  return form.querySelector(`input[name="${name}"]`)?.id;
}
function firstIn(group, prefix) {
  const item = items(group)[0];
  return item ? `${prefix}-${item.dataset.n}` : null;
}

/** The id of the control a problem belongs to, or null if the form does not show that field. */
function controlFor(path) {
  const item = path.match(/^(\w+)\[(\d+)\]\.?(\w*)/);
  if (item && ITEM_FIELDS[item[1]]) {
    const [, group, index, field] = item;
    const position = (current.rows[group] || [])[Number(index)];
    const element = items(group)[position];
    if (!element) return null;
    const prefix = ITEM_FIELDS[group][field] || Object.values(ITEM_FIELDS[group])[0];
    return prefix === 'vis' ? `vis-${element.dataset.n}-public` : `${prefix}-${element.dataset.n}`;
  }
  const target = FIELDS[path];
  return typeof target === 'function' ? target() : target || null;
}

function clearErrors() {
  form.querySelectorAll('.ds_question__error-message[data-generated]').forEach((p) => p.remove());
  form.querySelectorAll('.ds_question--error').forEach((q) => q.classList.remove('ds_question--error'));
  form.querySelectorAll('.ds_input--error').forEach((i) => i.classList.remove('ds_input--error'));
  form.querySelectorAll('[data-error-described]').forEach((i) => {
    const ids = (i.getAttribute('aria-describedby') || '').split(' ').filter((id) => !id.endsWith('-error'));
    if (ids.length) i.setAttribute('aria-describedby', ids.join(' ')); else i.removeAttribute('aria-describedby');
    i.removeAttribute('data-error-described');
  });
  document.getElementById('error-summary').hidden = true;
}

function showErrors(problems) {
  clearErrors();
  const summary = document.getElementById('error-summary');
  const list = document.getElementById('error-summary-list');
  list.replaceChildren();
  const placed = new Set();
  const located = problems.map((problem) => ({ ...problem, id: controlFor(problem.path) }));
  // Follow the order of the form, with fields it does not show last.
  const order = (id) => (id ? [...form.querySelectorAll('[id]')].findIndex((e) => e.id === id) : Infinity);
  located.sort((a, b) => order(a.id) - order(b.id));
  for (const problem of located) {
    const li = document.createElement('li');
    if (problem.id) {
      const a = document.createElement('a');
      a.href = `#${problem.id}`;
      a.textContent = problem.message;
      a.addEventListener('click', (event) => {
        event.preventDefault();
        const control = document.getElementById(problem.id);
        control.closest('.ds_question')?.scrollIntoView({ block: 'start' });
        control.focus({ preventScroll: true });
      });
      li.append(a);
      const control = document.getElementById(problem.id);
      const question = control.closest('fieldset.ds_question') && control.type && ['radio', 'checkbox'].includes(control.type)
        ? control.closest('fieldset.ds_question') : control.closest('.ds_question');
      if (question && !placed.has(question)) {
        placed.add(question);
        question.classList.add('ds_question--error');
        const message = document.createElement('p');
        message.className = 'ds_question__error-message';
        message.id = `${problem.id}-error`;
        message.dataset.generated = '';
        message.textContent = problem.message;
        // Immediately before the control (or its wrapper or group), as the design system places it.
        const anchor = control.closest('.ds_select-wrapper, .ds_field-group, .ds_input__wrapper') || control;
        anchor.before(message);
        if (['INPUT', 'TEXTAREA', 'SELECT'].includes(control.tagName) && !['radio', 'checkbox'].includes(control.type)) {
          control.classList.add('ds_input--error');
        }
        const described = control.getAttribute('aria-describedby');
        control.setAttribute('aria-describedby', [described, message.id].filter(Boolean).join(' '));
        control.dataset.errorDescribed = '';
      }
    } else {
      li.textContent = `${problem.path}: ${problem.message}`;
    }
    list.append(li);
  }
  summary.hidden = false;
  summary.focus();
}

/** Check the draft; show the problems or the "valid" panel. Returns true if valid. */
function validateDraft({ announceValid = true } = {}) {
  update();
  if (!validator) return true; // the validator could not load: let people continue
  const problems = check(validator, current.record, { today: today() });
  if (correcting() && !current.answers.own) {
    // Decides whether the correction confirms the record (the owner) or suggests a change to it (anyone else).
    problems.unshift({ path: 'record_status', message: 'Select whether you are from the owning organisation' });
  }
  if (problems.length) {
    showErrors(problems);
    return false;
  }
  clearErrors();
  if (announceValid) {
    const valid = document.getElementById('draft-valid');
    const title = document.getElementById('draft-valid-title');
    title.textContent = correcting() ? title.dataset.correction : title.dataset.new;
    document.getElementById('draft-valid-hosted').hidden = !(correcting() && base.hosting === 'owner-hosted');
    valid.hidden = false;
    valid.scrollIntoView({ block: 'start' });
    valid.focus({ preventScroll: true });
  }
  return true;
}

// The hand-off (specification 6.6)

const statusMessage = (text) => { document.getElementById('draft-handoff-status').textContent = text; };

/** True when the form was filled in from a record, so what is sent is a correction to it. */
const correcting = () => Boolean(base.id);

function issueUrl(withYaml) {
  const r = current.record;
  if (correcting()) {
    const params = new URLSearchParams({ template: 'suggest-correction.yml', title: `Correction: ${r.name || base.name} (${base.id})` });
    params.set('record-id', base.id);
    params.set('what-is-wrong', withYaml
      ? `The corrected solution.yml, from the draft form:\n\n\`\`\`yaml\n${current.yaml}\`\`\`\n`
      : 'The corrected solution.yml, from the draft form, is attached.');
    return `${config.repository}/issues/new?${params}`;
  }
  const params = new URLSearchParams({ template: 'suggest-asset.yml', title: `Suggest a solution: ${r.name || 'untitled'}` });
  params.set('asset-name', r.name || '');
  params.set('organisation', r.owner?.organisation || '');
  params.set('contact', r.contact?.value || '');
  if (withYaml) params.set('solution-yml', current.yaml);
  return `${config.repository}/issues/new?${params}`;
}

function updateIssueLink() {
  const full = issueUrl(true);
  const tooLong = full.length > ISSUE_URL_LIMIT;
  for (const link of document.querySelectorAll('[data-handoff="issue"]')) {
    link.href = tooLong ? issueUrl(false) : full;
    link.dataset.tooLong = tooLong ? 'true' : '';
  }
}

function download() {
  const blob = new Blob([current.yaml], { type: 'application/yaml' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'solution.yml';
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

async function copy() {
  try {
    await navigator.clipboard.writeText(current.yaml);
    statusMessage('Copied. Paste it into a GitHub issue, an email, or your own solution.yml file.');
  } catch {
    const range = document.createRange();
    range.selectNodeContents(preview);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);
    statusMessage('Your browser did not allow copying. The YAML is selected: copy it with Ctrl+C, or Cmd+C on a Mac.');
  }
}

/** Copy, download, GitHub issue and email, from the sidebar or from the "valid" panel. */
function wireHandOff() {
  document.addEventListener('click', (event) => {
    const control = event.target.closest('[data-handoff]');
    if (!control) return;
    const action = control.dataset.handoff;
    // The panel's options appear only once the draft is valid; check again in case it has changed since.
    if (!validateDraft({ announceValid: false })) { event.preventDefault(); return; }
    if (action === 'copy') copy();
    if (action === 'download') { download(); statusMessage('Downloaded solution.yml.'); }
    if (action === 'issue' && control.dataset.tooLong) {
      download();
      statusMessage('Your solution.yml is too long to include in the issue, so it has been downloaded. Attach it to the issue.');
    }
    if (action === 'email') {
      download();
      const name = current.record.name || 'a solution';
      const subject = correcting() ? `Correction to ${base.id}: ${name}` : `${config.title}: ${name}`;
      const body = (correcting() ? `Please find my corrected solution.yml for ${base.id} attached.` : 'Please find my solution.yml attached.')
        + '\nI have downloaded it from the draft form; please attach the downloaded file before sending.';
      control.href = `mailto:${config.mailbox}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      statusMessage('Downloaded solution.yml. Attach it to the email that opens.');
    }
  });
}

function reset() {
  base = {};
  form.reset();
  document.getElementById('draft-loaded').hidden = true;
  writeAnswers(emptyAnswers());
  changed();
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
  // A correction is discarded by going back to the record, not by starting a new, blank draft.
  const discard = document.getElementById('draft-discard');
  discard.href = `../assets/${id}/`;
  discard.hidden = false;
  document.getElementById('draft-reset').hidden = true;
  changed();
}

/** The answers changed: the "valid" panel no longer describes them. */
function changed() {
  document.getElementById('draft-valid').hidden = true;
  update();
}

if (form) {
  form.addEventListener('input', changed);
  form.addEventListener('change', changed);
  form.addEventListener('submit', (event) => { event.preventDefault(); validateDraft(); });
  form.addEventListener('click', (event) => {
    const add = event.target.closest('[data-add]');
    if (add) { addItem(add.dataset.add, { focus: true }); changed(); return; }
    const remove = event.target.closest('[data-remove]');
    if (remove) {
      const item = remove.closest('[data-item]');
      const group = item.dataset.item;
      const index = items(group).indexOf(item);
      item.remove();
      renumber(group);
      const next = items(group)[Math.min(index, items(group).length - 1)];
      next?.querySelector('input, select, textarea')?.focus();
      changed();
    }
  });
  document.getElementById('draft-reset').addEventListener('click', () => { clearErrors(); reset(); });
  wireHandOff();
  writeAnswers(emptyAnswers());
  update();
  const from = new URLSearchParams(window.location.search).get('from');
  if (from) loadFrom(from);
}

export { update, readAnswers, writeAnswers, validateDraft };
