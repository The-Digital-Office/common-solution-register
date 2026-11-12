// Renders each .dc.html wireframe to a full-page PNG.
// Usage: node render.js <projectDir> <cssPath> <outDir>
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const [projectDir, cssPath, outDir] = process.argv.slice(2);
fs.mkdirSync(outDir, { recursive: true });

const pages = [
  ['01-home', 'Main.dc.html'],
  ['01b-find-solutions', 'Solutions.dc.html'],
  ['02-browse', 'Browse.dc.html'],
  ['03-taxonomy-term', 'Term.dc.html'],
  ['04-record-service-with-codebase', 'Record-Hosted.dc.html'],
  ['05-record-demonstration', 'Record-Demonstration.dc.html'],
  ['06-record-fictional-example', 'Record-Example.dc.html'],
  ['06b-record-withdrawn', 'Record-Withdrawn.dc.html'],
  ['07-contribute', 'Contribute.dc.html'],
  ['08-add-a-solution', 'Draft.dc.html'],
  ['08b-add-a-solution-errors', 'Draft.dc.html', { checked: true, type: 'software', status: 'deprecated', charges: 'yes' }],
  ['09-validate', 'Validate.dc.html'],
  ['09b-validate-results', 'Validate.dc.html', { result: 'fail' }],
  ['10-field-reference', 'Reference.dc.html'],
  ['11-solutions-and-codebases', 'Publiccode.dc.html'],
  ['12-data-and-api', 'Data.dc.html'],
  ['13-currency', 'Currency.dc.html'],
  ['14-harvest-report', 'Harvest.dc.html'],
  ['15-about', 'About.dc.html'],
  ['16-accessibility-statement', 'Accessibility.dc.html'],
  ['17-privacy-notice', 'Privacy.dc.html'],
  ['18-page-not-found', 'NotFound.dc.html'],
];

// Evaluate the artboard's logic class to get its template values.
function computeVals(src, stateOverride) {
  const m = src.match(/<script type="text\/x-dc" data-dc-script[^>]*>([\s\S]*?)<\/script>/);
  class DCLogic {
    constructor(props) { this.props = props || {}; this.state = {}; }
    setState(p) { Object.assign(this.state, p); }
  }
  const Component = new Function('DCLogic', m[1] + '\nreturn Component;')(DCLogic);
  const c = new Component({});
  if (stateOverride) Object.assign(c.state, stateOverride);
  return JSON.parse(JSON.stringify(c.renderVals())); // drops functions
}

function buildHtml(src, css) {
  const title = (src.match(/<title>([\s\S]*?)<\/title>/) || [])[1] || '';
  const helmet = (src.match(/<helmet>([\s\S]*?)<\/helmet>/) || [])[1] || '';
  let body = (src.match(/<x-dc>([\s\S]*?)<\/x-dc>/) || [])[1] || '';
  body = body.replace(/<helmet>[\s\S]*?<\/helmet>/, '');
  return `<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>${title}</title>
<style>${css}</style>${helmet}</head><body><template id="tpl">${body}</template><div id="root"></div></body></html>`;
}

// Runs in the page: expands sc-for / sc-if / {{holes}} against vals.
function expandInPage(vals) {
  const lookup = (scope, p) => p.trim().split('.').reduce((o, k) => (o == null ? undefined : o[k]), scope);
  const holeRe = /\{\{\s*([^}]+?)\s*\}\}/g;
  const literal = (s, scope) => {
    const t = s.trim();
    if (t === 'true') return true;
    if (t === 'false') return false;
    return lookup(scope, t);
  };
  function expand(node, scope) {
    if (node.nodeType === 3) {
      node.textContent = node.textContent.replace(holeRe, (_, p) => { const v = literal(p, scope); return v == null ? '' : String(v); });
      return [node];
    }
    if (node.nodeType !== 1) return [node];
    const tag = node.tagName.toLowerCase();
    if (tag === 'sc-for') {
      const list = literal(node.getAttribute('list').replace(/[{}]/g, ''), scope) || [];
      const as = node.getAttribute('as');
      const out = [];
      list.forEach((item, i) => {
        const s = Object.assign({}, scope, { [as]: item, $index: i });
        Array.from(node.childNodes).forEach((ch) => out.push(...expand(ch.cloneNode(true), s)));
      });
      return out;
    }
    if (tag === 'sc-if') {
      const v = literal(node.getAttribute('value').replace(/[{}]/g, ''), scope);
      if (!v) return [];
      const out = [];
      Array.from(node.childNodes).forEach((ch) => out.push(...expand(ch.cloneNode(true), scope)));
      return out;
    }
    for (const a of Array.from(node.attributes)) {
      const whole = a.value.match(/^\s*\{\{\s*([^}]+?)\s*\}\}\s*$/);
      if (whole) {
        const v = literal(whole[1], scope);
        if (v === undefined || v === null || v === false) { node.removeAttribute(a.name); continue; }
        if (v === true) { node.setAttribute(a.name, ''); continue; }
        if (a.name === 'value' && tag === 'textarea') { node.removeAttribute('value'); node.textContent = String(v); continue; }
        node.setAttribute(a.name, String(v));
      } else if (holeRe.test(a.value)) {
        node.setAttribute(a.name, a.value.replace(holeRe, (_, p) => { const v = literal(p, scope); return v == null ? '' : String(v); }));
      }
      holeRe.lastIndex = 0;
    }
    const kids = Array.from(node.childNodes);
    kids.forEach((ch) => {
      const res = expand(ch, scope);
      if (res.length === 1 && res[0] === ch) return;
      res.forEach((r) => node.insertBefore(r, ch));
      node.removeChild(ch);
    });
    if (tag === 'select' && node.hasAttribute('value')) {
      const v = node.getAttribute('value');
      Array.from(node.options).forEach((o) => { if (o.value === v) o.setAttribute('selected', ''); });
    }
    return [node];
  }
  const frag = document.getElementById('tpl').content.cloneNode(true);
  const root = document.getElementById('root');
  Array.from(frag.childNodes).forEach((ch) => expand(ch, vals).forEach((r) => root.appendChild(r)));
  // Reflect select values set via attribute
  document.querySelectorAll('select[value]').forEach((s) => { s.value = s.getAttribute('value'); });
}

(async () => {
  const css = fs.readFileSync(cssPath, 'utf8');
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1 });
  for (const [name, file, override] of pages) {
    const src = fs.readFileSync(path.join(projectDir, file), 'utf8');
    const vals = computeVals(src, override);
    await page.setContent(buildHtml(src, css), { waitUntil: 'networkidle', timeout: 20000 }).catch(() => {});
    await page.evaluate(expandInPage, vals);
    await page.evaluate(() => document.fonts && document.fonts.ready);
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(outDir, name + '.png'), fullPage: true });
    console.log('rendered', name);
  }
  await browser.close();
})();
