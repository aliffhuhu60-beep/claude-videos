// node render3d.js out(.mp4|dir/) times|all
const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs'); const { spawn } = require('child_process');
(async()=>{ const [out, mode] = process.argv.slice(2);
  const env = JSON.parse(fs.readFileSync(path.join(__dirname,'trailer_env.json')));
  const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1920,height:1080}});
  p.on('pageerror',e=>console.error('[pageerror]',e)); p.on('console',m=>{ if(m.type()==='error') console.error('[console]',m.text()); });
  await p.goto('file://'+path.resolve(__dirname,'trailer3d.html')); await p.waitForFunction(()=>window.READY===true,null,{timeout:60000});
  await p.evaluate(e=>window.setEnv(e), env);
  if(mode!=='all'){ for(const t of mode.split(',')){ await p.evaluate(t=>window.draw(t), parseFloat(t)); await p.screenshot({path:`${out}_${t}.png`}); } await b.close(); return; }
  const N=Math.round(env.total*env.fps);
  const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate','30','-i','-','-i',path.join(__dirname,'trailer_mix.wav'),
    '-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
  const t0=Date.now();
  for(let i=0;i<N;i++){ await p.evaluate(t=>window.draw(t), i/30); const buf=await p.screenshot({type:'jpeg',quality:95});
    if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r)); if(i%60===0) console.error('frame',i,'/',N,((Date.now()-t0)/1000).toFixed(0)+'s'); }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.error('done',out); })();
