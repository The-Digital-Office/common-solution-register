// Checks a record against the schema with Ajv, plus the rules that need no
// network (appendix C: R06, R09), and words each problem for people.
// Pure functions: Ajv's constructor is passed in (tests/js/record-check.test.mjs).

export const SENTINEL = 'not-publicly-stated';

/** Field names, as people read them, keyed by schema path ("[]" stands for any list position). */
const LABELS = {
  schema_version: 'Schema version', id: 'Record ID', record_status: 'Whether you are from the owning organisation',
  name: 'Name', summary: 'Summary', purpose: 'Purpose', asset_type: 'Asset type', status: 'Status',
  'owner.organisation': 'Owning organisation', 'owner.sector': 'Owning sector', contact: 'Contact',
  'contact.value': 'Contact', 'contact.type': 'Contact type', service_areas: 'Service areas', capabilities: 'Capabilities',
  intended_adopters: 'Intended for', 'terms_of_use.type': 'Terms of use', 'terms_of_use.licence': 'Licence',
  'terms_of_use.url': 'Terms URL', 'adoption_route.summary': 'How another organisation can adopt it',
  'charging.applies': 'Charges', 'charging.model': 'Charging model', 'charging.url': 'Charging details URL',
  'charging.summary': 'Charging details', 'support.summary': 'Support arrangements', service_url: 'Service address',
  service_page_url: 'Your page describing the service', documentation_url: 'Documentation address',
  'sources[].url': 'Address of the public page', 'sources[].title': 'Title of the page',
  'sources[].accessed': 'Date you read it', 'deprecation.date': 'Deprecation date',
  'deprecation.migration_guidance': 'Migration guidance', 'withdrawal.date': 'Withdrawal date',
  'withdrawal.reason': 'Reason for withdrawal', 'interfaces[].type': 'Interface type',
  'interfaces[].documentation_url': 'Interface documentation URL', 'codebases[].repository_url': 'Repository URL',
  'codebases[].visibility': 'Visibility', 'codebases[].publiccode_url': 'publiccode.yml URL',
  'codebases[].maintenance': 'Maintenance', 'open_data[].title': 'Data link title',
  'open_data[].url': 'Catalogue URL', 'confirmation.last_confirmed': 'Date last confirmed',
};

/** What to say when something required is missing. */
const MISSING = {
  schema_version: 'Add schema_version: "0.1"', id: 'Add the record id (csr- followed by four digits)',
  asset_type: 'Choose the asset type', status: 'Choose the status', owner: 'Enter the owning organisation and sector',
  'owner.sector': 'Choose the owning sector', 'contact.type': 'Say whether the contact is a role mailbox, service desk or web form',
  'contact.value': 'Enter a contact', confirmation: "Add the owner's confirmation: the date, how and where it was given",
  'confirmation.last_confirmed': 'Enter the date the owner last confirmed the record',
  'confirmation.method': 'Say how the owner confirmed the record', 'confirmation.reference': 'Say where the confirmation can be found',
  'terms_of_use.type': 'Choose the terms of use', 'charging.applies': 'Say whether there are charges for adopters',
  'interfaces[].type': 'Choose the interface type', 'codebases[].maintenance': 'Choose how the codebase is maintained',
  record_status: 'Say whether you are from the owning organisation',
  name: "Enter the solution's name", summary: 'Enter a summary', purpose: 'Enter the purpose',
  'owner.organisation': 'Enter the owning organisation', contact: 'Enter a contact',
  service_areas: 'Choose at least one service area', capabilities: 'Choose at least one capability',
  intended_adopters: 'Choose who it is intended for',
  adoption_route: 'Say how another organisation can adopt it',
  'adoption_route.summary': 'Say how another organisation can adopt it',
  charging: 'Say whether there are charges for adopters', 'charging.model': 'Choose a charging model',
  support: 'Describe the support arrangements', 'support.summary': 'Describe the support arrangements',
  service_url: 'Enter the service address', service_page_url: 'Enter the address of your page describing the service',
  sources: 'Add at least one public source', 'sources[].url': 'Enter the address of the public page',
  'sources[].title': 'Enter the title of the page', 'sources[].accessed': 'Enter the date you read it',
  deprecation: 'Enter the deprecation date and migration guidance', 'deprecation.date': 'Enter the deprecation date',
  'deprecation.migration_guidance': 'Enter the migration guidance',
  withdrawal: 'Enter the withdrawal date and reason', 'withdrawal.date': 'Enter the withdrawal date',
  'withdrawal.reason': 'Enter the reason for withdrawal',
  interfaces: "Add the interface's documentation URL", 'interfaces[].documentation_url': "Enter the interface's documentation URL",
  codebases: 'Add at least one codebase: software must list one', 'codebases[].repository_url': 'Enter the repository URL',
  'codebases[].visibility': 'Choose whether the codebase is public or private',
  'open_data[].title': 'Enter a title for the data link', 'open_data[].url': 'Enter the catalogue URL',
  terms_of_use: 'Choose the terms of use',
};

