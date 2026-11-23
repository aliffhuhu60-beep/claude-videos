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

  window.P = P;
})();
