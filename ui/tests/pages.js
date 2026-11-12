// Every page in the page-to-template map (specification 6.13), named after its
// approved image in ui/baseline/, with the steps that bring it to the state the
// wireframe shows.

const SAMPLE = [
  'schema_version: "0.1"', 'id: csr-0042', 'record_status: owner-confirmed', 'name: Example Booking Component',
  'summary: A reusable appointment booking component for council services.', 'asset_type: component', 'owner:',
  '  organisation: Example Council', '  sector: local-government', 'contact:', '  type: role-mailbox',
  '  value: jane.smith@example.gov.uk', 'service_areas: [customer-and-corporate]', 'capabilities: []',
  'adoption_route:', '  summary: TODO', '',
].join('\n');

const PAGES = [
  { name: '01-home', path: '' },
  { name: '01b-find-solutions', path: 'solutions/' },
  { name: '02-browse', path: 'browse/' },
  { name: '03-taxonomy-term', path: 'capabilities/identity-and-access/' },
  { name: '04-record-service-with-codebase', path: 'assets/csr-0001/' },
  { name: '05-record-demonstration', path: 'assets/csr-0100/' },
  { name: '06-record-fictional-example', path: 'assets/csr-9003/' },
  { name: '06b-record-withdrawn', path: 'assets/csr-9005/' },
  { name: '07-contribute', path: 'contribute/' },
  { name: '08-add-a-solution', path: 'draft/' },
  {
    name: '08b-add-a-solution-errors',
    path: 'draft/',
    async setup(page) {
      await page.selectOption('#type', 'software');
      await page.selectOption('#status', 'deprecated');
      await page.click('label[for="ch-yes"]');
      await page.click('button[type="submit"]');
    },
  },
  { name: '09-validate', path: 'validate/' },
  {
    name: '09b-validate-results',
    path: 'validate/',
    async setup(page) {
      await page.fill('#yaml', SAMPLE);
      await page.click('#run');
      await page.waitForSelector('#result-fail:not([hidden])');
    },
  },
  { name: '10-field-reference', path: 'reference/' },
  { name: '11-solutions-and-codebases', path: 'reference/publiccode/' },
  { name: '12-data-and-api', path: 'data/' },
  { name: '13-currency', path: 'currency/' },
  { name: '14-harvest-report', path: 'harvest/' },
  { name: '15-about', path: 'about/' },
  { name: '16-accessibility-statement', path: 'accessibility/' },
  { name: '17-privacy-notice', path: 'privacy/' },
  { name: '18-page-not-found', path: '404.html' },
];

/** Open a page, bring it to its state, and wait until it is still. */
async function open(page, item) {
  await page.goto(item.path, { waitUntil: 'networkidle' });
  if (item.setup) await item.setup(page);
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => window.scrollTo(0, 0));
}

module.exports = { PAGES, SAMPLE, open };
