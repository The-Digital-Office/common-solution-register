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

/** Which of several errors on one field to show: the most specific. */
const RANK = ['required', 'minItems', 'format', 'pattern', 'minLength', 'maxLength', 'enum', 'type',
  'additionalProperties', 'uniqueItems', 'const', 'not'];

/**
 * Problems with a record: [{ path, message, rule }], one per field, in the order Ajv finds them.
 * `today` (YYYY-MM-DD) is used for R06.
 */
export function check(validate, record, { today = '' } = {}) {
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
    add(path, { path, message: message(error, path), rule: 'SCHEMA', rank });
  }
  for (const path of either) add(path, { path, message: EITHER[generic(path)], rule: 'SCHEMA', rank: -1 });

  // R09: no placeholders. R06: last_confirmed is not in the future.
  const walk = (value, path) => {
    if (typeof value === 'string' && value.trim().startsWith('TODO')) {
      add(path, { path, message: `${label(path)} still starts with TODO: replace it with the real value`, rule: 'R09', rank: -2 });
    } else if (Array.isArray(value)) value.forEach((item, i) => walk(item, `${path}[${i}]`));
    else if (value && typeof value === 'object') Object.entries(value).forEach(([k, v]) => walk(v, path ? `${path}.${k}` : k));
  };
  walk(record, '');
  const confirmed = record.confirmation?.last_confirmed;
  if (today && typeof confirmed === 'string' && isDate(confirmed) && confirmed > today) {
    const path = 'confirmation.last_confirmed';
    add(path, { path, message: 'The date last confirmed is in the future', rule: 'R06', rank: -2 });
  }
  return [...byPath.values()].map(({ path, message: text, rule }) => ({ path, message: text, rule }));
}
