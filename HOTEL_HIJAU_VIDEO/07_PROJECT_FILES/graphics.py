"""Penjana motion graphics v2 (2560x1440 @30fps) — SIMULASI PENGAJARAN MIKRO: MISI PENGAWAL BAHASA, HOTEL HIJAU.

Setiap grafik dijana sebagai jujukan PNG RGBA (Pillow) dan dikodkan ke .mov (qtrle, ber-alpha).
Grafik bersaiz kecil (bukan skrin penuh) di-overlay pada kedudukan (x, y) yang dicatat dalam
05_GRAPHICS/manifest.json — lebih pantas dan tajam.

Usage: python3 graphics.py <out_dir> <config.json> [nama_grafik ...]
config.json (dijana oleh build_video.py): {"teacher_mins": ["00:09 – 09:30", ...]}
"""
import json, math, os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 2560, 1440, 30
SC = W / 1920.0                      # reka bentuk dalam unit 1920x1080, diskala ke 1440p
def u(v): return int(round(v * SC))
FONT_DIR = "/usr/share/fonts/opentype/inter/"
_fc = {}
def F(name, size):
    k = (name, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(FONT_DIR + name, u(size))
    return _fc[k]

# ---- Palet ----
FOREST = (11, 59, 44); FOREST2 = (6, 38, 28); GREEN = (110, 176, 98); GREEN_L = (150, 214, 132)
GOLD = (212, 175, 55); GOLD_L = (240, 214, 130); WHITE = (255, 255, 255); SOFT = (222, 236, 222)

# ---- Data guru (ejaan TEPAT) ----
TEACHERS = [
    dict(no="01", name="MOHAMAD ALIFF BIN AHMAD SHAHABUDDIN", role="PENGURUS HOTEL HIJAU", phase="Set Induksi"),
    dict(no="02", name="MUHAMMAD IMAN IRFAN BIN MOHD RAMZI", role="KETUA PEMANTAU ZON", phase="Langkah 1"),
    dict(no="03", name="AMIN NAJMI BIN MOHYIDIN", role="KETUA PENGAWAL BAHASA", phase="Langkah 2 & Penutup (Refleksi)"),
]

# ---- Fasa PdP ----
PHASES = {
    "set_induksi": ("SET INDUKSI", "Salam, video Hotel Hijau, soal jawab & pembentukan kumpulan"),
    "langkah_1": ("LANGKAH 1", "Misi Pengawal Bahasa dalam Minecraft Education"),
    "langkah_2": ("LANGKAH 2", "Aktiviti AR: membina ayat aktif dan ayat pasif"),
    "penutup": ("PENUTUP (REFLEKSI)", "Tiket refleksi dan rumusan pembelajaran"),
}

# ---- Langkah aktiviti (berdasarkan teks sebenar pada skrin dalam rakaman) ----
STEPS = {
    "steps_misi1": ("MISI 1 · STESEN MINECRAFT", [
        "Pergi ke stesen dalam dunia Hotel Hijau",
        "Baca SOALAN pada papan stesen",
        "Tentukan: ayat AKTIF atau ayat PASIF?",
        "Pijak petak HIJAU untuk menjawab",
        "Lengkapkan aktiviti di stesen",
    ]),
    "steps_misi2": ("MISI 2 · TUKAR AYAT", [
        "Baca situasi dan ayat pada papan",
        "Tukar ayat mengikut arahan (pasif kepada aktif)",
        "Tulis NAMA dan jawapan dalam buku",
        "Letak buku di lectern stesen",
        "Lengkapkan aktiviti (cth. tuai 3 lobak merah)",
    ]),
    "steps_ar": ("AKTIVITI AR · MISI PENGAWAL BAHASA", [
        "Isi nama dan kelas, tekan Mula Kamera",
        "Pilih situasi kumpulan",
        "Perhatikan animasi AR",
        "Bina satu ayat AKTIF dan satu ayat PASIF",
        "Hantar — jawapan masuk ke Galeri Jawapan",
    ]),
}

# ---- Ayat murid (disalin daripada Galeri Jawapan & rakaman) ----
# setiap ayat: senarai segmen (teks, penting?)
SENTENCES = {
    "ayat_misi2": ("ARAHAN MISI 2 · SITUASI LADANG ORGANIK", [
        ("Tukar kepada ayat aktif", "PASIF",
         [("Sayur-sayuran ", 0), ("dituai", 1), (" oleh tukang kebun di ladang organik.", 0)], None),
    ]),
    "ayat_galeri": ("AYAT YANG DIBINA MURID · GALERI JAWAPAN", [
        ("Situasi 1 · kata kerja: mengasingkan", "AKTIF",
         [("Amin ", 0), ("mengasingkan", 1), (" sampah mengikut tong warna kitar semula.", 0)],
         [("Sampah ", 0), ("diasingkan", 1), (" oleh Amin mengikut tong warna kitar semula.", 0)]),
        ("Situasi 3 · kata kerja: memasang", "AKTIF",
         [("Ali ", 0), ("memasang", 1), (" lampu itu.", 0)],
         [("Lampu itu ", 0), ("dipasang", 1), (" oleh Ali.", 0)]),
        ("Situasi 3 · kata kerja: memasang", "AKTIF",
         [("Pelayan hotel sedang ", 0), ("memasang", 1), (" lampu di lobi hotel.", 0)],
         [("Lampu ", 0), ("dipasang", 1), (" oleh pelayan hotel di lobi hotel.", 0)]),
    ]),
    "ayat_rumusan": ("RUMUSAN · MURID MEMBACAKAN AYAT", [
        ("Ayat murid", "AKTIF",
         [("Saya ", 0), ("mempelajari", 1), (" tajuk ayat aktif dan pasif.", 0)],
         [("Tajuk ayat aktif dan pasif saya ", 0), ("pelajari", 1), (".", 0)]),
    ]),
}

# ---- Easing / util ----
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, t0, t1): return clamp((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t0)
def ease_out(x): return 1 - (1 - x) ** 3
def ease_io(x): return 3 * x * x - 2 * x * x * x
def ease_back(x, s=1.4):
    x -= 1; return x * x * ((s + 1) * x + s) + 1
def tw(font, s, tr=0): return font.getlength(s) + u(tr) * max(0, len(s) - 1)
def dtext(d, xy, s, font, fill, tr=0):
    x, y = xy
    if not tr: d.text((x, y), s, font=font, fill=fill); return
    for ch in s:
        d.text((x, y), ch, font=font, fill=fill); x += font.getlength(ch) + u(tr)
def alpha(img, a):
    if a >= 0.999: return img
    if a <= 0.001: return Image.new("RGBA", img.size, (0, 0, 0, 0))
    r, g, b, al = img.split(); return Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * a))))
