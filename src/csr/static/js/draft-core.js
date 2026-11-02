// The draft form's logic (specification 6.2 and 6.6): turn the form's answers
// into a solution.yml record, decide which conditional sections show, and
// turn a record back into answers for "Suggest a correction". Pure functions
// with no DOM access (tests/js/draft-core.test.mjs).

export const SENTINEL = 'not-publicly-stated';

/** Fields the form writes. Others in a record being corrected are kept as they were. */
const FORM_FIELDS = [
  'record_status', 'name', 'summary', 'purpose', 'asset_type', 'owner', 'contact', 'service_areas', 'capabilities',
  'status', 'intended_adopters', 'terms_of_use', 'adoption_route', 'charging', 'support', 'service_url',
  'service_page_url', 'sources', 'confirmation', 'withdrawal', 'deprecation', 'interfaces', 'codebases', 'open_data',
];

/** Answers for an empty form. */
export function emptyAnswers() {
  return {
    name: '', summary: '', purpose: '', asset_type: 'service', status: 'live', service_url: '', service_page_url: '',
    interfaces: [], deprecation_date: '', migration_guidance: '', support: '',
    owner: '', sector: 'local-government', contact: '', own: '', sources: [],
    withdrawal_date: '', withdrawal_reason: '',
    service_areas: [], capabilities: [], intended_adopters: [],
    terms_type: 'open-licence', terms_ref: '', adoption: '', charges: 'no', charging_model: 'recharge',
    charging_detail: '', codebases: [], open_data: [],
  };
}

const trim = (value) => String(value ?? '').trim();
const isUrl = (value) => /^https?:\/\//i.test(value);

/** "31/03/2026" or "2026-03-31" to "2026-03-31"; anything else is returned as typed, for validation to report. */
export function isoDate(value) {
  const text = trim(value);
  const uk = text.match(/^(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})$/);
  if (uk) return `${uk[3]}-${uk[2].padStart(2, '0')}-${uk[1].padStart(2, '0')}`;
  return text;
}

/** "2026-03-31" to "31/03/2026", for showing a stored date in the form. */
export function ukDate(value) {
  const iso = trim(value).match(/^(\d{4})-(\d{2})-(\d{2})$/);
  return iso ? `${iso[3]}/${iso[2]}/${iso[1]}` : trim(value);
}

/** The contact type a value implies: an email address, a web form, or a service desk. */
export function contactType(value) {
  const text = trim(value);
  if (/^[^@\s]+@[^@\s]+$/.test(text)) return 'role-mailbox';
  if (isUrl(text)) return 'web-form';
  return 'service-desk';
}

/** Which conditional sections show (specification 6.4, conditions 1 to 8). */
export function sections(answers, base = {}) {
  const serviceLike = ['service', 'platform'].includes(answers.asset_type);
  const inUse = ['beta', 'live'].includes(answers.status);
  return {
    unstated: answers.own === 'no', // condition 1: the sentinel is allowed
    sources: answers.own === 'no', // condition 1
    withdrawal: base.record_status === 'withdrawn', // condition 3: only when correcting a withdrawn record
    software: answers.asset_type === 'software', // condition 4
    interfaces: answers.asset_type === 'api' || (base.interfaces || []).length > 0, // condition 5
    charging: answers.charges === 'yes', // condition 6
    support: serviceLike && inUse, // condition 7
    deprecation: answers.status === 'deprecated', // condition 8
  };
}

function compact(object) {
  const result = {};
  for (const [key, value] of Object.entries(object)) {
    if (value === undefined || value === '' || (Array.isArray(value) && value.length === 0)) continue;
    if (value && typeof value === 'object' && !Array.isArray(value) && Object.keys(compact(value)).length === 0) continue;
    result[key] = value;
  }
  return result;
}

const orSentinel = (value, show) => (trim(value) ? trim(value) : show.unstated ? SENTINEL : '');

