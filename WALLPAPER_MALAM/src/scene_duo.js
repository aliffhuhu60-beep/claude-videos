// Tablet version — the white cat and the black cat side by side on a lamp-lit sill,
// watching a moonlit hill. Square 2304x2304 so it crops cleanly to landscape (2304x1440)
// and portrait (1440x2304); everything important sits in the central 1440x1440 square.
window.SCENES = window.SCENES || {};
SCENES.duo = function (opts) {
  const S = 2304, W = S, H = S, T = 15, TAU = P.TAU;
  const osc = (t, k, p = 0) => Math.sin(TAU * k * t / T + p);
  const R = P.rng(57), noise = P.makeNoise(13);
  const OP = { x0: 200, x1: 2104, y0: 110, y1: 1700 };   // window opening
  const SILL_F = 1860;
  const MOON = { x: 1500, y: 640, r: 82 };
  const WC = { x: 975, base: 1790, h: 410 };              // white cat
  const BC = { x: 1335, base: 1790, h: 420 };             // black cat
  const HEART = { x: 1150, y: 1794 };
  const CANDLE = { x: 760, y: 1772 };
  const hillY = (x) => 1530 - 90 * (x / S) - 40 * Math.sin(Math.PI * x / S);
  const mtnY = (x) => 1405 + 30 * Math.sin(x * 0.004 + 0.6) + 16 * Math.sin(x * 0.011 + 2);
  const skyStops = [[0, P.hex('#050b22')], [0.35, P.hex('#0b1840')], [0.7, P.hex('#183064')], [1, P.hex('#33528c')]];
  const skyCol = (y) => P.grad(skyStops, y / 1500);
  const L = {};

  // ---------------- sky ----------------
  function paintSky() {
    const c = P.canvas(W, H), g = c.getContext('2d');
    const lg = g.createLinearGradient(0, 0, 0, 1500);
    skyStops.forEach((s) => lg.addColorStop(s[0], P.css(s[1])));
    g.fillStyle = lg; g.fillRect(0, 0, W, 1750);
    P.fillStrokes(g, R, {
      x0: -30, y0: -30, x1: W + 30, y1: 1750, count: 30000, jit: 8,
      color: (x, y) => {
        let col = skyCol(y);
        const n = noise(x * 0.003, y * 0.003);
        col = P.mix(col, P.hex('#5468a8'), Math.max(0, n - 0.55) * 0.7);
        const dm = Math.hypot(x - MOON.x, y - MOON.y);
        if (dm < 700) col = P.mix(col, P.hex('#7186c4'), Math.pow(1 - dm / 700, 1.6) * 0.45);
        return col;
      },
      angle: (x, y, R) => (R() - 0.5) * 0.55, len: [40, 120], w: [10, 26], a: [0.16, 0.36],
    });
    const ax = -100, ay = 250, bx = 2400, by = 1150, ang = Math.atan2(by - ay, bx - ax);
    for (let i = 0; i < 2600; i++) {
      const u = R(), off = (R() + R() + R() - 1.5) * 150;
      const x = ax + (bx - ax) * u - Math.sin(ang) * off, y = ay + (by - ay) * u + Math.cos(ang) * off;
      g.fillStyle = `rgba(225,232,255,${P.rand(R, 0.12, 0.5)})`; g.beginPath(); g.arc(x, y, P.rand(R, 0.5, 1.3), 0, TAU); g.fill();
    }
    for (let i = 0; i < 3800; i++) {
      const x = R() * W, y = Math.pow(R(), 1.2) * 1650;
      const a = P.rand(R, 0.15, 0.65) * (1 - P.smooth(1200, 1650, y) * 0.85);
      g.fillStyle = `rgba(236,240,255,${a})`; g.beginPath(); g.arc(x, y, P.rand(R, 0.6, 1.6), 0, TAU); g.fill();
    }
    return c;
  }

  function paintMoon() {
    const r = MOON.r, s = r * 2 + 40, c = P.canvas(s, s), g = c.getContext('2d'), m = s / 2;
    const disc = new Path2D(); disc.arc(m, m, r, 0, TAU);
    const rg = g.createRadialGradient(m - r * 0.3, m - r * 0.3, r * 0.1, m, m, r);
    rg.addColorStop(0, '#fffaea'); rg.addColorStop(1, '#eadfbf');
    g.fillStyle = rg; g.fill(disc);
    P.fillStrokes(g, R, { path: disc, x0: m - r, y0: m - r, x1: m + r, y1: m + r, count: 520, jit: 8,
      color: (x, y) => (noise(x * 0.04, y * 0.04) > 0.55 ? P.hex('#d6c9a4') : P.hex('#fbf3dc')),
      angle: (x, y, R) => (R() - 0.5) * 1.2, len: [8, 22], w: [4, 10], a: [0.3, 0.6] });
    return c;
  }

  function makeCloud(w, h, seed, light) {
    const Rc = P.rng(seed), c = P.canvas(w + 100, h + 100), g = c.getContext('2d');
    g.translate(50, 50);
    const base = h * 0.82, puffs = [];
    const n = 6 + Math.floor(Rc() * 4);
    for (let i = 0; i < n; i++) {
      const u = (i + 0.5) / n, bell = Math.sin(Math.PI * u);
      const r = h * (0.15 + 0.27 * bell) * P.rand(Rc, 0.82, 1.12);
      puffs.push([w * (0.08 + 0.84 * u) + P.rand(Rc, -12, 12), base - r * P.rand(Rc, 0.45, 0.75), r]);
    }
    for (let i = 0; i < 3; i++) { const r = h * P.rand(Rc, 0.17, 0.25); puffs.push([w * P.rand(Rc, 0.3, 0.68), base - h * 0.42 - r * 0.25, r]); }
    const path = new Path2D();
    puffs.forEach(([x, y, r]) => { path.moveTo(x + r, y); path.arc(x, y, r, 0, TAU); });
    const top = Math.min(...puffs.map((p) => p[1] - p[2]));
    const LT = P.hex('#d3d9ef'), MID = P.hex('#7d8bbb'), DK = P.hex('#36456f');
    const colAt = (x, y) => {
      const v = P.clamp((y - top) / (base - top), 0, 1);
      let col = v < 0.5 ? P.mix(LT, MID, v / 0.5) : P.mix(MID, DK, (v - 0.5) / 0.5);
      let best = puffs[0], bd = 1e9;
      puffs.forEach((p) => { const d = Math.hypot(x - p[0], y - p[1]) - p[2]; if (d < bd) { bd = d; best = p; } });
      const lit = Math.max(0, (x - best[0]) / best[2] * light[0] + (y - best[1]) / best[2] * light[1]);
      return P.mix(col, P.hex('#e8ecfa'), lit * 0.55);
    };
    const inside = (x, y, skip) => puffs.some((q) => q !== skip && Math.hypot(x - q[0], y - q[1]) < q[2] * 0.97);
    g.save();
    const cp = [[-50, -50], [w + 50, -50], [w + 50, base]];
    for (let x = w + 40; x >= -40; x -= 18) cp.push([x, base + 6 + Math.sin(x * 0.05) * 5 + (Rc() - 0.5) * 8]);
    g.clip(P.roughPath(cp, Rc, 1.5, 9));
    g.filter = 'blur(5px)'; g.fillStyle = P.css(P.mix(MID, DK, 0.3)); g.fill(path); g.filter = 'none';
    P.fillStrokes(g, Rc, { path, x0: 0, y0: top, x1: w, y1: base + 8, count: Math.round(w * h / 30), jit: 11,
      color: colAt, angle: (x, y, R) => (R() - 0.5) * 1.1, len: [10, 30], w: [5, 14], a: [0.3, 0.65] });
    puffs.forEach((p) => {
      for (let i = 0; i < p[2] * 1.6; i++) {
        const an = Rc() * TAU, rr = p[2] * P.rand(Rc, 0.9, 1.06), x = p[0] + Math.cos(an) * rr, y = p[1] + Math.sin(an) * rr;
        if (y > base || inside(x, y, p)) continue;
        P.stroke(g, Rc, x, y, an + Math.PI / 2 + (Rc() - 0.5) * 0.9, P.rand(Rc, 8, 22), P.rand(Rc, 4, 10), P.css(P.jit(colAt(x, y), Rc, 8)), P.rand(Rc, 0.2, 0.45));
      }
    });
    g.restore();
    return c;
  }
  const CLOUDS = [
    { w: 700, h: 260, x: 700, y: 560, o: 0.0, s: 22 }, { w: 620, h: 230, x: 1750, y: 900, o: 0.5, s: 18 },
    { w: 420, h: 160, x: 520, y: 1150, o: 0.3, s: 26 }, { w: 460, h: 170, x: 1900, y: 1260, o: 0.8, s: 20 },
    { w: 520, h: 190, x: 1250, y: 300, o: 0.65, s: 24 }, { w: 380, h: 140, x: 300, y: 300, o: 0.15, s: 28 },
    { w: 400, h: 150, x: 1300, y: 1330, o: 0.4, s: 16 },
  ];
  function drawClouds(ctx, t) {
    CLOUDS.forEach((c) => {
      const p = ((t / T + c.o) % 1 + 1) % 1, x = c.x + c.s * T * (p - 0.5), a = P.smooth(0, 0.2, p) * (1 - P.smooth(0.8, 1, p));
      ctx.globalAlpha = 0.92 * a; ctx.drawImage(c.img, x - c.img.width / 2, c.y - c.img.height * 0.6);
    });
    ctx.globalAlpha = 1;
  }

  // ---------------- land outside ----------------
  function paintLand() {
    const c = P.canvas(W, H), g = c.getContext('2d');
    const mp = [];
    for (let x = -10; x <= W + 10; x += 6) mp.push([x, mtnY(x) - Math.abs(Math.sin(x * 0.08)) * 8 - noise(x * 0.015, 3) * 14]);
    mp.push([W + 10, 1800], [-10, 1800]);
    const mpath = P.roughPath(mp, R, 1.5, 6);
    g.fillStyle = '#142a3c'; g.fill(mpath);
    P.fillStrokes(g, R, { path: mpath, x0: -10, y0: 1330, x1: W + 10, y1: 1800, count: 7000, jit: 7,
      color: (x, y) => { const d = y - mtnY(x); return d < 30 ? P.hex('#2c4b62') : P.mix(P.hex('#1d3a4c'), P.hex('#11233a'), P.clamp(d / 200, 0, 1)); },
      angle: (x, y, R) => (R() - 0.5) * 0.5, len: [20, 60], w: [5, 12], a: [0.3, 0.6] });
    const mist = g.createLinearGradient(0, 1420, 0, 1560);
    mist.addColorStop(0, 'rgba(120,140,200,0)'); mist.addColorStop(0.5, 'rgba(120,140,200,0.16)'); mist.addColorStop(1, 'rgba(120,140,200,0)');
    g.fillStyle = mist; g.fillRect(0, 1420, W, 140);
    const hp = [];
    for (let x = -10; x <= W + 10; x += 4) hp.push([x, hillY(x) - (R() < 0.3 ? R() * 12 : R() * 4)]);
    hp.push([W + 10, 1800], [-10, 1800]);
    const hpath = P.roughPath(hp, R, 1, 4);
    g.fillStyle = '#1b3428'; g.fill(hpath);
    const pal = [P.hex('#22402f'), P.hex('#2a4a37'), P.hex('#1c3628'), P.hex('#162e22')];
    P.fillStrokes(g, R, { path: hpath, x0: -10, y0: 1400, x1: W + 10, y1: 1800, count: 22000, jit: 7,
      color: (x, y, R) => {
        const d = y - hillY(x);
        let col = P.mix(P.pick(R, pal), P.hex('#0e2017'), P.clamp(d / 260, 0, 1) * 0.6);
        if (d < 70) col = P.mix(col, P.hex('#46676a'), (1 - d / 70) * 0.6);
        if (R() < 0.06) col = P.mix(col, P.hex('#56726a'), 0.55);
        return col;
      },
      angle: (x, y, R) => -Math.PI / 2 + (R() - 0.5) * 0.5, len: [10, 30], w: [3, 8], a: [0.35, 0.7] });
    for (let i = 0; i < 160; i++) {
      const x = R() * W, y = P.rand(R, hillY(x) + 20, 1700);
      g.globalAlpha = P.rand(R, 0.25, 0.6); g.fillStyle = P.pick(R, ['#c9d3ee', '#e6dfc6', '#b9c4e6', '#d8c3d8']);
      g.beginPath(); g.arc(x, y, P.rand(R, 1.2, 2.4), 0, TAU); g.fill();
    }
    g.globalAlpha = 1;
    return c;
  }

  // ---------------- room: wall, frame, sill, pots, candle ----------------
  function paintRoom() {
    const c = P.canvas(W, H), g = c.getContext('2d');
    // wall around the opening
    const wall = new Path2D(); wall.rect(-10, -10, W + 20, OP.y1 + 10);
    const hole = new Path2D(); hole.rect(OP.x0, OP.y0, OP.x1 - OP.x0, OP.y1 - OP.y0);
    const wallP = new Path2D(); wallP.addPath(wall); wallP.addPath(hole);
    g.save(); g.fillStyle = '#2a1e1c'; g.fill(wallP, 'evenodd');
    g.clip(wallP, 'evenodd');
    P.fillStrokes(g, R, { x0: -10, y0: -10, x1: W + 10, y1: OP.y1, count: 4200, jit: 8,
      where: (x, y) => x < OP.x0 || x > OP.x1 || y < OP.y0,
      color: (x, y) => P.mix(P.hex('#1f1716'), P.hex('#8a5f45'), Math.pow(y / OP.y1, 2.4) * (x < S / 2 ? 1 : 0.7)),
      angle: () => Math.PI / 2 + (R() - 0.5) * 0.2, len: [30, 70], w: [5, 12], a: [0.3, 0.6] });
    g.restore();
    // painted window frame (moonlit cream)
    const fw = 26;
    const frame = (x, y, w, h) => {
      const p = P.roughPath([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], R, 1, 10);
      g.fillStyle = '#9ea9c4'; g.fill(p);
      P.fillStrokes(g, R, { path: p, x0: x, y0: y, x1: x + w, y1: y + h, count: (w * h) / 60, jit: 8,
        color: (px) => P.mix(P.hex('#727e9e'), P.hex('#d6deee'), P.clamp((px - x) / w, 0, 1)),
        angle: () => (w > h ? 0 : Math.PI / 2) + (R() - 0.5) * 0.2, len: [16, 40], w: [3, 7], a: [0.35, 0.7] });
    };
    frame(OP.x0 - fw, OP.y0 - fw, OP.x1 - OP.x0 + 2 * fw, fw);
    frame(OP.x0 - fw, OP.y0, fw, OP.y1 - OP.y0);
    frame(OP.x1, OP.y0, fw, OP.y1 - OP.y0);
    // open casement panels folded against both sides
    [[OP.x0, 1], [OP.x1 - 150, -1]].forEach(([px]) => {
      const pw = 150;
      const pp = P.roughPath([[px, OP.y0], [px + pw, OP.y0], [px + pw, OP.y1], [px, OP.y1]], R, 1, 12);
      g.fillStyle = '#a3afcb'; g.fill(pp);
      const rows = 7, bar = 14, paneH = (OP.y1 - OP.y0 - bar * (rows + 1)) / rows;
      for (let r = 0; r < rows; r++) {
        const y = OP.y0 + bar + r * (paneH + bar), q = P.roughPath([[px + bar, y], [px + pw - bar, y], [px + pw - bar, y + paneH], [px + bar, y + paneH]], R, 1.2, 10);
        g.save(); g.globalCompositeOperation = 'destination-out'; g.fill(q); g.restore();
        g.fillStyle = 'rgba(16,26,50,0.6)'; g.fill(q);
        g.save(); g.clip(q); P.stroke(g, R, px + pw / 2, y + paneH / 2, -0.9, paneH * 0.9, 18, 'rgba(190,205,240,1)', 0.08); g.restore();
      }
    });
    // sill
    const sill = P.roughPath([[OP.x0 - 40, OP.y1], [OP.x1 + 40, OP.y1], [W + 10, SILL_F], [-10, SILL_F]], R, 1.5, 14);
    g.fillStyle = '#a77866'; g.fill(sill);
    P.fillStrokes(g, R, { path: sill, x0: -10, y0: OP.y1, x1: W + 10, y1: SILL_F, count: 9000, jit: 8,
      color: (x) => { const d = Math.abs(x - CANDLE.x) / 1500; return P.mix(P.hex('#dba083'), P.hex('#7d6a7c'), P.smooth(0.05, 1, d)); },
      angle: (x, y, R) => (R() - 0.5) * 0.15, len: [24, 70], w: [4, 10], a: [0.35, 0.7] });
    g.save(); g.clip(sill); g.filter = 'blur(24px)'; g.fillStyle = 'rgba(160,180,240,0.14)';
    g.beginPath(); g.moveTo(1100, OP.y1); g.lineTo(1950, OP.y1); g.lineTo(2100, SILL_F); g.lineTo(1150, SILL_F); g.fill(); g.restore();
    g.fillStyle = 'rgba(40,24,22,0.5)'; g.fillRect(OP.x0 - 40, OP.y1 - 3, OP.x1 - OP.x0 + 80, 7);
    g.strokeStyle = 'rgba(255,214,170,0.35)'; g.lineWidth = 4; g.beginPath(); g.moveTo(0, SILL_F); g.lineTo(W, SILL_F); g.stroke();
    const face = P.roughPath([[-10, SILL_F], [W + 10, SILL_F], [W + 10, H + 10], [-10, H + 10]], R, 1, 14);
    const fg = g.createLinearGradient(0, SILL_F, 0, H);
    fg.addColorStop(0, '#5b3e33'); fg.addColorStop(1, '#1e1517');
    g.fillStyle = fg; g.fill(face);
    P.fillStrokes(g, R, { path: face, x0: -10, y0: SILL_F, x1: W + 10, y1: H + 10, count: 5000, jit: 7,
      color: (x, y) => P.mix(P.hex('#6e4a3a'), P.hex('#1d1418'), (y - SILL_F) / (H - SILL_F)), angle: () => (R() - 0.5) * 0.2, len: [24, 70], w: [4, 10], a: [0.3, 0.6] });
    // soft cast shadows on the sill (candle is to the left)
    g.save(); g.filter = 'blur(14px)'; g.fillStyle = 'rgba(40,18,18,0.42)';
    g.beginPath(); g.ellipse(WC.x + 110, WC.base + 6, 210, 22, 0, 0, TAU); g.fill();
    g.beginPath(); g.ellipse(BC.x + 120, BC.base + 6, 220, 22, 0, 0, TAU); g.fill();
    g.beginPath(); g.ellipse(690, 1790, 80, 14, 0, 0, TAU); g.fill();
    g.beginPath(); g.ellipse(1720, 1784, 70, 12, 0, 0, TAU); g.fill();
    g.restore();
    // pots
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
      const lp = P.leafPath(len, wid, curve), base = P.hex(P.pick(R, leafPal));
      g.fillStyle = P.css(base); g.fill(lp);
      g.save(); g.clip(lp);
      for (let k = 0; k < 6; k++) P.stroke(g, R, P.rand(R, len * 0.15, len * 0.85), P.rand(R, -wid * 0.4, wid * 0.4), (R() - 0.5) * 0.3, len * 0.3, wid * 0.5, P.css(P.jit(P.mix(base, P.hex('#b3cf78'), R() * 0.5), R, 6)), 0.5);
      g.restore(); g.restore();
    };
    for (let i = 0; i < 12; i++) {
      const a = -Math.PI / 2 + (i / 11 - 0.5) * 1.6 + (R() - 0.5) * 0.15;
      drawLeaf(620 + (R() - 0.5) * 20, 1660, a, P.rand(R, 180, 320) * (1 - Math.abs(i / 11 - 0.5) * 0.6), P.rand(R, 11, 16), (i / 11 - 0.5) * 30);
    }
    pot(620, 1792, 140, 128);
    for (let i = 0; i < 18; i++) drawLeaf(1700 + (R() - 0.5) * 18, 1690, -Math.PI / 2 + (R() - 0.5) * 2.6, P.rand(R, 60, 92), P.rand(R, 22, 30), (R() - 0.5) * 10);
    pot(1700, 1786, 105, 92);
    // candle jar
    const jx = CANDLE.x, jy = CANDLE.y;
    g.fillStyle = 'rgba(255,220,170,0.25)'; g.beginPath(); g.roundRect(jx - 32, jy - 74, 64, 78, 10); g.fill();
    g.strokeStyle = 'rgba(255,235,200,0.45)'; g.lineWidth = 2.5; g.stroke();
    g.fillStyle = '#efe2cc'; g.beginPath(); g.roundRect(jx - 22, jy - 44, 44, 46, 6); g.fill();
    g.fillStyle = 'rgba(255,255,255,0.35)'; g.fillRect(jx - 26, jy - 66, 6, 58);
    paintStrands(g);
    return { c, sill, face, wallP };
  }

  // ---------------- leaves (per-leaf flutter) ----------------
  function makeBranch(seed, o) {
    const Rb = P.rng(seed), c = P.canvas(W, H), g = c.getContext('2d');
    const pts = o.pts;
    g.strokeStyle = '#1a2418'; g.lineCap = 'round';
    for (let i = 0; i < pts.length - 1; i++) {
      g.lineWidth = o.stemW * (1 - i / pts.length * 0.7);
      g.beginPath(); g.moveTo(pts[i][0], pts[i][1]); g.lineTo(pts[i + 1][0], pts[i + 1][1]); g.stroke();
    }
    const leaves = [];
    for (let i = 0; i < o.n; i++) {
      const u = Rb(), seg = Math.min(pts.length - 2, Math.floor(u * (pts.length - 1))), f = u * (pts.length - 1) - seg;
      const a = pts[seg], b = pts[seg + 1];
      const x = a[0] + (b[0] - a[0]) * f, y = a[1] + (b[1] - a[1]) * f;
      const dir = Math.atan2(b[1] - a[1], b[0] - a[0]), side = Rb() < 0.5 ? -1 : 1;
      let ang = dir + side * P.rand(Rb, 0.5, 1.2);
      ang = ang + (Math.PI / 2 - ang) * (o.droop || 0.3) * Rb();
      const len = P.rand(Rb, o.len[0], o.len[1]) * (0.75 + 0.35 * u), wid = len * P.rand(Rb, 0.22, 0.3);
      const lc = P.canvas(Math.ceil(len + 12), Math.ceil(wid * 2.6 + 12)), lg = lc.getContext('2d'), lox = 6, loy = lc.height / 2;
      lg.translate(lox, loy);
      const lp = P.leafPath(len, wid, (Rb() - 0.5) * wid * 0.6), base = P.pick(Rb, o.pal);
      lg.fillStyle = P.css(P.jit(P.hex(base), Rb, 6)); lg.fill(lp);
      lg.save(); lg.clip(lp);
      for (let k = 0; k < 7; k++) P.stroke(lg, Rb, P.rand(Rb, len * 0.2, len * 0.8), P.rand(Rb, -wid * 0.4, wid * 0.4), (Rb() - 0.5) * 0.5, len * 0.35, wid * 0.4, P.css(P.jit(P.mix(P.hex(base), P.hex('#3b6655'), Rb() * 0.6), Rb, 6)), 0.5);
      lg.strokeStyle = 'rgba(160,185,230,0.4)'; lg.lineWidth = 2.5; lg.filter = 'blur(1px)';
      lg.beginPath(); lg.moveTo(len * 0.05, -wid * 0.1); lg.quadraticCurveTo(len * 0.45, -wid * 0.95, len, 0); lg.stroke(); lg.filter = 'none';
      lg.restore();
      lg.strokeStyle = 'rgba(0,0,0,0.25)'; lg.lineWidth = 1.2; lg.beginPath(); lg.moveTo(len * 0.05, 0); lg.lineTo(len * 0.9, 0); lg.stroke();
      leaves.push({ c: lc, ox: lox, oy: loy, x, y, ang, k: 5 + Math.floor(Rb() * 5), p: Rb() * TAU, f: P.rand(Rb, 0.07, 0.16) });
    }
    return { c, leaves, ax: pts[0][0], ay: pts[0][1], amp: o.amp, k: o.k, p: Rb() * TAU };
  }
  function drawBranch(ctx, b, t) {
    const gust = 1 + 0.9 * Math.pow(Math.max(0, Math.sin(TAU * 2 * t / T - b.ax * 0.0006)), 3);
    const a = gust * b.amp * Math.sin(TAU * b.k * t / T + b.p);
    ctx.save(); ctx.translate(b.ax, b.ay); ctx.rotate(a); ctx.translate(-b.ax, -b.ay); ctx.drawImage(b.c, 0, 0);
    b.leaves.forEach((l) => {
      ctx.save(); ctx.translate(l.x, l.y); ctx.rotate(l.ang + gust * l.f * Math.sin(TAU * l.k * t / T + l.p));
      ctx.drawImage(l.c, -l.ox, -l.oy); ctx.restore();
    });
    ctx.restore();
  }

  // ---------------- curtains ----------------
  function drawCurtain(ctx, t, side) {
    const x0 = side === 1 ? 120 : W - 120, inner = side === 1 ? 560 : W - 560;
    const gust = 1 + 0.8 * Math.pow(Math.max(0, Math.sin(TAU * 2 * t / T + (side === 1 ? 0 : 1.2))), 3);
    const edge = (y) => { const f = y / OP.y1; return inner + side * (-60 * f + f * gust * (40 * Math.sin(TAU * 3 * t / T - y * 0.0025 + side) + 14 * Math.sin(TAU * 7 * t / T - y * 0.006 + 1))); };
    ctx.save();
    ctx.beginPath(); ctx.moveTo(x0 - side * 40, 60);
    for (let y = 60; y <= OP.y1 - 10; y += 20) ctx.lineTo(edge(y), y);
    ctx.lineTo(x0 - side * 40, OP.y1 - 10); ctx.closePath();
    const cg = ctx.createLinearGradient(0, 0, 0, OP.y1);
    cg.addColorStop(0, 'rgba(90,90,120,0.2)'); cg.addColorStop(0.6, 'rgba(180,150,140,0.24)'); cg.addColorStop(1, 'rgba(255,210,170,0.34)');
    ctx.fillStyle = cg; ctx.fill(); ctx.clip();
    for (let i = 1; i <= 9; i++) {
      const f = i / 10; ctx.beginPath();
      for (let y = 60; y <= OP.y1; y += 25) { const x = x0 + (edge(y) - x0) * f + 8 * Math.sin(TAU * 4 * t / T + i * 1.7 + y * 0.003); if (y === 60) ctx.moveTo(x, y); else ctx.lineTo(x, y); }
      ctx.strokeStyle = i % 2 ? 'rgba(255,225,190,0.16)' : 'rgba(30,20,30,0.18)'; ctx.lineWidth = 10; ctx.stroke();
    }
    ctx.restore();
    ctx.strokeStyle = 'rgba(255,220,180,0.3)'; ctx.lineWidth = 2.5;
    ctx.beginPath(); for (let y = 60; y <= OP.y1 - 10; y += 20) { const x = edge(y); if (y === 60) ctx.moveTo(x, y); else ctx.lineTo(x, y); } ctx.stroke();
    // rod
    ctx.fillStyle = '#3a2a24'; ctx.fillRect(side === 1 ? 60 : W - 640, 48, 580, 14);
  }

  // ---------------- fireflies, stars ----------------
  const FF = Array.from({ length: 34 }, () => ({ x: P.rand(R, 250, 2050), y: P.rand(R, 1440, 1680), ax: P.rand(R, 20, 70), ay: P.rand(R, 10, 35),
    k1: 1 + Math.floor(R() * 2), k2: 1 + Math.floor(R() * 3), k3: 2 + Math.floor(R() * 3), p1: R() * TAU, p2: R() * TAU, p3: R() * TAU, s: P.rand(R, 0.7, 1.3) }));
  function drawFF(ctx, t) {
    FF.forEach((f) => {
      const x = f.x + f.ax * Math.sin(TAU * f.k1 * t / T + f.p1), y = f.y + f.ay * Math.sin(TAU * f.k2 * t / T + f.p2);
      const b = Math.pow(0.5 + 0.5 * Math.sin(TAU * f.k3 * t / T + f.p3), 2);
      if (b < 0.02) return;
      P.glow(ctx, x, y, 28 * f.s, [210, 240, 120], 0.45 * b);
      ctx.fillStyle = `rgba(255,252,210,${0.9 * b})`; ctx.beginPath(); ctx.arc(x, y, 2.6 * f.s, 0, TAU); ctx.fill();
    });
  }
  const STARS = Array.from({ length: 260 }, () => ({ x: R() * W, y: Math.pow(R(), 1.3) * 1400, r: P.rand(R, 1, 2.4), k: 1 + Math.floor(R() * 3), p: R() * TAU }));
  [[330, 220], [880, 160], [1950, 420], [620, 760], [1840, 1080], [2100, 220], [420, 1250]].forEach(([x, y]) => STARS.push({ x, y, r: 2.8, k: 1 + Math.floor(R() * 2), p: R() * TAU, ray: 18 }));
  function drawStars(ctx, t) {
    STARS.forEach((s) => {
      const a = 0.55 + 0.45 * Math.sin(TAU * s.k * t / T + s.p);
      ctx.fillStyle = `rgba(245,246,255,${a})`; ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, TAU); ctx.fill();
      if (s.ray) {
        P.glow(ctx, s.x, s.y, 26, [200, 215, 255], 0.35 * a);
        ctx.strokeStyle = `rgba(240,244,255,${0.6 * a})`; ctx.lineWidth = 1.3;
        const rr = s.ray * (0.75 + 0.25 * a);
        ctx.beginPath(); ctx.moveTo(s.x - rr, s.y); ctx.lineTo(s.x + rr, s.y); ctx.moveTo(s.x, s.y - rr); ctx.lineTo(s.x, s.y + rr); ctx.stroke();
      }
    });
  }
  const STAR_T0 = 3.0, STAR_D = 1.0, SS = [520, 400], SE = [1300, 690];
  const shootAt = (t) => { const u = P.clamp((t - STAR_T0) / STAR_D, 0, 1), e = 1 - Math.pow(1 - u, 2); return [SS[0] + (SE[0] - SS[0]) * e, SS[1] + (SE[1] - SS[1]) * e]; };
  function drawShootingStar(ctx, t) {
    if (t < STAR_T0 || t > STAR_T0 + STAR_D) return;
    const u = (t - STAR_T0) / STAR_D, a = Math.sin(Math.PI * u), [hx, hy] = shootAt(t);
    const dx = SE[0] - SS[0], dy = SE[1] - SS[1], dl = Math.hypot(dx, dy), tl = 260 * a;
    const tx = hx - dx / dl * tl, ty = hy - dy / dl * tl;
    const lg = ctx.createLinearGradient(tx, ty, hx, hy);
    lg.addColorStop(0, 'rgba(220,230,255,0)'); lg.addColorStop(1, `rgba(255,255,255,${0.9 * a})`);
    ctx.strokeStyle = lg; ctx.lineWidth = 3.2; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(tx, ty); ctx.lineTo(hx, hy); ctx.stroke();
    P.glow(ctx, hx, hy, 20, [220, 230, 255], 0.7 * a);
  }

  // ---------------- fairy lights along the front of the sill ----------------
  const STRANDS = [{ y: 1905, sag: 70, seg: 576, off: 0 }, { y: 2080, sag: 95, seg: 768, off: 384 }, { y: 2230, sag: 60, seg: 460, off: 120 }];
  const BULBS = [];
  STRANDS.forEach((st, si) => {
    for (let x = -40; x <= W + 40; x += 48) {
      const u = (((x + st.off) % st.seg) + st.seg) % st.seg / st.seg;
      BULBS.push({ x, y: st.y + st.sag * 4 * u * (1 - u), col: P.pick(R, [[255, 208, 138], [255, 176, 112], [255, 240, 192], [255, 196, 150]]),
        k: 1 + Math.floor(R() * 3), p: R() * TAU, si });
    }
  });
  function paintStrands(g) {
    g.strokeStyle = 'rgba(30,22,20,0.85)'; g.lineWidth = 2.2;
    STRANDS.forEach((st) => {
      g.beginPath();
      for (let x = -40; x <= W + 40; x += 6) {
        const u = (((x + st.off) % st.seg) + st.seg) % st.seg / st.seg, y = st.y + st.sag * 4 * u * (1 - u);
        if (x === -40) g.moveTo(x, y); else g.lineTo(x, y);
      }
      g.stroke();
    });
  }
  function drawBulbs(ctx, t) {
    BULBS.forEach((b) => {
      const a = 0.6 + 0.4 * Math.sin(TAU * b.k * t / T + b.p);
      P.glow(ctx, b.x, b.y + 6, 46, b.col, 0.4 * a);
      ctx.fillStyle = P.css(b.col, 0.55 + 0.45 * a); ctx.beginPath(); ctx.ellipse(b.x, b.y + 7, 5, 8, 0, 0, TAU); ctx.fill();
      ctx.fillStyle = `rgba(255,250,235,${0.5 * a})`; ctx.beginPath(); ctx.arc(b.x - 1, b.y + 5, 2, 0, TAU); ctx.fill();
    });
  }

  // ---------------- the two cats ----------------
  const BUDDY = [[7.6, 1750, 1250], [8.4, 1520, 1400], [9.2, 1320, 1470], [9.9, 1190, 1520], [10.5, 1160, 1545], [11.0, 1130, 1490],
    [11.8, 980, 1300], [12.6, 800, 1140], [13.4, 680, 980]];
  const buddyAt = (t) => { const [x, y] = P.pathAt(t, BUDDY); return [x + 12 * Math.sin(TAU * 23 * t / T), y + 9 * Math.sin(TAU * 17 * t / T + 1)]; };
  const buddyA = (t) => P.keys(t, [[7.6, 0], [8.1, 1], [12.9, 1], [13.4, 0]]);
  function look(t, cat, base) {
    const head = [cat.x, cat.base - cat.h * 0.74];
    let [lx, ly] = base;
    const track = (w, at) => {
      if (w <= 0) return;
      const [x, y] = at(t);
      lx += (P.clamp((x - head[0]) / 320, -1, 1) - lx) * w;
      ly += (P.clamp((head[1] - y) / 520, -0.3, 1) - ly) * w;
    };
    track(P.keys(t, [[2.8, 0], [3.1, 1], [4.0, 1], [4.5, 0]]), shootAt);
    track(P.keys(t, [[8.0, 0], [8.6, 1], [12.6, 1], [13.2, 0]]), buddyAt);
    return [lx, ly];
  }
  function whiteState(t) {
    const [lx, ly] = look(t, WC, [
      P.keys(t, [[0, 0.3], [4.7, 0.3], [5.2, 0.75], [7.0, 0.75], [7.5, 0.3], [15, 0.3]]),
      P.keys(t, [[0, 0.4], [4.7, 0.4], [5.2, 0.05], [7.0, 0.05], [7.5, 0.4], [15, 0.4]]),
    ]);
    return { lx, ly, t, T, tilt: P.keys(t, [[5.3, 0], [5.7, 0.14], [6.8, 0.14], [7.2, 0]]),
      earL: P.twitch(t, [1.2, 13.8]), earR: Math.max(P.twitch(t, [9.0]), P.keys(t, [[11.9, 0], [12.2, 0.55], [12.9, 0.55], [13.2, 0]])),
      alert: P.keys(t, [[8.2, 0], [8.8, 0.7], [12.2, 0.7], [12.8, 0]]), breath: osc(t, 3),
      tailLift: 1.5 + 0.2 * osc(t, 2), tailFlick: P.keys(t, [[8.6, 0], [9.2, 0.8], [12.0, 0.8], [12.6, 0]]) };
  }
  function blackState(t) {
    const [lx, ly] = look(t, BC, [
      P.keys(t, [[0, 0.12], [4.9, 0.12], [5.4, -0.75], [7.1, -0.75], [7.6, 0.12], [15, 0.12]]),
      P.keys(t, [[0, 0.42], [4.9, 0.42], [5.4, 0.05], [7.1, 0.05], [7.6, 0.42], [15, 0.42]]),
    ]);
    return { lx, ly, t, T, tilt: P.keys(t, [[5.6, 0], [6.0, -0.14], [6.9, -0.14], [7.3, 0]]),
      earL: Math.max(P.twitch(t, [2.0]), P.keys(t, [[4.6, 0], [4.8, 0.5], [5.3, 0.5], [5.5, 0]])), earR: P.twitch(t, [9.6, 14.0]),
      lean: P.keys(t, [[5.5, 0], [6.0, -0.045], [6.9, -0.045], [7.3, 0]]),
      alert: P.keys(t, [[8.2, 0], [8.8, 0.8], [12.2, 0.8], [12.8, 0]]), breath: osc(t, 3, 1.4),
      tailLift: 1.3 + 0.2 * osc(t, 3, 1) + 0.3 * P.keys(t, [[5.6, 0], [6.1, 1], [6.9, 1], [7.4, 0]]), tailFlick: P.keys(t, [[8.6, 0], [9.2, 1], [12.0, 1], [12.6, 0]]) };
  }

  return {
    W, H, T,
    async init() {
      L.sky = paintSky(); L.moon = paintMoon(); L.land = paintLand(); L.room = paintRoom();
      CLOUDS.forEach((c, i) => {
        const lt = [MOON.x - c.x, MOON.y - c.y], ll = Math.hypot(lt[0], lt[1]) || 1;
        c.img = makeCloud(c.w, c.h, 200 + i * 13, [lt[0] / ll * 0.9, lt[1] / ll * 0.9 - 0.3]);
      });
      L.white = P.makeCatRig(R, WC.h, 1, {
        base: '#d9dfec', jit: 7,
        color: (u, v) => P.mix(P.hex('#b4a8b8'), P.hex('#f7f4f2'), P.clamp(0.5 + u * 1.6 + v * 0.25, 0, 1)),
        edge: (u) => (u > 0 ? '#f2f3f8' : '#c4b4b8'), whisker: 'rgba(235,240,252,0.55)', pawRim: 'rgba(170,160,190,0.35)',
      });
      L.black = P.makeCatRig(R, BC.h, 1.04, {
        base: '#0c0b11', jit: 4,
        color: (u, v, R) => P.pick(R, [P.hex('#141320'), P.hex('#1b1a27'), P.hex('#0f0e16'), P.hex('#22212f')]),
        edge: (u) => (u > 0 ? '#4a5378' : '#3a2522'), whisker: 'rgba(235,238,248,0.8)', pawRim: 'rgba(130,150,210,0.45)', toe: 'rgba(120,135,190,0.45)',
        rim: (g, path, d) => {
          const { ox, oy, h, cw } = d;
          g.save(); g.clip(path); g.filter = 'blur(4px)';
          const rg = g.createLinearGradient(ox - h * 0.35, 0, ox + h * 0.35, 0);
          rg.addColorStop(0, 'rgba(210,130,80,0.6)'); rg.addColorStop(0.35, 'rgba(120,80,60,0)'); rg.addColorStop(0.6, 'rgba(110,130,190,0)'); rg.addColorStop(1, 'rgba(150,170,230,0.95)');
          g.strokeStyle = rg; g.lineWidth = 16; g.stroke(path);
          g.filter = 'blur(5px)'; g.strokeStyle = 'rgba(130,150,215,0.3)'; g.lineWidth = 9;
          g.save(); g.clip(new Path2D(`M0 0 H${cw} V${oy - h * 0.6} H0 Z`)); g.stroke(path); g.restore();
          g.restore();
        },
      });
      L.wTail = P.makeTail(81, { base: '#d6d4de', light: '#f6f3f1', shade: '#ad9fb0', edge: '#c3b5bb' });
      L.bTail = P.makeTail(82, { base: '#100f17', light: '#3b4466', shade: '#07060b', edge: '#5a3a2e' });
      const darkPal = ['#0e2218', '#14301f', '#1a3a27', '#21452f'];
      L.branches = [
        makeBranch(61, { pts: [[-60, 70], [160, 130], [380, 190], [560, 250], [720, 330]], n: 40, len: [110, 180], stemW: 11, pal: darkPal, amp: 0.02, k: 2, droop: 0.35 }),
        makeBranch(62, { pts: [[2364, 50], [2140, 110], [1920, 170], [1760, 230], [1620, 300]], n: 40, len: [110, 180], stemW: 11, pal: darkPal, amp: 0.02, k: 3, droop: 0.35 }),
        makeBranch(63, { pts: [[-40, 520], [120, 600], [260, 720], [340, 860]], n: 20, len: [90, 140], stemW: 7, pal: darkPal, amp: 0.03, k: 2, droop: 0.45 }),
        makeBranch(64, { pts: [[2344, 560], [2190, 660], [2060, 780], [1990, 920]], n: 20, len: [90, 140], stemW: 7, pal: darkPal, amp: 0.03, k: 3, droop: 0.45 }),
      ];
      L.text = opts.text === false ? null : P.textLayer(W, H, ['The night is softer', 'when we share it.'], S / 2, 1010, 118, 86, '#f6efdc', 'rgba(255,236,190,0.55)');
      L.vig = P.vignette(W, H, 0.5); L.grain = P.grain(W, H, 8, 32);
    },
    frame(ctx, t) {
      ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
      ctx.drawImage(L.sky, 0, 0);
      drawStars(ctx, t);
      drawShootingStar(ctx, t);
      const hal = 0.9 + 0.1 * osc(t, 2);
      P.glow(ctx, MOON.x, MOON.y, 480, [170, 185, 240], 0.3 * hal);
      P.glow(ctx, MOON.x, MOON.y, 170, [255, 245, 215], 0.4 * hal);
      ctx.drawImage(L.moon, MOON.x - L.moon.width / 2, MOON.y - L.moon.height / 2);
      drawClouds(ctx, t);
      ctx.drawImage(L.land, 0, 0);
      drawFF(ctx, t);
      ctx.drawImage(L.room.c, 0, 0);
      // candle light on the room
      const fl = 0.85 + 0.06 * osc(t, 11) + 0.05 * osc(t, 17, 1.3) + 0.04 * osc(t, 37, 2.1);
      ctx.save(); ctx.clip(L.room.sill); ctx.globalCompositeOperation = 'screen';
      const lg = ctx.createRadialGradient(CANDLE.x, CANDLE.y - 40, 0, CANDLE.x, CANDLE.y - 40, 1100);
      lg.addColorStop(0, `rgba(255,170,90,${0.45 * fl})`); lg.addColorStop(0.5, `rgba(255,150,80,${0.12 * fl})`); lg.addColorStop(1, 'rgba(255,150,80,0)');
      ctx.fillStyle = lg; ctx.fillRect(0, 0, W, H); ctx.restore();
      drawCurtain(ctx, t, 1); drawCurtain(ctx, t, -1);
      drawBulbs(ctx, t);
      // flame
      const fx = CANDLE.x + 2 * osc(t, 23), fy = CANDLE.y - 52, fh = 26 + 4 * osc(t, 31) + 2 * osc(t, 47, 1);
      P.glow(ctx, fx, fy - 6, 160, [255, 190, 110], 0.35 * fl);
      ctx.fillStyle = 'rgba(255,214,140,0.95)'; ctx.beginPath(); ctx.ellipse(fx, fy - fh * 0.35, 7, fh * 0.55, 0.05 * osc(t, 19), 0, TAU); ctx.fill();
      ctx.fillStyle = 'rgba(255,250,225,0.95)'; ctx.beginPath(); ctx.ellipse(fx, fy - fh * 0.25, 3.5, fh * 0.3, 0, 0, TAU); ctx.fill();
      // cats, then their heart-shaped tails on the sill in front
      // tails come out from behind the haunches; the white cat's curls up in the gap between them
      const ws = whiteState(t), bs = blackState(t);
      ws.tail = (c) => P.drawTail(c, L.wTail, WC.h, 1, ws.tailLift, TAU * 2 * t / T, ws.tailFlick, 0.42);
      bs.tail = (c) => P.drawTail(c, L.bTail, BC.h, 1, bs.tailLift, TAU * 2 * t / T + 1.3, bs.tailFlick, 0.5);
      P.drawCat(ctx, L.white, WC.x, WC.base, ws);
      P.drawCat(ctx, L.black, BC.x, BC.base, bs);
      const ba = buddyA(t);
      if (ba > 0) {
        const [bx, by] = buddyAt(t), pulse = 0.75 + 0.25 * osc(t, 19);
        P.glow(ctx, bx, by, 56, [215, 245, 120], 0.55 * ba * pulse);
        ctx.fillStyle = `rgba(255,253,215,${ba})`; ctx.beginPath(); ctx.arc(bx, by, 5, 0, TAU); ctx.fill();
      }
      L.branches.forEach((b) => drawBranch(ctx, b, t));
      if (L.text) ctx.drawImage(L.text, 0, 0);
      ctx.drawImage(L.vig, 0, 0);
      ctx.globalCompositeOperation = 'soft-light'; ctx.globalAlpha = 0.55;
      ctx.drawImage(L.grain, 0, 0);
      ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
    },
  };
};
