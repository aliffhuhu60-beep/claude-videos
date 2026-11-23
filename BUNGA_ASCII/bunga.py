#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bunga.py - Jambangan bunga liar ASCII 3D yang BERGERAK di terminal.

  * batang tumbuh dari bawah, kemudian bunga mekar satu per satu
  * ros, bunga matahari, kosmos, daisi, tulip, aster, lavender, baby's breath
  * jambangan berputar perlahan (3D sebenar: z-buffer + pencahayaan + kabus)
  * warna gradien lembut (24-bit truecolor bila terminal menyokong)
  * bunga beralun ditiup angin, bintang berkelip, kelopak gugur
  * pesanan ditaip di bawah jambangan

Cara jalankan (Python 3.8+, tiada pustaka tambahan diperlukan):

    python3 bunga.py
    python3 bunga.py "untuk awak, sayang"
    python3 bunga.py --256          # paksa 256 warna (terminal lama)
    python3 bunga.py --truecolor    # paksa warna 24-bit

Tekan Ctrl+C untuk berhenti.
Tip: besarkan tetingkap terminal dan kecilkan saiz fon (Ctrl/Cmd + -)
untuk bunga yang lebih besar dan halus.
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
SPIN_SPEED = 0.30       # kelajuan putaran (radian / saat)
TILT = 0.40             # pandangan sedikit dari atas (radian)
SPREAD = 58             # sudut kembang jambangan (darjah); kecil = lebih tinggi & ramping
SEED = 2026             # tukar nombor ini untuk susunan bunga yang lain

ASP = 2.0               # tinggi satu aksara terminal / lebarnya
CAM = 7.0               # jarak kamera (perspektif)
Y_OFF = 0.70            # anjakan menegak supaya jambangan di tengah
BASE_Y = -1.30          # titik semua batang bertemu (dalam pembalut)
LIGHT = (-0.35, 0.55, -0.75)
LEVELS = 12             # bilangan tahap cahaya

# warna RGB: (dalam, luar) — kelopak bergradien dari tengah ke hujung
PAL = {
    "rose_red":  ((150, 0, 35), (255, 70, 100)),
    "rose_pink": ((205, 45, 120), (255, 165, 200)),
    "cosmos":    ((235, 60, 160), (255, 195, 235)),
    "white":     ((250, 225, 190), (255, 255, 255)),
    "sun":       ((255, 150, 0), (255, 235, 70)),
    "orange":    ((255, 100, 20), (255, 200, 100)),
    "purple":    ((110, 55, 215), (205, 160, 255)),
    "lilac":     ((165, 115, 230), (235, 210, 255)),
    "lavender":  ((120, 80, 225), (175, 140, 255)),
    "blue":      ((40, 110, 245), (130, 190, 255)),
    "t_red":     ((190, 0, 40), (255, 90, 90)),
    "t_yellow":  ((255, 190, 0), (255, 245, 140)),
    "t_pink":    ((240, 80, 150), (255, 185, 215)),
    "gold":      ((255, 175, 20), (255, 215, 60)),
    "brown":     ((95, 50, 15), (165, 95, 30)),
    "stem":      ((70, 170, 80), (120, 225, 120)),
    "leaf":      ((25, 140, 60), (110, 225, 110)),
    "wrap":      ((240, 185, 200), (255, 225, 232)),
    "ribbon":    ((230, 30, 120), (255, 90, 170)),
    "bwhite":    ((240, 240, 255), (255, 255, 255)),
}

# jenis titik
K_SURF, K_STEM, K_LEAF, K_WRAP, K_DOT, K_CENTER = range(6)
RAMPS = {
    K_SURF: ".:-=+oO0@",
    K_LEAF: ".,-~=+*",
    K_WRAP: ".,:;=+*#",
    K_CENTER: ".:*#%@",
}

TRUECOLOR = False       # ditetapkan dalam main()


