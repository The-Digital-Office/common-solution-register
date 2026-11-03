// UI tests (specification 6.13): visual comparison with ui/baseline/, behaviour
// tests for the parity table, and axe-core accessibility checks. They run
// against the fixture register in ui/tests/fixtures/, built as on a fixed date,
// so the pages are the same wherever the tests run.
const path = require('node:path');
const { defineConfig } = require('@playwright/test');

const PORT = 4173;
const python = process.env.PYTHON || 'python';
const fixtures = 'ui/tests/fixtures/register';

module.exports = defineConfig({
  testDir: 'tests',
  // The approved images: they started as the wireframes and are updated, in the
  // same pull request, whenever the design deliberately changes.
  snapshotPathTemplate: '{testDir}/../baseline/{arg}{ext}',
  outputDir: '../test-results',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0,
  reporter: process.env.CI ? [['list'], ['html', { outputFolder: '../playwright-report', open: 'never' }]] : 'list',
  use: {
    baseURL: `http://localhost:${PORT}/`,
    browserName: 'chromium',
    locale: 'en-GB',
    timezoneId: 'Europe/London',
  },
  expect: {
    toHaveScreenshot: { maxDiffPixelRatio: 0.01, animations: 'disabled', caret: 'hide', scale: 'css' },
  },
  webServer: {
    command: [
      `csr build --root ${fixtures} --harvest ${fixtures}/harvest-state.json --date 2026-11-02 --no-history`,
      `--base-url http://localhost:${PORT}/ --out ui/build`,
      `&& ${python} ui/tests/serve.py ${PORT} ui/build`,
    ].join(' '),
    cwd: path.join(__dirname, '..'),
    url: `http://localhost:${PORT}/`,
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