/** Objects whose "one of these" choice fails as a whole. */
const EITHER = {
  terms_of_use: 'Enter a licence (SPDX identifier, for example MIT) or the address of the terms',
  charging: 'Enter the charging details or their address',
};

const DATE = /^(\d{4})-(\d{2})-(\d{2})$/;

/** A real calendar date in YYYY-MM-DD form. */
export function isDate(value) {
  const match = DATE.exec(value);
  if (!match) return false;
  const date = new Date(Date.UTC(+match[1], +match[2] - 1, +match[3]));
  return date.getUTCFullYear() === +match[1] && date.getUTCMonth() === +match[2] - 1 && date.getUTCDate() === +match[3];
}

/** An Ajv validator for a schema, with the formats it uses. */
export function compile(Ajv, schema) {
  const ajv = new Ajv({ allErrors: true, strict: false });
  ajv.addFormat('date', isDate);
  ajv.addFormat('email', /^[^@\s]+@[^@\s]+\.[^@\s]+$/);
  ajv.addFormat('uri', /^[a-z][a-z0-9+.-]*:\S+$/i);
  return ajv.compile(schema);
}

/** "/codebases/0/repository_url" to "codebases[0].repository_url". */
export function dotted(pointer) {
  return pointer.split('/').slice(1).map((part) => part.replace(/~1/g, '/').replace(/~0/g, '~'))
    .reduce((path, part) => (/^\d+$/.test(part) ? `${path}[${part}]` : path ? `${path}.${part}` : part), '');
}

/** "codebases[0].repository_url" to "codebases[].repository_url". */
const generic = (path) => path.replace(/\[\d+\]/g, '[]');
const label = (path) => LABELS[generic(path)] || generic(path);

function message(error, path) {
  const name = label(path);
  const p = error.params || {};
  switch (error.keyword) {
    case 'required': return MISSING[generic(path)] || `Enter ${name.toLowerCase()}`;
    case 'minLength': return `${name} must be at least ${p.limit} characters`;
    case 'maxLength': return `${name} must be ${p.limit} characters or fewer`;
    case 'minItems': return MISSING[generic(path)] || `${name}: add at least ${p.limit}`;
    case 'format':
      if (p.format === 'date') return `${name} must be a real date, for example 31/03/2026`;
      if (p.format === 'email') return `${name} must be an email address, a web address starting https://, or a phone number`;
      return `${name} must be a full web address starting https://`;
    case 'pattern':
      if (p.pattern?.startsWith('^https://')) return `${name} must be a full web address starting https://`;
      if (p.pattern?.startsWith('^[0-9]{4}')) return `${name} must be a date, for example 31/03/2026`;
      if (p.pattern?.includes('@')) return `${name} must be an email address, a web address starting https://, or a phone number`;
      if (p.pattern?.startsWith('^csr-')) return `${name} must be csr- followed by four digits`;
      if (p.pattern?.startsWith('^[A-Za-z0-9.+-]+')) return `${name} must be an SPDX licence identifier, for example MIT or OGL-UK-3.0`;
      return `${name} is not in the right form`;
    case 'enum': return `Choose ${name.toLowerCase()} from the list`;
    case 'const': return `${name} must be ${JSON.stringify(error.params.allowedValue)}`;
    case 'not': return `"Not stated in public sources" can only be used by people who are not from the owning organisation`;
    case 'additionalProperties': return `${name}: "${p.additionalProperty}" is not a field the register uses`;
    case 'type': return `${name} must be ${p.type === 'array' ? 'a list' : p.type === 'object' ? 'a group of fields' : `a ${p.type}`}`;
    case 'uniqueItems': return `${name} lists the same choice twice`;
    default: return `${name} is not valid`;
  }
}

/** What to do about a schema problem, by keyword. */
function fixFor(error, path) {
  switch (error.keyword) {
    case 'required': case 'minItems':
      if (['service_areas', 'capabilities', 'intended_adopters', 'owner.sector'].includes(generic(path))) {
        return 'Choose from the taxonomy (see the field reference).';
      }
      return 'Add it: see the field reference for what it should contain.';
    case 'format': case 'pattern': return 'Correct the value: see the field reference for the format.';
    case 'minLength': case 'maxLength': return 'Change the length of the text.';
    case 'enum': return 'Use one of the values in the field reference.';
    case 'not': return 'Give the actual value: the owner can state it.';
    case 'additionalProperties': return 'Remove the field, or check its spelling against the field reference.';
    default: return 'See the field reference for what is allowed.';
  }
}

