"""Penjana motion graphics (PNG sequence RGBA 1920x1080 @30fps) untuk projek
MISI PENGAWAL BAHASA: HOTEL HIJAU.

Semua grafik dijana secara prosedur dengan Pillow, kemudian dikodkan ke
.mov (qtrle, ber-alpha) dalam 05_GRAPHICS/ supaya boleh di-overlay oleh FFmpeg.

Usage: python3 graphics.py <out_dir>
"""
import math, os, subprocess, sys, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 30
FONT_DIR = "/usr/share/fonts/opentype/inter/"
def F(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)

# ---- Palet ----
FOREST = (11, 59, 44)        # dark forest green
FOREST2 = (6, 38, 28)
GREEN = (110, 176, 98)       # natural green
GOLD = (212, 175, 55)
GOLD_L = (240, 214, 130)
WHITE = (255, 255, 255)

# ---- Data guru (ejaan TEPAT seperti diberi) ----
TEACHERS = [
    dict(no="01", name="MOHAMAD ALIFF BIN AHMAD SHAHABUDDIN", role="PENGURUS HOTEL HIJAU",
         mins="Minit 00:00 – 10:00", act="Set Induksi & Misi 1"),
    dict(no="02", name="MUHAMMAD IMAN IRFAN BIN MOHD RAMZI", role="KETUA PEMANTAU ZON",
         mins="Minit 10:00 – 20:00", act="Misi 2 & Aktiviti AR"),
    dict(no="03", name="AMIN NAJMI BIN MOHYIDIN", role="KETUA PENGAWAL BAHASA",
         mins="Minit 20:00 – 30:00", act="Semakan, Pembetulan & Tiket Refleksi"),
]

# ---- Easing ----
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, t0, t1): return clamp((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t0)
def ease_out(x): return 1 - (1 - x) ** 3
def ease_in_out(x): return 3 * x * x - 2 * x * x * x
def ease_back(x, s=1.4):
    x -= 1; return x * x * ((s + 1) * x + s) + 1

def text_w(font, s, tracking=0):
    return font.getlength(s) + tracking * max(0, len(s) - 1)

def draw_tracked(d, xy, s, font, fill, tracking=0):
    x, y = xy
    if tracking == 0:
        d.text((x, y), s, font=font, fill=fill); return
    for ch in s:
        d.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking

def layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))

def with_alpha(img, a):
    if a >= 0.999: return img
    r, g, b, al = img.split()
    al = al.point(lambda v: int(v * a))
    return Image.merge("RGBA", (r, g, b, al))

def light_sweep(size, p, angle_w=160):
    """Jalur cahaya lembut (subtle light sweep) melintasi kawasan size, p 0..1."""
    w, h = size
    m = Image.new("L", size, 0); d = ImageDraw.Draw(m)
    cx = -angle_w * 2 + p * (w + angle_w * 4)
    for i in range(angle_w):
        a = int(70 * math.sin(math.pi * i / angle_w) ** 2)
        x = cx + i
        d.line([(x, 0), (x - h * 0.35, h)], fill=a, width=2)
    return m

def save_seq(frames_fn, n, out_mov, tmp):
    if os.path.exists(tmp): shutil.rmtree(tmp)
    os.makedirs(tmp)
    for i in range(n):
        frames_fn(i / FPS).save(f"{tmp}/{i:04d}.png", compress_level=1)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{tmp}/%04d.png",
                    "-c:v", "qtrle", "-pix_fmt", "argb", out_mov], check=True)
    # simpan satu frame rujukan (PNG) untuk semakan
    mid = min(n - 1, int(n * 0.55))
    shutil.copy(f"{tmp}/{mid:04d}.png", out_mov.replace(".mov", "_still.png"))
    shutil.rmtree(tmp)

