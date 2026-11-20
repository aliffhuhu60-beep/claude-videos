// shared helpers
const W = 1920, H = 1080;
const C = { maroon:'#6E1E2B', maroonD:'#3A0D16', maroonDD:'#22070D', cream:'#F7EDE0', pink:'#F4B6C6', pinkD:'#E58FA6', black:'#141012', yellow:'#FFD54A', white:'#FFFFFF' };
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const lerp=(a,b,t)=>a+(b-a)*t;
const ease={ out:t=>1-Math.pow(1-clamp(t),3), inOut:t=>{t=clamp(t);return t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2}, outBack:t=>{t=clamp(t);const c1=1.4,c3=c1+1;return 1+c3*Math.pow(t-1,3)+c1*Math.pow(t-1,2)}, in:t=>Math.pow(clamp(t),3) };
const prog=(t,a,b)=>clamp((t-a)/(b-a));
// fade window: in over [a,a+d], out over [b-d2,b]
const win=(t,a,b,d=0.4,d2=d)=>Math.min(ease.out(prog(t,a,a+d)), 1-ease.inOut(prog(t,b-d2,b)));
function setup(){ const cv=document.createElement('canvas'); cv.width=W; cv.height=H; document.body.appendChild(cv); return cv.getContext('2d'); }
function font(w,s){ return `${w} ${s}px Poppins`; }
function rrect(ctx,x,y,w,h,r){ ctx.beginPath(); ctx.moveTo(x+r,y); ctx.arcTo(x+w,y,x+w,y+h,r); ctx.arcTo(x+w,y+h,x,y+h,r); ctx.arcTo(x,y+h,x,y,r); ctx.arcTo(x,y,x+w,y,r); ctx.closePath(); }
// rich text: segments [{t:'text', c:'#fff'}], drawn centered or left
function measureSegs(ctx,segs){ return segs.reduce((s,g)=>s+ctx.measureText(g.t).width,0); }
function drawSegs(ctx,segs,x,y,align='center'){ let w=measureSegs(ctx,segs); let cx= align==='center'? x-w/2 : align==='right'? x-w : x; for(const g of segs){ ctx.fillStyle=g.c; ctx.fillText(g.t,cx,y); cx+=ctx.measureText(g.t).width; } return w; }
// seeded random
function rng(seed){ let s=seed>>>0; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; }
function fontsReady(){ return Promise.all(['400','500','600','700','800'].map(w=>document.fonts.load(`${w} 40px Poppins`))); }
