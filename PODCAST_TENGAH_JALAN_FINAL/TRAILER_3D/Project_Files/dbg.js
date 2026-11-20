const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs');
(async()=>{ const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']}); const p=await b.newPage({viewport:{width:1920,height:1080}});
 p.on('pageerror',e=>console.error(e)); await p.goto('file://'+path.resolve(__dirname,'trailer3d.html')); await p.waitForFunction(()=>window.READY===true);
 await p.evaluate(e=>window.setEnv(e), JSON.parse(fs.readFileSync(path.join(__dirname,'trailer_env.json'))));
 const views=JSON.parse(process.argv[2]); let i=0; for(const v of views){ await p.evaluate(v=>window.debugCam(v[0],v[1]), v); await p.screenshot({path:`../thumbs/t3/dbg_${i++}.png`}); } await b.close(); })();
