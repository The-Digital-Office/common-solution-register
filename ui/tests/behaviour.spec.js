// Behaviour tests (specification 6.13, acceptance 2): one test per row of the
// behaviour-parity table, against the fixture register.
const fs = require('node:fs');
const path = require('node:path');
const { test, expect } = require('@playwright/test');
const { SAMPLE } = require('./pages');

const FIXTURES = path.join(__dirname, 'fixtures', 'register');
const visible = (page) => page.$$eval('.ds_search-result:not([hidden])', (items) => items.map((li) => li.dataset.id));
const heading = (page) => page.locator('.ds_search-results__title');
const tick = (page, id) => page.click(`label[for="${id}"]`); // the design system draws its own checkbox over the input

test('1. Search: name, summary, owner, purpose and synonyms; the query is kept in the address', async ({ page }) => {
  await page.goto('');
  await page.fill('#q', 'payments');
  expect(await visible(page)).toEqual(['csr-9001', 'csr-9003']);
  await expect(page).toHaveURL(/\?q=payments$/);
  await page.fill('#q', 'social security agency'); // owner
  expect(await visible(page)).toEqual(['csr-9002']);
  await page.fill('#q', 'bulky waste'); // purpose
  expect(await visible(page)).toEqual(['csr-9003']);
  await page.fill('#q', 'sms'); // a synonym of notifications
  expect(await visible(page)).toEqual(['csr-9004']);
  await page.fill('#q', 'authentication'); // a synonym of identity and access
  expect(await visible(page)).toEqual(['csr-0100']);
  await page.fill('#q', 'gis'); // matches the start of words only, not "register"
  expect(await visible(page)).toEqual([]);
  await page.goto('?q=booking'); // a shared link
  await expect(page.locator('#q')).toHaveValue('booking');
  expect(await visible(page)).toEqual(['csr-9006', 'csr-9003']);
});

test('2. Provenance and asset-type filters, with counts', async ({ page }) => {
  await page.goto('');
  await tick(page, 'p-owner-confirmed');
  expect(await visible(page)).toEqual(['csr-0001', 'csr-0002']);
  await expect(page.locator('label[for="t-pattern"]')).toHaveText('Pattern (1)');
  await expect(page.locator('label[for="t-component"]')).toHaveText('Component (0)');
  await tick(page, 't-service');
  expect(await visible(page)).toEqual(['csr-0001']);
  await expect(page).toHaveURL(/provenance=owner-confirmed/);
  await expect(page).toHaveURL(/type=service/);
});

test('3. Sector, service area, capability, currency and withdrawn filters, with counts', async ({ page }) => {
  await page.goto('');
  await page.selectOption('#f-sector', 'executive-agencies');
  expect(await visible(page)).toEqual(['csr-9002', 'csr-0100']);
  await page.selectOption('#f-sector', '');
  await page.selectOption('#f-area', 'environment-and-waste');
  expect(await visible(page)).toEqual(['csr-9006', 'csr-9003']);
  await page.selectOption('#f-area', '');
  await expect(page.locator('#f-cap option[value="payments"]')).toHaveText('Payments (2)');
  await page.selectOption('#f-cap', 'payments');
  await tick(page, 'c-stale');
  expect(await visible(page)).toEqual(['csr-9003']);
  await page.goto('');
  await expect(heading(page)).toHaveText('8 solutions');
  await tick(page, 'show-withdrawn');
  expect(await visible(page)).toContain('csr-9005');
  await expect(heading(page)).toHaveText('9 solutions');
});

test('4. Sort: name, recently changed, recently confirmed', async ({ page }) => {
  await page.goto('');
  expect((await visible(page))[0]).toBe('csr-0001'); // name, A to Z
  await page.selectOption('#sort-by', 'confirmed');
  const ids = await visible(page);
  expect(ids[0]).toBe('csr-0001'); // confirmed 2 November 2026
  expect(ids.slice(-2)).toEqual(['csr-9003', 'csr-0100']); // 2 September 2025, then never confirmed
  await expect(page).toHaveURL(/sort=confirmed/);
  await page.selectOption('#sort-by', 'changed');
  await expect(page).toHaveURL(/sort=changed/);
});

test('5. Clear all filters; the result count is announced', async ({ page }) => {
  await page.goto('?provenance=example&type=api');
  await expect(heading(page)).toHaveText('1 solution');
  await page.click('#clear-filters');
  await expect(heading(page)).toHaveText('8 solutions');
  await expect(page).toHaveURL(/\/$/);
  await page.fill('#q', 'zzzz');
  await expect(page.locator('#no-results')).toBeVisible();
  await expect(page.locator('#results-status')).toHaveText('0 solutions found');
});

