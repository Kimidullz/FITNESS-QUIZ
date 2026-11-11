// Turns the TESTIMONIALS list in index.html into 9:16 posters in the WDT team-poster style: img/t/<id>-<ms|en>.jpg
// Run: node testimonials/build.js   (needs Playwright; crops below are in source-image pixels)
const fs = require('fs'), path = require('path'), { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..');
const html0 = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
const TESTIMONIALS = eval(html0.match(/const TESTIMONIALS = (\[[\s\S]*?\n\]);/)[1]);
// before/after crops [x0,y0,x1,y1]; one crop = show the whole picture as a single panel
const CROPS = {
  sakeenah: [[127,78,292,365],[320,82,482,365]],
  eka:      [[128,78,292,365],[318,80,482,365]],
  nurse:    [[18,0,226,400],[268,0,473,400]],
  '68-58':  [[30,0,215,385],[268,0,485,385]],
  '11kg':   [[0,0,500,500]],
  alya:     [[0,0,484,800]],
};
const TXT = {
  ms: { head:"TESTIMONI", disc:"PENAFIAN: RESULT BERBEZA MENGIKUT INDIVIDU. IA BUKAN TIPIKAL." },
  en: { head:"REAL RESULTS", disc:"DISCLAIMER: RESULTS VARY FROM PERSON TO PERSON. THEY ARE NOT TYPICAL." },
};
const b64 = f => 'data:image/jpeg;base64,' + fs.readFileSync(path.join(ROOT, f)).toString('base64');
const L = (v, l) => typeof v === 'string' ? v : v[l];
const logo = b64('img/wdt/01.jpg');   // WDT logo is cropped from a team poster so it matches the others exactly
const panel = (src, [x0,y0,x1,y1], W, H, label) => {
  const w = W - 6, h = H - 6;   // inside the 3px border
  const s = Math.max(w/(x1-x0), h/(y1-y0));   // cover the panel, centred
  const iw = (x1-x0)*s, ih = (y1-y0)*s;
  return `<div class="p" style="width:${W}px;height:${H}px"><div class="crop" style="left:${(w-iw)/2}px;top:${(h-ih)/2}px;width:${iw}px;height:${ih}px">
    <img src="${src}" style="left:${-x0*s}px;top:${-y0*s}px;width:${src.natW*s}px"></div>${label ? `<span>${label}</span>` : ''}</div>`;
};
function page(t, l) {
  const src = new String(b64(t.photo)); src.natW = t.natW;
  const crops = CROPS[t.id]; assert(crops, 'no crop for ' + t.id);
  const [name, place] = L(t.name, l).split(', ');
  const kg = t.result.match(/[\d.]+/g);
  const lab = i => crops.length === 2 && kg.length === 2 ? `${kg[i]} KG${t.months ? ' · ' + L(t.months, l).split(' → ')[i].toUpperCase() : ''}` : '';
  const photos = crops.length === 2 ? crops.map((c, i) => panel(src, c, 222, 410, lab(i))).join('')
    : panel(src, crops[0], crops[0][2]/crops[0][3] > 0.9 ? 470 : 300, crops[0][2]/crops[0][3] > 0.9 ? 470 : 470, '');
  return `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:ital,wght@0,600;0,800;1,500&display=swap" rel="stylesheet">
<style>*{margin:0;padding:0;box-sizing:border-box}
body{display:flow-root;width:540px;height:960px;overflow:hidden;background:radial-gradient(ellipse 80% 55% at 50% 38%,#2b2b2b 0%,#101010 60%,#000 100%);color:#fff;font-family:Montserrat,sans-serif;text-align:center;position:relative}
.logo{width:150px;height:72px;margin:44px auto 0;background:url(${logo}) -192px -42px/540px 960px;mix-blend-mode:screen}
h1{font-family:Anton;font-size:34px;letter-spacing:.5px;margin-top:22px}
.ph{display:flex;justify-content:center;gap:18px;margin-top:22px;height:470px;align-items:center}
.p{position:relative;border:3px solid #fff;background:#000;overflow:hidden}
.crop{position:absolute;overflow:hidden}.crop img{position:absolute}
.p span{position:absolute;left:50%;bottom:10px;transform:translateX(-50%);background:#fff;color:#000;font-family:Anton;font-size:19px;padding:2px 10px;white-space:nowrap}
.nm{font-family:Anton;font-size:40px;line-height:1.05;margin-top:22px;text-transform:uppercase}
.rs{font-family:Anton;font-size:26px;color:#FFD200;margin-top:6px;text-transform:uppercase}
q{display:block;font-style:italic;font-weight:500;font-size:15.5px;line-height:1.4;margin:12px 36px 0;color:#e8e8e8}
.disc{position:absolute;left:20px;right:20px;top:908px;font-size:10.5px;letter-spacing:.3px;color:#bdbdbd}
</style></head><body>
<div class="logo"></div><h1>${TXT[l].head}</h1>
<div class="ph">${photos}</div>
<div class="nm">${name}</div><div class="rs">${t.result.replace('kg','KG')}${place ? ' · ' + place : ''}</div>
${t.quote ? `<q>${L(t.quote, l)}</q>` : ''}
<div class="disc">${TXT[l].disc}</div></body></html>`;
}
function assert(c, m) { if (!c) throw new Error(m); }
(async () => {
  const out = path.join(ROOT, 'img', 't'); fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 540, height: 960 } });
  for (const t of TESTIMONIALS) {
    t.natW = await p.evaluate(async s => { const i = new Image(); i.src = s; await i.decode(); return i.naturalWidth; }, b64(t.photo));
    for (const l of ['ms', 'en']) {
      await p.setContent(page(t, l), { waitUntil: 'networkidle' });
      await p.evaluate(() => document.fonts.ready);
      assert(await p.evaluate(() => document.fonts.check('40px Anton')), 'Anton font did not load');
      const over = await p.evaluate(() => { const q = document.querySelector('q'), d = document.querySelector('.disc'); return q && q.getBoundingClientRect().bottom > d.getBoundingClientRect().top - 8; });
      assert(!over, `quote runs into the disclaimer: ${t.id} ${l}`);
      await p.screenshot({ path: path.join(out, `${t.id}-${l}.jpg`), type: 'jpeg', quality: 84 });
    }
  }
  await b.close(); console.log('posters', TESTIMONIALS.length * 2);
})();