def sweep(size, p, wdt=160):
    w, h = size; m = Image.new("L", size, 0); d = ImageDraw.Draw(m)
    wdt = u(wdt); cx = -wdt * 2 + p * (w + wdt * 4)
    for i in range(0, wdt, 2):
        a = int(70 * math.sin(math.pi * i / wdt) ** 2); x = cx + i
        d.line([(x, 0), (x - h * 0.35, h)], fill=a, width=3)
    return m
def card(w, h, r=18, fill=FOREST + (238,), outline=GOLD + (90,)):
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle([0, 0, w - 1, h - 1], u(r), fill=fill)
    g = Image.new("L", (w, h)); gd = ImageDraw.Draw(g)
    for x in range(0, w, 2): gd.line([(x, 0), (x, h)], fill=int(70 * x / w), width=2)
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], u(r), fill=255)
    c.paste(Image.new("RGBA", (w, h), FOREST2 + (255,)), (0, 0), Image.composite(g, Image.new("L", (w, h), 0), m))
    d = ImageDraw.Draw(c); d.rounded_rectangle([1, 1, w - 2, h - 2], u(r), outline=outline, width=max(2, u(2)))
    return c, m
def shadow(w, h, r=22, a=120, blur=18):
    s = Image.new("RGBA", (w + u(80), h + u(80)), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle([u(40), u(50), w + u(40), h + u(40)], u(r), fill=(0, 0, 0, a))
    return s.filter(ImageFilter.GaussianBlur(u(blur)))

MANIFEST = {}
def save_seq(name, fn, n, size, pos, out):
    tmp = os.path.join(out, "_tmp_" + name)
    if os.path.exists(tmp): shutil.rmtree(tmp)
    os.makedirs(tmp)
    for i in range(n):
        im = fn(i / FPS)
        if im.size != size: im = im.crop((0, 0) + size)
        im.save(f"{tmp}/{i:04d}.png", compress_level=1)
    mov = os.path.join(out, name + ".mov")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{tmp}/%04d.png", "-c:v", "qtrle",
                    "-pix_fmt", "argb", mov], check=True)
    shutil.copy(f"{tmp}/{min(n - 1, int(n * 0.6)):04d}.png", os.path.join(out, name + "_still.png"))
    shutil.rmtree(tmp)
    MANIFEST[name] = dict(x=pos[0], y=pos[1], w=size[0], h=size[1], dur=n / FPS)

