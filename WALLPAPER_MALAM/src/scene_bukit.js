// Version 1 — white cat on a moonlit hill, drifting night clouds.
window.SCENES = window.SCENES || {};
SCENES.bukit = function (opts) {
  const W = 1080, H = 2400, T = 20, TAU = P.TAU;
  const osc = (t, k, p = 0) => Math.sin(TAU * k * t / T + p);
  const R = P.rng(11), noise = P.makeNoise(5);
  const hillY = (x) => 1700 - 300 * (x / W) - 60 * Math.sin(Math.PI * x / W);
  const mtnY = (x) => 1470 + 35 * Math.sin(x * 0.005 + 0.6) + 18 * Math.sin(x * 0.013 + 2);
  const MOON = { x: 800, y: 560, r: 64 };
  const CAT = { x: 745, base: 2040, h: 315 };
  const skyStops = [[0, P.hex('#050b22')], [0.3, P.hex('#0b1840')], [0.62, P.hex('#183064')], [0.86, P.hex('#2a4884')], [1, P.hex('#3b5a92')]];
  const skyCol = (y) => P.grad(skyStops, y / 1720);
  const L = {};

  function paintSky() {
    const c = P.canvas(W, H), g = c.getContext('2d');
    const lg = g.createLinearGradient(0, 0, 0, 1720);
    skyStops.forEach((s) => lg.addColorStop(s[0], P.css(s[1])));
    g.fillStyle = lg; g.fillRect(0, 0, W, H);
    P.fillStrokes(g, R, {
      x0: -30, y0: -30, x1: W + 30, y1: 1760, count: 15000, jit: 8,
      color: (x, y) => {
        let col = skyCol(y);
        const n = noise(x * 0.004, y * 0.004);
        col = P.mix(col, P.hex('#5468a8'), Math.max(0, n - 0.55) * 0.7);
        const dm = Math.hypot(x - MOON.x, y - MOON.y);
        if (dm < 520) col = P.mix(col, P.hex('#7186c4'), Math.pow(1 - dm / 520, 1.6) * 0.45);
        return col;
      },
      angle: (x, y, R) => (R() - 0.5) * 0.55 + 0.12 * Math.sin(y * 0.01),
      len: [30, 95], w: [8, 22], a: [0.16, 0.36],
    });
    // faint milky way band
    const ax = -120, ay = 180, bx = 1200, by = 1020, ang = Math.atan2(by - ay, bx - ax);
    for (let i = 0; i < 420; i++) {
      const u = R(), off = (R() + R() + R() - 1.5) * 120;
      const x = ax + (bx - ax) * u - Math.sin(ang) * off, y = ay + (by - ay) * u + Math.cos(ang) * off;
      P.stroke(g, R, x, y, ang + (R() - 0.5) * 0.3, P.rand(R, 60, 140), P.rand(R, 16, 40), P.css(P.jit(P.hex('#4b5e9e'), R, 10)), P.rand(R, 0.03, 0.08));
    }
    for (let i = 0; i < 1400; i++) {
      const u = R(), off = (R() + R() + R() - 1.5) * 110;
      const x = ax + (bx - ax) * u - Math.sin(ang) * off, y = ay + (by - ay) * u + Math.cos(ang) * off;
      g.fillStyle = `rgba(225,232,255,${P.rand(R, 0.12, 0.5)})`; g.beginPath(); g.arc(x, y, P.rand(R, 0.4, 1.1), 0, TAU); g.fill();
    }
    // static stars
    for (let i = 0; i < 1700; i++) {
      const x = R() * W, y = Math.pow(R(), 1.25) * 1680;
      const a = P.rand(R, 0.15, 0.65) * (1 - P.smooth(1150, 1680, y) * 0.85);
      g.fillStyle = `rgba(236,240,255,${a})`; g.beginPath(); g.arc(x, y, P.rand(R, 0.5, 1.4), 0, TAU); g.fill();
    }
    return c;
  }

  function paintMoon() {
    const r = MOON.r, s = r * 2 + 40, c = P.canvas(s, s), g = c.getContext('2d'), m = s / 2;
    const disc = new Path2D(); disc.arc(m, m, r, 0, TAU);
    const rg = g.createRadialGradient(m - r * 0.3, m - r * 0.3, r * 0.1, m, m, r);
    rg.addColorStop(0, '#fffaea'); rg.addColorStop(1, '#eadfbf');
    g.fillStyle = rg; g.fill(disc);
    P.fillStrokes(g, R, {
      path: disc, x0: m - r, y0: m - r, x1: m + r, y1: m + r, count: 380, jit: 8,
      color: (x, y) => (noise(x * 0.05, y * 0.05) > 0.55 ? P.hex('#d6c9a4') : P.hex('#fbf3dc')),
      angle: (x, y, R) => (R() - 0.5) * 1.2, len: [8, 20], w: [4, 9], a: [0.3, 0.6],
    });
    // soft painted edge
    for (let i = 0; i < 70; i++) {
      const an = R() * TAU;
      P.stroke(g, R, m + Math.cos(an) * r, m + Math.sin(an) * r, an + Math.PI / 2, P.rand(R, 8, 16), 4, 'rgba(250,244,222,1)', 0.35);
    }
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
    for (let i = 0; i < 3; i++) {
      const r = h * P.rand(Rc, 0.17, 0.25);
      puffs.push([w * P.rand(Rc, 0.3, 0.68), base - h * 0.42 - r * 0.25, r]);
    }
    const path = new Path2D();
    puffs.forEach(([x, y, r]) => { path.moveTo(x + r, y); path.arc(x, y, r, 0, TAU); });
    const top = Math.min(...puffs.map((p) => p[1] - p[2]));
    const LT = P.hex('#d3d9ef'), MID = P.hex('#7d8bbb'), DK = P.hex('#36456f');
    const colAt = (x, y) => {
      const v = P.clamp((y - top) / (base - top), 0, 1);
      let col = v < 0.5 ? P.mix(LT, MID, v / 0.5) : P.mix(MID, DK, (v - 0.5) / 0.5);
      let best = null, bd = 1e9;
      puffs.forEach((p) => { const d = Math.hypot(x - p[0], y - p[1]) - p[2]; if (d < bd) { bd = d; best = p; } });
      const dx = (x - best[0]) / best[2], dy = (y - best[1]) / best[2];
      const lit = Math.max(0, dx * light[0] + dy * light[1]);
      col = P.mix(col, P.hex('#e8ecfa'), lit * 0.55);
      return col;
    };
    const inside = (x, y, skip) => puffs.some((q) => q !== skip && Math.hypot(x - q[0], y - q[1]) < q[2] * 0.97);
    g.save();
    const cp = [[-50, -50], [w + 50, -50], [w + 50, base]];
    for (let x = w + 40; x >= -40; x -= 18) cp.push([x, base + 6 + Math.sin(x * 0.05) * 5 + (Rc() - 0.5) * 8]);
    const cut = P.roughPath(cp, Rc, 1.5, 9); g.clip(cut);
    g.filter = 'blur(5px)'; g.fillStyle = P.css(P.mix(MID, DK, 0.3)); g.fill(path); g.filter = 'none';
    P.fillStrokes(g, Rc, {
      path, x0: 0, y0: top, x1: w, y1: base + 8, count: Math.round(w * h / 30), jit: 11,
      color: colAt, angle: (x, y, R) => (R() - 0.5) * 1.1, len: [10, 30], w: [5, 14], a: [0.3, 0.65],
    });
    // fuzzy pastel edges
    puffs.forEach((p) => {
      for (let i = 0; i < p[2] * 1.6; i++) {
        const an = Rc() * TAU, rr = p[2] * P.rand(Rc, 0.9, 1.06), x = p[0] + Math.cos(an) * rr, y = p[1] + Math.sin(an) * rr;
        if (y > base || inside(x, y, p)) continue;
        P.stroke(g, Rc, x, y, an + Math.PI / 2 + (Rc() - 0.5) * 0.9, P.rand(Rc, 8, 22), P.rand(Rc, 4, 10), P.css(P.jit(colAt(x, y), Rc, 8)), P.rand(Rc, 0.2, 0.45));
      }
    });
    g.restore();
    // soft underside
    for (let i = 0; i < w / 6; i++) {
      const x = P.rand(Rc, w * 0.05, w * 0.95);
      P.stroke(g, Rc, x, base + P.rand(Rc, -4, 6), (Rc() - 0.5) * 0.2, P.rand(Rc, 18, 40), 5, P.css(P.jit(DK, Rc, 8)), P.rand(Rc, 0.12, 0.3));
    }
    return c;
  }

  function paintLand() {
    const c = P.canvas(W, H), g = c.getContext('2d');
    // distant mountains
    const mp = [];
    for (let x = -10; x <= W + 10; x += 6) mp.push([x, mtnY(x) - Math.abs(Math.sin(x * 0.09)) * 7 - noise(x * 0.02, 3) * 12]);
    mp.push([W + 10, 1900], [-10, 1900]);
    const mpath = P.roughPath(mp, R, 1.5, 6);
    g.fillStyle = '#142a3c'; g.fill(mpath);
    P.fillStrokes(g, R, {
      path: mpath, x0: -10, y0: 1380, x1: W + 10, y1: 1900, count: 4200, jit: 7,
      color: (x, y) => { const d = y - mtnY(x); return d < 30 ? P.hex('#2c4b62') : P.mix(P.hex('#1d3a4c'), P.hex('#11233a'), P.clamp(d / 260, 0, 1)); },
      angle: (x, y, R) => (R() - 0.5) * 0.5, len: [18, 50], w: [5, 12], a: [0.3, 0.6],
    });
    // low mist
    const mist = g.createLinearGradient(0, 1480, 0, 1640);
    mist.addColorStop(0, 'rgba(120,140,200,0)'); mist.addColorStop(0.5, 'rgba(120,140,200,0.16)'); mist.addColorStop(1, 'rgba(120,140,200,0)');
    g.fillStyle = mist; g.fillRect(0, 1480, W, 160);

    // the big hill
    const hp = [];
    for (let x = -10; x <= W + 10; x += 4) hp.push([x, hillY(x) - (R() < 0.3 ? R() * 14 : R() * 4)]);
    hp.push([W + 10, H + 10], [-10, H + 10]);
    const hpath = P.roughPath(hp, R, 1, 4);
    const hg = g.createLinearGradient(0, 1400, 0, H);
    hg.addColorStop(0, '#223d31'); hg.addColorStop(0.4, '#182f23'); hg.addColorStop(1, '#0b1913');
    g.fillStyle = hg; g.fill(hpath);
    const pal = [P.hex('#22402f'), P.hex('#2a4a37'), P.hex('#1c3628'), P.hex('#162e22')];
    P.fillStrokes(g, R, {
      path: hpath, x0: -10, y0: 1390, x1: W + 10, y1: H + 10, count: 34000, jit: 7,
      color: (x, y, R) => {
        const d = y - hillY(x), yy = P.clamp((y - 1400) / 1000, 0, 1);
        let col = P.mix(P.pick(R, pal), P.hex('#0a1811'), yy * 0.7);
        if (d < 120) col = P.mix(col, P.hex('#46676a'), (1 - d / 120) * 0.6);
        const n = noise(x * 0.006, y * 0.006);
        if (n > 0.58) col = P.mix(col, P.hex('#3d5a45'), (n - 0.58) * 1.6);
        if (R() < 0.06) col = P.mix(col, P.hex('#56726a'), 0.55);
        if (R() < 0.08) col = P.mix(col, P.hex('#3a5c66'), 0.5);
        return col;
      },
      angle: (x, y, R) => -Math.PI / 2 + (R() - 0.5) * 0.5, len: [12, 40], w: [3, 9], a: [0.35, 0.7],
    });
    // tiny pale flowers on the hill
    for (let i = 0; i < 150; i++) {
      const x = R() * W, y = P.rand(R, hillY(x) + 40, H - 50);
      const col = P.pick(R, ['#c9d3ee', '#e6dfc6', '#b9c4e6', '#d8c3d8']);
      g.globalAlpha = P.rand(R, 0.25, 0.6); g.fillStyle = col;
      g.beginPath(); g.arc(x, y, P.rand(R, 1.2, 2.6), 0, TAU); g.fill();
    }
    g.globalAlpha = 1;
    // cat shadow (moon is upper-right -> shadow falls lower-left)
    g.save(); g.filter = 'blur(10px)'; g.fillStyle = 'rgba(4,14,10,0.5)';
    g.beginPath(); g.ellipse(CAT.x - 70, CAT.base + 4, 140, 20, -0.08, 0, TAU); g.fill(); g.restore();
    return c;
  }

  function makeRig() {
    return P.makeCatRig(R, CAT.h, 1, {
      base: '#d9dfec', jit: 7,
      color: (u, v) => {
        let col = P.mix(P.hex('#aab4d2'), P.hex('#f7f7fb'), P.clamp(0.5 + u * 1.6 + v * 0.25, 0, 1));
        if (v > 0.6 && v < 0.64) col = P.mix(col, P.hex('#b5bdd8'), 0.4);
        return col;
      },
      edge: (u) => (u > 0 ? '#f2f3f8' : '#b8c0da'),
      whisker: 'rgba(235,240,252,0.5)', snout: '#e4e8f2', snoutRim: 'rgba(170,180,215,0.5)',
      pawRim: 'rgba(160,170,210,0.35)',
    });
  }

  // ---- the cat's little story (20 s loop) ----
  const BUDDY = [ // firefly that comes to play: [t, x, y]
    [7.6, 60, 1560], [8.6, 230, 1640], [9.6, 450, 1720], [10.6, 660, 1670], [11.5, 860, 1740], [12.2, 905, 1715],
    [12.8, 880, 1740], [13.2, 905, 1720], [13.55, 970, 1640], [14.2, 1010, 1450], [15.0, 980, 1270], [15.8, 1040, 1100],
  ];
  const buddyAt = (t) => {
    const [x, y] = P.pathAt(t, BUDDY);
    return [x + 14 * Math.sin(TAU * 31 * t / T), y + 10 * Math.sin(TAU * 23 * t / T + 1)];
  };
  const buddyA = (t) => P.keys(t, [[7.6, 0], [8.2, 1], [15.0, 1], [15.8, 0]]);
  function catState(t) {
    const head = [CAT.x, CAT.base - CAT.h * 0.74];
    // 0.9-3.8 yawn toward the moon | 7-9 shooting star | 9.4-16.4 plays with firefly | 16.6-19.6 licks its paw
    let lx = P.keys(t, [[0, 0.25], [0.9, 0.25], [1.4, 0.8], [3.2, 0.8], [3.8, 0.25], [4, 0.25], [5, 0.05], [6.9, 0.05], [7.5, -0.6], [8.5, -0.35], [9.3, 0],
      [16.3, 0], [16.9, -0.6], [19.2, -0.6], [19.8, 0.25], [20, 0.25]]);
    let ly = P.keys(t, [[0, 0.35], [0.9, 0.35], [1.4, 0.8], [3.2, 0.8], [3.8, 0.35], [6.9, 0.3], [7.5, 0.9], [8.5, 0.6], [9.3, 0.1],
      [16.3, 0.1], [16.9, -0.4], [19.2, -0.4], [19.8, 0.35], [20, 0.35]]);
    const w = P.keys(t, [[9.4, 0], [10.2, 1], [15.4, 1], [16.3, 0]]);
    if (w > 0) {
      const [bx, by] = buddyAt(t);
      lx += (P.clamp((bx - head[0]) / 260, -1, 1) - lx) * w;
      ly += (P.clamp((head[1] - by) / 420, -0.3, 1) - ly) * w;
    }
    const yawn = P.keys(t, [[1.3, 0], [2.0, 1], [2.7, 1], [3.3, 0]]);
    const lick = P.keys(t, [[16.8, 0], [17.25, 1], [19.0, 1], [19.4, 0]]);
    const lickBeat = Math.max(0, Math.sin(TAU * 40 * t / T));
    ly += lick * 0.1 * lickBeat;
    const snout = Math.max(P.keys(t, [[0.9, 0], [1.4, 1], [3.2, 1], [3.8, 0]]), P.keys(t, [[16.4, 0], [16.9, 1], [19.2, 1], [19.8, 0]]));
    const exc = P.keys(t, [[9.8, 0], [10.8, 1], [14.6, 1], [16.2, 0]]);
    const wig = P.keys(t, [[11.6, 0], [11.9, 1], [12.5, 1], [12.75, 0]]);
    const swipe = P.keys(t, [[12.75, 0], [12.97, 1], [13.13, 0.78], [13.3, 1], [13.72, 0]]);
    const paw = swipe > 0.001 ? { side: 1, amt: swipe, wave: 0.15 * Math.sin(TAU * 60 * t / T) * swipe }
      : { side: -1, amt: lick, up: -1.36, wave: 0.09 * lickBeat * lick };
    return {
      lx, ly, t, T, snout, open: yawn, tongue: lick * lickBeat, stretch: yawn,
      earL: Math.max(P.twitch(t, [4.5, 15.9]), 0.65 * yawn), earR: Math.max(P.twitch(t, [5.6, 10.1, 13.9]), 0.65 * yawn),
      alert: exc, crouch: 0.5 * wig + 0.2 * exc * (1 - swipe), wiggle: wig * 7 * Math.sin(TAU * 40 * t / T),
      lean: 0.07 * swipe - 0.03 * lick, breath: osc(t, 5) * (1 + exc * 0.6),
      paw,
      tailCurl: 2.7 + 0.5 * osc(t, 2) + 0.15 * osc(t, 5, 1) + exc * 0.55 * osc(t, 30),
    };
  }

  function grassData() {
    const blades = [];
    const pal = ['#0d2014', '#14301c', '#1c3a23', '#25462c', '#2d5233'];
    for (let i = 0; i < 520; i++) {
      const y = P.rand(R, 2120, H + 30), depth = P.clamp((y - 2120) / 300, 0, 1);
      blades.push({ x: P.rand(R, -20, W + 20), y, h: P.rand(R, 30, 70) * (0.7 + depth * 0.9), w: P.rand(R, 3, 6) * (0.8 + depth * 0.6), col: P.pick(R, pal), rim: R() < 0.35, lean: (R() - 0.5) * 0.5, p: R() * TAU });
    }
    // tufts in front of the cat's paws to ground it
    for (let i = 0; i < 70; i++) {
      blades.push({ x: CAT.x + P.rand(R, -130, 150), y: CAT.base + P.rand(R, 0, 26), h: P.rand(R, 18, 42), w: P.rand(R, 2.5, 4.5), col: P.pick(R, pal.slice(2)), rim: R() < 0.5, lean: (R() - 0.5) * 0.6, p: R() * TAU });
    }
    blades.sort((a, b) => a.y - b.y);
    const flowers = [];
    const fl = [[150, 2200], [210, 2290], [360, 2260], [90, 2330], [300, 2360], [880, 2300], [960, 2240], [520, 2330]];
    fl.forEach(([x, y], i) => flowers.push({ x, y, h: P.rand(R, 50, 80), r: P.rand(R, 6, 9), col: ['#c7d2f2', '#efe2c4', '#d8c6e6'][i % 3], p: R() * TAU }));
    return { blades, flowers };
  }

  function swayAt(x, t, p) {
    const gust = 1 + 0.9 * Math.pow(Math.max(0, Math.sin(TAU * 2 * t / T - x * 0.002)), 4);
    return gust * 0.18 * Math.sin(TAU * 3 * t / T - x * 0.006 + p * 0.25) + 0.06 * Math.sin(TAU * 7 * t / T + p);
  }

  function drawBlade(ctx, b, t) {
    const s = swayAt(b.x, t, b.p) + b.lean;
    const tx = b.x + s * b.h, ty = b.y - b.h * (1 - Math.abs(s) * 0.15);
    ctx.fillStyle = b.col;
    ctx.beginPath();
    ctx.moveTo(b.x - b.w / 2, b.y);
    ctx.quadraticCurveTo(b.x - b.w * 0.2 + s * b.h * 0.3, b.y - b.h * 0.55, tx, ty);
    ctx.quadraticCurveTo(b.x + b.w * 0.2 + s * b.h * 0.3, b.y - b.h * 0.5, b.x + b.w / 2, b.y);
    ctx.fill();
    if (b.rim) {
      ctx.strokeStyle = 'rgba(120,150,170,0.28)'; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(b.x + b.w * 0.3, b.y - 2); ctx.quadraticCurveTo(b.x + s * b.h * 0.3, b.y - b.h * 0.55, tx, ty); ctx.stroke();
    }
  }

  const SEEDS = Array.from({ length: 9 }, (_, i) => ({ o: i / 9, y: 1500 + (i * 137) % 700, a: 30 + (i * 53) % 50, k: 2 + (i % 3), r: 2 + (i % 3) * 0.6 }));
  function drawSeeds(ctx, t) {
    SEEDS.forEach((s) => {
      const p = ((t / T + s.o) % 1 + 1) % 1, x = -60 + p * (W + 120), y = s.y - p * 260 + s.a * Math.sin(TAU * s.k * t / T + s.o * 9);
      const a = P.smooth(0, 0.1, p) * (1 - P.smooth(0.9, 1, p)) * 0.7;
      P.glow(ctx, x, y, 14, [220, 228, 255], 0.35 * a);
      ctx.strokeStyle = `rgba(240,244,255,${0.8 * a})`; ctx.lineWidth = 1;
      ctx.beginPath();
      for (let k = 0; k < 8; k++) { const an = k / 8 * TAU + TAU * 2 * t / T; ctx.moveTo(x, y); ctx.lineTo(x + Math.cos(an) * s.r * 2.5, y + Math.sin(an) * s.r * 2.5); }
      ctx.stroke();
    });
  }

  function fireflyData() {
    const list = [];
    for (let i = 0; i < 26; i++) {
      list.push({
        x: P.rand(R, 40, W - 40), y: P.rand(R, 1560, 2330), ax: P.rand(R, 20, 60), ay: P.rand(R, 12, 40),
        k1: 1 + Math.floor(R() * 2), k2: 1 + Math.floor(R() * 3), k3: 2 + Math.floor(R() * 4), p1: R() * TAU, p2: R() * TAU, p3: R() * TAU,
        front: R() < 0.45, size: P.rand(R, 0.8, 1.3),
      });
    }
    return list;
  }

  function drawFirefly(ctx, f, t) {
    const x = f.x + f.ax * Math.sin(TAU * f.k1 * t / T + f.p1), y = f.y + f.ay * Math.sin(TAU * f.k2 * t / T + f.p2);
    const b = Math.pow(0.5 + 0.5 * Math.sin(TAU * f.k3 * t / T + f.p3), 2);
    if (b < 0.02) return;
    P.glow(ctx, x, y, 26 * f.size, [210, 240, 120], 0.45 * b);
    ctx.fillStyle = `rgba(255,252,210,${0.9 * b})`; ctx.beginPath(); ctx.arc(x, y, 2.4 * f.size, 0, TAU); ctx.fill();
  }

  function starData() {
    const stars = [];
    for (let i = 0; i < 150; i++) stars.push({ x: R() * W, y: Math.pow(R(), 1.3) * 1450, r: P.rand(R, 0.9, 2.1), k: 1 + Math.floor(R() * 4), p: R() * TAU, b: P.rand(R, 0.5, 1) });
    const spark = [[150, 210], [430, 120], [960, 300], [620, 820], [90, 1020], [300, 520], [1010, 860], [520, 1080], [700, 230]];
    spark.forEach(([x, y]) => stars.push({ x, y, r: P.rand(R, 1.8, 2.6), k: 1 + Math.floor(R() * 3), p: R() * TAU, b: 1, ray: P.rand(R, 9, 16) }));
    return stars;
  }

  function drawStars(ctx, t) {
    L.stars.forEach((s) => {
      const a = s.b * (0.55 + 0.45 * Math.sin(TAU * s.k * t / T + s.p));
      ctx.fillStyle = `rgba(245,246,255,${a})`;
      ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, TAU); ctx.fill();
      if (s.ray) {
        P.glow(ctx, s.x, s.y, s.ray * 1.4, [200, 215, 255], 0.35 * a);
        ctx.strokeStyle = `rgba(240,244,255,${0.6 * a})`; ctx.lineWidth = 1.1;
        const rr = s.ray * (0.75 + 0.25 * a);
        ctx.beginPath(); ctx.moveTo(s.x - rr, s.y); ctx.lineTo(s.x + rr, s.y); ctx.moveTo(s.x, s.y - rr); ctx.lineTo(s.x, s.y + rr); ctx.stroke();
      }
    });
  }

  function drawShootingStar(ctx, t) {
    const t0 = 7.2, dur = 1.1;
    if (t < t0 || t > t0 + dur) return;
    const u = (t - t0) / dur, e = 1 - Math.pow(1 - u, 2);
    const sx = 140, sy = 260, ex = 560, ey = 520;
    const hx = sx + (ex - sx) * e, hy = sy + (ey - sy) * e;
    const tl = 170 * Math.sin(Math.PI * u), dx = (ex - sx), dy = (ey - sy), dl = Math.hypot(dx, dy);
    const tx = hx - dx / dl * tl, ty = hy - dy / dl * tl;
    const a = Math.sin(Math.PI * u);
    const lg = ctx.createLinearGradient(tx, ty, hx, hy);
    lg.addColorStop(0, 'rgba(220,230,255,0)'); lg.addColorStop(1, `rgba(255,255,255,${0.9 * a})`);
    ctx.strokeStyle = lg; ctx.lineWidth = 2.4; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(tx, ty); ctx.lineTo(hx, hy); ctx.stroke();
    P.glow(ctx, hx, hy, 14, [220, 230, 255], 0.7 * a);
  }

  function cloudData() {
    const defs = [
      { w: 640, h: 250, x: 330, y: 820, o: 0.0, s: 5.5 },
      { w: 600, h: 230, x: 960, y: 1090, o: 0.45, s: 4.5 },
      { w: 360, h: 150, x: 230, y: 1260, o: 0.7, s: 6 },
      { w: 380, h: 150, x: 1010, y: 1330, o: 0.2, s: 4 },
      { w: 460, h: 180, x: 560, y: 360, o: 0.6, s: 5 },
      { w: 320, h: 130, x: 120, y: 240, o: 0.3, s: 6.5 },
      { w: 420, h: 160, x: 760, y: 1500, o: 0.85, s: 3.5 },
    ];
    return defs.map((d, i) => {
      const light = [MOON.x - d.x, MOON.y - d.y], ll = Math.hypot(light[0], light[1]) || 1;
      return { ...d, img: makeCloud(d.w, d.h, 100 + i * 17, [light[0] / ll * 0.9, light[1] / ll * 0.9 - 0.3]) };
    });
  }

  function drawClouds(ctx, t) {
    L.clouds.forEach((c) => {
      const p = ((2 * t / T + c.o) % 1 + 1) % 1;
      const x = c.x + c.s * 5 * (T / 2) * (p - 0.5), a = P.smooth(0, 0.2, p) * (1 - P.smooth(0.8, 1, p));
      ctx.globalAlpha = 0.92 * a;
      ctx.drawImage(c.img, x - c.img.width / 2, c.y - c.img.height * 0.6);
    });
    ctx.globalAlpha = 1;
  }

  return {
    W, H, T,
    async init() {
      L.sky = paintSky(); L.moon = paintMoon(); L.land = paintLand(); L.cat = makeRig();
      L.clouds = cloudData(); L.stars = starData(); L.grass = grassData(); L.ff = fireflyData();
      L.text = opts.text === false ? null : P.textLayer(W, H, ['The stars', 'have nowhere', 'they need to be.'], 540, 1290, 84, 62, '#f6efdc', 'rgba(255,236,190,0.55)');
      L.vig = P.vignette(W, H, 0.55); L.grain = P.grain(W, H, 3, 34);
    },
    frame(ctx, t) {
      ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
      ctx.drawImage(L.sky, 0, 0);
      drawStars(ctx, t);
      drawShootingStar(ctx, t);
      // moon + breathing halo
      const hal = 0.9 + 0.1 * osc(t, 2);
      P.glow(ctx, MOON.x, MOON.y, 360, [170, 185, 240], 0.32 * hal);
      P.glow(ctx, MOON.x, MOON.y, 130, [255, 245, 215], 0.4 * hal);
      ctx.drawImage(L.moon, MOON.x - L.moon.width / 2, MOON.y - L.moon.height / 2);
      drawClouds(ctx, t);
      ctx.drawImage(L.land, 0, 0);
      L.ff.filter((f) => !f.front).forEach((f) => drawFirefly(ctx, f, t));
      // cat with its little story
      const st = catState(t);
      st.tail = (c) => {
        const tail = P.tailPath(CAT.h * 0.2, -CAT.h * 0.035, CAT.h * 1.35, 1, st.tailCurl, TAU * 2 * t / T, 0.38);
        c.fillStyle = '#ccd3e5'; c.fill(tail.path);
        c.strokeStyle = 'rgba(250,250,255,0.7)'; c.lineWidth = 3; c.lineCap = 'round';
        c.beginPath(); tail.left.slice(4).forEach((q, i) => (i ? c.lineTo(q[0], q[1]) : c.moveTo(q[0], q[1]))); c.stroke();
      };
      P.drawCat(ctx, L.cat, CAT.x, CAT.base, st);
      // moon glow around the cat
      P.glow(ctx, CAT.x + 20, CAT.base - CAT.h * 0.55, 220, [190, 205, 255], 0.08);
      L.grass.blades.forEach((b) => drawBlade(ctx, b, t));
      L.grass.flowers.forEach((f) => {
        const s = swayAt(f.x, t, f.p) * 0.8, tx = f.x + s * f.h, ty = f.y - f.h;
        ctx.strokeStyle = '#1f3d27'; ctx.lineWidth = 2.5;
        ctx.beginPath(); ctx.moveTo(f.x, f.y); ctx.quadraticCurveTo(f.x + s * f.h * 0.3, f.y - f.h * 0.5, tx, ty); ctx.stroke();
        ctx.fillStyle = f.col; ctx.globalAlpha = 0.85;
        for (let k = 0; k < 5; k++) { const an = k / 5 * TAU + f.p; ctx.beginPath(); ctx.ellipse(tx + Math.cos(an) * f.r * 0.8, ty + Math.sin(an) * f.r * 0.8, f.r * 0.6, f.r * 0.38, an, 0, TAU); ctx.fill(); }
        ctx.fillStyle = '#e8d48a'; ctx.beginPath(); ctx.arc(tx, ty, f.r * 0.32, 0, TAU); ctx.fill(); ctx.globalAlpha = 1;
      });
      L.ff.filter((f) => f.front).forEach((f) => drawFirefly(ctx, f, t));
      const ba = buddyA(t);
      if (ba > 0) {
        const [bx, by] = buddyAt(t), pulse = 0.75 + 0.25 * Math.sin(TAU * 25 * t / T);
        P.glow(ctx, bx, by, 46, [215, 245, 120], 0.55 * ba * pulse);
        ctx.fillStyle = `rgba(255,253,215,${ba})`; ctx.beginPath(); ctx.arc(bx, by, 4, 0, TAU); ctx.fill();
      }
      drawSeeds(ctx, t);
      if (L.text) ctx.drawImage(L.text, 0, 0);
      ctx.drawImage(L.vig, 0, 0);
      ctx.globalCompositeOperation = 'soft-light'; ctx.globalAlpha = 0.55;
      ctx.drawImage(L.grain, 0, 0);
      ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
    },
  };
};