/** Which of several errors on one field to show: the most specific. */
const RANK = ['required', 'minItems', 'format', 'pattern', 'minLength', 'maxLength', 'enum', 'type',
  'additionalProperties', 'uniqueItems', 'const', 'not'];

/**
 * Problems with a record: [{ path, message, fix, rule, severity }], one error per field, in the order Ajv
 * finds them, plus any warnings. `today` (YYYY-MM-DD) is used for R06; with `context` (see `rules`), the
 * other rules that need no network are applied too.
 */
export function check(validate, record, { today = '', context = null } = {}) {
  const candidate = record.id === 'csr-NNNN' ? { ...record, id: 'csr-0000' } : record; // allocated when registered
  validate(candidate);
  const byPath = new Map();
  const add = (path, entry) => {
    const current = byPath.get(path);
    if (!current || entry.rank < current.rank) byPath.set(path, entry);
  };
  const either = new Set();
  for (const error of validate.errors || []) {
    const parent = dotted(error.instancePath);
    if (error.keyword === 'anyOf' && EITHER[generic(parent)]) either.add(parent);
  }
  for (const error of validate.errors || []) {
    if (['if', 'anyOf', 'oneOf', 'allOf', 'then', 'else', 'false schema'].includes(error.keyword)) continue;
    const parent = dotted(error.instancePath);
    if (either.has(parent) && error.schemaPath.includes('/anyOf/')) continue;
    if (error.keyword === 'const' && error.params.allowedValue === SENTINEL) continue; // the other branch is reported
    const path = error.keyword === 'required' ? (parent ? `${parent}.${error.params.missingProperty}` : error.params.missingProperty) : parent;
    const rank = RANK.indexOf(error.keyword) < 0 ? RANK.length : RANK.indexOf(error.keyword);
    add(path, { path, message: message(error, path), fix: fixFor(error, path), rule: 'SCHEMA', severity: 'error', rank });
  }
  for (const path of either) {
    add(path, { path, message: EITHER[generic(path)], fix: 'Add one of them.', rule: 'SCHEMA', severity: 'error', rank: -1 });
  }

  // R09: no placeholders. R06: last_confirmed is not in the future.
  const walk = (value, path) => {
    if (typeof value === 'string' && value.trim().startsWith('TODO')) {
      add(path, { path, message: `${label(path)} still starts with TODO`, fix: 'Replace the placeholder with the real value.',
        rule: 'R09', severity: 'error', rank: -2 });
    } else if (Array.isArray(value)) value.forEach((item, i) => walk(item, `${path}[${i}]`));
    else if (value && typeof value === 'object') Object.entries(value).forEach(([k, v]) => walk(v, path ? `${path}.${k}` : k));
  };
  walk(record, '');
  const confirmed = record.confirmation?.last_confirmed;
  if (today && typeof confirmed === 'string' && isDate(confirmed) && confirmed > today) {
    const path = 'confirmation.last_confirmed';
    add(path, { path, message: 'The date last confirmed is in the future',
      fix: 'Give the date the owner actually confirmed the record.', rule: 'R06', severity: 'error', rank: -2 });
  }
  for (const finding of context ? rules(record, context) : []) add(finding.path, { ...finding, rank: finding.severity === 'error' ? -2 : 5 });
  const found = [...byPath.values()].map(({ rank, ...finding }) => finding);
  // Warnings that share a field with an error are still shown.
  for (const finding of context ? rules(record, context) : []) {
    if (finding.severity === 'warning' && !found.some((f) => f.path === finding.path && f.rule === finding.rule)) found.push(finding);
  }
  return found;
}

// The rules in appendix C that need no network, as csr validate applies them
// (src/csr/rules.py). R01 needs the register's files, R08 and R13 to R17 the
// network or the repository, R19 a codebase's publiccode.yml.

/** Local parts of email addresses that name a role, not a person (R07). */
const ROLE_WORDS = new Set(['admin', 'contact', 'contactus', 'customer', 'customers', 'data', 'digital', 'dpo',
  'enquiries', 'enquiry', 'feedback', 'foi', 'hello', 'help', 'helpdesk', 'info', 'information', 'it', 'mail', 'office',
  'platform', 'platforms', 'product', 'products', 'register', 'registry', 'service', 'servicedesk', 'services',
  'solution', 'solutions', 'support', 'team', 'technology', 'web', 'webmaster']);