# =====================================================================
# 1. TAJUK PEMBUKAAN — skrin penuh, latar legap (tiada preview rakaman)
# =====================================================================
def _bg_title():
    import numpy as np
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W * 0.5) / (W * 0.6)) ** 2 + ((yy - H * 0.45) / (H * 0.7)) ** 2)
    t = np.clip(r, 0, 1)[..., None]
    a = np.array(FOREST, float) * 1.15; b = np.array((3, 22, 16), float)
    img = (a * (1 - t) + b * t).clip(0, 255).astype("uint8")
    return Image.fromarray(img, "RGB").convert("RGBA")
def title_open(dur=9.0):
    bg = _bg_title()
    f_k = F("Inter-SemiBold.otf", 26); f_1 = F("InterDisplay-Black.otf", 104); f_2 = F("InterDisplay-Bold.otf", 54)
    f_3 = F("Inter-SemiBold.otf", 40); f_4 = F("Inter-Medium.otf", 30)
    K = "DOKUMENTASI PdP  ·  BAHASA MELAYU TAHUN 5"; L1 = "SIMULASI PENGAJARAN MIKRO"; L2 = "(MICRO TEACHING)"
    L3 = "MISI PENGAWAL BAHASA: HOTEL HIJAU"; L4 = "Ayat Aktif dan Ayat Pasif  ·  SP 5.3.3"
    cy = H // 2 - u(40)
    def fr(t):
        img = bg.copy()
        # sinar cahaya lembut bergerak
        rays = sweep((W, H), (t / dur) * 0.9 + 0.05, 420)
        img.paste(Image.new("RGBA", (W, H), (255, 255, 255, 255)), (0, 0), rays.point(lambda v: v // 5))
        d = ImageDraw.Draw(img)
        pk = ease_out(prog(t, 0.3, 1.1))
        if pk > 0:
            tl = Image.new("RGBA", (W, H)); dtext(ImageDraw.Draw(tl), ((W - tw(f_k, K, 8)) / 2, cy - u(190) + u(14) * (1 - pk)), K, f_k, GOLD_L, 8)
            img.alpha_composite(alpha(tl, pk))
        pr = ease_io(prog(t, 0.8, 2.1))
        if pr > 0:
            tl = Image.new("RGBA", (W, H)); w1 = tw(f_1, L1)
            ImageDraw.Draw(tl).text(((W - w1) / 2, cy - u(140)), L1, font=f_1, fill=WHITE)
            m = Image.new("L", (W, H), 0); hw = (w1 / 2 + u(20)) * pr
            ImageDraw.Draw(m).rectangle([W / 2 - hw, 0, W / 2 + hw, H], fill=255)
            msk = Image.composite(tl.split()[3], Image.new("L", (W, H), 0), m)
            img.paste(tl, (0, 0), msk)
            sp = prog(t, 2.3, 3.5)
            if 0 < sp < 1:
                img.paste(Image.new("RGBA", (W, H), GOLD_L + (255,)), (0, 0), Image.composite(sweep((W, H), sp, 220), Image.new("L", (W, H), 0), msk))
        p2 = ease_out(prog(t, 1.8, 2.7))
        if p2 > 0:
            tl = Image.new("RGBA", (W, H)); w2 = tw(f_2, L2, 10)
            dtext(ImageDraw.Draw(tl), ((W - w2) / 2, cy - u(10) + u(20) * (1 - p2)), L2, f_2, GOLD, 10)
            img.alpha_composite(alpha(tl, p2))
        pg = ease_out(prog(t, 2.4, 3.3))
        if pg > 0:
            d = ImageDraw.Draw(img); lw = u(560) * pg
            d.rectangle([W / 2 - lw / 2, cy + u(78), W / 2 + lw / 2, cy + u(82)], fill=GOLD + (255,))
        p3 = ease_out(prog(t, 2.9, 3.8))
        if p3 > 0:
            tl = Image.new("RGBA", (W, H)); td = ImageDraw.Draw(tl)
            td.text(((W - tw(f_3, L3)) / 2, cy + u(110) + u(18) * (1 - p3)), L3, font=f_3, fill=WHITE)
            td.text(((W - tw(f_4, L4)) / 2, cy + u(172) + u(18) * (1 - p3)), L4, font=f_4, fill=GREEN_L)
            img.alpha_composite(alpha(tl, p3))
        return alpha(img, 1 - ease_io(prog(t, dur - 1.0, dur)))
    return fr, int(dur * FPS), (W, H), (0, 0)

# =====================================================================
# 2. KAD FASA (Set Induksi / Langkah 1 / Langkah 2 / Penutup) — atas-kiri, 5 s
# =====================================================================
def phase_card(key, dur=5.0):
    title, sub = PHASES[key]
    f_k = F("Inter-Bold.otf", 22); f_t = F("InterDisplay-Black.otf", 62); f_s = F("Inter-Medium.otf", 28)
    pad = u(34); tw_ = int(max(tw(f_t, title), tw(f_s, sub)) + 2 * pad); th = u(176)
    Wc, Hc = tw_ + u(16), th + u(10); x0, y0 = u(80), u(70)
    def fr(t):
        img = Image.new("RGBA", (Wc, Hc)); d = ImageDraw.Draw(img)
        pl = ease_out(prog(t, 0.0, 0.5)); d.rectangle([0, 0, u(6), int(th * pl)], fill=GOLD + (255,))
        pp = ease_out(prog(t, 0.1, 0.8))
        if pp > 0:
            pn = Image.new("RGBA", (Wc, Hc)); ImageDraw.Draw(pn).rectangle([u(6), 0, u(6) + int(tw_ * pp), th], fill=FOREST + (215,))
            img.alpha_composite(pn); d = ImageDraw.Draw(img); d.rectangle([0, 0, u(6), int(th * pl)], fill=GOLD + (255,))
        txt = Image.new("RGBA", (Wc, Hc)); td = ImageDraw.Draw(txt)
        dtext(td, (pad, u(20)), "FASA PdP", f_k, GOLD_L, 6)
        td.text((pad, u(52)), title, font=f_t, fill=WHITE)
        td.text((pad, u(128)), sub, font=f_s, fill=SOFT)
        m = Image.new("L", (Wc, Hc), 0); ImageDraw.Draw(m).rectangle([u(6), 0, u(6) + int(tw_ * ease_out(prog(t, 0.3, 1.1))), th], fill=255)
        img.paste(txt, (0, 0), Image.composite(txt.split()[3], Image.new("L", (Wc, Hc), 0), m))
        sp = prog(t, 1.2, 2.2)
        if 0 < sp < 1:
            img.paste(Image.new("RGBA", (Wc, Hc), (255, 255, 255, 255)), (0, 0), Image.composite(sweep((Wc, Hc), sp), Image.new("L", (Wc, Hc), 0), img.split()[3]))
        return alpha(img, 1 - ease_io(prog(t, dur - 0.6, dur)))
    return fr, int(dur * FPS), (Wc, Hc), (x0, y0)

# =====================================================================
# 3. POP-UP PENGENALAN GURU — bawah-kiri (di atas zon sari kata), 5 s
# =====================================================================
POPUP_SCALE = 0.66  # pop-up dikecilkan supaya tidak menutup skrin (maklum balas v2)

def teacher_popup(i, mins, dur=7.0):
    T = TEACHERS[i]
    f_no = F("InterDisplay-Black.otf", 150); f_lab = F("Inter-Bold.otf", 22); f_role = F("Inter-SemiBold.otf", 30); f_info = F("Inter-Medium.otf", 24)
    size = 46
    while tw(F("InterDisplay-Bold.otf", size), T["name"]) > u(900) and size > 32: size -= 1
    f_name = F("InterDisplay-Bold.otf", size)
    info = f"Minit {mins}   |   {T['phase']}"
    left = u(250); cw = int(left + u(40) + max(tw(f_name, T["name"]), tw(f_role, T["role"], 2), tw(f_info, info)) + u(60)); ch = u(270)
    c0, cmask = card(cw, ch); cd = ImageDraw.Draw(c0)
    cd.rounded_rectangle([0, 0, u(9), ch - 1], u(4), fill=GOLD + (255,)); cd.line([(left, u(40)), (left, ch - u(40))], fill=GOLD + (150,), width=max(2, u(2)))
    sh = shadow(cw, ch)
    Wc, Hc = u(70) + cw + u(60), ch + u(80); x0, y0 = 0, H - u(225) - ch - u(40)
    cx = u(70)
    def fr(t):
        img = Image.new("RGBA", (Wc, Hc)); p = ease_out(prog(t, 0.0, 0.7)); x = int(cx - (cw + cx) * (1 - p))
        c = c0.copy(); sp = prog(t, 1.6, 2.6)
        if 0 < sp < 1:
            c.paste(Image.new("RGBA", (cw, ch), (255, 255, 255, 255)), (0, 0), Image.composite(sweep((cw, ch), sp), Image.new("L", (cw, ch), 0), cmask))
        img.alpha_composite(alpha(sh, p), (max(0, x - u(40)), 0)) if x - u(40) >= 0 else None
        img.paste(alpha(c, p), (x, u(40)), alpha(c, p))
        ps = prog(t, 0.35, 1.05)
        if ps > 0:
            s = max(0.05, ease_back(ps)); nb = Image.new("RGBA", (left, ch)); nd = ImageDraw.Draw(nb)
            dtext(nd, ((left - tw(f_lab, "GURU", 6)) / 2, u(40)), "GURU", f_lab, GOLD_L, 6)
            bb = nd.textbbox((0, 0), T["no"], font=f_no); nd.text(((left - (bb[2] - bb[0])) / 2 - bb[0] + u(6), u(80) - bb[1]), T["no"], font=f_no, fill=GOLD)
            nw, nh = max(1, int(left * s)), max(1, int(ch * s)); nbs = nb.resize((nw, nh), Image.LANCZOS)
            img.alpha_composite(alpha(nbs, min(1, ps * 2)), (max(0, int(x + (left - nw) / 2)), int(u(40) + (ch - nh) / 2)))
        tx = x + left + u(40); ty = u(40)
        layers = [(0.55, 1.1, lambda td, k: dtext(td, (tx, ty + u(34)), "GURU SEDANG MENGAJAR", f_lab, GREEN + (255,), 4), "out"),
                  (0.75, 1.45, lambda td, k: td.text((tx, ty + u(72)), T["name"], font=f_name, fill=WHITE), "io"),
                  (1.05, 1.75, lambda td, k: dtext(td, (tx, ty + u(138) + int(u(22) * (1 - k))), T["role"], f_role, GOLD, 2), "out"),
                  (1.35, 2.0, lambda td, k: (td.line([(tx, ty + u(192)), (tx + u(60) * k, ty + u(192))], fill=GOLD + (255,), width=u(3)),
                                             td.text((tx, ty + u(206)), info, font=f_info, fill=(235, 242, 236))), "out")]
        for a0, a1, draw, e in layers:
            k = (ease_out if e == "out" else ease_io)(prog(t, a0, a1))
            if k > 0:
                tl = Image.new("RGBA", (Wc, Hc)); draw(ImageDraw.Draw(tl), k); img.alpha_composite(alpha(tl, k))
        return alpha(img, 1 - ease_io(prog(t, dur - 0.7, dur)))
    K = POPUP_SCALE; Ws, Hs = int(Wc * K) // 2 * 2, int(Hc * K) // 2 * 2
    def frs(t): return fr(t).resize((Ws, Hs), Image.LANCZOS)
    return frs, int(dur * FPS), (Ws, Hs), (x0, y0 + Hc - Hs)

# =====================================================================
# 4. PANEL LANGKAH AKTIVITI — kanan, langkah muncul satu demi satu
# =====================================================================
def steps_panel(key, step_gap=1.6, hold=6.0):
    title, steps = STEPS[key]
    f_k = F("Inter-Bold.otf", 20); f_t = F("InterDisplay-Bold.otf", 34); f_s = F("Inter-SemiBold.otf", 27); f_n = F("InterDisplay-Black.otf", 26)
    pw = u(700); pad = u(36); row = u(74)
    ph = u(150) + row * len(steps) + u(30)
    dur = 1.0 + step_gap * len(steps) + hold
    c0, cmask = card(pw, ph, fill=FOREST + (230,)); cd = ImageDraw.Draw(c0)
    cd.rounded_rectangle([0, 0, pw - 1, u(8)], u(4), fill=GOLD + (255,))
    dtext(cd, (pad, u(30)), "LANGKAH AKTIVITI", f_k, GOLD_L, 5)
    cd.text((pad, u(62)), title, font=f_t, fill=WHITE)
    cd.line([(pad, u(122)), (pw - pad, u(122))], fill=GOLD + (120,), width=max(2, u(2)))
    Wc, Hc = pw + u(140), ph + u(80); x0, y0 = W - Wc, u(150)
    def fr(t):
        img = Image.new("RGBA", (Wc, Hc)); p = ease_out(prog(t, 0, 0.7)); x = int(u(60) + (pw + u(80)) * (1 - p))
        c = c0.copy(); d = ImageDraw.Draw(c)
        for i, s in enumerate(steps):
            k = ease_out(prog(t, 0.9 + i * step_gap, 0.9 + i * step_gap + 0.6))
            if k <= 0: continue
            y = u(150) + i * row; cxn = pad + u(24)
            r = int(u(22) * ease_back(k));
            d.ellipse([cxn - r, y + u(22) - r, cxn + r, y + u(22) + r], fill=GOLD + (255,))
            nb = d.textbbox((0, 0), str(i + 1), font=f_n)
            if k > 0.6: d.text((cxn - (nb[2] - nb[0]) / 2 - nb[0], y + u(22) - (nb[3] - nb[1]) / 2 - nb[1]), str(i + 1), font=f_n, fill=FOREST2)
            tl = Image.new("RGBA", (pw, ph)); ImageDraw.Draw(tl).text((pad + u(64) + int(u(20) * (1 - k)), y + u(6)), s, font=f_s, fill=WHITE)
            c.alpha_composite(alpha(tl, k))
            # langkah semasa diserlahkan
            cur = 0.9 + i * step_gap <= t < 0.9 + (i + 1) * step_gap and i < len(steps)
            if cur:
                d.rounded_rectangle([pad - u(8), y - u(6), pw - pad + u(8), y + u(52)], u(10), outline=GOLD_L + (180,), width=max(2, u(2)))
        img.alpha_composite(alpha(c, p), (min(x, Wc - 1), u(40)))
        return alpha(img, 1 - ease_io(prog(t, dur - 0.7, dur)))
    K = POPUP_SCALE; Ws, Hs = int(Wc * K) // 2 * 2, int(Hc * K) // 2 * 2
    def frs(t): return fr(t).resize((Ws, Hs), Image.LANCZOS)
    return frs, int(dur * FPS), (Ws, Hs), (x0, y0 + Hc - Hs)

# =====================================================================
# 5. PANEL AYAT MURID (AKTIF → PASIF) — tengah atas
# =====================================================================
def _rich(d, x, y, segs, f_n, f_b, col_n, col_b, maxw):
    """Lukis segmen teks (biasa / penting) dengan pembalutan baris. Pulang tinggi."""
    words = []
    for txt, key in segs:
        for j, wd in enumerate(txt.split(" ")):
            if wd == "" and j > 0: continue
            words.append((wd, key, j < len(txt.split(" ")) - 1))
    lh = int(f_n.size * 1.35); cx, cy = x, y
    for wd, key, sp in words:
        f = f_b if key else f_n; ww = f.getlength(wd)
        if cx + ww > x + maxw and cx > x: cx = x; cy += lh
        d.text((cx, cy), wd, font=f, fill=col_b if key else col_n)
        cx += ww + (f_n.getlength(" ") if sp else 0)
    return cy + lh - y
def sentence_panel(key, per=6.5):
    title, items = SENTENCES[key]
    f_k = F("Inter-Bold.otf", 21); f_tag = F("Inter-SemiBold.otf", 25); f_chip = F("Inter-Bold.otf", 22)
    f_n = F("Inter-Medium.otf", 38); f_b = F("Inter-ExtraBold.otf", 38)
    pw = u(1480); pad = u(44); ph = u(285) if any(it[3] is not None for it in items) else u(200)
    dur = 0.8 + per * len(items) + 0.6
    Wc, Hc = pw + u(80), ph + u(80); x0, y0 = (W - Wc) // 2, u(110)
    base, bmask = card(pw, ph, fill=FOREST + (236,)); bd = ImageDraw.Draw(base)
    bd.rounded_rectangle([0, 0, pw - 1, u(8)], u(4), fill=GOLD + (255,))
    dtext(bd, (pad, u(30)), title, f_k, GOLD_L, 5)
    def chip(d, x, y, label, col):
        w = int(f_chip.getlength(label) + u(28)); d.rounded_rectangle([x, y, x + w, y + u(40)], u(20), fill=col + (255,))
        d.text((x + u(14), y + u(7)), label, font=f_chip, fill=FOREST2); return w
    def fr(t):
        img = Image.new("RGBA", (Wc, Hc)); p = ease_out(prog(t, 0, 0.6))
        c = base.copy()
        i = min(len(items) - 1, int(max(0, t - 0.6) // per)); ti = t - 0.6 - i * per
        tag, kind, s1, s2 = items[i]
        a_in = ease_out(prog(ti, 0.0, 0.6)) if i > 0 or t > 0.6 else ease_out(prog(t, 0.3, 0.9))
        a_out = 1 - ease_io(prog(ti, per - 0.5, per)) if i < len(items) - 1 else 1.0
        k = min(a_in, a_out)
        tl = Image.new("RGBA", (pw, ph)); d = ImageDraw.Draw(tl)
        d.text((pad, u(74)), tag, font=f_tag, fill=SOFT)
        if len(items) > 1: d.text((pw - pad - f_tag.getlength(f"{i + 1}/{len(items)}"), u(74)), f"{i + 1}/{len(items)}", font=f_tag, fill=GOLD_L)
        y = u(130)
        cw = chip(d, pad, y + u(6), "AYAT " + kind if s2 is not None else "AYAT " + kind, GOLD if kind == "AKTIF" else GREEN_L)
        h1 = _rich(d, pad + cw + u(20), y, s1, f_n, f_b, WHITE, GOLD if kind == "AKTIF" else GREEN_L, pw - 2 * pad - cw - u(20))
        y += max(h1, u(56)) + u(18)
        k2 = ease_out(prog(ti, 1.6, 2.3))
        if s2 is not None and k2 > 0:
            d2 = Image.new("RGBA", (pw, ph)); dd = ImageDraw.Draw(dd_img := d2)
            dd.text((pad + u(8), y - u(6)), "↓", font=F("Inter-Bold.otf", 40), fill=GOLD_L)
            y2 = y + u(50)
            cw2 = chip(dd, pad, y2 + u(6), "AYAT PASIF", GREEN_L)
            _rich(dd, pad + cw2 + u(20), y2, s2, f_n, f_b, WHITE, GREEN_L, pw - 2 * pad - cw2 - u(20))
            tl.alpha_composite(alpha(d2, k2))
        elif s2 is None:
            d.text((pad, y + u(10)), tag if False else "", font=f_tag, fill=SOFT)
        c.alpha_composite(alpha(tl, k))
        img.alpha_composite(alpha(c, p), (u(40), u(30) + int(u(30) * (1 - p))))
        return alpha(img, 1 - ease_io(prog(t, dur - 0.6, dur)))
    return fr, int(dur * FPS), (Wc, Hc), (x0, y0)

# =====================================================================
# 6. PENUTUP: kad penghargaan & tajuk akhir — skrin penuh
# =====================================================================
def closing_card(lines, dur):
    def fr(t):
        img = Image.new("RGBA", (W, H)); bg = ease_io(prog(t, 0, 0.8))
        img.alpha_composite(Image.new("RGBA", (W, H), FOREST2 + (int(185 * bg),)))
        total = sum(int(u(s) * 1.35) for _, s, _, _ in lines); y = (H - total) / 2
        for i, (txt, s, col, fn) in enumerate(lines):
            f = F(fn, s); p = ease_out(prog(t, 0.5 + 0.3 * i, 1.3 + 0.3 * i))
            if txt and p > 0:
                tr = 6 if fn.startswith("Inter-Bold") and s < 30 else 0
                tl = Image.new("RGBA", (W, H)); dtext(ImageDraw.Draw(tl), ((W - tw(f, txt, tr)) / 2, y + u(18) * (1 - p)), txt, f, col, tr)
                img.alpha_composite(alpha(tl, p))
            y += int(u(s) * 1.35)
        return alpha(img, 1 - ease_io(prog(t, dur - 0.8, dur)))
    return fr, int(dur * FPS), (W, H), (0, 0)
def end_title(dur):
    f1 = F("InterDisplay-Black.otf", 96); f2 = F("InterDisplay-Bold.otf", 48); f3 = F("InterDisplay-Bold.otf", 58); fk = F("Inter-Bold.otf", 24)
    def fr(t):
        img = Image.new("RGBA", (W, H)); img.alpha_composite(Image.new("RGBA", (W, H), FOREST2 + (int(205 * ease_io(prog(t, 0, 1.0))),)))
        cy = H // 2 - u(110)
        p1 = ease_io(prog(t, 0.5, 1.6)); tl = Image.new("RGBA", (W, H)); td = ImageDraw.Draw(tl)
        K = "SIMULASI PENGAJARAN MIKRO (MICRO TEACHING)"; dtext(td, ((W - tw(fk, K, 6)) / 2, cy - u(150)), K, fk, GOLD_L, 6)
        L1 = "MISI PENGAWAL BAHASA"; w1 = tw(f1, L1); td.text(((W - w1) / 2, cy - u(100)), L1, font=f1, fill=WHITE)
        L2 = "HOTEL HIJAU"; dtext(td, ((W - tw(f2, L2, 16)) / 2, cy + u(25)), L2, f2, GOLD, 16)
        m = Image.new("L", (W, H), 0); hw = (w1 / 2 + u(30)) * p1; ImageDraw.Draw(m).rectangle([W / 2 - hw, 0, W / 2 + hw, H], fill=255)
        img.paste(tl, (0, 0), Image.composite(tl.split()[3], Image.new("L", (W, H), 0), m)); d = ImageDraw.Draw(img)
        pg = ease_out(prog(t, 1.6, 2.4)); lw = u(600) * pg
        if pg > 0: d.rectangle([W / 2 - lw / 2, cy + u(115), W / 2 + lw / 2, cy + u(119)], fill=GOLD + (255,))
        ps = ease_out(prog(t, 2.2, 3.2))
        if ps > 0:
            sl = "JAGA ALAM, JAGA BAHASA"; tl = Image.new("RGBA", (W, H))
            dtext(ImageDraw.Draw(tl), ((W - tw(f3, sl, 6)) / 2, cy + u(155) + u(20) * (1 - ps)), sl, f3, GREEN_L, 6)
            img.alpha_composite(alpha(tl, ps))
            sp = prog(t, 3.4, 4.6)
            if 0 < sp < 1: img.paste(Image.new("RGBA", (W, H), (255, 255, 255, 255)), (0, 0), Image.composite(sweep((W, H), sp, 220), Image.new("L", (W, H), 0), tl.split()[3]))
        fo = ease_io(prog(t, dur - 2.5, dur))
        if fo > 0: img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * fo))))
        return img
    return fr, int(dur * FPS), (W, H), (0, 0)