test.describe('6. Without JavaScript', () => {
  test.use({ javaScriptEnabled: false });
  test('the full list is shown and the filters are hidden', async ({ page }) => {
    await page.goto('?q=payments');
    expect(await visible(page)).toHaveLength(8);
    for (const control of ['.ds_search-filters', '#sort-by', '#q']) await expect(page.locator(control)).toBeHidden();
  });
});

test('7. Draft form conditional sections: every condition in 6.4', async ({ page }) => {
  await page.goto('draft/');
  const section = (name) => page.locator(`[data-section="${name}"]`);
  await expect(section('support')).toBeVisible(); // condition 7: a live service
  await page.selectOption('#type', 'component');
  await expect(section('support')).toBeHidden();
  await page.selectOption('#type', 'api');
  await expect(section('interfaces')).toBeVisible(); // condition 5
  await page.selectOption('#type', 'software');
  await expect(section('software')).toBeVisible(); // condition 4
  await page.selectOption('#status', 'deprecated');
  await expect(section('deprecation')).toBeVisible(); // condition 8
  await tick(page, 'ch-yes');
  await expect(section('charging')).toBeVisible(); // condition 6
  await tick(page, 'own-no');
  await expect(section('sources')).toBeVisible(); // condition 1
  await expect(page.locator('label[for="ch-unstated"]')).toBeVisible();
  await tick(page, 'own-yes');
  await expect(page.locator('#draft-yaml')).toContainText('confirmation:'); // condition 2
  await page.goto('draft/?from=csr-9005');
  await expect(section('withdrawal')).toBeVisible(); // condition 3
});

test('8. Draft form validation: every field, with an error summary and inline errors', async ({ page }) => {
  await page.goto('draft/');
  await page.click('button[type="submit"]');
  await expect(page.locator('#error-summary')).toBeFocused();
  const links = page.locator('#error-summary-list a');
  await expect(links.first()).toHaveText("Enter the solution's name");
  await expect(links.first()).toHaveAttribute('href', '#name');
  await expect(page.locator('#name-error')).toBeVisible();
  await expect(page.locator('#name')).toHaveAttribute('aria-describedby', 'name-error');
  await page.locator('#error-summary-list a[href="#purpose"]').click();
  await expect(page.locator('#purpose')).toBeFocused();

  await page.fill('#name', 'Booking component');
  await page.fill('#summary', 'A reusable booking component for council services.');
  await page.fill('#purpose', 'Lets council services take bookings for collections, appointments and rooms through one component.');
  await page.selectOption('#type', 'component');
  await page.fill('#owner', 'Example Council');
  await page.fill('#contact', 'booking@example.gov.uk');
  await tick(page, 'own-yes');
  await tick(page, 'service_areas-housing');
  await tick(page, 'capabilities-booking-and-scheduling');
  await tick(page, 'intended_adopters-local-government');
  await page.fill('#licence', 'MIT');
  await page.fill('#adopt', 'Deploy the component from its repository.');
  await page.fill('#repo-1', 'http://code.example.gov.uk/booking');
  await tick(page, 'vis-1-public');
  await page.click('button[type="submit"]');
  await expect(links).toHaveText(['Repository URL must be a full web address starting https://']);
  await page.fill('#repo-1', 'https://code.example.gov.uk/booking');
  await page.click('button[type="submit"]');
  await expect(page.locator('#draft-valid')).toBeFocused();
  await expect(page.locator('#error-summary')).toBeHidden();
});

test('9. Draft form classification: every term, from the taxonomy', async ({ page }) => {
  await page.goto('draft/');
  const terms = (name) => JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'build', 'api', 'v0', 'taxonomy', `${name}.json`))).terms.map((t) => t.id);
  for (const [field, taxonomy] of [['service_areas', 'service-areas'], ['capabilities', 'capabilities'], ['intended_adopters', 'sectors']]) {
    expect(await page.$$eval(`input[name="${field}"]`, (inputs) => inputs.map((i) => i.value))).toEqual(terms(taxonomy));
  }
});

test('10. The solution.yml preview is complete and updates live', async ({ page }) => {
  await page.goto('draft/');
  await expect(page.locator('#draft-yaml')).toContainText("schema_version: '0.1'\nid: csr-NNNN  # allocated when registered");
  await page.fill('#name', 'Booking component');
  await expect(page.locator('#draft-yaml')).toContainText('name: Booking component');
  await page.goto('draft/?from=csr-9003');
  const preview = page.locator('#draft-yaml');
  await expect(preview).toContainText('id: csr-9003');
  await expect(preview).toContainText('adopters:'); // a field the form does not show is kept
  await expect(preview).not.toContainText('currency:'); // fields the register derives are not part of solution.yml
});

