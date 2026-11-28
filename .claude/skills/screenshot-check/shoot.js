// Usage: node shoot.js <url-or-html-file> [outDir] [widths]
// Example: node shoot.js index.html /tmp/shots 390,768,1440
// Full-page PNGs at each width (phone first). Uses the pre-installed Playwright.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const [target, outDir = 'shots', widthsArg = '390,1440'] = process.argv.slice(2);
  if (!target) { console.error('usage: node shoot.js <url-or-file> [outDir] [widths]'); process.exit(1); }
  const url = /^https?:|^file:/.test(target) ? target : 'file://' + path.resolve(target);
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const errors = [];
  for (const w of widthsArg.split(',').map(Number)) {
    const page = await browser.newPage({ viewport: { width: w, height: w < 800 ? 844 : 900 }, deviceScaleFactor: 1 });
    page.on('pageerror', e => errors.push(`${w}px: ${e.message}`));
    await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 }).catch(e => errors.push(`${w}px load: ${e.message}`));
    await page.waitForTimeout(800);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    if (overflow > 1) errors.push(`${w}px: page scrolls sideways by ${overflow}px`);
    const file = path.join(outDir, `shot-${w}.png`);
    await page.screenshot({ path: file, fullPage: true });
    console.log('saved', file);
    await page.close();
  }
  await browser.close();
  console.log(errors.length ? 'PROBLEMS:\n' + errors.join('\n') : 'no JS errors, no sideways scroll');
})();