# =====================================================================
# 1. POP-UP PENGENALAN GURU (5 saat)
# =====================================================================
def teacher_popup(t_info, dur=5.0):
    f_no = F("InterDisplay-Black.otf", 150)
    f_lab = F("Inter-Bold.otf", 22)
    f_role = F("Inter-SemiBold.otf", 30)
    f_info = F("Inter-Medium.otf", 24)
    # Auto-fit nama
    size = 46
    while True:
        f_name = F("InterDisplay-Bold.otf", size)
        if text_w(f_name, t_info["name"]) <= 900 or size <= 32: break
        size -= 1
    left_w = 250
    content_w = max(text_w(f_name, t_info["name"]), text_w(f_role, t_info["role"], 2),
                    text_w(f_info, t_info["mins"] + "   |   " + t_info["act"]))
    cw, ch = int(left_w + 40 + content_w + 60), 270
    cx0, cy0 = 70, H - 70 - ch           # bawah-kiri (tidak menutup muka guru)

    def frame(t):
        img = layer()
        out_a = 1 - ease_in_out(prog(t, dur - 0.7, dur))
        # --- kad (slide-in) ---
        p = ease_out(prog(t, 0.0, 0.7))
        x = int(cx0 - (cw + 120) * (1 - p))
        card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
        cd.rounded_rectangle([0, 0, cw - 1, ch - 1], 18, fill=FOREST + (235,))
        # gradien halus ke kanan
        grad = Image.new("L", (cw, ch)); gd = ImageDraw.Draw(grad)
        for gx in range(cw): gd.line([(gx, 0), (gx, ch)], fill=int(60 * gx / cw))
        dark = Image.new("RGBA", (cw, ch), FOREST2 + (255,))
        mask = Image.new("L", (cw, ch), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw - 1, ch - 1], 18, fill=255)
        card.paste(dark, (0, 0), Image.composite(grad, Image.new("L", (cw, ch), 0), mask))
        cd = ImageDraw.Draw(card)
        cd.rounded_rectangle([0, 0, 9, ch - 1], 4, fill=GOLD + (255,))           # bar emas
        cd.line([(left_w, 40), (left_w, ch - 40)], fill=GOLD + (150,), width=2)    # pemisah
        cd.rounded_rectangle([1, 1, cw - 2, ch - 2], 18, outline=GOLD + (90,), width=2)
        # light sweep
        sp = prog(t, 1.6, 2.6)
        if 0 < sp < 1:
            sw = light_sweep((cw, ch), sp)
            sw = Image.composite(sw, Image.new("L", (cw, ch), 0), mask)
            card.paste(Image.new("RGBA", (cw, ch), (255, 255, 255, 255)), (0, 0), sw)
        # shadow
        sh = Image.new("RGBA", (cw + 80, ch + 80), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([40, 50, cw + 40, ch + 40], 22, fill=(0, 0, 0, 120))
        sh = sh.filter(ImageFilter.GaussianBlur(18))
        img.alpha_composite(with_alpha(sh, p), (x - 40, cy0 - 40))
        img.alpha_composite(with_alpha(card, p), (x, cy0))
        d = ImageDraw.Draw(img)
        # --- nombor guru (scale-up) ---
        ps = prog(t, 0.35, 1.05)
        if ps > 0:
            s = max(0.05, ease_back(ps))
            nb = Image.new("RGBA", (left_w, ch), (0, 0, 0, 0)); nd = ImageDraw.Draw(nb)
            lab = "GURU"
            nd.text(((left_w - text_w(f_lab, lab, 6)) / 2, 38), "", font=f_lab)
            draw_tracked(nd, ((left_w - text_w(f_lab, lab, 6)) / 2 + 6, 40), lab, f_lab, GOLD_L, 6)
            bb = nd.textbbox((0, 0), t_info["no"], font=f_no)
            nd.text(((left_w - (bb[2] - bb[0])) / 2 - bb[0] + 6, 70 - bb[1] + 10), t_info["no"], font=f_no, fill=GOLD)
            nw, nh = int(left_w * s), int(ch * s)
            nbs = nb.resize((max(1, nw), max(1, nh)), Image.LANCZOS)
            img.alpha_composite(with_alpha(nbs, min(1, ps * 2)),
                                (int(x + (left_w - nw) / 2), int(cy0 + (ch - nh) / 2)))
        tx = x + left_w + 40
        # label kecil
        pl = ease_out(prog(t, 0.55, 1.1))
        if pl > 0:
            tl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            draw_tracked(ImageDraw.Draw(tl), (tx, cy0 + 34), "GURU SEDANG MENGAJAR", f_lab, GREEN + (255,), 4)
            img.alpha_composite(with_alpha(tl, pl))
        # nama (fade-in)
        pn = ease_in_out(prog(t, 0.75, 1.45))
        if pn > 0:
            tl = layer(); ImageDraw.Draw(tl).text((tx, cy0 + 72), t_info["name"], font=f_name, fill=WHITE)
            img.alpha_composite(with_alpha(tl, pn))
        # jawatan (fade-up)
        pr = ease_out(prog(t, 1.05, 1.75))
        if pr > 0:
            tl = layer(); draw_tracked(ImageDraw.Draw(tl), (tx, cy0 + 138 + int(22 * (1 - pr))), t_info["role"], f_role, GOLD, 2)
            img.alpha_composite(with_alpha(tl, pr))
        # minit + aktiviti
        pi = ease_out(prog(t, 1.35, 2.0))
        if pi > 0:
            tl = layer(); td = ImageDraw.Draw(tl)
            td.line([(tx, cy0 + 192), (tx + 60 * pi, cy0 + 192)], fill=GOLD + (255,), width=3)
            td.text((tx, cy0 + 206), t_info["mins"] + "   |   " + t_info["act"], font=f_info, fill=(235, 242, 236))
            img.alpha_composite(with_alpha(tl, pi))
        return with_alpha(img, out_a)
    return frame, int(dur * FPS)

# =====================================================================
# 2. TAJUK BABAK (chapter title, 4 saat) — atas-kiri
# =====================================================================
def chapter_title(num, title, sub, dur=4.0):
    f_num = F("Inter-Bold.otf", 22); f_t = F("InterDisplay-Bold.otf", 50); f_s = F("Inter-Medium.otf", 26)
    x0, y0 = 90, 80
    tw = max(text_w(f_t, title), text_w(f_s, sub)) + 40
    def frame(t):
        img = layer(); d = ImageDraw.Draw(img)
        out_a = 1 - ease_in_out(prog(t, dur - 0.6, dur))
        # garis emas tumbuh (mask reveal)
        pl = ease_out(prog(t, 0.0, 0.6))
        d.rectangle([x0, y0, x0 + 4, y0 + int(150 * pl)], fill=GOLD + (255,))
        # panel lut sinar
        pp = ease_out(prog(t, 0.15, 0.85))
        if pp > 0:
            pw = int((tw + 30) * pp)
            pnl = layer(); ImageDraw.Draw(pnl).rectangle([x0 + 4, y0, x0 + 4 + pw, y0 + 150], fill=FOREST + (200,))
            img.alpha_composite(pnl); d = ImageDraw.Draw(img)
            d.rectangle([x0, y0, x0 + 4, y0 + int(150 * pl)], fill=GOLD + (255,))
        # teks dengan mask reveal (dipotong oleh lebar panel)
        txt = layer(); td = ImageDraw.Draw(txt)
        draw_tracked(td, (x0 + 30, y0 + 20), f"BABAK {num}", f_num, GOLD + (255,), 5)
        td.text((x0 + 30, y0 + 52), title, font=f_t, fill=WHITE)
        td.text((x0 + 30, y0 + 110), sub, font=f_s, fill=(215, 232, 214))
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).rectangle([x0 + 4, y0, x0 + 4 + int((tw + 30) * ease_out(prog(t, 0.3, 1.1))), y0 + 150], fill=255)
        img.paste(txt, (0, 0), Image.composite(txt.split()[3], Image.new("L", (W, H), 0), m))
        return with_alpha(img, out_a)
    return frame, int(dur * FPS)