test('11. Copy YAML, Download, open as a GitHub issue, send by email', async ({ page, context }) => {
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  await page.goto('draft/?from=csr-9001');
  await tick(page, 'own-yes');
  await page.click('#draft-copy');
  const yaml = await page.locator('#draft-yaml').textContent();
  expect(await page.evaluate(() => navigator.clipboard.readText())).toBe(yaml);
  const [download] = await Promise.all([page.waitForEvent('download'), page.click('#draft-download')]);
  expect(download.suggestedFilename()).toBe('solution.yml');
  expect(fs.readFileSync(await download.path(), 'utf8')).toBe(yaml);
  const issue = new URL(await page.getAttribute('#draft-issue', 'href'));
  expect(issue.searchParams.get('template')).toBe('suggest-asset.yml');
  expect(issue.searchParams.get('solution-yml')).toBe(yaml);
  expect(issue.searchParams.get('asset-name')).toBe('Example: Council Payments Gateway');
  await expect(page.locator('#draft-issue')).toHaveAttribute('target', '_blank');
  const [mailed] = await Promise.all([page.waitForEvent('download'), page.click('#draft-email').catch(() => {})]);
  expect(mailed.suggestedFilename()).toBe('solution.yml');
  const mailto = new URL(await page.getAttribute('#draft-email', 'href'));
  expect(mailto.pathname).toBe('solution-register@digitaloffice.scot');
  expect(mailto.searchParams.get('body').split('\n')).toHaveLength(2);
});

test('12. Validate page: real validation in paste, upload and URL modes', async ({ page }) => {
  await page.goto('validate/');
  await page.fill('#yaml', SAMPLE);
  await page.click('#run');
  await expect(page.locator('#result-fail')).toBeFocused();
  const rows = page.locator('#result-rows tr');
  await expect(rows.filter({ hasText: 'R09' })).toContainText('adoption_route.summary');
  await expect(rows.filter({ hasText: 'R07' })).toContainText('Warning');

  await page.click('[data-mode="upload"]');
  await expect(page.locator('[data-mode="upload"]')).toHaveAttribute('aria-pressed', 'true');
  await page.setInputFiles('#file', path.join(FIXTURES, 'examples', 'hosted', 'csr-9007', 'solution.yml'));
  await page.click('#run');
  await expect(page.locator('#result-fail')).toBeVisible();

  const hosted = 'https://code.example.gov.uk/booking/raw/main/solution.yml';
  await page.route(hosted, (route) => route.fulfill({ status: 200, headers: { 'access-control-allow-origin': '*' },
    body: fs.readFileSync(path.join(FIXTURES, 'examples', 'hosted', 'csr-9006', 'solution.yml'), 'utf8') }));
  await page.goto(`validate/?url=${encodeURIComponent(hosted)}`);
  await expect(page.locator('#result-pass')).toBeVisible();
  await expect(page.locator('#result-pass-text')).toContainText('meets schema version 0.1');
});

test('13. Record page actions are working links; Download solution.yml gives the record', async ({ page }) => {
  await page.goto('assets/csr-9001/');
  await expect(page.locator('a.ds_button', { hasText: 'Go to the service' })).toHaveAttribute('href', 'https://pay.example.gov.uk/');
  await expect(page.locator('a', { hasText: 'More information from the owner' })).toHaveAttribute('href', 'https://example.gov.uk/payments-gateway/');
  const [download] = await Promise.all([page.waitForEvent('download'), page.click('text=Download solution.yml')]);
  expect(fs.readFileSync(await download.path(), 'utf8')).toBe(fs.readFileSync(path.join(FIXTURES, 'records', 'csr-9001.yaml'), 'utf8'));
  const json = await page.request.get(new URL(await page.getAttribute('text=View as JSON', 'href'), page.url()).href);
  expect((await json.json()).id).toBe('csr-9001');
  await page.click('text=Suggest a correction');
  await expect(page.locator('#name')).toHaveValue('Example: Council Payments Gateway');
});

test.describe('14. Mobile navigation', () => {
  test.use({ viewport: { width: 375, height: 800 } });
  test("uses the design system's mobile menu", async ({ page }) => {
    await page.goto('');
    const menu = page.locator('button.js-toggle-menu');
    await expect(menu).toHaveAttribute('aria-expanded', 'false');
    await expect(page.locator('#mobile-navigation')).toBeHidden();
    await menu.click();
    await expect(menu).toHaveAttribute('aria-expanded', 'true');
    await expect(page.locator('#mobile-navigation')).toBeVisible();
    await page.click('#mobile-navigation >> text=Browse');
    await expect(page).toHaveURL(/browse\/$/);
  });
});