def jobs(cfg):
    J = {"title_open": title_open(cfg.get("title_dur", 9.0))}
    for k in PHASES: J["phase_" + k] = phase_card(k)
    for i in range(3): J[f"popup_guru{i + 1}"] = teacher_popup(i, cfg["teacher_mins"][i])
    for k in STEPS: J[k] = steps_panel(k)
    for k in SENTENCES: J[k] = sentence_panel(k)
    J["credits_1"] = closing_card([
        ("SETINGGI-TINGGI PENGHARGAAN", 26, GOLD_L, "Inter-Bold.otf"), ("", 20, WHITE, "Inter-Regular.otf"),
        ("DR. RASIDAYANTY BINTI SAION", 64, WHITE, "InterDisplay-Bold.otf"), ("Pensyarah Kursus Pedagogi", 36, GOLD, "Inter-SemiBold.otf"),
        ("", 30, WHITE, "Inter-Regular.otf"), ("atas bimbingan, tunjuk ajar dan dorongan yang diberikan", 30, SOFT, "Inter-Regular.otf")], 10.0)
    J["credits_2"] = closing_card([
        ("TERIMA KASIH KEPADA", 26, GOLD_L, "Inter-Bold.otf"), ("", 20, WHITE, "Inter-Regular.otf"),
        ("KELUARGA BMONETHO", 72, WHITE, "InterDisplay-Black.otf"), ("", 24, WHITE, "Inter-Regular.otf"),
        ("atas sokongan, kerjasama dan semangat kekeluargaan", 30, SOFT, "Inter-Regular.otf")], 9.0)
    J["credits_3"] = closing_card([
        ("DIBAWAKAN OLEH", 26, GOLD_L, "Inter-Bold.otf"), ("", 16, WHITE, "Inter-Regular.otf"),
        ("MOHAMAD ALIFF BIN AHMAD SHAHABUDDIN", 42, WHITE, "InterDisplay-Bold.otf"), ("Pengurus Hotel Hijau", 28, GOLD, "Inter-SemiBold.otf"),
        ("", 14, WHITE, "Inter-Regular.otf"),
        ("MUHAMMAD IMAN IRFAN BIN MOHD RAMZI", 42, WHITE, "InterDisplay-Bold.otf"), ("Ketua Pemantau Zon", 28, GOLD, "Inter-SemiBold.otf"),
        ("", 14, WHITE, "Inter-Regular.otf"),
        ("AMIN NAJMI BIN MOHYIDIN", 42, WHITE, "InterDisplay-Bold.otf"), ("Ketua Pengawal Bahasa", 28, GOLD, "Inter-SemiBold.otf")], 10.0)
    J["end_title"] = end_title(cfg.get("end_dur", 14.0))
    return J

if __name__ == "__main__":
    out = sys.argv[1]; cfg = json.load(open(sys.argv[2])); only = sys.argv[3:]
    os.makedirs(out, exist_ok=True)
    mpath = os.path.join(out, "manifest.json")
    if os.path.exists(mpath): MANIFEST.update(json.load(open(mpath)))
    J = jobs(cfg)
    for name, (fn, n, size, pos) in J.items():
        if only and name not in only: continue
        print("render", name, n, "frames", size, flush=True)
        save_seq(name, fn, n, size, pos, out)
        json.dump(MANIFEST, open(mpath, "w"), indent=1)
