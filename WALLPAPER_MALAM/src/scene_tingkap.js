// Version 2 — black cat on a lamp-lit window sill, looking out over a moonlit garden.
window.SCENES = window.SCENES || {};
SCENES.tingkap = function (opts) {
  const W = 1080, H = 2400, T = 30, TAU = P.TAU;
  const osc = (t, k, p = 0) => Math.sin(TAU * k * t / T + p);
  const R = P.rng(23), noise = P.makeNoise(9);
  const WALL = 78, SILL_B = 1985, SILL_F = 2150, PX0 = 838, PX1 = 1008;
  const MOON = { x: 585, y: 235, r: 46 };
  const CAT = { x: 600, base: 2098, h: 480 };
  const L = {};
  const skyStops = [[0, P.hex('#050a20')], [0.55, P.hex('#10224f')], [1, P.hex('#22407a')]];

  function paintSky() {
    const c = P.canvas(W, H), g = c.getContext('2d');
    const lg = g.createLinearGradient(0, 0, 0, 700);
    skyStops.forEach((s) => lg.addColorStop(s[0], P.css(s[1])));
    g.fillStyle = lg; g.fillRect(0, 0, W, 760);
    P.fillStrokes(g, R, {
      x0: -20, y0: -20, x1: W + 20, y1: 760, count: 5000, jit: 8,
      color: (x, y) => {
        let col = P.grad(skyStops, y / 700);
        const dm = Math.hypot(x - MOON.x, y - MOON.y);
        if (dm < 380) col = P.mix(col, P.hex('#6c82c2'), Math.pow(1 - dm / 380, 1.7) * 0.5);
        return col;
      },
      angle: (x, y, R) => (R() - 0.5) * 0.5, len: [25, 80], w: [8, 20], a: [0.18, 0.38],
    });
    for (let i = 0; i < 650; i++) {
      const x = R() * W, y = Math.pow(R(), 1.2) * 620;
      g.fillStyle = `rgba(236,240,255,${P.rand(R, 0.15, 0.6)})`; g.beginPath(); g.arc(x, y, P.rand(R, 0.5, 1.3), 0, TAU); g.fill();
    }
    return c;
  }

  function paintMoon() {
    const r = MOON.r, s = r * 2 + 30, c = P.canvas(s, s), g = c.getContext('2d'), m = s / 2;
    const disc = new Path2D(); disc.arc(m, m, r, 0, TAU);
    g.fillStyle = '#f6eed6'; g.fill(disc);
    P.fillStrokes(g, R, {
      path: disc, x0: m - r, y0: m - r, x1: m + r, y1: m + r, count: 220, jit: 7,
      color: (x, y) => (noise(x * 0.06, y * 0.06) > 0.56 ? P.hex('#ddd0ac') : P.hex('#fff7e2')),
      angle: (x, y, R) => (R() - 0.5) * 1.2, len: [6, 16], w: [3, 8], a: [0.35, 0.65],
    });
    // carve a crescent
    g.globalCompositeOperation = 'destination-out'; g.filter = 'blur(1.5px)';
    g.beginPath(); g.arc(m - r * 0.55, m - r * 0.28, r * 0.98, 0, TAU); g.fill();
    g.globalCompositeOperation = 'source-over'; g.filter = 'none';
    return c;
  }

  // union-of-circles foliage, lit from above by the moon
  function foliage(g, blobs, cols, count, seed) {
    const Rf = P.rng(seed);
    const path = new Path2D();
    blobs.forEach(([x, y, r]) => { path.moveTo(x + r, y); path.arc(x, y, r, 0, TAU); });
    const ys = blobs.map((b) => b[1] - b[2]), top = Math.min(...ys), bot = Math.max(...blobs.map((b) => b[1] + b[2]));
    g.save(); g.filter = 'blur(3px)'; g.fillStyle = cols.base; g.fill(path); g.filter = 'none'; g.restore();
    const colAt = (x, y, R) => {
      let best = blobs[0], bd = 1e9;
      blobs.forEach((b) => { const d = Math.hypot(x - b[0], y - b[1]) / b[2]; if (d < bd) { bd = d; best = b; } });
      const up = P.clamp(-(y - best[1]) / best[2], -1, 1), side = (x - best[0]) / best[2];
      const lit = P.clamp(up * 0.8 + side * 0.15 + 0.1, 0, 1);
      let col = P.mix(P.hex(cols.dark), P.hex(cols.mid), P.clamp(lit * 1.6, 0, 1));
      if (lit > 0.55) col = P.mix(col, P.hex(cols.lit), (lit - 0.55) * 1.8);
      col = P.mix(col, P.hex(cols.dark), P.clamp((y - top) / (bot - top), 0, 1) * 0.35);
      if (R() < 0.05) col = P.mix(col, P.hex(cols.lit), 0.4);
      return col;
    };
    P.fillStrokes(g, Rf, { path, x0: Math.min(...blobs.map((b) => b[0] - b[2])), x1: Math.max(...blobs.map((b) => b[0] + b[2])), y0: top, y1: bot, count, jit: 9, kind: 'dab', color: colAt, w: [4, 11], a: [0.45, 0.85] });
    // leafy fringe
    blobs.forEach((b) => {
      for (let i = 0; i < b[2] * 0.7; i++) {
        const an = -Math.PI / 2 + (Rf() - 0.5) * 3.6, rr = b[2] * P.rand(Rf, 0.92, 1.08);
        const x = b[0] + Math.cos(an) * rr, y = b[1] + Math.sin(an) * rr;
        if (blobs.some((q) => q !== b && Math.hypot(x - q[0], y - q[1]) < q[2] * 0.95)) continue;
        P.dab(g, Rf, x, y, P.rand(Rf, 3, 7), P.css(P.jit(colAt(x, y, Rf), Rf, 8)), P.rand(Rf, 0.4, 0.8));
      }
    });
  }

  function blobRow(Rb, x0, x1, yTop, yBot, rMin, rMax, n) {
    const out = [];
    for (let i = 0; i < n; i++) out.push([P.rand(Rb, x0, x1), P.rand(Rb, yTop, yBot), P.rand(Rb, rMin, rMax)]);
    return out;
  }

  const pathCenter = (y) => { // centre-x and half-width of the garden path at height y
    const u = P.clamp((SILL_B - y) / (SILL_B - 820), 0, 1);
    const cx = 470 + 80 * u + 40 * Math.sin(u * 5.5) - 10 * u * u;
    return [cx, 200 * Math.pow(1 - u, 1.25) + 18];
  };

  function paintBack() {
    const c = P.canvas(W, H), g = c.getContext('2d');
    // distant forested hill
    const hp = [[260, 470]];
    for (let x = 260; x <= 900; x += 8) hp.push([x, 470 - (x - 260) * 0.2 - 22 * Math.sin(x * 0.012) - Math.abs(Math.sin(x * 0.11)) * 9]);
    hp.push([900, 760], [260, 760]);
    const hpath = P.roughPath(hp, R, 2, 8);
    g.fillStyle = '#10203a'; g.fill(hpath);
    P.fillStrokes(g, R, { path: hpath, x0: 260, y0: 300, x1: 900, y1: 760, count: 2200, jit: 7, kind: 'dab',
      color: (x, y) => (noise(x * 0.03, y * 0.03) > 0.55 ? P.hex('#22395a') : P.hex('#15284a')), w: [4, 10], a: [0.4, 0.8] });
    // château
    const hx = 470, hy = 505;
    const wall = (x, y, w, h, col) => {
      const p = P.roughPath([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], R, 1, 8);
      g.fillStyle = col; g.fill(p);
      P.fillStrokes(g, R, { path: p, x0: x, y0: y, x1: x + w, y1: y + h, count: w * h / 40, jit: 8, color: () => P.hex(col), angle: () => Math.PI / 2 + (R() - 0.5) * 0.4, len: [6, 14], w: [3, 6], a: [0.3, 0.6] });
    };
    wall(hx, hy, 175, 115, '#7f8db3');
    wall(hx + 175, hy + 22, 70, 93, '#6c789d');
    wall(hx - 40, hy + 30, 44, 85, '#6f7ca2');
    const roof = (pts, col) => { const p = P.roughPath(pts, R, 1.2, 8); g.fillStyle = col; g.fill(p); P.fillStrokes(g, R, { path: p, x0: 300, y0: 400, x1: 800, y1: 640, count: 120, jit: 8, color: () => P.hex(col), angle: () => (R() - 0.5) * 0.4, len: [8, 18], w: [3, 6], a: [0.3, 0.6] }); };
    roof([[hx - 6, hy], [hx + 30, hy - 38], [hx + 150, hy - 38], [hx + 181, hy]], '#26304d');
    roof([[hx + 170, hy + 22], [hx + 205, hy - 8], [hx + 248, hy + 22]], '#5a3c46');
    roof([[hx - 44, hy + 30], [hx - 18, hy + 4], [hx + 6, hy + 30]], '#4a3540');
    g.fillStyle = '#26304d'; g.fillRect(hx + 120, hy - 58, 14, 24); g.fillRect(hx + 40, hy - 52, 11, 18);
    L.windows = [];
    for (let row = 0; row < 2; row++) for (let col = 0; col < 6; col++) {
      L.windows.push({ x: hx + 14 + col * 27, y: hy + 20 + row * 42, w: 10, h: 17, on: R() < 0.7, k: 1 + Math.floor(R() * 3), p: R() * TAU });
    }
    for (let col = 0; col < 2; col++) L.windows.push({ x: hx + 190 + col * 26, y: hy + 45, w: 10, h: 16, on: true, k: 2, p: R() * TAU });
    L.windows.push({ x: hx - 26, y: hy + 55, w: 9, h: 15, on: true, k: 3, p: 1 });
    L.windows.forEach((w) => { g.fillStyle = '#2a2f45'; g.fillRect(w.x, w.y, w.w, w.h); });

    // garden ground
    const gp = P.roughPath([[WALL - 10, 640], [PX1 + 80, 600], [PX1 + 80, SILL_B + 10], [WALL - 10, SILL_B + 10]], R, 3, 20);
    const gg = g.createLinearGradient(0, 640, 0, SILL_B);
    gg.addColorStop(0, '#0f2119'); gg.addColorStop(1, '#152c20');
    g.fillStyle = gg; g.fill(gp);
    const gpal = [P.hex('#173323'), P.hex('#1d3b29'), P.hex('#22432f'), P.hex('#10231a')];
    P.fillStrokes(g, R, { path: gp, x0: WALL - 10, y0: 600, x1: PX1 + 80, y1: SILL_B + 10, count: 16000, jit: 8,
      color: (x, y, R) => { let col = P.pick(R, gpal); const n = noise(x * 0.008, y * 0.008); if (n > 0.57) col = P.mix(col, P.hex('#35565a'), (n - 0.57) * 1.8); return col; },
      angle: (x, y, R) => -Math.PI / 2 + (R() - 0.5) * 0.9, len: [10, 28], w: [4, 9], a: [0.4, 0.75] });

    // path, moonlit
    const left = [], right = [];
    for (let y = SILL_B + 10; y >= 800; y -= 10) { const [cx, hw] = pathCenter(y); left.push([cx - hw, y]); right.push([cx + hw, y]); }
    const pp = P.roughPath(left.concat(right.reverse()), R, 3, 10);
    g.fillStyle = '#5f5a72'; g.fill(pp);
    P.fillStrokes(g, R, { path: pp, x0: 200, y0: 790, x1: 800, y1: SILL_B + 10, count: 5200, jit: 8,
      color: (x, y, R) => { const u = (y - 800) / (SILL_B - 800); let col = P.mix(P.hex('#7c7792'), P.hex('#8d7f8c'), u); if (R() < 0.15) col = P.mix(col, P.hex('#a9a6c4'), 0.5); return P.mix(col, P.hex('#4b4860'), noise(x * 0.01, y * 0.01) * 0.5); },
      angle: (x, y, R) => (R() - 0.5) * 0.5, len: [10, 30], w: [4, 9], a: [0.4, 0.7] });

    // flower beds along the path
    const fcols = ['#b8c6ee', '#d6b6cc', '#e6e3f0', '#c9c58e', '#9fb2e6'];
    for (let i = 0; i < 900; i++) {
      const y = P.rand(R, 860, SILL_B), [cx, hw] = pathCenter(y), side = R() < 0.5 ? -1 : 1;
      const x = cx + side * (hw + P.rand(R, 6, 140) * (0.4 + (y - 800) / 1200));
      if (x < WALL || x > PX0) continue;
      const sc = 0.5 + (y - 800) / 1200;
      if (R() < 0.55) P.dab(g, R, x, y, P.rand(R, 4, 9) * sc, P.css(P.jit(P.hex(P.pick(R, ['#1e3d2b', '#264a33', '#2f5a3e'])), R, 8)), 0.8);
      else P.dab(g, R, x, y, P.rand(R, 1.5, 3.2) * sc, P.pick(R, fcols), P.rand(R, 0.45, 0.85));
    }

    // trees and shrubs
    const RB = P.rng(77);
    const fcol = { base: '#10231b', dark: '#09160f', mid: '#1a3428', lit: '#3d6463' };
    foliage(g, blobRow(RB, 590, 700, 600, 700, 30, 55, 7), fcol, 1100, 1);           // shrubs before house
    foliage(g, blobRow(RB, 640, 880, 520, 1100, 60, 120, 11), fcol, 4200, 2);         // right trees
    foliage(g, blobRow(RB, 60, 300, 160, 900, 90, 170, 10), fcol, 6500, 3);           // big left tree
    foliage(g, blobRow(RB, 250, 470, 380, 760, 60, 110, 6), fcol, 2400, 4);           // left tree spill
    foliage(g, blobRow(RB, 60, 330, 900, 1500, 80, 140, 9), fcol, 5200, 5);          // left lower bushes
    foliage(g, blobRow(RB, 650, 860, 1050, 1600, 70, 130, 8), fcol, 4200, 6);         // right lower bushes
    foliage(g, blobRow(RB, 330, 460, 700, 830, 30, 55, 6), fcol, 900, 7);             // mid shrubs
    foliage(g, blobRow(RB, 560, 700, 820, 920, 30, 50, 5), fcol, 700, 8);
    foliage(g, blobRow(RB, 640, 860, 1620, 1950, 60, 110, 7), { ...fcol, lit: '#557c66' }, 3200, 9);
    foliage(g, blobRow(RB, 70, 260, 1550, 1950, 60, 110, 6), { ...fcol, lit: '#557c66' }, 2800, 10);
    // night wash: pull the whole garden toward deep moonlit blue
    g.globalCompositeOperation = 'source-atop';
    const nw = g.createLinearGradient(0, 300, 0, SILL_B);
    nw.addColorStop(0, 'rgba(10,18,48,0.42)'); nw.addColorStop(1, 'rgba(8,14,36,0.3)');
    g.fillStyle = nw; g.fillRect(0, 0, W, H);
    g.globalCompositeOperation = 'source-over';
    return c;
  }

  function makeWisp(seed, w, h) {
    const Rw = P.rng(seed), c = P.canvas(w, h), g = c.getContext('2d');
    g.filter = 'blur(7px)';
    for (let i = 0; i < 26; i++) {
      const u = Rw(), x = w * (0.1 + 0.8 * u), y = h * (0.5 + (Rw() - 0.5) * 0.35) - Math.sin(Math.PI * u) * h * 0.12;
      g.fillStyle = P.css(P.mix(P.hex('#5d6ea6'), P.hex('#b9c4e6'), Rw() * 0.7), 0.35);
      g.beginPath(); g.ellipse(x, y, P.rand(Rw, 30, 70) * (0.35 + 0.65 * Math.sin(Math.PI * u)), P.rand(Rw, 10, 22), 0, 0, TAU); g.fill();
    }
    g.filter = 'blur(3px)';
    for (let i = 0; i < 10; i++) { const x = w * P.rand(Rw, 0.25, 0.75), y = h * P.rand(Rw, 0.3, 0.45); g.fillStyle = 'rgba(215,222,245,0.25)'; g.beginPath(); g.ellipse(x, y, P.rand(Rw, 20, 50), P.rand(Rw, 5, 10), 0, 0, TAU); g.fill(); }
    return c;
  }
  const WISPS = [{ x: 380, y: 200, o: 0, s: 16, w: 420 }, { x: 720, y: 330, o: 0.5, s: 13, w: 360 }, { x: 260, y: 420, o: 0.3, s: 18, w: 320 }, { x: 640, y: 120, o: 0.75, s: 14, w: 380 }];
  function drawWisps(ctx, t) {
    WISPS.forEach((c) => {
      const p = ((t / T + c.o) % 1 + 1) % 1, x = c.x + c.s * T * (p - 0.5), a = P.smooth(0, 0.2, p) * (1 - P.smooth(0.8, 1, p));
      ctx.globalAlpha = a; ctx.drawImage(c.img, x - c.img.width / 2, c.y - c.img.height / 2);
    });
    ctx.globalAlpha = 1;
  }

  function makeBranch(seed, o) {
    const Rb = P.rng(seed), c = P.canvas(W, H), g = c.getContext('2d');
    const pts = o.pts;
    g.strokeStyle = o.stem || '#1a2418'; g.lineCap = 'round';
    for (let i = 0; i < pts.length - 1; i++) {
      g.lineWidth = o.stemW * (1 - i / pts.length * 0.7);
      g.beginPath(); g.moveTo(pts[i][0], pts[i][1]); g.lineTo(pts[i + 1][0], pts[i + 1][1]); g.stroke();
    }
    const leaves = [];
    for (let i = 0; i < o.n; i++) {
      const u = Rb(), seg = Math.min(pts.length - 2, Math.floor(u * (pts.length - 1))), f = u * (pts.length - 1) - seg;
      const a = pts[seg], b = pts[seg + 1];
      const x = a[0] + (b[0] - a[0]) * f, y = a[1] + (b[1] - a[1]) * f;
      const dir = Math.atan2(b[1] - a[1], b[0] - a[0]);
      const side = Rb() < 0.5 ? -1 : 1;
      let ang = dir + side * P.rand(Rb, 0.5, 1.2);
      ang = ang + (Math.PI / 2 - ang) * (o.droop || 0.25) * Rb();
      const len = P.rand(Rb, o.len[0], o.len[1]) * (0.75 + 0.35 * u), wid = len * P.rand(Rb, 0.22, 0.3);
      const lc = P.canvas(Math.ceil(len + 12), Math.ceil(wid * 2.6 + 12)), lg = lc.getContext('2d'), lox = 6, loy = lc.height / 2;
      lg.translate(lox, loy);
      const lp = P.leafPath(len, wid, (Rb() - 0.5) * wid * 0.6);
      const base = P.pick(Rb, o.pal);
      lg.fillStyle = P.css(P.jit(P.hex(base), Rb, 6)); lg.fill(lp);
      lg.save(); lg.clip(lp);
      for (let k = 0; k < 7; k++) P.stroke(lg, Rb, P.rand(Rb, len * 0.2, len * 0.8), P.rand(Rb, -wid * 0.4, wid * 0.4), (Rb() - 0.5) * 0.5, len * 0.35, wid * 0.4, P.css(P.jit(P.mix(P.hex(base), P.hex(o.hi), Rb() * 0.6), Rb, 6)), 0.5);
      lg.strokeStyle = o.rim; lg.lineWidth = 2.5; lg.filter = 'blur(1px)';
      lg.beginPath(); lg.moveTo(len * 0.05, -wid * 0.1); lg.quadraticCurveTo(len * 0.45, -wid * 0.95, len, 0); lg.stroke(); lg.filter = 'none';
      lg.restore();
      lg.strokeStyle = 'rgba(0,0,0,0.25)'; lg.lineWidth = 1.2;
      lg.beginPath(); lg.moveTo(len * 0.05, 0); lg.lineTo(len * 0.9, 0); lg.stroke();
      leaves.push({ c: lc, ox: lox, oy: loy, x, y, ang, k: 7 + Math.floor(Rb() * 6), p: Rb() * TAU, f: P.rand(Rb, 0.07, 0.16) });
    }
    return { c, leaves, ax: pts[0][0], ay: pts[0][1], amp: o.amp * 2.2, k: o.k + 1, p: Rb() * TAU };
  }

  function paintFront() {
    const c = P.canvas(W, H), g = c.getContext('2d');
    // dark exterior beyond the open casement
    g.fillStyle = '#0c1a14'; g.fillRect(PX1 - 5, 0, W - PX1 + 5, SILL_B);
    P.fillStrokes(g, R, { x0: PX1, y0: 0, x1: W, y1: SILL_B, count: 1800, jit: 7, kind: 'dab', color: (x, y, R) => P.pick(R, [P.hex('#10231a'), P.hex('#163024'), P.hex('#24453a')]), w: [4, 10], a: [0.5, 0.85] });
    // casement window panel
    const fr = P.roughPath([[PX0, -30], [PX1, -30], [PX1, SILL_B + 4], [PX0, SILL_B + 4]], R, 1, 12);
    g.fillStyle = '#a3afcb'; g.fill(fr);
    const rows = 7, bar = 15, mull = 10, paneW = (PX1 - PX0 - bar * 2 - mull) / 2, top = 40, paneH = (SILL_B - top - bar - mull * (rows - 1)) / rows;
    const panes = [];
    for (let r = 0; r < rows; r++) for (let cI = 0; cI < 2; cI++) panes.push([PX0 + bar + cI * (paneW + mull), top + r * (paneH + mull), paneW, paneH]);
    P.fillStrokes(g, R, { path: fr, x0: PX0, y0: -30, x1: PX1, y1: SILL_B, count: 2600, jit: 8,
      color: (x) => P.mix(P.hex('#6f7c9c'), P.hex('#d3dcee'), P.clamp((x - PX0) / (PX1 - PX0) * 1.3 - 0.1, 0, 1)),
      angle: (x, y, R) => Math.PI / 2 + (R() - 0.5) * 0.25, len: [16, 40], w: [3, 8], a: [0.35, 0.7] });
    panes.forEach(([x, y, w, h]) => {
      const p = P.roughPath([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], R, 1.2, 10);
      g.save(); g.globalCompositeOperation = 'destination-out'; g.fill(p); g.restore();
      g.fillStyle = 'rgba(16,26,50,0.62)'; g.fill(p);
      g.save(); g.clip(p);
      for (let k = 0; k < 3; k++) P.stroke(g, R, x + w * P.rand(R, 0.2, 0.8), y + h * P.rand(R, 0.2, 0.8), -0.9, h * 0.8, P.rand(R, 6, 16), 'rgba(190,205,240,1)', 0.08);
      g.restore();
      g.strokeStyle = 'rgba(70,80,110,0.5)'; g.lineWidth = 2; g.stroke(p);
    });
    // left wall, warm lamp light from below-left
    const wallP = P.roughPath([[-10, -10], [WALL, -10], [WALL + 2, SILL_B], [-10, SILL_B]], R, 2, 12);
    const wg = g.createLinearGradient(0, 0, 0, SILL_B);
    wg.addColorStop(0, '#1b1414'); wg.addColorStop(0.55, '#3b2a24'); wg.addColorStop(1, '#8a5f45');
    g.fillStyle = wg; g.fill(wallP);
    P.fillStrokes(g, R, { path: wallP, x0: -10, y0: -10, x1: WALL + 4, y1: SILL_B, count: 1500, jit: 8,
      color: (x, y) => P.mix(P.hex('#1d1615'), P.hex('#a26c4c'), Math.pow(y / SILL_B, 2.2)), angle: () => Math.PI / 2 + (R() - 0.5) * 0.2, len: [20, 50], w: [4, 9], a: [0.3, 0.6] });
    g.fillStyle = 'rgba(0,0,0,0.35)'; g.fillRect(WALL - 4, 0, 8, SILL_B);
    // sill top surface
    const sill = P.roughPath([[WALL, SILL_B], [W + 10, SILL_B], [W + 10, SILL_F], [-10, SILL_F], [-10, SILL_B + 10]], R, 1.5, 12);
    g.fillStyle = '#a77866'; g.fill(sill);
    P.fillStrokes(g, R, { path: sill, x0: -10, y0: SILL_B, x1: W + 10, y1: SILL_F, count: 5200, jit: 8,
      color: (x, y) => { const u = x / W; let col = P.mix(P.hex('#dba083'), P.hex('#7d6a7c'), P.smooth(0.15, 0.95, u)); return P.mix(col, P.hex('#e8b896'), (1 - (y - SILL_B) / (SILL_F - SILL_B)) * 0.15 * (1 - u)); },
      angle: (x, y, R) => (R() - 0.5) * 0.15, len: [20, 60], w: [4, 9], a: [0.35, 0.7] });
    // moonlight pooling on the sill through the window
    g.save(); g.clip(sill); g.filter = 'blur(18px)'; g.fillStyle = 'rgba(160,180,240,0.16)';
    g.beginPath(); g.moveTo(330, SILL_B); g.lineTo(PX0, SILL_B); g.lineTo(PX0 + 80, SILL_F); g.lineTo(260, SILL_F); g.fill(); g.restore();
    g.fillStyle = 'rgba(40,24,22,0.5)'; g.fillRect(WALL, SILL_B - 3, W, 6);
    g.strokeStyle = 'rgba(255,214,170,0.35)'; g.lineWidth = 3; g.beginPath(); g.moveTo(0, SILL_F); g.lineTo(W, SILL_F); g.stroke();
    // front face below the sill
    const face = P.roughPath([[-10, SILL_F], [W + 10, SILL_F], [W + 10, H + 10], [-10, H + 10]], R, 1, 14);
    const fg = g.createLinearGradient(0, SILL_F, 0, H);
    fg.addColorStop(0, '#5b3e33'); fg.addColorStop(1, '#22171a');
    g.fillStyle = fg; g.fill(face);
    P.fillStrokes(g, R, { path: face, x0: -10, y0: SILL_F, x1: W + 10, y1: H + 10, count: 2600, jit: 7,
      color: (x, y) => P.mix(P.mix(P.hex('#6e4a3a'), P.hex('#3e2b2c'), x / W), P.hex('#1d1418'), (y - SILL_F) / (H - SILL_F)), angle: () => (R() - 0.5) * 0.2, len: [20, 60], w: [4, 9], a: [0.3, 0.6] });

    // cast shadows (lamp is off to the left)
    g.save(); g.filter = 'blur(12px)'; g.fillStyle = 'rgba(40,18,18,0.45)';
    g.beginPath(); g.ellipse(255, 2078, 85, 16, 0, 0, TAU); g.fill();
    g.beginPath(); g.ellipse(385, 2064, 60, 12, 0, 0, TAU); g.fill();
    g.beginPath(); g.ellipse(CAT.x + 120, CAT.base + 6, 230, 24, 0, 0, TAU); g.fill();
    g.restore();

    // terracotta pots + plants
    const pot = (cx, base, w, h) => {
      const p = P.roughPath([[cx - w / 2, base - h], [cx + w / 2, base - h], [cx + w * 0.38, base], [cx - w * 0.38, base]], R, 1, 8);
      g.fillStyle = '#a95c3a'; g.fill(p);
      P.fillStrokes(g, R, { path: p, x0: cx - w / 2, y0: base - h, x1: cx + w / 2, y1: base, count: w * h / 25, jit: 8,
        color: (x) => P.mix(P.hex('#e09464'), P.hex('#5e2c1f'), P.clamp((x - cx + w / 2) / w * 1.2, 0, 1)), angle: () => Math.PI / 2 + (R() - 0.5) * 0.3, len: [10, 24], w: [3, 7], a: [0.4, 0.75] });
      const rim = P.roughPath([[cx - w / 2 - 5, base - h - 16], [cx + w / 2 + 5, base - h - 16], [cx + w / 2 + 3, base - h + 4], [cx - w / 2 - 3, base - h + 4]], R, 1, 8);
      g.fillStyle = '#b8673f'; g.fill(rim);
      P.fillStrokes(g, R, { path: rim, x0: cx - w / 2 - 6, y0: base - h - 17, x1: cx + w / 2 + 6, y1: base - h + 5, count: w * 0.8, jit: 8,
        color: (x) => P.mix(P.hex('#f0a874'), P.hex('#6a3222'), P.clamp((x - cx + w / 2) / w * 1.2, 0, 1)), angle: () => (R() - 0.5) * 0.2, len: [10, 20], w: [3, 6], a: [0.4, 0.75] });
      g.fillStyle = '#2a1a14'; g.beginPath(); g.ellipse(cx, base - h - 14, w / 2, 5, 0, 0, TAU); g.fill();
    };
    const leafPal = ['#4f7a35', '#6b9446', '#3a5f2b', '#82a957', '#2c4a24'];
    const drawLeaf = (x, y, ang, len, wid, curve) => {
      g.save(); g.translate(x, y); g.rotate(ang);
      const lp = P.leafPath(len, wid, curve);
      const base = P.hex(P.pick(R, leafPal));
      g.fillStyle = P.css(base); g.fill(lp);
      g.save(); g.clip(lp);
      for (let k = 0; k < 6; k++) P.stroke(g, R, P.rand(R, len * 0.15, len * 0.85), P.rand(R, -wid * 0.4, wid * 0.4), (R() - 0.5) * 0.3, len * 0.3, wid * 0.5, P.css(P.jit(P.mix(base, P.hex('#b3cf78'), R() * 0.5), R, 6)), 0.5);
      g.restore();
      g.restore();
    };
    // spiky plant (pot 1)
    for (let i = 0; i < 11; i++) {
      const a = -Math.PI / 2 + (i / 10 - 0.5) * 1.6 + (R() - 0.5) * 0.15;
      drawLeaf(255 + (R() - 0.5) * 20, 1950, a, P.rand(R, 170, 300) * (1 - Math.abs(i / 10 - 0.5) * 0.6), P.rand(R, 10, 15), (i / 10 - 0.5) * 30);
    }
    pot(255, 2078, 130, 120);
    // round-leaf plant (pot 2)
    for (let i = 0; i < 16; i++) {
      const a = -Math.PI / 2 + (R() - 0.5) * 2.6;
      drawLeaf(385 + (R() - 0.5) * 16, 1975, a, P.rand(R, 55, 85), P.rand(R, 20, 28), (R() - 0.5) * 10);
    }
    pot(385, 2064, 95, 85);
    return { c, sill, wallP, face };
  }

  function makeRig() {
    return P.makeCatRig(R, CAT.h, 1.04, {
      base: '#0c0b11', jit: 4,
      color: (u, v, R) => P.pick(R, [P.hex('#141320'), P.hex('#1b1a27'), P.hex('#0f0e16'), P.hex('#22212f')]),
      edge: (u) => (u > 0 ? '#4a5378' : '#3a2522'),
      whisker: 'rgba(235,238,248,0.8)',
      pawRim: 'rgba(130,150,210,0.45)', toe: 'rgba(120,135,190,0.45)',
      rim: (g, path, d) => {
        const { ox, oy, h, cw } = d;
        g.save(); g.clip(path); g.filter = 'blur(4px)';
        const rg = g.createLinearGradient(ox - h * 0.35, 0, ox + h * 0.35, 0);
        rg.addColorStop(0, 'rgba(210,130,80,0.55)'); rg.addColorStop(0.35, 'rgba(120,80,60,0)'); rg.addColorStop(0.6, 'rgba(110,130,190,0)'); rg.addColorStop(1, 'rgba(150,170,230,0.95)');
        g.strokeStyle = rg; g.lineWidth = 16; g.stroke(path);
        g.filter = 'blur(5px)'; g.strokeStyle = 'rgba(130,150,215,0.3)'; g.lineWidth = 9;
        g.save(); g.clip(new Path2D(`M0 0 H${cw} V${oy - h * 0.6} H0 Z`)); g.stroke(path); g.restore();
        g.restore();
      },
    });
  }

  // ---- story: a moth drifts in, the cat watches, pounces, the moth escapes to the garden ----
  const MOTH = [
    [1.4, 1130, 980], [2.6, 900, 1180], [3.8, 700, 1420], [5.0, 520, 1520], [6.2, 400, 1600], [7.3, 520, 1680],
    [8.3, 455, 1640], [9.0, 410, 1700], [9.5, 395, 1690], [10.0, 360, 1560], [11.0, 300, 1330], [12.2, 470, 1120],
    [13.3, 640, 900], [14.4, 720, 700], [15.4, 690, 560],
  ];
  const mothAt = (t) => { const [x, y] = P.pathAt(t, MOTH); return [x + 12 * Math.sin(TAU * 40 * t / T), y + 9 * Math.sin(TAU * 52 * t / T + 2)]; };
  const mothA = (t) => P.keys(t, [[1.4, 0], [2.0, 1], [14.6, 1], [15.4, 0]]);
  const mothS = (t) => P.keys(t, [[10.5, 1], [15.4, 0.45]]); // shrinks as it flies far into the garden
  // a bat flits across the moonlit sky
  const BAT = [[18.4, -60, 430], [19.2, 280, 320], [19.8, 540, 300], [20.4, 790, 200], [21.0, 1150, 130]];
  const batAt = (t) => { const [x, y] = P.pathAt(t, BAT); return [x, y + 14 * Math.sin(TAU * 45 * t / T)]; };
  function drawBat(ctx, t) {
    if (t < 18.4 || t > 21.0) return;
    const [x, y] = batAt(t), f = Math.sin(TAU * 180 * t / T), s = 1.7;
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.fillStyle = '#080b17';
    [-1, 1].forEach((d) => {
      ctx.beginPath(); ctx.moveTo(0, 0);
      ctx.quadraticCurveTo(d * 10, -10 * f - 4, d * 22, -14 * f);
      ctx.quadraticCurveTo(d * 17, -4 * f + 2, d * 13, -2 * f + 4);
      ctx.quadraticCurveTo(d * 8, 0, d * 2, 4); ctx.closePath(); ctx.fill();
    });
    ctx.beginPath(); ctx.ellipse(0, 1, 3.5, 6, 0, 0, TAU); ctx.fill();
    ctx.beginPath(); ctx.moveTo(-3, -4); ctx.lineTo(-2.5, -9); ctx.lineTo(-0.5, -5); ctx.lineTo(0.5, -5); ctx.lineTo(2.5, -9); ctx.lineTo(3, -4); ctx.fill();
    ctx.restore();
  }
  function catState(t) {
    const head = [CAT.x, CAT.base - CAT.h * 0.74];
    // 1.8-15 watches & swats the moth | 15.6-18 shooting star | 18.4-21 follows a bat, then cocks its head
    // 24-24.9 head shake | 25.3-27.2 sniffs the breeze
    let lx = P.keys(t, [[0, -0.1], [15.3, -0.1], [15.9, -0.15], [16.6, 0.1], [17.2, 0.15], [18.0, -0.1], [21.0, 0.3], [22.6, 0.3], [23.2, -0.1],
      [25.0, -0.1], [25.5, -0.25], [27.0, -0.25], [27.6, -0.1], [30, -0.1]]);
    let ly = P.keys(t, [[0, 0.15], [15.3, 0.15], [15.9, 0.95], [17.2, 0.8], [18.0, 0.15], [21.0, 0.6], [22.6, 0.55], [23.2, 0.15],
      [25.0, 0.15], [25.5, 0.6], [27.0, 0.6], [27.6, 0.15], [30, 0.15]]);
    let tilt = P.keys(t, [[21.0, 0], [21.4, 0.28], [21.9, 0.28], [22.2, -0.14], [22.6, -0.14], [23.1, 0]]);
    const track = (w, at) => {
      if (w <= 0) return;
      const [mx, my] = at(t);
      lx += (P.clamp((mx - head[0]) / 300, -1, 1) - lx) * w;
      ly += (P.clamp((head[1] - my) / 520, -0.3, 1) - ly) * w;
    };
    track(P.keys(t, [[1.8, 0], [2.6, 1], [14.3, 1], [15.1, 0]]), mothAt);
    track(P.keys(t, [[18.3, 0], [18.8, 1], [20.5, 1], [21.0, 0]]), batAt);
    const shake = P.keys(t, [[24.0, 0], [24.1, 1], [24.5, 1], [24.85, 0]]), sb = Math.sin(TAU * 150 * t / T);
    lx += shake * 0.4 * sb; tilt += shake * 0.12 * Math.sin(TAU * 150 * t / T + 1);
    const sniffE = P.keys(t, [[25.5, 0], [25.8, 1], [26.7, 1], [27.0, 0]]), sniff = sniffE * Math.sin(TAU * 120 * t / T);
    ly += sniffE * 0.05 * Math.max(0, sniff);
    const exc = P.keys(t, [[2.5, 0], [4, 0.6], [8, 1], [11, 1], [14, 0.4], [15, 0]]);
    const wig = P.keys(t, [[7.9, 0], [8.2, 1], [8.8, 1], [9.05, 0]]);
    const flap = shake * Math.abs(sb) * 0.8;
    return {
      lx, ly, tilt, t, T, sniff,
      earL: Math.max(P.twitch(t, [0.8, 6.6, 12.0]), flap),
      earR: Math.max(P.twitch(t, [4.2, 28.6]), P.keys(t, [[20.9, 0], [21.2, 0.6], [22.3, 0.6], [22.6, 0]]), flap),
      alert: Math.max(exc, P.keys(t, [[18.3, 0], [18.8, 0.8], [22.6, 0.8], [23.2, 0]])), crouch: 0.5 * wig + 0.2 * exc, wiggle: wig * 8 * Math.sin(TAU * 60 * t / T),
      breath: osc(t, 8) * (1 + exc * 0.6),
      tailLift: 1.35 + 0.25 * osc(t, 3, 0.6) + 0.08 * osc(t, 7), tailFlick: exc,
    };
  }
  function drawMoth(ctx, t) {
    const a = mothA(t); if (a <= 0) return;
    const [x, y] = mothAt(t), sc = mothS(t), flap = 0.35 + 0.65 * Math.abs(Math.sin(TAU * 180 * t / T));
    P.glow(ctx, x, y, 60 * sc, [255, 230, 190], 0.25 * a);
    ctx.save(); ctx.translate(x, y); ctx.scale(sc * 1.5, sc * 1.5); ctx.rotate(0.15 * Math.sin(TAU * 14 * t / T));
    ctx.globalAlpha = a;
    [-1, 1].forEach((s) => {
      ctx.fillStyle = '#e9dcc6';
      ctx.beginPath(); ctx.ellipse(s * 11 * flap, -4, 13 * flap, 9, s * 0.5, 0, TAU); ctx.fill();
      ctx.fillStyle = '#cdbfa8';
      ctx.beginPath(); ctx.ellipse(s * 8 * flap, 7, 9 * flap, 6, -s * 0.4, 0, TAU); ctx.fill();
    });
    ctx.fillStyle = '#8a7a66'; ctx.beginPath(); ctx.ellipse(0, 1, 3, 9, 0, 0, TAU); ctx.fill();
    ctx.strokeStyle = 'rgba(120,100,80,0.8)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(-1, -8); ctx.lineTo(-6, -16); ctx.moveTo(1, -8); ctx.lineTo(6, -16); ctx.stroke();
    ctx.restore(); ctx.globalAlpha = 1;
  }
  // sheer curtain breathing in the night breeze
  function drawCurtain(ctx, t) {
    const gust = 1 + 0.8 * Math.pow(Math.max(0, Math.sin(TAU * 3 * t / T)), 3);
    const right = (y) => { const f = y / SILL_B; return 120 + 40 * f + f * gust * (40 * Math.sin(TAU * 4 * t / T - y * 0.003) + 15 * Math.sin(TAU * 9 * t / T - y * 0.007 + 1)); };
    ctx.save();
    ctx.beginPath(); ctx.moveTo(-10, -10);
    for (let y = -10; y <= SILL_B - 20; y += 20) ctx.lineTo(right(y), y);
    ctx.lineTo(-10, SILL_B - 20); ctx.closePath();
    const cg = ctx.createLinearGradient(0, 0, 0, SILL_B);
    cg.addColorStop(0, 'rgba(90,90,120,0.16)'); cg.addColorStop(0.6, 'rgba(180,150,140,0.2)'); cg.addColorStop(1, 'rgba(255,210,170,0.3)');
    ctx.fillStyle = cg; ctx.fill(); ctx.clip();
    for (let i = 1; i <= 7; i++) {
      const f = i / 8; ctx.beginPath();
      for (let y = -10; y <= SILL_B; y += 25) { const x = right(y) * f + 6 * Math.sin(TAU * 5 * t / T + i * 1.7 + y * 0.004); if (y < 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); }
      ctx.strokeStyle = i % 2 ? 'rgba(255,225,190,0.16)' : 'rgba(30,20,30,0.18)'; ctx.lineWidth = 7; ctx.stroke();
    }
    ctx.restore();
    ctx.strokeStyle = 'rgba(255,220,180,0.3)'; ctx.lineWidth = 2;
    ctx.beginPath(); for (let y = 0; y <= SILL_B - 20; y += 20) { const x = right(y); if (y) ctx.lineTo(x, y); else ctx.moveTo(x, y); } ctx.stroke();
  }
  // leaves falling past the window outside
  const FALL = [{ o: 0.05, x: 300 }, { o: 0.25, x: 640 }, { o: 0.45, x: 180 }, { o: 0.62, x: 520 }, { o: 0.82, x: 720 }];
  function drawFalling(ctx, t) {
    FALL.forEach((f, i) => {
      const p = ((2 * t / T + f.o) % 1 + 1) % 1; if (p > 0.6) return;
      const u = p / 0.6, y = 150 + u * 1800, x = f.x + 80 * Math.sin(TAU * 8 * t / T + i) + u * 140;
      const a = P.smooth(0, 0.08, u) * (1 - P.smooth(0.88, 1, u));
      ctx.save(); ctx.translate(x, y); ctx.rotate(0.9 * Math.sin(TAU * 8 * t / T + i + 0.8)); ctx.globalAlpha = 0.85 * a;
      ctx.fillStyle = ['#2b4a3a', '#3b5a40', '#4a5e3a', '#33503a', '#45603f'][i];
      ctx.fill(P.leafPath(34, 9, 3));
      ctx.strokeStyle = 'rgba(160,185,220,0.4)'; ctx.lineWidth = 1.2; ctx.stroke(P.leafPath(34, 9, 3));
      ctx.restore(); ctx.globalAlpha = 1;
    });
  }

  function fireflyData() {
    const list = [];
    for (let i = 0; i < 30; i++) list.push({ x: P.rand(R, 110, 820), y: P.rand(R, 680, 1940), ax: P.rand(R, 15, 50), ay: P.rand(R, 10, 35), k1: 1 + Math.floor(R() * 2), k2: 1 + Math.floor(R() * 3), k3: 2 + Math.floor(R() * 4), p1: R() * TAU, p2: R() * TAU, p3: R() * TAU, size: P.rand(R, 0.6, 1.2) * (0.6 + (i % 10) / 18) });
    return list;
  }
  function drawFirefly(ctx, f, t) {
    const x = f.x + f.ax * Math.sin(TAU * f.k1 * t / T + f.p1), y = f.y + f.ay * Math.sin(TAU * f.k2 * t / T + f.p2);
    const b = Math.pow(0.5 + 0.5 * Math.sin(TAU * f.k3 * t / T + f.p3), 2);
    if (b < 0.02) return;
    P.glow(ctx, x, y, 24 * f.size + 8, [210, 240, 120], 0.45 * b);
    ctx.fillStyle = `rgba(255,252,210,${0.9 * b})`; ctx.beginPath(); ctx.arc(x, y, 2.2 * f.size + 0.6, 0, TAU); ctx.fill();
  }

  function starData() {
    const s = [];
    for (let i = 0; i < 70; i++) s.push({ x: R() * W, y: Math.pow(R(), 1.2) * 520, r: P.rand(R, 0.9, 2), k: 1 + Math.floor(R() * 4), p: R() * TAU });
    [[420, 130], [760, 300], [330, 360], [700, 110]].forEach(([x, y]) => s.push({ x, y, r: 2.2, k: 1 + Math.floor(R() * 3), p: R() * TAU, ray: 12 }));
    return s;
  }

  return {
    W, H, T,
    async init() {
      L.sky = paintSky(); L.moon = paintMoon(); L.back = paintBack(); L.front = paintFront(); L.cat = makeRig();
      L.tail = P.makeTail(72, { base: '#100f17', light: '#3b4466', shade: '#07060b', edge: '#5a3a2e' });
      L.stars = starData(); L.ff = fireflyData();
      WISPS.forEach((c, i) => { c.img = makeWisp(300 + i, c.w, 130); });
      const onW = L.windows.filter((w) => w.on), offW = L.windows.filter((w) => !w.on);
      L.switchWin = onW[3]; L.switchWin2 = offW[0]; if (L.switchWin2) L.switchWin2.on = true;
      const darkPal = ['#0e2218', '#14301f', '#1a3a27', '#21452f'];
      L.mid = makeBranch(31, { pts: [[60, 1560], [170, 1470], [280, 1390], [390, 1330], [470, 1300]], n: 26, len: [60, 95], stemW: 6, pal: darkPal, hi: '#3f6b5a', rim: 'rgba(150,180,220,0.35)', amp: 0.018, k: 2, droop: 0.3 });
      L.fg = [
        makeBranch(41, { pts: [[-40, 40], [80, 90], [200, 130], [310, 150], [420, 190]], n: 34, len: [80, 140], stemW: 9, pal: darkPal, hi: '#3b6655', rim: 'rgba(160,185,230,0.4)', amp: 0.012, k: 2, droop: 0.35 }),
        makeBranch(42, { pts: [[1120, 20], [1000, 70], [880, 110], [760, 140], [680, 175]], n: 34, len: [80, 140], stemW: 9, pal: darkPal, hi: '#3b6655', rim: 'rgba(160,185,230,0.4)', amp: 0.012, k: 3, droop: 0.35 }),
        makeBranch(43, { pts: [[1120, 260], [1040, 330], [990, 420], [960, 520]], n: 16, len: [70, 110], stemW: 6, pal: darkPal, hi: '#3b6655', rim: 'rgba(160,185,230,0.35)', amp: 0.02, k: 2, droop: 0.4 }),
        makeBranch(44, { pts: [[1130, 2430], [1040, 2330], [950, 2270], [850, 2240], [760, 2250]], n: 30, len: [90, 160], stemW: 8, pal: ['#0d1e15', '#132a1d', '#193524', '#1f3f2b'], hi: '#40624f', rim: 'rgba(200,170,140,0.3)', amp: 0.016, k: 2, droop: 0.1 }),
        makeBranch(45, { pts: [[1130, 2200], [1060, 2120], [1000, 2060]], n: 12, len: [80, 130], stemW: 6, pal: ['#0d1e15', '#132a1d', '#193524'], hi: '#40624f', rim: 'rgba(160,185,230,0.3)', amp: 0.02, k: 3, droop: 0.1 }),
      ];
      L.interior = new Path2D(); L.interior.addPath(L.front.wallP); L.interior.addPath(L.front.sill); L.interior.addPath(L.front.face);
      L.text = opts.text === false ? null : P.textLayer(W, H, ['And for a little while,', 'the stars will keep watch.'], 458, 1040, 82, 56, '#f8eedb', 'rgba(255,220,170,0.5)');
      L.vig = P.vignette(W, H, 0.5); L.grain = P.grain(W, H, 4, 34);
    },
    frame(ctx, t) {
      ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
      ctx.drawImage(L.sky, 0, 0);
      L.stars.forEach((s) => {
        const a = 0.55 + 0.45 * Math.sin(TAU * s.k * t / T + s.p);
        ctx.fillStyle = `rgba(245,246,255,${a})`; ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, TAU); ctx.fill();
        if (s.ray) {
          P.glow(ctx, s.x, s.y, 18, [200, 215, 255], 0.35 * a);
          ctx.strokeStyle = `rgba(240,244,255,${0.6 * a})`; ctx.lineWidth = 1.1;
          const rr = s.ray * (0.75 + 0.25 * a);
          ctx.beginPath(); ctx.moveTo(s.x - rr, s.y); ctx.lineTo(s.x + rr, s.y); ctx.moveTo(s.x, s.y - rr); ctx.lineTo(s.x, s.y + rr); ctx.stroke();
        }
      });
      // shooting star
      if (t > 15.9 && t < 16.9) {
        const u = (t - 15.9) / 1.0, e = 1 - Math.pow(1 - u, 2), a = Math.sin(Math.PI * u);
        const sx = 330, sy = 90, ex = 700, ey = 260, hx = sx + (ex - sx) * e, hy = sy + (ey - sy) * e, dl = Math.hypot(ex - sx, ey - sy), tl = 150 * a;
        const lg = ctx.createLinearGradient(hx - (ex - sx) / dl * tl, hy - (ey - sy) / dl * tl, hx, hy);
        lg.addColorStop(0, 'rgba(220,230,255,0)'); lg.addColorStop(1, `rgba(255,255,255,${0.9 * a})`);
        ctx.strokeStyle = lg; ctx.lineWidth = 2.2; ctx.lineCap = 'round';
        ctx.beginPath(); ctx.moveTo(hx - (ex - sx) / dl * tl, hy - (ey - sy) / dl * tl); ctx.lineTo(hx, hy); ctx.stroke();
        P.glow(ctx, hx, hy, 12, [220, 230, 255], 0.7 * a);
      }
      const hal = 0.9 + 0.1 * osc(t, 2);
      P.glow(ctx, MOON.x, MOON.y, 260, [170, 185, 240], 0.3 * hal);
      ctx.drawImage(L.moon, MOON.x - L.moon.width / 2, MOON.y - L.moon.height / 2);
      drawWisps(ctx, t);
      drawBat(ctx, t);
      ctx.drawImage(L.back, 0, 0);
      // lit windows of the distant house
      L.windows.forEach((w) => {
        if (!w.on) return;
        let a = 0.82 + 0.12 * Math.sin(TAU * w.k * t / T + w.p) + 0.06 * Math.sin(TAU * 9 * t / T + w.p * 3);
        if (w === L.switchWin) a *= P.keys(t, [[5.8, 1], [6.1, 0], [13.6, 0], [13.9, 1]]);
        if (w === L.switchWin2) a *= P.keys(t, [[2.0, 0], [2.3, 1], [17.6, 1], [17.9, 0]]);
        ctx.fillStyle = `rgba(255,205,120,${a})`; ctx.fillRect(w.x, w.y, w.w, w.h);
        P.glow(ctx, w.x + w.w / 2, w.y + w.h / 2, 22, [255, 190, 100], 0.35 * a);
      });
      L.ff.forEach((f) => drawFirefly(ctx, f, t));
      const sway = (b) => {
        const gust = 1 + 0.9 * Math.pow(Math.max(0, Math.sin(TAU * 3 * t / T - b.ax * 0.001)), 3);
        const a = gust * b.amp * (Math.sin(TAU * b.k * t / T + b.p) * 0.8 + 0.2 * Math.sin(TAU * (b.k * 3) * t / T + b.p * 2));
        ctx.save(); ctx.translate(b.ax, b.ay); ctx.rotate(a); ctx.translate(-b.ax, -b.ay); ctx.drawImage(b.c, 0, 0);
        b.leaves.forEach((l) => {
          ctx.save(); ctx.translate(l.x, l.y); ctx.rotate(l.ang + gust * l.f * Math.sin(TAU * l.k * t / T + l.p));
          ctx.drawImage(l.c, -l.ox, -l.oy); ctx.restore();
        });
        ctx.restore();
      };
      drawFalling(ctx, t);
      sway(L.mid);
      ctx.drawImage(L.front.c, 0, 0);
      drawCurtain(ctx, t);
      // flickering lamp glow on the interior
      const fl = 0.85 + 0.06 * osc(t, 7) + 0.05 * osc(t, 13, 1.3) + 0.04 * osc(t, 29, 2.1);
      ctx.save(); ctx.clip(L.interior); ctx.globalCompositeOperation = 'screen';
      const lg = ctx.createRadialGradient(-120, 2260, 0, -120, 2260, 1300);
      lg.addColorStop(0, `rgba(255,170,90,${0.42 * fl})`); lg.addColorStop(0.5, `rgba(255,150,80,${0.14 * fl})`); lg.addColorStop(1, 'rgba(255,150,80,0)');
      ctx.fillStyle = lg; ctx.fillRect(0, 0, W, H); ctx.restore();
      // cat
      const st = catState(t);
      st.tail = (c) => P.drawTail(c, L.tail, CAT.h, -1, st.tailLift, TAU * 3 * t / T, st.tailFlick);
      P.drawCat(ctx, L.cat, CAT.x, CAT.base, st);
      drawMoth(ctx, t);
      L.fg.forEach(sway);
      if (L.text) ctx.drawImage(L.text, 0, 0);
      ctx.drawImage(L.vig, 0, 0);
      ctx.globalCompositeOperation = 'soft-light'; ctx.globalAlpha = 0.55;
      ctx.drawImage(L.grain, 0, 0);
      ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
    },
  };
};
