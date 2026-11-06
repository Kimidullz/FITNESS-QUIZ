// Usage: node render.js [outDir=frames] [workers=4]
// Screenshots index.html frame by frame (1080x1920 PNGs) with the preinstalled
// Playwright Chromium. Then: ffmpeg -framerate 30 -i frames/f_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 out.mp4
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const outDir = process.argv[2] || 'frames';
const workers = +(process.argv[3] || 4);
const url = 'file://' + path.join(__dirname, 'index.html');
(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files', '--use-gl=angle', '--use-angle=swiftshader'] });
  const probe = await browser.newPage(); await probe.goto(url); await probe.evaluate(() => window.ready);
  const total = await probe.evaluate(() => window.TOTAL_FRAMES); await probe.close();
  const frames = Array.from({ length: total }, (_, i) => i);
  await Promise.all(Array.from({ length: workers }, async (_, w) => {
    const page = await browser.newPage({ viewport: { width: 540, height: 960 }, deviceScaleFactor: 2 });
    await page.goto(url); await page.evaluate(() => window.ready);
    for (const f of frames.filter((_, i) => i % workers === w)) {
      await page.evaluate((f) => window.renderFrame(f), f);
      await page.screenshot({ path: path.join(outDir, `f_${String(f).padStart(4, '0')}.png`) });
    }
    await page.close();
  }));
  await browser.close();
  console.log('rendered', total, 'frames to', outDir);
})();
