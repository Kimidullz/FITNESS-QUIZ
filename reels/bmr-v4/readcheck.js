// Reading-time check (lemo-opuscar rule): each text must stay on screen for
// at least non-space letters / 15 + 1.5 s. Uses window.TEXTS(t) from index.html.
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 540, height: 960 } });
  await p.goto('file://' + path.join(__dirname, 'index.html')); await p.evaluate(() => window.ready);
  const runs = {};
  for (let f = 0; f < 900; f++) {
    const list = await p.evaluate(f => window.TEXTS(f / 30), f);
    for (const t of list) { const k = t.id + '|' + t.text; const r = runs[k] || (runs[k] = { first: f, last: f }); r.last = f; }
  }
  let fail = 0;
  for (const [k, r] of Object.entries(runs)) {
    const text = k.split('|')[1]; const need = text.replace(/\s/g, '').length / 15 + 1.5; const have = (r.last - r.first + 1) / 30;
    const ok = have + 1e-6 >= need; if (!ok) fail++;
    console.log(`${ok ? 'OK  ' : 'SHORT'} ${have.toFixed(2)}s on screen, needs ${need.toFixed(2)}s  frames ${r.first}-${r.last}  "${text}"`);
  }
  await b.close(); process.exit(fail ? 1 : 0);
})();
