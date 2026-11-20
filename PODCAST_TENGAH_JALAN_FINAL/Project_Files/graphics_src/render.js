// usage: node render.js page.html out.(mp4|mov) duration fps [alpha] [query]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
(async () => {
  const [html, out, dur, fps, alpha, query] = process.argv.slice(2);
  const A = alpha === 'alpha';
  const N = Math.round(parseFloat(dur) * parseFloat(fps));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('console', m => console.error('[page]', m.text()));
  page.on('pageerror', e => console.error('[pageerror]', e));
  await page.goto('file://' + path.resolve(html) + (query ? '?' + query : ''));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => window.READY === true, null, { timeout: 30000 });
  const args = ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', fps, '-i', '-'];
  if (A) args.push('-c:v', 'qtrle', '-pix_fmt', 'argb', out);
  else args.push('-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', out);
  const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < N; i++) {
    await page.evaluate(t => window.draw(t), i / parseFloat(fps));
    const buf = await page.screenshot({ type: A ? 'png' : 'jpeg', quality: A ? undefined : 95, omitBackground: A });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.error('done', out, N, 'frames');
})();