# =====================================================================
# 3. TAJUK PEMBUKAAN (10 saat) — tengah skrin
# =====================================================================
def _vignette():
    import numpy as np
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 1.414
    a = (0.45 + 0.5 * np.clip(r, 0, 1) ** 1.6) * 255
    al = Image.fromarray(a.astype("uint8"), "L")
    v = Image.new("RGBA", (W, H), FOREST2 + (255,)); v.putalpha(al); return v
VIGNETTE = _vignette()

def opening_title(dur=10.0):
    f_k = F("Inter-SemiBold.otf", 28); f_t1 = F("InterDisplay-Black.otf", 120)
    f_t2 = F("InterDisplay-Bold.otf", 64); f_s = F("Inter-Medium.otf", 34); f_s2 = F("Inter-Regular.otf", 28)
    L1, L2 = "MISI PENGAWAL BAHASA", "HOTEL HIJAU"
    S1 = "Bahasa Melayu Tahun 5"
    S2 = "Ayat Aktif dan Ayat Pasif  •  SP 5.3.3"
    K = "DOKUMENTASI PdP"
    def frame(t):
        img = layer()
        out_a = 1 - ease_in_out(prog(t, dur - 1.0, dur))
        cy = H // 2 - 40
        # gelapkan latar + vignette radial hijau gelap
        va = ease_in_out(prog(t, 0, 1.2))
        img.alpha_composite(with_alpha(VIGNETTE, va))
        d = ImageDraw.Draw(img)
        # kicker
        pk = ease_out(prog(t, 0.4, 1.2))
        if pk > 0:
            tl = layer(); kw = text_w(f_k, K, 10)
            draw_tracked(ImageDraw.Draw(tl), ((W - kw) / 2, cy - 170 + 15 * (1 - pk)), K, f_k, GOLD_L, 10)
            img.alpha_composite(with_alpha(tl, pk))
        # tajuk utama: mask reveal dari tengah
        pr = ease_in_out(prog(t, 0.9, 2.2))
        if pr > 0:
            tl = layer(); td = ImageDraw.Draw(tl)
            w1 = text_w(f_t1, L1); td.text(((W - w1) / 2, cy - 130), L1, font=f_t1, fill=WHITE)
            m = Image.new("L", (W, H), 0); half = (w1 / 2 + 20) * pr
            ImageDraw.Draw(m).rectangle([W / 2 - half, 0, W / 2 + half, H], fill=255)
            img.paste(tl, (0, 0), Image.composite(tl.split()[3], Image.new("L", (W, H), 0), m))
            # light sweep atas tajuk
            sp = prog(t, 2.4, 3.6)
            if 0 < sp < 1:
                sw = light_sweep((W, H), sp, 220)
                glow = Image.composite(sw, Image.new("L", (W, H), 0), tl.split()[3])
                img.paste(Image.new("RGBA", (W, H), GOLD_L + (255,)), (0, 0), glow)
        # garis emas
        pg = ease_out(prog(t, 1.8, 2.8))
        if pg > 0:
            d = ImageDraw.Draw(img); lw = 520 * pg
            d.rectangle([W / 2 - lw / 2, cy + 20, W / 2 + lw / 2, cy + 24], fill=GOLD + (255,))
        # HOTEL HIJAU
        ph = ease_out(prog(t, 2.2, 3.1))
        if ph > 0:
            tl = layer(); w2 = text_w(f_t2, L2, 18)
            draw_tracked(ImageDraw.Draw(tl), ((W - w2) / 2, cy + 48 + 25 * (1 - ph)), L2, f_t2, GOLD, 18)
            img.alpha_composite(with_alpha(tl, ph))
        # subjudul
        ps = ease_out(prog(t, 3.0, 3.9))
        if ps > 0:
            tl = layer(); td = ImageDraw.Draw(tl)
            ws = text_w(f_s, S1); td.text(((W - ws) / 2, cy + 160 + 20 * (1 - ps)), S1, font=f_s, fill=WHITE)
            ws2 = text_w(f_s2, S2); td.text(((W - ws2) / 2, cy + 210 + 20 * (1 - ps)), S2, font=f_s2, fill=(205, 228, 200))
            img.alpha_composite(with_alpha(tl, ps))
        return with_alpha(img, out_a)
    return frame, int(dur * FPS)

