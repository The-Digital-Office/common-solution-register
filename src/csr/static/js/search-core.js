// Search, filter, count and sort for the home page (specification 6.13,
// parity rows 1 to 6). Pure functions with no DOM access, so they can be
// tested on their own (tests/js/search-core.test.mjs).

/** The filter groups, their URL parameter, and the record field each tests. */
export const GROUPS = {
  provenance: { param: 'provenance', field: 'provenance', multiple: true },
  type: { param: 'type', field: 'type', multiple: true },
  sector: { param: 'sector', field: 'sector', multiple: false },
  area: { param: 'area', field: 'areas', multiple: false },
  capability: { param: 'capability', field: 'capabilities', multiple: false },
  currency: { param: 'currency', field: 'currency', multiple: true },
};

export const SORTS = ['name', 'changed', 'confirmed'];

/** Lower-case, strip accents, and turn punctuation into spaces, for matching. */
export function normalise(text) {
  return String(text || '')
    .normalize('NFD')
    .replace(/\p{M}/gu, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();
}

/** An empty state: no query, no filters, withdrawn records hidden, sorted by name. */
export function emptyState() {
  const filters = {};
  for (const key of Object.keys(GROUPS)) filters[key] = [];
  return { q: '', filters, withdrawn: false, sort: 'name' };
}

/** Read the state from a URL query string, ignoring anything unknown. */
export function stateFromQuery(search) {
  const params = new URLSearchParams(search);
  const state = emptyState();
  state.q = params.get('q') || '';
  for (const [key, group] of Object.entries(GROUPS)) {
    const values = params.getAll(group.param).filter(Boolean);
    state.filters[key] = group.multiple ? [...new Set(values)] : values.slice(0, 1);
  }
  state.withdrawn = params.get('withdrawn') === '1';
  state.sort = SORTS.includes(params.get('sort')) ? params.get('sort') : 'name';
  return state;
}

/** Write the state as a URL query string, leaving out defaults ('' when nothing is set). */
export function queryFromState(state) {
  const params = new URLSearchParams();
  if (state.q.trim()) params.set('q', state.q.trim());
  for (const [key, group] of Object.entries(GROUPS)) {
    for (const value of state.filters[key]) params.append(group.param, value);
  }
  if (state.withdrawn) params.set('withdrawn', '1');
  if (state.sort !== 'name') params.set('sort', state.sort);
  const query = params.toString();
  return query ? `?${query}` : '';
}

/** Every query word must start a word in the record ("pay" finds "payments"; "gis" does not find "register"). */
function matchesQuery(record, words) {
  const text = ` ${record.text}`;
  return words.every((word) => text.includes(` ${word}`));
}

function matchesGroup(record, key, values) {
  if (values.length === 0) return true;
  const value = record[GROUPS[key].field];
  return Array.isArray(value) ? values.some((v) => value.includes(v)) : values.includes(value);
}

/** Does a record match the state, optionally ignoring one filter group (for counts)? */
export function matches(record, state, ignoreGroup = null) {
  if (record.withdrawn && !state.withdrawn) return false;
  const words = normalise(state.q).split(' ').filter(Boolean);
  if (!matchesQuery(record, words)) return false;
  return Object.keys(GROUPS).every((key) => key === ignoreGroup || matchesGroup(record, key, state.filters[key]));
}

/**
 * Counts for every option in every group: how many records would match if
 * that option were chosen, given the query and the other groups.
 */
export function counts(records, state) {
  const result = {};
  for (const [key, group] of Object.entries(GROUPS)) {
    result[key] = {};
    for (const record of records) {
      if (!matches(record, state, key)) continue;
      const value = record[group.field];
      for (const v of Array.isArray(value) ? value : [value]) {
        if (v) result[key][v] = (result[key][v] || 0) + 1;
      }
    }
  }
  return result;
}

const byName = (a, b) => a.name.localeCompare(b.name, 'en-GB', { sensitivity: 'base' });

/** Newest date first; records without a date last; then by name. */
function byDate(field) {
  return (a, b) => {
    if (a[field] !== b[field]) {
      if (!a[field]) return 1;
      if (!b[field]) return -1;
      return a[field] < b[field] ? 1 : -1;
    }
    return byName(a, b);
  };
}

/** The matching records, in the chosen order. */
export function results(records, state) {
  const order = state.sort === 'changed' ? byDate('changed') : state.sort === 'confirmed' ? byDate('confirmed') : byName;
  return records.filter((record) => matches(record, state)).sort(order);
}

/** "1 solution", "7 solutions". */
export function countText(n) {
  return n === 1 ? '1 solution' : `${n} solutions`;
}