/**
 * Build the record. `base` is the record being corrected, if any; `order` is
 * the schema's field order; `today` is an ISO date.
 */
export function buildRecord(answers, options = {}) {
  return buildDraft(answers, options).record;
}

/**
 * Build the record, and say which group in the form each list entry came
 * from: rows.codebases[0] is the position, among the form's codebase
 * groups, of the record's first codebase (empty groups are left out).
 */
export function buildDraft(answers, { base = {}, order = [], today = '', schemaVersion = '0.1' } = {}) {
  const show = sections(answers, base);
  const record = {};
  const rows = {};
  const keep = (group, list, filled) => {
    const kept = list.map((item, index) => [item, index]).filter(([item]) => filled(item));
    rows[group] = kept.map(([, index]) => index);
    return kept.map(([item]) => item);
  };
  const ownerConfirmed = answers.own === 'yes';
  const recordStatus = show.withdrawal ? 'withdrawn' : answers.own === 'yes' ? 'owner-confirmed'
    : answers.own === 'no' ? 'demonstration' : base.record_status;

  record.schema_version = schemaVersion;
  record.id = base.id || 'csr-NNNN';
  record.record_status = recordStatus;
  record.name = trim(answers.name);
  record.summary = trim(answers.summary);
  record.purpose = trim(answers.purpose);
  record.asset_type = answers.asset_type;
  record.owner = compact({ organisation: trim(answers.owner), sector: answers.sector });
  record.contact = trim(answers.contact) ? { type: contactType(answers.contact), value: trim(answers.contact) } : undefined;
  record.service_areas = [...answers.service_areas];
  record.capabilities = [...answers.capabilities];
  record.status = answers.status;
  record.intended_adopters = [...answers.intended_adopters];

  const termsRef = trim(answers.terms_ref);
  record.terms_of_use = answers.terms_type === SENTINEL
    ? { type: SENTINEL }
    : compact({ ...(base.terms_of_use || {}), type: answers.terms_type,
      licence: termsRef && !isUrl(termsRef) ? termsRef : undefined, url: isUrl(termsRef) ? termsRef : undefined });
  record.adoption_route = compact({ ...(base.adoption_route || {}), summary: orSentinel(answers.adoption, show) });

  const detail = trim(answers.charging_detail);
  if (answers.charges === 'yes') {
    record.charging = compact({ applies: true, model: answers.charging_model,
      url: isUrl(detail) ? detail : undefined, summary: detail && !isUrl(detail) ? detail : undefined });
  } else if (answers.charges === 'no') {
    record.charging = { applies: false };
  } else if (answers.charges === 'unstated' && show.unstated) {
    record.charging = { applies: SENTINEL };
  }

  if (show.support) record.support = compact({ ...(base.support || {}), summary: orSentinel(answers.support, show) });
  record.service_url = orSentinel(answers.service_url, { unstated: show.unstated && show.support });
  record.service_page_url = orSentinel(answers.service_page_url, { unstated: show.unstated && show.support });

  if (show.sources) {
    record.sources = keep('sources', answers.sources.map((s) => compact({
      url: trim(s.url), title: trim(s.title), publisher: trim(s.publisher), accessed: isoDate(s.accessed) || today,
    })), (s) => s.url || s.title);
  }
  if (ownerConfirmed) {
    record.confirmation = { last_confirmed: today, method: 'draft form', reference: 'Submitted with the draft form' };
  } else if (recordStatus === base.record_status && base.confirmation) {
    record.confirmation = base.confirmation;
  }
  if (show.withdrawal) {
    record.withdrawal = compact({ date: isoDate(answers.withdrawal_date), reason: trim(answers.withdrawal_reason) });
  }
  if (show.deprecation) {
    record.deprecation = compact({ date: isoDate(answers.deprecation_date), migration_guidance: trim(answers.migration_guidance) });
  }
  if (show.interfaces) {
    record.interfaces = keep('interfaces', answers.interfaces.map((i, n) => compact({
      ...((base.interfaces || [])[n] || {}), type: i.type, documentation_url: trim(i.documentation_url),
    })), (i) => i.documentation_url);
  }
  record.codebases = keep('codebases', answers.codebases.map((c, n) => compact({
    ...((base.codebases || [])[n] || {}), repository_url: trim(c.repository_url), visibility: c.visibility,
    publiccode_url: trim(c.publiccode_url), maintenance: c.maintenance,
  })), (c) => c.repository_url || c.publiccode_url || c.visibility);
  record.open_data = keep('open_data', answers.open_data.map((d, n) => compact({
    ...((base.open_data || [])[n] || {}), title: trim(d.title), url: trim(d.url),
  })), (d) => d.title || d.url);

  // Fields the form does not show are kept from the record being corrected.
  for (const [key, value] of Object.entries(base)) {
    if (!FORM_FIELDS.includes(key) && !(key in record) && !DERIVED.includes(key)) record[key] = value;
  }
  return { record: ordered(compact(record), order), rows };
}

