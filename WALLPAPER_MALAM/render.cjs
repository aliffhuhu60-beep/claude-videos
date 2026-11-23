// Usage:
//   node render.cjs still <scene> <out.png> [t] [text=1|0]
//   node render.cjs video <scene> <out.mp4> [fps=30] [text=1|0]
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const SRC = path.join(__dirname, 'src');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2' };

function serve() {
  return new Promise((res) => {
    const srv = http.createServer((req, rsp) => {
      const f = path.join(SRC, decodeURIComponent(req.url.split('?')[0]));
      if (!f.startsWith(SRC) || !fs.existsSync(f)) { rsp.writeHead(404); return rsp.end(); }
      rsp.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' });
      fs.createReadStream(f).pipe(rsp);
    });
    srv.listen(0, '127.0.0.1', () => res(srv));
  });
}

(async () => {
  const [mode, scene, out, a4, a5] = process.argv.slice(2);
  const text = a5 !== '0';
  const srv = await serve();
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 2400 }, deviceScaleFactor: 1 });
  page.on('console', (m) => console.log('[page]', m.text()));
  await page.goto(`http://127.0.0.1:${srv.address().port}/index.html?scene=${scene}&text=${text ? 1 : 0}`);
  await page.waitForFunction(() => window.ready || window.err, null, { timeout: 300000 });
  const err = await page.evaluate(() => window.err);
  if (err) { console.error(err); process.exit(1); }
  console.log('init ms', Math.round(await page.evaluate(() => window.initMs)));
  const canvas = await page.$('#c');

  if (mode === 'still') {
    const ts = (a4 || '0').split(',').map(Number);
    for (const t of ts) {
      await page.evaluate((t) => window.renderFrame(t), t);
      const o = ts.length > 1 ? out.replace(/\.png$/, `_t${t}.png`) : out;
      await canvas.screenshot({ path: o });
      console.log('wrote', o);
    }
  } else {
    const fps = Number(a4 || 30), T = await page.evaluate(() => window.sceneT), N = Math.round(T * fps);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
      '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const t0 = Date.now();
    for (let i = 0; i < N; i++) {
      await page.evaluate((t) => window.renderFrame(t), i / fps);
      const buf = await canvas.screenshot({ type: 'png' });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
      if (i % 60 === 0) console.log(`frame ${i}/${N} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end();
    await new Promise((r) => ff.on('close', r));
    console.log('wrote', out);
  }
  await browser.close(); srv.close();
})();
