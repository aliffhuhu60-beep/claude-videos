#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bunga.py - Jambangan bunga liar ASCII 3D yang BERGERAK di terminal.

  * batang tumbuh dari bawah, kemudian bunga mekar satu per satu
  * jambangan berputar perlahan (3D sebenar: z-buffer + pencahayaan)
  * bunga beralun ditiup angin, bintang berkelip, kelopak gugur
  * pesanan ditaip di bahagian bawah skrin

Cara jalankan (Python 3.7+, tiada pustaka tambahan diperlukan):

    python3 bunga.py
    python3 bunga.py "untuk awak, sayang"

Tekan Ctrl+C untuk berhenti.
Tip: besarkan tetingkap terminal dan kecilkan saiz fon (Ctrl/Cmd + -)
untuk hasil yang lebih halus dan cantik.
"""

import math
import os
import random
import shutil
import sys
import time

# --------------------------------------------------------------------- tetapan
MESSAGE = "bunga ini khas untuk awak <3"
FPS = 30
GROW_SECONDS = 7.0      # tempoh batang tumbuh & bunga mekar
SPIN_SPEED = 0.35       # kelajuan putaran (radian / saat)
TILT = 0.26             # pandangan sedikit dari atas (radian)
SEED = 2026             # tukar nombor ini untuk susunan bunga yang lain

ASP = 2.0               # tinggi satu aksara terminal / lebarnya
CAM = 7.0               # jarak kamera (perspektif)
Y_OFF = 0.70            # anjakan menegak supaya jambangan di tengah
BASE_Y = -1.30          # titik semua batang bertemu (dalam pembalut)
LIGHT = (-0.35, 0.55, -0.75)

# warna ANSI 256: (terang, malap)
COL = {
    "pink":   (213, 169),
    "rose":   (205, 161),
    "red":    (196, 124),
    "purple": (141, 97),
    "lilac":  (183, 139),
    "blue":   (75, 32),
    "yellow": (227, 178),
    "orange": (215, 166),
    "white":  (231, 250),
    "gold":   (220, 136),
    "brown":  (137, 94),
    "stem":   (114, 65),
    "leaf":   (77, 28),
    "wrap":   (230, 180),
    "ribbon": (204, 125),
}

# jenis titik
K_SURF, K_STEM, K_LEAF, K_WRAP, K_DOT, K_CENTER = range(6)
RAMPS = {
    K_SURF: ".:-=oO0@",
    K_LEAF: ".,-~=+",
    K_WRAP: ".,:;=+*#",
    K_CENTER: ".:*#@",
}

# ------------------------------------------------------------- matematik 3D
def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def unit(a):
    n = math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2]) or 1.0
    return (a[0] / n, a[1] / n, a[2] / n)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def frame_of(axis):
    """Dua vektor unit yang berserenjang dengan paksi (untuk kelopak)."""
    helper = (0.0, 1.0, 0.0) if abs(axis[1]) < 0.9 else (1.0, 0.0, 0.0)
    u = unit(cross(helper, axis))
    return u, cross(axis, u)


def frange(a, b, step):
    n = max(1, int(round((b - a) / step)))
    return [a + (b - a) * i / n for i in range(n + 1)]


def bezier(a, c, b, s):
    m = 1 - s
    return tuple(m * m * a[i] + 2 * m * s * c[i] + s * s * b[i] for i in range(3))


def bezier_tan(a, c, b, s):
    return unit(tuple(2 * (1 - s) * (c[i] - a[i]) + 2 * s * (b[i] - c[i]) for i in range(3)))


# ---------------------------------------------------------------- pembina
class Scene:
    def __init__(self, h, rnd):
        self.h = h          # jarak antara titik (ketumpatan)
        self.rnd = rnd
        self.pts = []

    def add(self, p, n, kind, color, appear, phase=None, ch=" "):
        sway = 0.0 if phase is None else 0.016 * max(0.0, p[1] - BASE_Y) ** 2
        hi, lo = COL[color]
        self.pts.append((p[0], p[1], p[2], n[0], n[1], n[2], kind, hi, lo, ch,
                         min(appear, 0.99), sway, phase or 0.0))

    # --- batang (lengkung Bezier)
    def stem(self, a, c, b, t0, t1, phase, color="stem"):
        length = math.dist(a, c) + math.dist(c, b)
        for s in frange(0.0, 1.0, self.h / length):
            self.add(bezier(a, c, b, s), bezier_tan(a, c, b, s), K_STEM, color,
                     t0 + (t1 - t0) * s, phase)

    # --- daun
    def leaf(self, base, out, length, width, appear, phase):
        ld = unit(add(out, (0.0, 0.9, 0.0)))
        side = unit(cross(ld, (0.0, 1.0, 0.0)))
        nrm = unit(cross(side, ld))
        for a in frange(0.0, 1.0, self.h / length):
            hw = width * math.sin(math.pi * a) ** 0.8
            centre = add(add(base, mul(ld, a * length)), (0.0, -0.3 * length * a * a, 0.0))
            bs = frange(-hw, hw, self.h) if hw > self.h * 0.5 else [0.0]
            for b in bs:
                p = add(add(centre, mul(side, b)), mul(nrm, abs(b) * 0.6))
                self.add(p, nrm, K_LEAF, "leaf", appear + 0.12 * a, phase)

    # --- bunga daisy / kosmos / matahari
    def daisy(self, c, axis, R, petals, pcol, ccol, appear, phase, centre=0.28):
        u, w = frame_of(axis)
        h = self.h
        rc = R * centre
        for r in frange(0.0, rc, h):
            n = int(2 * math.pi * r / h) + 1
            for j in range(n):
                th = 2 * math.pi * j / n
                rad = add(mul(u, math.cos(th)), mul(w, math.sin(th)))
                lift = rc * 0.6 * (1 - (r / rc) ** 2)
                p = add(add(c, mul(rad, r)), mul(axis, lift))
                self.add(p, unit(add(axis, mul(rad, r / rc))), K_CENTER, ccol, appear, phase)
        off = self.rnd.uniform(0, math.pi)
        half = math.pi / petals * 0.85
        r0 = rc * 0.7
        for k in range(petals):
            a0 = off + 2 * math.pi * k / petals
            for r in frange(r0, R, h * 0.8):
                s = (r - r0) / (R - r0)
                wid = half * math.sin(math.pi * (0.08 + 0.92 * s)) ** 0.5
                n = int(r * wid / h * 1.2)
                for j in range(-n, n + 1):
                    th = a0 + (wid * j / n if n else 0.0)
                    rad = add(mul(u, math.cos(th)), mul(w, math.sin(th)))
                    p = add(add(c, mul(rad, r)), mul(axis, R * 0.3 * s * s))
                    self.add(p, unit(add(axis, mul(rad, -0.6 * s))), K_SURF, pcol,
                             appear + 0.25 * s, phase)

    # --- tulip (cawan 3 kelopak)
    def tulip(self, c, axis, R, col, appear, phase):
        u, w = frame_of(axis)
        H = R * 1.5
        off = self.rnd.uniform(0, math.pi)
        for v in frange(0.0, 1.0, self.h / H):
            r = R * (0.25 + 0.75 * math.sin(math.pi * (0.1 + 0.6 * v)))
            n = int(2 * math.pi * r / self.h) + 3
            for j in range(n):
                th = 2 * math.pi * j / n
                if v > 0.78 + 0.22 * abs(math.cos(1.5 * (th - off))):
                    continue
                rad = add(mul(u, math.cos(th)), mul(w, math.sin(th)))
                p = add(add(c, mul(rad, r)), mul(axis, v * H))
                self.add(p, unit(add(rad, mul(axis, -0.3))), K_SURF, col, appear + 0.2 * v, phase)

    # --- lavender (tangkai bermanik)
    def lavender(self, c, axis, L, col, appear, phase):
        u, w = frame_of(axis)
        steps = max(4, int(L / (self.h * 1.6)))
        for i in range(steps + 1):
            v = i / steps
            r = 0.055 * (1 - 0.55 * v)
            for j in range(6):
                th = 2 * math.pi * j / 6 + v * 7
                rad = add(mul(u, math.cos(th)), mul(w, math.sin(th)))
                p = add(add(c, mul(axis, v * L)), mul(rad, r))
                self.add(p, rad, K_DOT, col, appear + 0.2 * v, phase, self.rnd.choice("oO0"))

    # --- bunga baby's breath (titik putih kecil)
    def babys_breath(self, c, axis, appear, phase):
        rnd = self.rnd
        for _ in range(rnd.randint(5, 8)):
            d = unit(add(axis, (rnd.uniform(-0.9, 0.9), rnd.uniform(-0.3, 0.6), rnd.uniform(-0.9, 0.9))))
            end = add(c, mul(d, rnd.uniform(0.08, 0.2)))
            self.stem(c, add(c, mul(d, 0.05)), end, appear, appear + 0.05, phase)
            for _ in range(rnd.randint(2, 4)):
                q = add(end, (rnd.uniform(-0.04, 0.04), rnd.uniform(-0.02, 0.04), rnd.uniform(-0.04, 0.04)))
                self.add(q, d, K_DOT, "white", appear + 0.1, phase, rnd.choice("oo.*"))

    # --- pembalut kertas + reben
    def wrapping(self):
        h = self.h
        y0, y1, r0, r1 = -1.75, -0.72, 0.07, 0.62
        H = y1 - y0
        slope = (r1 - r0) / H
        opening = math.pi / 2
        for v in frange(0.0, 1.07, h / (H * 1.15)):
            y = y0 + v * H
            r = r0 + (r1 - r0) * v
            n = int(2 * math.pi * r / h) + 4
            for j in range(n):
                th = 2 * math.pi * j / n
                gap = abs((th - opening + math.pi) % (2 * math.pi) - math.pi)
                if gap < 0.65 * v:                              # belahan kertas
                    continue
                if y > y1 + 0.07 * math.sin(6 * th):            # tepi beralun
                    continue
                rad = (math.cos(th), 0.0, math.sin(th))
                self.add((rad[0] * r, y, rad[2] * r), unit((rad[0], -slope, rad[2])),
                         K_WRAP, "wrap", 0.15 * v)
        # reben melilit pembalut
        yr = -1.38
        rr = r0 + (r1 - r0) * (yr - y0) / H + 0.015
        for y in frange(yr - 0.04, yr + 0.04, h):
            n = int(2 * math.pi * rr / h) + 4
            for j in range(n):
                th = 2 * math.pi * j / n
                rad = (math.cos(th), 0.0, math.sin(th))
                self.add((rad[0] * rr, y, rad[2] * rr), rad, K_SURF, "ribbon", 0.2)
        # simpulan reben (dua gelung + dua hujung)
        front = -math.pi / 2
        rad = (math.cos(front), 0.0, math.sin(front))
        tan = (-math.sin(front), 0.0, math.cos(front))
        knot = mul(rad, rr + 0.02)
        knot = (knot[0], yr, knot[2])
        for side in (-1, 1):
            for k in range(int(2 * math.pi * 0.08 / h) + 6):
                a = 2 * math.pi * k / (int(2 * math.pi * 0.08 / h) + 6)
                p = add(knot, add(mul(tan, side * (0.08 + 0.08 * math.cos(a))),
                                  (0.0, 0.05 * math.sin(a), 0.0)))
                self.add(add(p, mul(rad, 0.03)), rad, K_SURF, "ribbon", 0.22)
            for s in frange(0.0, 1.0, h / 0.25):
                p = add(knot, add(mul(tan, side * 0.07 * s), (0.0, -0.25 * s, 0.0)))
                self.add(add(p, mul(rad, 0.03)), rad, K_SURF, "ribbon", 0.22)
        # hujung batang yang terkeluar di bawah
        for k in range(7):
            a = 2 * math.pi * k / 7
            x, z = 0.035 * math.cos(a), 0.035 * math.sin(a)
            for y in frange(-2.05, BASE_Y, h):
                self.add((x, y, z), (0.0, 1.0, 0.0), K_STEM, "stem", 0.05)


FLOWERS = [
    ("sunflower", "yellow", "brown"),
    ("daisy", "pink", "gold"),
    ("tulip", "red", None),
    ("lavender", "purple", None),
    ("daisy", "white", "yellow"),
    ("daisy", "orange", "brown"),
    ("tulip", "rose", None),
    ("aster", "purple", "gold"),
    ("daisy", "pink", "gold"),
    ("lavender", "blue", None),
    ("tulip", "yellow", None),
    ("daisy", "white", "gold"),
    ("aster", "lilac", "yellow"),
    ("daisy", "red", "gold"),
]


def build_scene(h):
    rnd = random.Random(SEED)
    sc = Scene(h, rnd)
    base = (0.0, BASE_Y, 0.0)
    golden = math.pi * (3 - math.sqrt(5))
    sc.wrapping()

    def stalk(el, az, dist, t_head):
        d = (math.sin(el) * math.cos(az), math.cos(el), math.sin(el) * math.sin(az))
        head = add(base, mul(d, dist))
        sb = add(base, (rnd.uniform(-0.04, 0.04), 0.0, rnd.uniform(-0.04, 0.04)))
        ctrl = (sb[0] + d[0] * dist * 0.3, sb[1] + d[1] * dist * 0.65, sb[2] + d[2] * dist * 0.3)
        phase = rnd.uniform(0, 2 * math.pi)
        sc.stem(sb, ctrl, head, 0.03 + 0.12 * rnd.random(), t_head, phase)
        return d, head, unit(add(d, (0.0, 0.6, 0.0))), phase, (sb, ctrl, head)

    n = 16
    for i in range(n):
        f = i / (n - 1)
        el = math.radians(3 + 60 * math.sqrt(f))
        az = i * golden + rnd.uniform(-0.2, 0.2)
        t_head = 0.5 + 0.2 * rnd.random()
        d, head, axis, phase, curve = stalk(el, az, rnd.uniform(2.0, 2.3) - 0.25 * f, t_head)

        if rnd.random() < 0.55:                       # daun
            s = rnd.uniform(0.35, 0.6)
            out = unit((d[0], 0.0, d[2])) if el > 0.2 else (1.0, 0.0, 0.0)
            sc.leaf(bezier(*curve, s), out, rnd.uniform(0.28, 0.4), 0.07, t_head * s + 0.05, phase)

        kind, c1, c2 = FLOWERS[i % len(FLOWERS)]
        if kind == "sunflower":
            sc.daisy(head, axis, 0.27, 16, c1, c2, t_head, phase, centre=0.45)
        elif kind == "daisy":
            sc.daisy(head, axis, rnd.uniform(0.19, 0.24), rnd.choice((8, 10, 12)), c1, c2, t_head, phase)
        elif kind == "aster":
            sc.daisy(head, axis, rnd.uniform(0.17, 0.2), 14, c1, c2, t_head, phase, centre=0.32)
        elif kind == "tulip":
            sc.tulip(head, axis, rnd.uniform(0.12, 0.14), c1, t_head, phase)
        else:
            sc.lavender(head, axis, rnd.uniform(0.3, 0.4), c1, t_head, phase)

    for _ in range(8):                                # pengisi baby's breath
        el = math.radians(rnd.uniform(15, 62))
        az = rnd.uniform(0, 2 * math.pi)
        t_head = 0.6 + 0.25 * rnd.random()
        d, head, axis, phase, _ = stalk(el, az, rnd.uniform(1.6, 2.0), t_head)
        sc.babys_breath(head, axis, t_head, phase)
    return sc.pts


# ---------------------------------------------------------------- lukisan
def extents(scene):
    """Ukur saiz jambangan (dari semua sudut putaran) supaya muat di skrin."""
    ct, st = math.cos(TILT), math.sin(TILT)
    xmax, ymin, ymax = 0.0, 1e9, -1e9
    for a in range(0, 360, 15):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        for p in scene[::7]:
            x, y, z = p[0], p[1] + Y_OFF, p[2]
            x1, z1 = x * ca + z * sa, z * ca - x * sa
            y2, z2 = y * ct + z1 * st, z1 * ct - y * st
            k = CAM / (CAM + z2)
            xmax = max(xmax, abs(x1 * k))
            ymin, ymax = min(ymin, y2 * k), max(ymax, y2 * k)
    return xmax + 0.05, ymin - 0.05, ymax + 0.08


def make_view(cols, rows, ext):
    xmax, ymin, ymax = ext
    usable = rows - 2
    S = min((usable - 1) / (ymax - ymin), (cols - 2) / (2 * xmax * ASP))
    return cols, rows, S, cols / 2.0, (usable - (ymax - ymin) * S) / 2.0 + ymax * S


def render(scene, t, g, view, stars, petals, msg, dt):
    cols, rows, S, cx, cy = view
    size = cols * rows
    zbuf = [1e9] * size
    chars = [" "] * size
    colors = [0] * size

    ang = t * SPIN_SPEED
    ca, sa = math.cos(ang), math.sin(ang)
    ct, st = math.cos(TILT), math.sin(TILT)
    lx, ly, lz = unit(LIGHT)
    sin, cos, atan2 = math.sin, math.cos, math.atan2
    kS = S * ASP

    for (x, y, z, nx, ny, nz, kind, hi, lo, ch, appear, sway, ph) in scene:
        if appear > g:
            continue
        if sway:                                     # alunan angin
            x += sway * sin(t * 1.3 + ph)
            z += sway * cos(t * 1.05 + ph * 1.7)
        x1 = x * ca + z * sa
        z1 = z * ca - x * sa
        y1 = y + Y_OFF
        y2 = y1 * ct + z1 * st
        z2 = z1 * ct - y1 * st
        k = CAM / (CAM + z2)
        sx = int(cx + x1 * k * kS + 0.5)
        sy = int(cy - y2 * k * S + 0.5)
        if sx < 0 or sx >= cols or sy < 0 or sy >= rows - 2:
            continue
        i = sy * cols + sx
        if z2 >= zbuf[i]:
            continue
        zbuf[i] = z2
        nx1 = nx * ca + nz * sa
        nz1 = nz * ca - nx * sa
        ny2 = ny * ct + nz1 * st
        if kind == K_STEM:
            deg = math.degrees(atan2(ny2, nx1)) % 180
            ch = "-" if deg < 22.5 or deg >= 157.5 else "/" if deg < 67.5 else "|" if deg < 112.5 else "\\"
            col = hi if z2 < 0.2 else lo
        else:
            nz2 = nz1 * ct - ny * st
            if kind == K_DOT:
                col = hi if nz2 < 0.3 else lo
            else:
                lum = 0.15 + 0.85 * abs(nx1 * lx + ny2 * ly + nz2 * lz)
                ramp = RAMPS[kind]
                ch = ramp[min(len(ramp) - 1, int(lum * len(ramp)))]
                col = hi if lum > 0.4 else lo
        chars[i] = ch
        colors[i] = col

    # bintang berkelip
    for (sx, sy, ph, sp) in stars:
        i = sy * cols + sx
        if chars[i] != " ":
            continue
        b = sin(t * sp + ph)
        if b > 0.3:
            chars[i] = "*" if b > 0.9 else "+" if b > 0.7 else "."
            colors[i] = 229 if b > 0.7 else 244

    # kelopak gugur (selepas mekar)
    if g >= 1.0:
        for p in petals:
            p[1] += p[2] * dt
            p[0] += sin(t * 1.4 + p[3]) * dt * 1.5
            if p[1] >= rows - 2:
                p[0], p[1] = random.uniform(0, cols - 1), -1.0
            sx, sy = int(p[0]), int(p[1])
            if 0 <= sx < cols and 0 <= sy < rows - 2:
                chars[sy * cols + sx] = p[4]
                colors[sy * cols + sx] = p[5]

    # pesanan ditaip
    t_msg = GROW_SECONDS * 0.85
    if t > t_msg:
        shown = msg[: int((t - t_msg) * 14)]
        row = rows - 1
        start = max(0, (cols - len(msg)) // 2)
        wave = (213, 219, 225, 231, 225, 219)
        for j, c in enumerate(shown):
            if start + j < cols:
                chars[row * cols + start + j] = c
                colors[row * cols + start + j] = wave[(j + int(t * 8)) % len(wave)]

    out = ["\x1b[H"]
    for r in range(rows):
        last = -1
        base = r * cols
        for c in range(cols):
            ch = chars[base + c]
            if ch != " ":
                co = colors[base + c]
                if co != last:
                    out.append("\x1b[38;5;%dm" % co)
                    last = co
            out.append(ch)
        out.append("\x1b[0m")
        if r < rows - 1:
            out.append("\n")
    return "".join(out)


def make_stars(cols, rows, rnd):
    return [(rnd.randrange(cols), rnd.randrange(rows - 2), rnd.uniform(0, 6.3), rnd.uniform(0.6, 2.2))
            for _ in range(cols * rows // 45)]


def make_petals(cols, rows, rnd):
    return [[rnd.uniform(0, cols - 1), rnd.uniform(-rows, 0), rnd.uniform(1.5, 3.5),
             rnd.uniform(0, 6.3), rnd.choice("*o',"), rnd.choice((213, 205, 231, 219))]
            for _ in range(max(6, cols // 12))]


def main():
    msg = " ".join(sys.argv[1:]) or MESSAGE
    if os.name == "nt":
        os.system("")                                # hidupkan warna ANSI di Windows
    out = sys.stdout
    out.write("\x1b[?1049h\x1b[?25l\x1b[2J")
    size = ext = None
    start = last = time.time()
    try:
        while True:
            now = time.time()
            t, dt = now - start, now - last
            last = now
            ts = shutil.get_terminal_size((100, 40))
            if (ts.columns, ts.lines) != size:          # saiz terminal berubah -> bina semula
                size = (ts.columns, ts.lines)
                cols, rows = max(20, ts.columns - 1), max(10, ts.lines)
                if ext is None:
                    ext = extents(build_scene(0.05))
                view = make_view(cols, rows, ext)
                scene = build_scene(max(0.012, 0.32 / view[2]))
                rnd = random.Random()
                stars, petals = make_stars(cols, rows, rnd), make_petals(cols, rows, rnd)
                out.write("\x1b[2J")
            x = min(1.0, t / GROW_SECONDS)
            g = x * x * (3 - 2 * x)                     # smoothstep
            out.write(render(scene, t, g, view, stars, petals, msg, dt))
            out.flush()
            time.sleep(max(0.0, 1.0 / FPS - (time.time() - now)))
    except KeyboardInterrupt:
        pass
    finally:
        out.write("\x1b[0m\x1b[?25h\x1b[?1049l")
        out.flush()


if __name__ == "__main__":
    main()