# =====================================================================
# 4. LOWER THIRD ringkas (contoh: label aktiviti / rakaman) 4 saat — bawah-kanan
# =====================================================================
def lower_third(title, sub, dur=4.0):
    f_t = F("Inter-Bold.otf", 34); f_s = F("Inter-Medium.otf", 24)
    tw = int(max(text_w(f_t, title), text_w(f_s, sub)) + 70)
    x1 = W - 80; y0 = H - 80 - 110
    def frame(t):
        img = layer(); out_a = 1 - ease_in_out(prog(t, dur - 0.5, dur))
        p = ease_out(prog(t, 0, 0.6))
        x0 = x1 - int(tw * p)
        d = ImageDraw.Draw(img)
        d.rectangle([x0, y0, x1, y0 + 110], fill=FOREST + (225,))
        d.rectangle([x1 - 6, y0, x1, y0 + 110], fill=GOLD + (255,))
        pt = ease_in_out(prog(t, 0.4, 1.0))
        tl = layer(); td = ImageDraw.Draw(tl)
        td.text((x1 - tw + 30, y0 + 16), title, font=f_t, fill=WHITE)
        td.text((x1 - tw + 30, y0 + 64), sub, font=f_s, fill=GOLD_L)
        img.alpha_composite(with_alpha(tl, pt))
        return with_alpha(img, out_a)
    return frame, int(dur * FPS)

