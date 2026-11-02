// Home page search, filters and sort (specification 6.13, parity rows 1 to 6).
// Without JavaScript the page shows the full list; this script reveals the
// filters and keeps the state in the URL so results can be shared.
import {
  GROUPS, counts, countText, emptyState, normalise, queryFromState, results, stateFromQuery,
} from './search-core.js';

const indexElement = document.getElementById('csr-search-index');
const list = document.querySelector('.ds_search-results__list');

if (indexElement && list) {
  const index = JSON.parse(indexElement.textContent).map((record) => ({ ...record, text: normalise(record.text) }));
  const items = new Map([...list.children].map((li) => [li.dataset.id, li]));
  const query = document.getElementById('q');
  const sort = document.getElementById('sort-by');
  const withdrawn = document.getElementById('show-withdrawn');
  const heading = document.querySelector('.ds_search-results__title');
  const noResults = document.getElementById('no-results');
  const status = document.getElementById('results-status');
  const checkboxes = [...document.querySelectorAll('input[type="checkbox"][data-group]')];
  const selects = [...document.querySelectorAll('select[data-group]')];
  let state = stateFromQuery(window.location.search);
  let announceTimer;

  // The visible heading is not a live region with JavaScript: a separate
  // status message is announced once typing pauses.
  heading.removeAttribute('aria-live');

  const show = () => {
    query.value = state.q;
    sort.value = state.sort;
    withdrawn.checked = state.withdrawn;
    checkboxes.forEach((box) => { box.checked = state.filters[box.dataset.group].includes(box.value); });
    selects.forEach((select) => { select.value = state.filters[select.dataset.group][0] || ''; });
  };

  const render = ({ announce = true } = {}) => {
    const matching = results(index, state);
    const ids = new Set(matching.map((record) => record.id));
    items.forEach((li, id) => { li.hidden = !ids.has(id); });
    list.append(...matching.map((record) => items.get(record.id)));

    const facetCounts = counts(index, state);
    checkboxes.forEach((box) => {
      const label = document.querySelector(`label[for="${box.id}"]`);
      label.textContent = `${label.dataset.label} (${facetCounts[box.dataset.group][box.value] || 0})`;
    });
    selects.forEach((select) => {
      [...select.options].forEach((option) => {
        if (option.value) option.textContent = `${option.dataset.label} (${facetCounts[select.dataset.group][option.value] || 0})`;
      });
    });

    const text = countText(matching.length);
    heading.textContent = text;
    noResults.hidden = matching.length > 0;
    window.history.replaceState(null, '', window.location.pathname + queryFromState(state) + window.location.hash);
    if (announce) {
      clearTimeout(announceTimer);
      announceTimer = setTimeout(() => { status.textContent = `${text} found`; }, 600);
    }
  };

  query.addEventListener('input', () => { state.q = query.value; render(); });
  query.form.addEventListener('submit', (event) => { event.preventDefault(); state.q = query.value; render(); });
  sort.addEventListener('change', () => { state.sort = sort.value; render(); });
  withdrawn.addEventListener('change', () => { state.withdrawn = withdrawn.checked; render(); });
  checkboxes.forEach((box) => box.addEventListener('change', () => {
    const values = new Set(state.filters[box.dataset.group]);
    if (box.checked) values.add(box.value); else values.delete(box.value);
    state.filters[box.dataset.group] = [...values];
    render();
  }));
  selects.forEach((select) => select.addEventListener('change', () => {
    state.filters[select.dataset.group] = select.value ? [select.value] : [];
    render();
  }));
  document.getElementById('clear-filters').addEventListener('click', () => {
    state = { ...emptyState(), q: state.q, sort: state.sort };
    show();
    render();
  });

  // Groups not shown as controls cannot be set from the URL.
  Object.keys(GROUPS).forEach((group) => {
    const known = new Set([
      ...checkboxes.filter((box) => box.dataset.group === group).map((box) => box.value),
      ...selects.filter((select) => select.dataset.group === group).flatMap((select) => [...select.options].map((o) => o.value)),
    ]);
    state.filters[group] = state.filters[group].filter((value) => known.has(value));
  });
  show();
  render({ announce: false });
}
