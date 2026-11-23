// node rakam_wallpaper.js <html> <out.mp4> <width> <height> <fps> <seconds> [testTimes]
// rakam hari_lahir.html dari t=0 hingga <seconds>
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const [html, out, W, H, FPS, SEC, test] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch({ args: ['--force-color-profile=srgb'] });
  const p = await (await b.newContext({ viewport: { width: +W, height: +H }, deviceScaleFactor: 1 })).newPage();
  p.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await p.goto('file://' + html + '?capture');
  await p.waitForFunction(() => window.renderAt);
  const shot = async t => { await p.evaluate(t => window.renderAt(t), t); return p.screenshot({ type: 'png' }); };
  if (test) {
    for (const t of test.split(',')) require('fs').writeFileSync(`test_${t}.png`, await shot(+t));
    await b.close(); return;
  }
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', FPS, '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
    '-movflags', '+faststart', '-r', FPS, out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const N = Math.round(+FPS * +SEC);
  const t0 = Date.now();
  for (let i = 0; i < N; i++) {
    const buf = await shot(i / +FPS);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 60 === 0) console.log(`frame ${i}/${N}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await b.close();
  console.log('done', out);
})();
