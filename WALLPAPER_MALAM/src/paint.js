// Shared painterly helpers (pastel / gouache look) for the night wallpapers.
(function () {
  const P = {};
  P.TAU = Math.PI * 2;

  P.rng = function (seed) {
    let s = seed >>> 0;
    return function () {
      s = (s + 0x6D2B79F5) >>> 0;
      let t = s;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  };
  P.hex = (h) => { h = h.replace('#', ''); return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)]; };
  P.mix = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
  P.css = (c, a = 1) => `rgba(${Math.max(0, Math.min(255, c[0])) | 0},${Math.max(0, Math.min(255, c[1])) | 0},${Math.max(0, Math.min(255, c[2])) | 0},${a})`;
  P.jit = (c, R, amt) => { const d = (R() - 0.5) * 2 * amt; return [c[0] + d + (R() - 0.5) * amt * 0.6, c[1] + d + (R() - 0.5) * amt * 0.6, c[2] + d + (R() - 0.5) * amt * 0.6]; };
  P.grad = (stops, t) => {
    if (t <= stops[0][0]) return stops[0][1];
    for (let i = 1; i < stops.length; i++) {
      if (t <= stops[i][0]) { const a = stops[i - 1], b = stops[i]; return P.mix(a[1], b[1], (t - a[0]) / (b[0] - a[0])); }
    }
    return stops[stops.length - 1][1];
  };
  P.pick = (R, arr) => arr[Math.floor(R() * arr.length)];
  P.rand = (R, a, b) => a + (b - a) * R();
  P.clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  P.smooth = (e0, e1, x) => { const t = P.clamp((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t); };

  P.makeNoise = function (seed) {
    const R = P.rng(seed), N = 256, perm = new Uint16Array(512), val = new Float32Array(N);
    for (let i = 0; i < N; i++) { perm[i] = i; val[i] = R(); }
    for (let i = N - 1; i > 0; i--) { const j = Math.floor(R() * (i + 1)); const tmp = perm[i]; perm[i] = perm[j]; perm[j] = tmp; }
    for (let i = 0; i < N; i++) perm[i + N] = perm[i];
    const v = (x, y) => val[perm[(perm[x & 255] + (y & 255)) & 511]];
    const n = (x, y) => {
      const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi;
      const u = xf * xf * (3 - 2 * xf), w = yf * yf * (3 - 2 * yf);
      const a = v(xi, yi), b = v(xi + 1, yi), c = v(xi, yi + 1), d = v(xi + 1, yi + 1);
      return a + (b - a) * u + (c - a) * w + (a - b - c + d) * u * w;
    };
    return (x, y) => n(x, y) * 0.6 + n(x * 2.1 + 17, y * 2.1 + 9) * 0.3 + n(x * 4.3 + 3, y * 4.3 + 31) * 0.1;
  };

  P.canvas = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };

  // A dry-brush stroke made of several thin bristle lines.
  P.stroke = function (ctx, R, x, y, ang, len, w, col, a) {
    const n = Math.max(2, Math.round(w / 2));
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang);
    const bend = (R() - 0.5) * len * 0.3;
    ctx.strokeStyle = col; ctx.lineCap = 'round';
    for (let i = 0; i < n; i++) {
      const oy = (i / (n - 1) - 0.5) * w + (R() - 0.5) * 1.2;
      const l0 = -len / 2 + R() * len * 0.25, l1 = len / 2 - R() * len * 0.25;
      ctx.globalAlpha = a * (0.3 + 0.7 * R());
      ctx.lineWidth = 0.9 + R() * 1.8;
      ctx.beginPath(); ctx.moveTo(l0, oy); ctx.quadraticCurveTo(0, oy + bend, l1, oy + (R() - 0.5) * 2); ctx.stroke();
    }
    ctx.restore(); ctx.globalAlpha = 1;
  };

  // Irregular blob of paint.
  P.dab = function (ctx, R, x, y, r, col, a) {
    const n = 7 + Math.floor(R() * 4);
    ctx.globalAlpha = a; ctx.fillStyle = col; ctx.beginPath();
    const rot = R() * P.TAU;
    for (let i = 0; i < n; i++) {
      const an = rot + i / n * P.TAU, rr = r * (0.65 + R() * 0.45);
      const px = x + Math.cos(an) * rr, py = y + Math.sin(an) * rr * 0.85;
      if (i) ctx.lineTo(px, py); else ctx.moveTo(px, py);
    }
    ctx.closePath(); ctx.fill(); ctx.globalAlpha = 1;
  };

  // Scatter strokes/dabs inside a region.
  P.fillStrokes = function (ctx, R, o) {
    ctx.save();
    if (o.path && o.clip !== false) ctx.clip(o.path);
    let placed = 0, tries = 0;
    while (placed < o.count && tries < o.count * 8) {
      tries++;
      const x = P.rand(R, o.x0, o.x1), y = P.rand(R, o.y0, o.y1);
      if (o.path && o.test !== false && !ctx.isPointInPath(o.path, x, y)) continue;
      if (o.where && !o.where(x, y)) continue;
      placed++;
      const col = P.css(P.jit(o.color(x, y, R), R, o.jit ?? 10));
      const a = P.rand(R, o.a[0], o.a[1]);
      if (o.kind === 'dab') P.dab(ctx, R, x, y, P.rand(R, o.w[0], o.w[1]), col, a);
      else P.stroke(ctx, R, x, y, o.angle(x, y, R), P.rand(R, o.len[0], o.len[1]), P.rand(R, o.w[0], o.w[1]), col, a);
    }
    ctx.restore();
  };

  // Polygon with jittered (hand-painted) edges.
  P.roughPath = function (pts, R, amp, seg = 14, closed = true) {
    const out = [];
    const n = pts.length, m = closed ? n : n - 1;
    for (let i = 0; i < m; i++) {
      const a = pts[i], b = pts[(i + 1) % n];
      const d = Math.hypot(b[0] - a[0], b[1] - a[1]), k = Math.max(1, Math.round(d / seg));
      const nx = -(b[1] - a[1]) / (d || 1), ny = (b[0] - a[0]) / (d || 1);
      for (let j = 0; j < k; j++) {
        const t = j / k, off = j === 0 ? 0 : (R() - 0.5) * 2 * amp;
        out.push([a[0] + (b[0] - a[0]) * t + nx * off, a[1] + (b[1] - a[1]) * t + ny * off]);
      }
    }
    if (!closed) out.push(pts[n - 1]);
    const p = new Path2D();
    out.forEach((q, i) => (i ? p.lineTo(q[0], q[1]) : p.moveTo(q[0], q[1])));
    if (closed) p.closePath();
    return p;
  };

  P.glow = function (ctx, x, y, r, rgb, a) {
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, P.css(rgb, a)); g.addColorStop(0.35, P.css(rgb, a * 0.35)); g.addColorStop(1, P.css(rgb, 0));
    ctx.fillStyle = g; ctx.fillRect(x - r, y - r, r * 2, r * 2);
  };

  P.grain = function (w, h, seed, amt) {
    const c = P.canvas(w, h), g = c.getContext('2d'), id = g.createImageData(w, h), R = P.rng(seed), d = id.data;
    for (let i = 0; i < d.length; i += 4) {
      const v = 128 + (R() - 0.5) * 2 * amt + (R() - 0.5) * amt * 0.5;
      d[i] = d[i + 1] = d[i + 2] = v; d[i + 3] = 255;
    }
    g.putImageData(id, 0, 0);
    return c;
  };

  P.vignette = function (w, h, strength) {
    const c = P.canvas(w, h), g = c.getContext('2d');
    const rg = g.createRadialGradient(w / 2, h * 0.48, h * 0.25, w / 2, h * 0.5, h * 0.72);
    rg.addColorStop(0, 'rgba(0,0,10,0)'); rg.addColorStop(1, `rgba(2,4,14,${strength})`);
    g.fillStyle = rg; g.fillRect(0, 0, w, h);
    return c;
  };

  // Hand-lettered caption with a soft glow, pre-rendered.
  P.textLayer = function (w, h, lines, cx, cy, lh, size, color, glow) {
    const c = P.canvas(w, h), g = c.getContext('2d');
    g.font = `700 ${size}px Gaegu`; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.letterSpacing = `${Math.round(size * 0.07)}px`;
    const y0 = cy - (lines.length - 1) * lh / 2;
    g.shadowColor = glow; g.shadowBlur = size * 0.6;
    lines.forEach((s, i) => { g.fillStyle = color; g.fillText(s, cx, y0 + i * lh); });
    g.shadowColor = 'rgba(0,0,0,0.35)'; g.shadowBlur = 6; g.shadowOffsetY = 2;
    lines.forEach((s, i) => { g.fillStyle = color; g.fillText(s, cx, y0 + i * lh); });
    return c;
  };

  // Sitting cat seen from behind. Unit coords: base centre = (0,0), height = 1, y up is negative.
  P.catPath = function (cx, base, H, sx = 1) {
    const X = (u) => cx + u * H * sx, Y = (v) => base + v * H;
    const p = new Path2D();
    p.moveTo(X(0), Y(0));
    p.lineTo(X(0.25), Y(-0.008));
    p.bezierCurveTo(X(0.335), Y(-0.03), X(0.345), Y(-0.2), X(0.275), Y(-0.33));
    p.bezierCurveTo(X(0.22), Y(-0.45), X(0.15), Y(-0.55), X(0.14), Y(-0.615));
    p.bezierCurveTo(X(0.205), Y(-0.66), X(0.215), Y(-0.76), X(0.172), Y(-0.815));
    p.quadraticCurveTo(X(0.2), Y(-0.93), X(0.19), Y(-0.985));
    p.quadraticCurveTo(X(0.14), Y(-0.93), X(0.09), Y(-0.872));
    p.bezierCurveTo(X(0.04), Y(-0.89), X(-0.04), Y(-0.89), X(-0.09), Y(-0.872));
    p.quadraticCurveTo(X(-0.14), Y(-0.93), X(-0.19), Y(-0.985));
    p.quadraticCurveTo(X(-0.2), Y(-0.93), X(-0.172), Y(-0.815));
    p.bezierCurveTo(X(-0.215), Y(-0.76), X(-0.205), Y(-0.66), X(-0.14), Y(-0.615));
    p.bezierCurveTo(X(-0.15), Y(-0.55), X(-0.22), Y(-0.45), X(-0.275), Y(-0.33));
    p.bezierCurveTo(X(-0.345), Y(-0.2), X(-0.335), Y(-0.03), X(-0.25), Y(-0.008));
    p.closePath();
    return p;
  };

  // Tapered tail as a curling chain. dir = 1 (to the right) or -1 (to the left).
  P.tailPath = function (x0, y0, H, dir, curl, phase, len = 0.5) {
    const n = 28, L = len * H / n;
    const wts = []; let sum = 0;
    for (let i = 1; i <= n; i++) { const s = i / n, w = Math.pow(Math.max(0, s - 0.42), 1.5); wts.push(w); sum += w; }
    let x = x0, y = y0, th = dir === 1 ? 0.1 : Math.PI - 0.1;
    const pts = [[x, y, th, 0]];
    for (let i = 1; i <= n; i++) {
      const s = i / n;
      th += -dir * curl * wts[i - 1] / sum + 0.03 * Math.sin(phase - s * 5) * dir;
      x += Math.cos(th) * L; y += Math.sin(th) * L;
      pts.push([x, y, th, s]);
    }
    const left = [], right = [];
    pts.forEach(([px, py, a, s]) => {
      const hw = H * (0.062 * (1 - s) + 0.03 * s) / 2;
      left.push([px + Math.cos(a - Math.PI / 2) * hw, py + Math.sin(a - Math.PI / 2) * hw]);
      right.push([px + Math.cos(a + Math.PI / 2) * hw, py + Math.sin(a + Math.PI / 2) * hw]);
    });
    const tip = pts[pts.length - 1];
    const p = new Path2D();
    left.forEach((q, i) => (i ? p.lineTo(q[0], q[1]) : p.moveTo(q[0], q[1])));
    const hw = H * 0.015;
    p.quadraticCurveTo(tip[0] + Math.cos(tip[2]) * hw * 2.2, tip[1] + Math.sin(tip[2]) * hw * 2.2, right[right.length - 1][0], right[right.length - 1][1]);
    for (let i = right.length - 1; i >= 0; i--) p.lineTo(right[i][0], right[i][1]);
    p.closePath();
    return { path: p, pts, left };
  };

  // Simple leaf shape at origin pointing along +x.
  P.leafPath = function (len, wid, curve = 0) {
    const p = new Path2D();
    p.moveTo(0, 0);
    p.quadraticCurveTo(len * 0.45, -wid + curve, len, curve * 0.6);
    p.quadraticCurveTo(len * 0.5, wid + curve, 0, 0);
    p.closePath();
    return p;
  };

  // ---------- animation helpers ----------
  // Smooth keyframes: [[t, v], ...] sorted by t.
  P.keys = function (t, k) {
    if (t <= k[0][0]) return k[0][1];
    for (let i = 1; i < k.length; i++) {
      if (t <= k[i][0]) { const a = k[i - 1], b = k[i], u = (t - a[0]) / (b[0] - a[0]); return a[1] + (b[1] - a[1]) * u * u * (3 - 2 * u); }
    }
    return k[k.length - 1][1];
  };
  // Catmull-Rom path through [[t, x, y], ...]
  P.pathAt = function (t, k) {
    if (t <= k[0][0]) return [k[0][1], k[0][2]];
    if (t >= k[k.length - 1][0]) { const l = k[k.length - 1]; return [l[1], l[2]]; }
    let i = 1; while (t > k[i][0]) i++;
    const p0 = k[Math.max(0, i - 2)], p1 = k[i - 1], p2 = k[i], p3 = k[Math.min(k.length - 1, i + 1)];
    const u = (t - p1[0]) / (p2[0] - p1[0]), u2 = u * u, u3 = u2 * u;
    const cr = (a, b, c, d) => 0.5 * ((2 * b) + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u2 + (-a + 3 * b - 3 * c + d) * u3);
    return [cr(p0[1], p1[1], p2[1], p3[1]), cr(p0[2], p1[2], p2[2], p3[2])];
  };
  // Quick double ear-flick starting at each time in `times`.
  P.twitch = function (t, times) {
    let e = 0;
    times.forEach((t0) => { const d = t - t0; if (d > 0 && d < 0.5) e = Math.max(e, Math.abs(Math.sin(P.TAU * d / 0.5))); });
    return e;
  };

  // ---------- articulated cat (seen from behind) ----------
  P.makeCatRig = function (R, h, sx, style) {
    const cw = Math.round(1.3 * h * sx), ch = Math.round(1.12 * h), ox = cw / 2, oy = ch - 0.06 * h;
    const X = (u) => ox + u * h * sx, Y = (v) => oy + v * h;
    const body = new Path2D();
    body.moveTo(X(0), Y(0)); body.lineTo(X(0.25), Y(-0.008));
    body.bezierCurveTo(X(0.335), Y(-0.03), X(0.345), Y(-0.2), X(0.275), Y(-0.33));
    body.bezierCurveTo(X(0.22), Y(-0.45), X(0.15), Y(-0.55), X(0.14), Y(-0.63));
    body.quadraticCurveTo(X(0), Y(-0.67), X(-0.14), Y(-0.63));
    body.bezierCurveTo(X(-0.15), Y(-0.55), X(-0.22), Y(-0.45), X(-0.275), Y(-0.33));
    body.bezierCurveTo(X(-0.345), Y(-0.2), X(-0.335), Y(-0.03), X(-0.25), Y(-0.008));
    body.closePath();
    const head = new Path2D();
    head.moveTo(X(0.13), Y(-0.6));
    head.bezierCurveTo(X(0.205), Y(-0.64), X(0.218), Y(-0.76), X(0.172), Y(-0.815));
    head.bezierCurveTo(X(0.14), Y(-0.86), X(0.1), Y(-0.886), X(0), Y(-0.888));
    head.bezierCurveTo(X(-0.1), Y(-0.886), X(-0.14), Y(-0.86), X(-0.172), Y(-0.815));
    head.bezierCurveTo(X(-0.218), Y(-0.76), X(-0.205), Y(-0.64), X(-0.13), Y(-0.6));
    head.quadraticCurveTo(X(0), Y(-0.575), X(0.13), Y(-0.6));
    head.closePath();
    const ear = (s) => {
      const p = new Path2D();
      p.moveTo(X(s * 0.06), Y(-0.85));
      p.quadraticCurveTo(X(s * 0.14), Y(-0.93), X(s * 0.19), Y(-0.985));
      p.quadraticCurveTo(X(s * 0.208), Y(-0.9), X(s * 0.19), Y(-0.78));
      p.closePath();
      return p;
    };
    const paint = (path, count, angleFn) => {
      const c = P.canvas(cw, ch), g = c.getContext('2d');
      g.fillStyle = style.base; g.fill(path);
      P.fillStrokes(g, R, {
        path, x0: 0, y0: 0, x1: cw, y1: ch, count, jit: style.jit || 6,
        color: (x, y, R) => style.color((x - ox) / (h * sx), (oy - y) / h, R),
        angle: angleFn || ((x, y, R) => -Math.PI / 2 + (x - ox) / h * 0.9 + (R() - 0.5) * 0.5), len: [8, 22].map((v) => v * h / 315), w: [3, 7], a: [0.4, 0.78],
      });
      if (style.rim) style.rim(g, path, { ox, oy, h, cw, ch });
      g.lineWidth = 8;
      const n = Math.round(count / 14);
      for (let i = 0, tries = 0; i < n && tries < 30000; tries++) {
        const x = P.rand(R, 0, cw), y = P.rand(R, 0, ch);
        if (!g.isPointInStroke(path, x, y)) continue;
        i++;
        P.stroke(g, R, x, y, -Math.PI / 2 + (R() - 0.5) * 1.4, P.rand(R, 5, 10), 2, style.edge((x - ox) / (h * sx)), 0.5);
      }
      return c;
    };
    const area = h * h / (315 * 315);
    const rig = { h, sx, ox, oy, style };
    rig.body = paint(body, Math.round(1800 * area));
    rig.head = paint(head, Math.round(700 * area), (x, y, R) => -Math.PI / 2 + (x - ox) / h * 2.2 + (R() - 0.5) * 0.6);
    rig.earL = paint(ear(-1), Math.round(90 * area)); rig.earR = paint(ear(1), Math.round(90 * area));
    // front paw, painted along +x from its shoulder pivot
    const pl = 0.37 * h, pw = 0.052 * h, pcw = Math.round(pl + 0.2 * h), pch = Math.round(0.2 * h), pox = 0.08 * h, poy = pch / 2;
    const paw = new Path2D();
    paw.moveTo(pox - 0.05 * h, poy - pw);
    paw.lineTo(pox + pl - 0.06 * h, poy - pw * 1.05);
    paw.arc(pox + pl - 0.06 * h, poy, pw * 1.12, -Math.PI / 2, Math.PI / 2);
    paw.lineTo(pox - 0.05 * h, poy + pw);
    paw.closePath();
    const pc = P.canvas(pcw, pch), pg = pc.getContext('2d');
    pg.fillStyle = style.base; pg.fill(paw);
    P.fillStrokes(pg, R, { path: paw, x0: 0, y0: 0, x1: pcw, y1: pch, count: Math.round(160 * area), jit: style.jit || 6,
      color: (x, y, R) => style.color(0.25, 0.45 + (poy - y) / h, R), angle: (x, y, R) => (R() - 0.5) * 0.4, len: [8, 18], w: [3, 6], a: [0.4, 0.75] });
    pg.strokeStyle = style.toe || 'rgba(60,70,100,0.35)'; pg.lineWidth = 1.6; pg.lineCap = 'round';
    [-0.35, 0.35].forEach((f) => { pg.beginPath(); pg.moveTo(pox + pl - 0.03 * h, poy + f * pw); pg.lineTo(pox + pl + 0.035 * h, poy + f * pw * 0.9); pg.stroke(); });
    if (style.pawRim) { pg.save(); pg.clip(paw); pg.filter = 'blur(3px)'; pg.strokeStyle = style.pawRim; pg.lineWidth = 8; pg.stroke(paw); pg.restore(); }
    rig.paw = { c: pc, ox: pox, oy: poy };
    return rig;
  };

  // s: { lx, ly, earL, earR, alert, paw:{side, amt, wave}, lean, breath, crouch, wiggle, t, tail(ctx) }
  P.drawCat = function (ctx, rig, x, base, s) {
    const h = rig.h, sx = rig.sx;
    ctx.save();
    ctx.translate(x + (s.wiggle || 0), base); ctx.rotate(s.lean || 0);
    if (s.tail) s.tail(ctx);
    const pa = s.paw;
    if (pa && pa.amt > 0.01) {
      const up = -1.12 + (pa.wave || 0);
      const ang = pa.side === 1 ? Math.PI / 2 + (up - Math.PI / 2) * pa.amt : Math.PI / 2 + (Math.PI - up - Math.PI / 2) * pa.amt;
      ctx.save(); ctx.translate(pa.side * 0.2 * h * sx, -0.42 * h); ctx.rotate(ang);
      if (pa.side === -1) ctx.scale(1, -1);
      ctx.drawImage(rig.paw.c, -rig.paw.ox, -rig.paw.oy); ctx.restore();
    }
    const b = s.breath || 0, cr = s.crouch || 0;
    ctx.scale(1 + 0.003 * b + 0.02 * cr, 1 + 0.008 * b - 0.04 * cr);
    ctx.drawImage(rig.body, -rig.ox, -rig.oy);
    // head
    const lx = s.lx || 0, ly = s.ly || 0;
    ctx.translate(0, -0.62 * h);
    ctx.rotate(lx * 0.17);
    ctx.translate(lx * 0.045 * h * sx, ly * 0.018 * h);
    ctx.scale(1 - Math.abs(lx) * 0.04, 1 - ly * 0.035);
    ctx.translate(0, 0.62 * h);
    if (rig.style.whisker) {
      ctx.strokeStyle = rig.style.whisker; ctx.lineCap = 'round';
      const tw = 0.02 * Math.sin(P.TAU * 17 * (s.t || 0) / 20); // loop-safe (T = 20 s)
      [-1, 1].forEach((sd) => {
        const f = P.clamp(1 + sd * lx * 0.5, 0.45, 1.5);
        for (let k = 0; k < 3; k++) {
          const wx = sd * 0.185 * h * sx, wy = -h * (0.70 - k * 0.022);
          ctx.lineWidth = (1.6 - k * 0.2) * h / 480;
          ctx.beginPath(); ctx.moveTo(wx, wy);
          ctx.quadraticCurveTo(wx + sd * h * 0.1 * f, wy - h * (0.014 + tw) + k * 4, wx + sd * h * (0.19 - k * 0.015) * f, wy + h * (0.008 + k * 0.02 + tw));
          ctx.stroke();
        }
      });
    }
    [[-1, rig.earL, s.earL || 0], [1, rig.earR, s.earR || 0]].forEach(([sd, img, e]) => {
      const px = sd * 0.13 * h * sx, py = -0.83 * h;
      ctx.save(); ctx.translate(px, py);
      ctx.rotate(sd * (0.5 * e - 0.12 * (s.alert || 0)));
      ctx.scale(1 - 0.28 * Math.max(0, sd * lx), 1 - 0.1 * e);
      ctx.translate(-px, -py);
      ctx.drawImage(img, -rig.ox, -rig.oy); ctx.restore();
    });
    ctx.drawImage(rig.head, -rig.ox, -rig.oy);
    ctx.restore();
  };

  window.P = P;
})();