# ---------------------------------------------------------------- warna
def to256(r, g, b):
    q = lambda v: 0 if v < 48 else 1 if v < 115 else min(5, (v - 35) // 40)
    return 16 + 36 * q(r) + 6 * q(g) + q(b)


def esc(rgb):
    r, g, b = (max(0, min(255, int(c))) for c in rgb)
    return "\x1b[38;2;%d;%d;%dm" % (r, g, b) if TRUECOLOR else "\x1b[38;5;%dm" % to256(r, g, b)


_SHADES = {}
SHADE_TABLE = []


def shade_id(rgb):
    """Senarai kod warna untuk satu warna asas, dari gelap ke terang."""
    rgb = tuple(int(c) for c in rgb)
    if rgb not in _SHADES:
        row = []
        for L in range(LEVELS):
            e = L / (LEVELS - 1)
            k = 0.4 + 0.75 * e
            c = [v * k for v in rgb]
            if e > 0.8:                                  # kilauan
                m = (e - 0.8) * 1.6
                c = [v + (255 - v) * m for v in c]
            row.append(esc(c))
        _SHADES[rgb] = len(SHADE_TABLE)
        SHADE_TABLE.append(row)
    return _SHADES[rgb]


def mix(a, b, s):
    return tuple(a[i] + (b[i] - a[i]) * s for i in range(3))


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
        self.h = h
        self.rnd = rnd
        self.pts = []

    def add(self, p, n, kind, pal, s, appear, phase=None, ch=" "):
        """pal = nama warna, s = 0..1 kedudukan dalam gradien (dalam -> luar)."""
        sway = 0.0 if phase is None else 0.014 * max(0.0, p[1] - BASE_Y) ** 2
        a, b = PAL[pal]
        sid = shade_id(mix(a, b, round(s * 4) / 4))
        self.pts.append((p[0], p[1], p[2], n[0], n[1], n[2], kind, sid, ch,
                         min(appear, 0.99), sway, phase or 0.0))

    def stem(self, a, c, b, t0, t1, phase, pal="stem"):
        length = math.dist(a, c) + math.dist(c, b)
        for s in frange(0.0, 1.0, self.h / length):
            self.add(bezier(a, c, b, s), bezier_tan(a, c, b, s), K_STEM, pal, s,
                     t0 + (t1 - t0) * s, phase)

    def leaf(self, base, out, length, width, appear, phase):
        ld = unit(add(out, (0.0, 0.8, 0.0)))
        side = unit(cross(ld, (0.0, 1.0, 0.0)))
        nrm = unit(cross(side, ld))
        for a in frange(0.0, 1.0, self.h / length):
            hw = width * math.sin(math.pi * a) ** 0.7
            centre = add(add(base, mul(ld, a * length)), (0.0, -0.35 * length * a * a, 0.0))
            bs = frange(-hw, hw, self.h) if hw > self.h * 0.5 else [0.0]
            for b in bs:
                p = add(add(centre, mul(side, b)), mul(nrm, abs(b) * 0.6))
                self.add(p, nrm, K_LEAF, "leaf", a, appear + 0.12 * a, phase)

    def daisy(self, c, axis, R, petals, pal, cpal, appear, phase, centre=0.28, cup=0.3):
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
                self.add(p, unit(add(axis, mul(rad, r / rc))), K_CENTER, cpal, r / rc, appear, phase)
        off = self.rnd.uniform(0, math.pi)
        half = math.pi / petals * 0.9
        r0 = rc * 0.7
        for k in range(petals):
            a0 = off + 2 * math.pi * k / petals
            for r in frange(r0, R, h * 0.75):
                s = (r - r0) / (R - r0)
                wid = half * math.sin(math.pi * (0.08 + 0.92 * s)) ** 0.5
                n = int(r * wid / h * 1.3)
                for j in range(-n, n + 1):
                    th = a0 + (wid * j / n if n else 0.0)
                    rad = add(mul(u, math.cos(th)), mul(w, math.sin(th)))
                    p = add(add(c, mul(rad, r)), mul(axis, R * cup * s * s))
                    self.add(p, unit(add(axis, mul(rad, -0.6 * s))), K_SURF, pal, s,
                             appear + 0.25 * s, phase)

    def rose(self, c, axis, R, pal, appear, phase):
        """Kelopak berlingkar (spiral) seperti bunga ros."""
        u, w = frame_of(axis)
        h = self.h
        turns = 3.3
        thmax = 2 * math.pi * turns
        off = self.rnd.uniform(0, 2 * math.pi)
        th = 0.6
        while th < thmax:
            s = th / thmax
            r = R * s
            Hh = R * 0.62 * (1 - 0.4 * s) * (0.82 + 0.18 * math.cos(th * 1.7))
            for v in frange(0.0, Hh, h):
                f = (v / Hh) ** 2 * 0.3 * R * s           # kelopak luar mengembang
                rad = add(mul(u, math.cos(th + off)), mul(w, math.sin(th + off)))
                p = add(add(c, mul(rad, r + f)), mul(axis, v - 0.15 * R))
                self.add(p, unit(add(rad, mul(axis, -0.5 * f / R))), K_SURF, pal, s,
                         appear + 0.25 * s, phase)
            th += h / max(r, 0.03) * 0.9
        for r in frange(0.0, R, h):                       # dasar cawan
            n = int(2 * math.pi * r / h) + 1
            for j in range(n):
                t2 = 2 * math.pi * j / n
                rad = add(mul(u, math.cos(t2)), mul(w, math.sin(t2)))
                self.add(add(add(c, mul(rad, r)), mul(axis, -0.15 * R)), axis, K_SURF, pal,
                         0.0, appear, phase)

    def tulip(self, c, axis, R, pal, appear, phase):
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
                self.add(p, unit(add(rad, mul(axis, -0.3))), K_SURF, pal, v, appear + 0.2 * v, phase)

    def lavender(self, c, axis, L, pal, appear, phase):
        u, w = frame_of(axis)
        steps = max(4, int(L / (self.h * 1.4)))
        for i in range(steps + 1):
            v = i / steps
            r = 0.065 * (1 - 0.55 * v)
            for j in range(7):
                th = 2 * math.pi * j / 7 + v * 7
                rad = add(mul(u, math.cos(th)), mul(w, math.sin(th)))
                p = add(add(c, mul(axis, v * L)), mul(rad, r))
                self.add(p, rad, K_DOT, pal, v, appear + 0.2 * v, phase, self.rnd.choice("oO0@"))

    def babys_breath(self, c, axis, appear, phase):
        rnd = self.rnd
        for _ in range(rnd.randint(6, 9)):
            d = unit(add(axis, (rnd.uniform(-0.9, 0.9), rnd.uniform(-0.3, 0.6), rnd.uniform(-0.9, 0.9))))
            end = add(c, mul(d, rnd.uniform(0.1, 0.24)))
            self.stem(c, add(c, mul(d, 0.05)), end, appear, appear + 0.05, phase)
            for _ in range(rnd.randint(3, 5)):
                q = add(end, (rnd.uniform(-0.05, 0.05), rnd.uniform(-0.02, 0.05), rnd.uniform(-0.05, 0.05)))
                self.add(q, d, K_DOT, "bwhite", 1.0, appear + 0.1, phase, rnd.choice("oo*."))

    def wrapping(self):
        h = self.h
        y0, y1, r0, r1 = -1.75, -0.72, 0.07, 0.66
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
                if gap < 0.65 * v:
                    continue
                if y > y1 + 0.08 * math.sin(6 * th):
                    continue
                rad = (math.cos(th), 0.0, math.sin(th))
                self.add((rad[0] * r, y, rad[2] * r), unit((rad[0], -slope, rad[2])),
                         K_WRAP, "wrap", v, 0.15 * v)
        yr = -1.38
        rr = r0 + (r1 - r0) * (yr - y0) / H + 0.015
        for y in frange(yr - 0.045, yr + 0.045, h):
            n = int(2 * math.pi * rr / h) + 4
            for j in range(n):
                th = 2 * math.pi * j / n
                rad = (math.cos(th), 0.0, math.sin(th))
                self.add((rad[0] * rr, y, rad[2] * rr), rad, K_SURF, "ribbon", 0.5, 0.2)
        front = -math.pi / 2
        rad = (math.cos(front), 0.0, math.sin(front))
        tan = (-math.sin(front), 0.0, math.cos(front))
        knot = mul(rad, rr + 0.02)
        knot = (knot[0], yr, knot[2])
        nl = int(2 * math.pi * 0.1 / h) + 6
        for side in (-1, 1):
            for lw in frange(-0.025, 0.025, h):
                for k in range(nl):
                    a = 2 * math.pi * k / nl
                    p = add(knot, add(mul(tan, side * (0.1 + 0.1 * math.cos(a))),
                                      (0.0, 0.06 * math.sin(a) + lw, 0.0)))
                    self.add(add(p, mul(rad, 0.03)), rad, K_SURF, "ribbon", 1.0, 0.22)
            for s in frange(0.0, 1.0, h / 0.3):
                p = add(knot, add(mul(tan, side * 0.09 * s), (0.0, -0.3 * s, 0.0)))
                self.add(add(p, mul(rad, 0.03)), rad, K_SURF, "ribbon", 0.5, 0.22)
        for k in range(7):
            a = 2 * math.pi * k / 7
            x, z = 0.035 * math.cos(a), 0.035 * math.sin(a)
            for y in frange(-2.05, BASE_Y, h):
                self.add((x, y, z), (0.0, 1.0, 0.0), K_STEM, "stem", 0.0, 0.05)


FLOWERS = [
    ("rose", "rose_red"),
    ("sunflower", "sun"),
    ("daisy", "cosmos"),
    ("tulip", "t_red"),
    ("lavender", "lavender"),
    ("rose", "rose_pink"),
    ("daisy", "white"),
    ("daisy", "orange"),
    ("aster", "purple"),
    ("tulip", "t_pink"),
    ("rose", "rose_red"),
    ("lavender", "blue"),
    ("daisy", "cosmos"),
    ("tulip", "t_yellow"),
    ("aster", "lilac"),
    ("rose", "rose_pink"),
    ("daisy", "white"),
]


def build_scene(h, spread=None):
    spread = SPREAD if spread is None else spread
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
        return d, head, unit(add(mul(d, 0.8), (0.0, 1.0, 0.0))), phase, (sb, ctrl, head)

    n = len(FLOWERS)
    for i in range(n):
        f = i / (n - 1)
        el = math.radians(3 + (spread - 3) * math.sqrt(f))
        az = i * golden + rnd.uniform(-0.2, 0.2)
        t_head = 0.5 + 0.2 * rnd.random()
        d, head, axis, phase, curve = stalk(el, az, rnd.uniform(2.05, 2.35) - 0.3 * f, t_head)

        for _ in range(2 if rnd.random() < 0.5 else 1):         # daun
            s = rnd.uniform(0.3, 0.6)
            out = unit((d[0], 0.0, d[2])) if el > 0.2 else (math.cos(az), 0.0, math.sin(az))
            out = unit(add(out, (rnd.uniform(-0.6, 0.6), 0.0, rnd.uniform(-0.6, 0.6))))
            sc.leaf(bezier(*curve, s), out, rnd.uniform(0.32, 0.46), 0.08, t_head * s + 0.05, phase)

        kind, pal = FLOWERS[i]
        if kind == "sunflower":
            sc.daisy(head, axis, 0.36, 20, pal, "brown", t_head, phase, centre=0.45, cup=0.2)
        elif kind == "daisy":
            cp = "brown" if pal == "orange" else "gold"
            sc.daisy(head, axis, rnd.uniform(0.25, 0.3), rnd.choice((8, 10, 12)), pal, cp, t_head, phase)
        elif kind == "aster":
            sc.daisy(head, axis, rnd.uniform(0.22, 0.26), 16, pal, "gold", t_head, phase, centre=0.3)
        elif kind == "rose":
            sc.rose(head, axis, rnd.uniform(0.25, 0.3), pal, t_head, phase)
        elif kind == "tulip":
            sc.tulip(head, axis, rnd.uniform(0.15, 0.17), pal, t_head, phase)
        else:
            sc.lavender(head, axis, rnd.uniform(0.38, 0.48), pal, t_head, phase)

    for _ in range(9):                                            # pengisi baby's breath
        el = math.radians(rnd.uniform(12, spread + 2))
        az = rnd.uniform(0, 2 * math.pi)
        t_head = 0.6 + 0.25 * rnd.random()
        d, head, axis, phase, _ = stalk(el, az, rnd.uniform(1.75, 2.15), t_head)
        sc.babys_breath(head, axis, t_head, phase)
    return sc.pts


# ---------------------------------------------------------------- lukisan
def extents(scene):
    """Ukur saiz jambangan (dari semua sudut putaran) supaya muat di skrin."""
    ct, st = math.cos(TILT), math.sin(TILT)
    xmax, ymin, ymax = 0.0, 1e9, -1e9
    for a in range(0, 360, 15):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        for p in scene[::5]:
            x, y, z = p[0], p[1] + Y_OFF, p[2]
            x1, z1 = x * ca + z * sa, z * ca - x * sa
            y2, z2 = y * ct + z1 * st, z1 * ct - y * st
            k = CAM / (CAM + z2)
            xmax = max(xmax, abs(x1 * k))
            ymin, ymax = min(ymin, y2 * k), max(ymax, y2 * k)
    return xmax + 0.1, ymin - 0.03, ymax + 0.14   # + ruang untuk alunan


def make_view(cols, rows, ext):
    xmax, ymin, ymax = ext
    usable = rows - 2
    S = min(usable / (ymax - ymin), cols / (2 * xmax * ASP))
    cy = (usable - (ymax - ymin) * S) / 2.0 + ymax * S
    bottom = int(cy - ymin * S)
    return cols, rows, S, cols / 2.0, cy, min(rows - 1, bottom + 1)


def render(scene, t, g, view, stars, petals, msg, dt):
    cols, rows, S, cx, cy, msg_row = view
    size = cols * rows
    zbuf = [1e9] * size
    chars = [" "] * size
    colors = [""] * size

    ang = t * SPIN_SPEED
    ca, sa = math.cos(ang), math.sin(ang)
    ct, st = math.cos(TILT), math.sin(TILT)
    lx, ly, lz = unit(LIGHT)
    sin, cos, atan2 = math.sin, math.cos, math.atan2
    kS = S * ASP
    top = LEVELS - 1
    table = SHADE_TABLE

    for (x, y, z, nx, ny, nz, kind, sid, ch, appear, sway, ph) in scene:
        if appear > g:
            continue
        if sway:
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
        if sx < 0 or sx >= cols or sy < 0 or sy >= rows - 1:
            continue
        i = sy * cols + sx
        if z2 >= zbuf[i]:
            continue
        zbuf[i] = z2
        fog = 1.0 - 0.22 * min(1.0, max(0.0, (z2 + 0.6) / 1.8))   # belakang lebih malap
        nx1 = nx * ca + nz * sa
        nz1 = nz * ca - nx * sa
        ny2 = ny * ct + nz1 * st
        if kind == K_STEM:
            deg = math.degrees(atan2(ny2, nx1)) % 180
            ch = "-" if deg < 22.5 or deg >= 157.5 else "/" if deg < 67.5 else "|" if deg < 112.5 else "\\"
            e = 0.65 * fog
        else:
            nz2 = nz1 * ct - ny * st
            if kind == K_DOT:
                e = (0.9 if nz2 < 0.3 else 0.5) * fog
            else:
                e = (0.12 + 0.88 * abs(nx1 * lx + ny2 * ly + nz2 * lz)) * fog
                ramp = RAMPS[kind]
                ch = ramp[min(len(ramp) - 1, int(e * len(ramp)))]
        chars[i] = ch
        colors[i] = table[sid][min(top, int(e * LEVELS))]

    star_hi, star_lo, star_mid = STAR_CODES
    for (sx, sy, ph, sp) in stars:
        i = sy * cols + sx
        if chars[i] != " ":
            continue
        b = sin(t * sp + ph)
        if b > 0.3:
            chars[i] = "*" if b > 0.9 else "+" if b > 0.7 else "."
            colors[i] = star_hi if b > 0.9 else star_mid if b > 0.7 else star_lo

    if g >= 1.0:
        for p in petals:
            p[1] += p[2] * dt
            p[0] += sin(t * 1.4 + p[3]) * dt * 1.5
            if p[1] >= rows - 1:
                p[0], p[1] = random.uniform(0, cols - 1), -1.0
            sx, sy = int(p[0]), int(p[1])
            if 0 <= sx < cols and 0 <= sy < rows - 1:
                chars[sy * cols + sx] = p[4]
                colors[sy * cols + sx] = p[5]

    t_msg = GROW_SECONDS * 0.85
    if t > t_msg:
        shown = msg[: int((t - t_msg) * 14)]
        start = max(0, (cols - len(msg)) // 2)
        for j, c in enumerate(shown):
            if start + j < cols:
                i = msg_row * cols + start + j
                chars[i] = c
                colors[i] = MSG_CODES[(j + int(t * 8)) % len(MSG_CODES)]

    out = ["\x1b[H"]
    for r in range(rows):
        last = ""
        base = r * cols
        for c in range(cols):
            ch = chars[base + c]
            if ch != " ":
                co = colors[base + c]
                if co != last:
                    out.append(co)
                    last = co
            out.append(ch)
        out.append("\x1b[0m")
        if r < rows - 1:
            out.append("\n")
    return "".join(out)


def make_stars(cols, rows, rnd):
    return [(rnd.randrange(cols), rnd.randrange(rows - 1), rnd.uniform(0, 6.3), rnd.uniform(0.6, 2.2))
            for _ in range(cols * rows // 40)]


def make_petals(cols, rows, rnd):
    cols_ = [esc(c) for c in ((255, 130, 200), (255, 90, 150), (255, 255, 255), (255, 190, 230))]
    return [[rnd.uniform(0, cols - 1), rnd.uniform(-rows, 0), rnd.uniform(1.5, 3.5),
             rnd.uniform(0, 6.3), rnd.choice("*o',"), rnd.choice(cols_)]
            for _ in range(max(8, cols // 10))]


def main():
    global TRUECOLOR, STAR_CODES, MSG_CODES
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    msg = " ".join(args) or MESSAGE
    TRUECOLOR = "--truecolor" in flags or (
        "--256" not in flags and os.environ.get("COLORTERM", "").lower() in ("truecolor", "24bit"))
    STAR_CODES = (esc((255, 255, 210)), esc((110, 110, 140)), esc((220, 220, 160)))
    MSG_CODES = [esc(c) for c in ((255, 120, 200), (255, 160, 220), (255, 200, 235),
                                  (255, 255, 255), (255, 200, 235), (255, 160, 220))]
    if os.name == "nt":
        os.system("")
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
            if (ts.columns, ts.lines) != size:
                size = (ts.columns, ts.lines)
                cols, rows = max(20, ts.columns - 1), max(10, ts.lines)
                if ext is None:
                    ext = extents(build_scene(0.05))
                view = make_view(cols, rows, ext)
                scene = build_scene(max(0.01, 0.3 / view[2]))
                rnd = random.Random()
                stars, petals = make_stars(cols, rows, rnd), make_petals(cols, rows, rnd)
                out.write("\x1b[2J")
            x = min(1.0, t / GROW_SECONDS)
            g = x * x * (3 - 2 * x)
            out.write(render(scene, t, g, view, stars, petals, msg, dt))
            out.flush()
            time.sleep(max(0.0, 1.0 / FPS - (time.time() - now)))
    except KeyboardInterrupt:
        pass
    finally:
        out.write("\x1b[0m\x1b[?25h\x1b[?1049l")
        out.flush()


STAR_CODES = MSG_CODES = None

if __name__ == "__main__":
    main()
