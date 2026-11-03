// Visual comparison (specification 6.13, acceptance 1): every page at 1280 and
// 375 pixels wide, compared with its approved image in ui/baseline/. A
// deliberate change to the design updates the image in the same pull request
// (npm run test:ui:update), so the change is visible and reviewed.
const { test, expect } = require('@playwright/test');
const { PAGES, open } = require('./pages');

for (const width of [1280, 375]) {
  test.describe(`${width} pixels`, () => {
    test.use({ viewport: { width, height: 900 } });
    for (const item of PAGES) {
      test(item.name, async ({ page }) => {
        await open(page, item);
        await expect(page).toHaveScreenshot(`${item.name}${width === 375 ? '-375' : ''}.png`, { fullPage: true });
      });
    }
  });
}
