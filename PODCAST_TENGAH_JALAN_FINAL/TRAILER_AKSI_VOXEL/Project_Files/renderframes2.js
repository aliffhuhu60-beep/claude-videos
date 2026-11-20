// resumable: node renderframes.js outdir start end
const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs');
(async()=>{ const [outdir, s0, s1] = process.argv.slice(2); fs.mkdirSync(outdir,{recursive:true});
  const env = JSON.parse(fs.readFileSync(path.join(__dirname,'action2_env.json')));
  const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const p=await b.newPage({viewport:{width:1920,height:1080}}); p.on('pageerror',e=>console.error('[pageerror]',e));
  await p.goto('file://'+path.resolve(__dirname,'voxel2.html')); await p.waitForFunction(()=>window.READY===true,null,{timeout:120000});
  await p.evaluate(e=>window.setEnv(e), env);
  const t0=Date.now(); let n=0;
  for(let i=parseInt(s0); i<parseInt(s1); i++){ const f=path.join(outdir,String(i).padStart(5,'0')+'.jpg'); if(fs.existsSync(f)) continue;
    await p.evaluate(t=>window.draw(t), i/30); await p.screenshot({path:f+'.tmp.jpg',type:'jpeg',quality:95}); fs.renameSync(f+'.tmp.jpg',f); n++;
    if(n%30===0) console.error('frame',i,((Date.now()-t0)/1000).toFixed(0)+'s'); }
  await b.close(); console.error('done',s0,s1); })();
