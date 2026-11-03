// Accessibility (specification 6.13, acceptance 3): axe-core on every page, in
// the states the wireframes show, with no serious or critical issues. Minor and
// moderate findings are reported for review. A manual keyboard and screen-reader
// pass is also done before publication (slice S16).
const { test, expect } = require('@playwright/test');
const { default: AxeBuilder } = require('@axe-core/playwright');
const { PAGES, open } = require('./pages');

const BLOCKING = ['serious', 'critical'];

async function check(page, testInfo) {
  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice']).analyze();
  const lines = results.violations.map((v) => `${v.impact}: ${v.id} (${v.nodes.length}) ${v.help}`);
  if (lines.length) await testInfo.attach('axe findings', { body: lines.join('\n'), contentType: 'text/plain' });
  for (const line of lines) console.log(`${testInfo.title}: ${line}`);
  const blocking = results.violations.filter((v) => BLOCKING.includes(v.impact))
    .map((v) => ({ rule: v.id, impact: v.impact, help: v.help, targets: v.nodes.map((n) => n.target.join(' ')) }));
  expect(blocking).toEqual([]);
}

for (const item of PAGES) {
  test(item.name, async ({ page }, testInfo) => {
    await open(page, item);
    await check(page, testInfo);
  });
}

test.describe('375 pixels', () => {
  test.use({ viewport: { width: 375, height: 800 } });
  test('mobile menu open', async ({ page }, testInfo) => {
    await page.goto('');
    await page.click('button.js-toggle-menu');
    await check(page, testInfo);
  });
});