# =====================================================================
# 5. PENUTUP: penghargaan & slogan (kad statik dianimasi)
# =====================================================================
def closing_card(lines, dur, kicker=None):
    """lines: senarai (teks, saiz, warna, font) dipaparkan di tengah, muncul berperingkat."""
    def frame(t):
        img = layer()
        bg = ease_in_out(prog(t, 0, 0.8))
        img.alpha_composite(Image.new("RGBA", (W, H), FOREST2 + (int(175 * bg),)))
        out_a = 1 - ease_in_out(prog(t, dur - 0.8, dur))
        total_h = sum(int(s * 1.35) for _, s, _, _ in lines)
        y = (H - total_h) / 2
        for i, (txt, s, col, fn) in enumerate(lines):
            f = F(fn, s); p = ease_out(prog(t, 0.5 + 0.35 * i, 1.3 + 0.35 * i))
            if txt and p > 0:
                tl = layer(); tr = 6 if fn.startswith("Inter-Bold") and s < 30 else 0
                w = text_w(f, txt, tr)
                draw_tracked(ImageDraw.Draw(tl), ((W - w) / 2, y + 18 * (1 - p)), txt, f, col, tr)
                img.alpha_composite(with_alpha(tl, p))
            y += int(s * 1.35)
        return with_alpha(img, out_a)
    return frame, int(dur * FPS)

def end_title(dur=9.0):
    f_t1 = F("InterDisplay-Black.otf", 104); f_t2 = F("InterDisplay-Bold.otf", 54); f_sl = F("InterDisplay-Bold.otf", 60)
    def frame(t):
        img = layer()
        bg = ease_in_out(prog(t, 0, 1.0))
        img.alpha_composite(Image.new("RGBA", (W, H), FOREST2 + (int(200 * bg),)))
        cy = H // 2 - 100
        p1 = ease_in_out(prog(t, 0.5, 1.6))
        tl = layer(); td = ImageDraw.Draw(tl)
        L1 = "MISI PENGAWAL BAHASA"; w1 = text_w(f_t1, L1)
        td.text(((W - w1) / 2, cy - 90), L1, font=f_t1, fill=WHITE)
        L2 = "HOTEL HIJAU"; w2 = text_w(f_t2, L2, 16)
        draw_tracked(td, ((W - w2) / 2, cy + 40), L2, f_t2, GOLD, 16)
        m = Image.new("L", (W, H), 0); half = (w1 / 2 + 20) * p1
        ImageDraw.Draw(m).rectangle([W / 2 - half, 0, W / 2 + half, H], fill=255)
        img.paste(tl, (0, 0), Image.composite(tl.split()[3], Image.new("L", (W, H), 0), m))
        d = ImageDraw.Draw(img)
        pg = ease_out(prog(t, 1.6, 2.4)); lw = 600 * pg
        if pg > 0: d.rectangle([W / 2 - lw / 2, cy + 135, W / 2 + lw / 2, cy + 139], fill=GOLD + (255,))
        ps = ease_out(prog(t, 2.2, 3.2))
        if ps > 0:
            sl = "JAGA ALAM, JAGA BAHASA"; ws = text_w(f_sl, sl, 6)
            tl = layer(); draw_tracked(ImageDraw.Draw(tl), ((W - ws) / 2, cy + 175 + 20 * (1 - ps)), sl, f_sl, GREEN + (255,), 6)
            img.alpha_composite(with_alpha(tl, ps))
            sp = prog(t, 3.4, 4.6)
            if 0 < sp < 1:
                sw = light_sweep((W, H), sp, 220)
                img.paste(Image.new("RGBA", (W, H), (255, 255, 255, 255)), (0, 0), Image.composite(sw, Image.new("L", (W, H), 0), tl.split()[3]))
        # fade ke hitam pada hujung (cinematic fade-out)
        fo = ease_in_out(prog(t, dur - 2.0, dur))
        if fo > 0: img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * fo))))
        return img
    return frame, int(dur * FPS)