/** Fields the register adds when publishing, which are never part of a solution.yml. */
const DERIVED = ['last_changed', 'history_url', 'merged_in', 'currency', 'hosting', 'source', 'harvested_at',
  'content_hash', 'source_state', 'record_url'];

function ordered(record, order) {
  const result = {};
  for (const key of order) if (key in record) result[key] = record[key];
  for (const key of Object.keys(record)) if (!(key in result)) result[key] = record[key];
  return result;
}

/** Answers that reproduce a record, for "Suggest a correction". */
export function answersFromRecord(record) {
  const a = emptyAnswers();
  const pick = (value) => (value === SENTINEL ? '' : value ?? '');
  a.name = record.name || '';
  a.summary = record.summary || '';
  a.purpose = record.purpose || '';
  a.asset_type = record.asset_type || a.asset_type;
  a.status = record.status || a.status;
  a.service_url = pick(record.service_url);
  a.service_page_url = pick(record.service_page_url);
  a.interfaces = (record.interfaces || []).map((i) => ({ type: i.type, documentation_url: i.documentation_url || '' }));
  a.deprecation_date = ukDate(record.deprecation?.date);
  a.migration_guidance = record.deprecation?.migration_guidance || '';
  a.support = pick(record.support?.summary);
  a.owner = record.owner?.organisation || '';
  a.sector = record.owner?.sector || a.sector;
  a.contact = record.contact?.value || '';
  // Left unanswered unless the record is a demonstration entry: whoever corrects
  // a record says for themselves whether they are from the owning organisation.
  a.own = record.record_status === 'demonstration' ? 'no' : '';
  a.sources = (record.sources || []).map((s) => ({ url: s.url || '', title: s.title || '', publisher: s.publisher || '',
    accessed: ukDate(s.accessed) }));
  a.withdrawal_date = ukDate(record.withdrawal?.date);
  a.withdrawal_reason = record.withdrawal?.reason || '';
  a.service_areas = [...(record.service_areas || [])];
  a.capabilities = [...(record.capabilities || [])];
  a.intended_adopters = [...(record.intended_adopters || [])];
  a.terms_type = record.terms_of_use?.type || a.terms_type;
  a.terms_ref = record.terms_of_use?.licence || record.terms_of_use?.url || '';
  a.adoption = pick(record.adoption_route?.summary);
  const applies = record.charging?.applies;
  a.charges = applies === true ? 'yes' : applies === false ? 'no' : applies === SENTINEL ? 'unstated' : '';
  a.charging_model = record.charging?.model || a.charging_model;
  a.charging_detail = record.charging?.summary || record.charging?.url || '';
  a.codebases = (record.codebases || []).map((c) => ({ repository_url: c.repository_url || '',
    visibility: c.visibility || '', publiccode_url: c.publiccode_url || '', maintenance: c.maintenance || 'internal' }));
  a.open_data = (record.open_data || []).map((d) => ({ title: d.title || '', url: d.url || '' }));
  return a;
}