// firstname.lastname@ or firstname_lastname@; role mailboxes usually use hyphens (digital-services@).
const PERSONAL_EMAIL = /^([a-z]{2,})[._]([a-z]{2,})[0-9]*@/i;
const HTTPS = /^https:\/\/[^\s/$.?#][^\s]*$/;

/**
 * Rule findings for a record. `context` is { taxonomies: { sectors: [{ id, label, status, replaced_by }], ... },
 * knownIds: [ids] or null, today }.
 */
export function rules(record, context) {
  const found = [];
  const finding = (rule, severity, path, text, fix) => found.push({ path, message: text, fix, rule, severity });
  const status = record.record_status;
  const idMatch = /^csr-(\d{4})$/.exec(record.id || '');

  // R02: ID range matches provenance. Withdrawn records may use either range.
  if (idMatch) {
    const n = Number(idMatch[1]);
    if (status === 'example' && (n < 9000 || n > 9999)) {
      finding('R02', 'error', 'id', `${record.id} is an example record outside csr-9000 to csr-9999`,
        'Give fictional example records an id from csr-9000 to csr-9999.');
    } else if (['owner-confirmed', 'demonstration'].includes(status) && (n < 1 || n > 8999)) {
      finding('R02', 'error', 'id', `${record.id} is reserved for fictional examples or is not allowed`,
        'Give real records an id from csr-0001 to csr-8999.');
    }
  }

  // R03 and R04: taxonomy terms exist and are current.
  const refs = [['sectors', 'owner.sector', record.owner?.sector]];
  for (const [field, taxonomy] of [['intended_adopters', 'sectors'], ['service_areas', 'service-areas'], ['capabilities', 'capabilities']]) {
    if (Array.isArray(record[field])) record[field].forEach((v, i) => refs.push([taxonomy, `${field}[${i}]`, v]));
  }
  for (const [taxonomy, path, value] of refs) {
    if (typeof value !== 'string') continue;
    const terms = context.taxonomies[taxonomy] || [];
    const term = terms.find((t) => t.id === value);
    if (!term) {
      finding('R03', 'error', path, `"${value}" is not a term in the ${taxonomy.replace('-', ' ')} taxonomy`,
        'Use a term id from the taxonomy terms in the field reference.');
    } else if (path === 'owner.sector' && term.intended_adopters_only) {
      finding('R03', 'error', path, `"${value}" describes who a solution is for, not who owns it`,
        "Use the owning organisation's own sector; list it under intended_adopters instead.");
    } else if (term.status === 'deprecated') {
      finding('R04', 'warning', path, `"${value}" is a deprecated term`,
        term.replaced_by ? `Use "${term.replaced_by}" instead.` : 'Choose a current term.');
    }
  }

  // R05: related records exist.
  if (context.knownIds && Array.isArray(record.related_assets)) {
    record.related_assets.forEach((item, i) => {
      if (item && typeof item.id === 'string' && !context.knownIds.includes(item.id)) {
        finding('R05', 'error', `related_assets[${i}].id`, `${item.id} is not a record in the register`,
          'Check the id, or remove the related record.');
      }
    });
  }

  // R07: a contact that looks like a named person's address.
  const contact = record.contact?.value;
  const personal = typeof contact === 'string' ? PERSONAL_EMAIL.exec(contact) : null;
  if (personal && !ROLE_WORDS.has(personal[1].toLowerCase()) && !ROLE_WORDS.has(personal[2].toLowerCase())) {
    finding('R07', 'warning', 'contact.value', `"${contact}" looks like a named person's address`,
      'Use a role mailbox, service desk or web form, so the contact survives staff changes.');
  }

  // R11: example names begin "Example:".
  if (status === 'example' && typeof record.name === 'string' && !record.name.startsWith('Example:')) {
    finding('R11', 'error', 'name', 'A fictional example\'s name must begin "Example:"', `Rename it "Example: ${record.name}".`);
  }

  // R12: public codebases link their publiccode.yml.
  (Array.isArray(record.codebases) ? record.codebases : []).forEach((c, i) => {
    if (c && c.visibility === 'public' && !c.publiccode_url) {
      finding('R12', 'warning', `codebases[${i}]`, 'Public codebase has no publiccode_url',
        "Add a publiccode.yml to the codebase's repository and link it.");
    }
  });

  // R18: the addresses an adopter follows are HTTPS.
  const addresses = ['service_url', 'service_page_url', 'documentation_url'].map((f) => [f, record[f]]);
  (Array.isArray(record.codebases) ? record.codebases : []).forEach((c, i) => addresses.push([`codebases[${i}].repository_url`, c?.repository_url]));
  (Array.isArray(record.open_data) ? record.open_data : []).forEach((d, i) => addresses.push([`open_data[${i}].url`, d?.url]));
  for (const [path, value] of addresses) {
    if (value === undefined || value === null || value === SENTINEL) continue; // the sentinel is R10's concern
    if (!(typeof value === 'string' && HTTPS.test(value))) {
      finding('R18', 'error', path, `"${value}" is not an HTTPS URL`, 'Use a full address starting https://.');
    }
  }
  return found;
}