# =====================================================================
if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    tmp = os.path.join(out, "_tmp")
    only = sys.argv[2:]  # optional subset
    jobs = {}
    for i, t in enumerate(TEACHERS):
        jobs[f"popup_guru{i+1}"] = teacher_popup(t)
    CH = [
        ("01", "Salam & Set Induksi", "Selamat datang ke Hotel Hijau"),
        ("02", "Pembentukan Kumpulan & Misi 1", "Murid dibahagikan kepada empat kumpulan"),
        ("03", "Misi 2", "Murid bekerjasama membina ayat aktif dan ayat pasif"),
        ("04", "Aktiviti AR", "Meneroka situasi Hotel Hijau melalui Minecraft Education"),
        ("05", "Semakan & Pembetulan", "Ruang Guru: menyemak jawapan murid"),
        ("06", "Tiket Refleksi & Rumusan", "Murid menilai pembelajaran sendiri"),
    ]
    for num, ti, su in CH:
        jobs[f"chapter_{num}"] = chapter_title(num, ti, su)
    jobs["opening_title"] = opening_title()
    jobs["end_title"] = end_title(22.0)
    jobs["credits_1"] = closing_card([
        ("SETINGGI-TINGGI PENGHARGAAN", 26, GOLD_L, "Inter-Bold.otf"),
        ("", 20, WHITE, "Inter-Regular.otf"),
        ("DR. RASIDAYANTY BINTI SAION", 64, WHITE, "InterDisplay-Bold.otf"),
        ("Pensyarah Kursus Pedagogi", 36, GOLD, "Inter-SemiBold.otf"),
        ("", 30, WHITE, "Inter-Regular.otf"),
        ("atas bimbingan, tunjuk ajar dan dorongan yang diberikan", 30, (220, 234, 220), "Inter-Regular.otf"),
    ], 11.0)
    jobs["credits_2"] = closing_card([
        ("TERIMA KASIH KEPADA", 26, GOLD_L, "Inter-Bold.otf"),
        ("", 20, WHITE, "Inter-Regular.otf"),
        ("KELUARGA BMONETHO", 72, WHITE, "InterDisplay-Black.otf"),
        ("", 24, WHITE, "Inter-Regular.otf"),
        ("atas sokongan, kerjasama dan semangat kekeluargaan", 30, (220, 234, 220), "Inter-Regular.otf"),
    ], 10.0)
    jobs["credits_3"] = closing_card([
        ("DIBAWAKAN OLEH", 26, GOLD_L, "Inter-Bold.otf"),
        ("", 16, WHITE, "Inter-Regular.otf"),
        ("MOHAMAD ALIFF BIN AHMAD SHAHABUDDIN", 42, WHITE, "InterDisplay-Bold.otf"),
        ("Pengurus Hotel Hijau", 28, GOLD, "Inter-SemiBold.otf"),
        ("", 14, WHITE, "Inter-Regular.otf"),
        ("MUHAMMAD IMAN IRFAN BIN MOHD RAMZI", 42, WHITE, "InterDisplay-Bold.otf"),
        ("Ketua Pemantau Zon", 28, GOLD, "Inter-SemiBold.otf"),
        ("", 14, WHITE, "Inter-Regular.otf"),
        ("AMIN NAJMI BIN MOHYIDIN", 42, WHITE, "InterDisplay-Bold.otf"),
        ("Ketua Pengawal Bahasa", 28, GOLD, "Inter-SemiBold.otf"),
    ], 11.0)
    LT = [
        ("lt_video", "Tayangan Video Hotel Hijau", "Set induksi"),
        ("lt_papan", "Murid menulis jawapan di papan putih", "Ciri-ciri dan aktiviti Hotel Hijau"),
        ("lt_ar", "Membina ayat dalam Minecraft Education", "Aktiviti AR"),
        ("lt_galeri", "Galeri Jawapan Murid", "Semakan melalui Ruang Guru"),
        ("lt_baca", "Murid membacakan ayat aktif dan ayat pasif", "Rumusan"),
    ]
    for key, ti, su in LT:
        jobs[key] = lower_third(ti, su, 4.5)
    for name, (fn, n) in jobs.items():
        if only and name not in only: continue
        print("render", name, n, "frames", flush=True)
        save_seq(fn, n, os.path.join(out, name + ".mov"), tmp)

def progress_assets(out, segs, total_label=("GURU 01", "GURU 02", "GURU 03")):
    """Bar kemajuan babak: track.png (statik) + fill.png (digerakkan oleh FFmpeg overlay)."""
    y = H - 14; x0, x1 = 90, W - 90
    tr = layer(); d = ImageDraw.Draw(tr)
    d.rectangle([x0, y, x1, y + 4], fill=(255, 255, 255, 70))
    f = F("Inter-SemiBold.otf", 16)
    tot = sum(segs); acc = 0
    for i, sdur in enumerate(segs):
        xs = x0 + (x1 - x0) * acc / tot
        d.rectangle([xs - 1, y - 6, xs + 1, y + 4], fill=GOLD + (200,))
        draw_tracked(d, (xs + 8, y - 24), total_label[i], f, (255, 255, 255, 150), 2)
        acc += sdur
    tr.save(os.path.join(out, "progress_track.png"))
    fl = Image.new("RGBA", (x1 - x0, 4), GOLD + (230,)); fl.save(os.path.join(out, "progress_fill.png"))
    return x0, x1, y
