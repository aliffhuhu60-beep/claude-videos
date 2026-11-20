const { chromium } = require('playwright'); const path=require('path');
(async()=>{ const [html, times, prefix, query]=process.argv.slice(2);
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1920,height:1080}});
 p.on('pageerror',e=>console.error('[pageerror]',e)); p.on('console',m=>console.error('[page]',m.text()));
 await p.goto('file://'+path.resolve(html)+(query?'?'+query:'')); await p.waitForFunction(()=>window.READY===true);
 for(const t of times.split(',')){ await p.evaluate(t=>window.draw(t),parseFloat(t)); await p.screenshot({path:`${prefix}_${t}.png`, omitBackground:true}); }
 await b.close(); })();
