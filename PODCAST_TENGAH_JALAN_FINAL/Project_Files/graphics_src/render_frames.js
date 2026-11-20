// usage: node render_frames.js page.html outdir duration fps "query"
const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs');
(async()=>{ const [html,outdir,dur,fps,query]=process.argv.slice(2);
  fs.mkdirSync(outdir,{recursive:true}); const N=Math.round(parseFloat(dur)*parseFloat(fps));
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1920,height:1080}});
  p.on('pageerror',e=>console.error('[pageerror]',html,e));
  await p.goto('file://'+path.resolve(html)+(query?'?'+query:'')); await p.waitForFunction(()=>window.READY===true);
  for(let i=0;i<N;i++){ await p.evaluate(t=>window.draw(t), i/parseFloat(fps)); await p.screenshot({path:path.join(outdir,String(i).padStart(5,'0')+'.png'), omitBackground:true}); }
  await b.close(); console.error('done',outdir,N); })();
