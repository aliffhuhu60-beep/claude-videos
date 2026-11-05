#!/usr/bin/env python3
"""SIMULASI PENGAJARAN MIKRO — MISI PENGAWAL BAHASA: HOTEL HIJAU — skrip suntingan utama v2 (FFmpeg).

Langkah:
  python3 build_video.py edl       # EDL -> 07_PROJECT_FILES/edl.csv, markers.json, gfx_config.json
  python3 build_video.py audio     # trek dialog sahaja (pantas) -> _work/dialog.wav  (untuk transkripsi)
  python3 build_video.py subs      # transkripsi (Whisper large-v3-turbo) -> 06_SUBTITLES/*.srt + *.ass
  python3 build_video.py clips     # render klip 2560x1440 (gred, nyah-hingar, penajaman CAS) -> _work/clips
  python3 build_video.py rough     # cantum klip -> 08_PREVIEW/ROUGH_CUT_*.mp4
  python3 build_video.py final     # grafik + sari kata + muzik + SFX + ducking + loudnorm -> 09_FINAL_EXPORT

Masa sumber merujuk fail asal dalam 01_RAW_VIDEO (fail asal TIDAK diubah). Panjang dikunci TEPAT 30:00.
"""
import csv, json, math, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "01_RAW_VIDEO"); GFX = os.path.join(ROOT, "05_GRAPHICS"); AUD = os.path.join(ROOT, "02_AUDIO")
WORK = os.environ.get("HH_WORK", os.path.join(HERE, "_work"))
SRC = {"v1": os.path.join(RAW, "vid sintaksis 1.MOV"), "v2": os.path.join(RAW, "vid sintaksis 2.MOV"), "v3": os.path.join(RAW, "vid3.mp4")}
FPS = 30; TOTAL = 1800.0; TOTAL_FRAMES = int(TOTAL * FPS)
OW, OH = 2560, 1440
TITLE_DUR = 8.0          # tajuk pembukaan legap (tiada preview rakaman)
CREDITS_DUR = 43.0       # kad penghargaan + tajuk akhir

# Offset penyegerakan B-roll (seg: v2_start, v2_end, v1_offset) — sync_broll.py, disemak visual
SYNC = {
    1: (4.7, 18.9, 21.20), 2: (18.9, 43.7, 63.88), 3: (43.7, 53.1, 95.58), 4: (53.1, 64.6, 117.90),
    5: (64.6, 72.4, 140.27), 7: (85.9, 90.8, 218.95), 8: (90.8, 136.0, 294.95), 9: (136.0, 152.9, 373.32),
    10: (152.9, 158.1, 419.81), 12: (169.7, 184.0, 462.31), 13: (184.0, 216.4, 489.51), 14: (216.4, 228.2, 570.89),
    17: (237.4, 245.4, 688.36), 19: (250.5, 260.0, 987.54), 20: (260.0, 267.6, 1005.41), 22: (275.2, 282.6, 1048.06),
    24: (287.5, 307.2, 1085.41), 27: (316.0, 328.7, 1147.66), 29: (341.2, 349.0, 1249.04), 30: (349.0, 357.5, 1260.20),
    35: (390.1, 400.0, 1449.94), 39: (410.2, 679.7, 1760.08), 41: (715.9, 764.9, 2205.70), 42: (764.9, 956.0, 2473.10),
    44: (971.2, 978.4, 219.46), 46: (979.2, 1011.3, 353.88), 47: (1011.3, 1026.2, 620.93), 49: (1032.6, 1042.8, 678.39),
    50: (1042.8, 1061.4, 891.54), 51: (1061.4, 1071.9, 915.86), 53: (1086.4, 1110.3, 1297.79), 54: (1110.3, 1180.7, 1323.83),
    55: (1180.7, 1195.5, 1406.95), 56: (1195.5, 1204.3, 1468.63), 59: (1287.3, 1319.8, 1871.16), 62: (1335.5, 1376.3, 2197.06),
    64: (1377.3, 1422.5, 2361.67), 66: (1437.4, 1451.2, 2537.69), 70: (1474.0, 1486.2, 2593.72),
}
# Dikecualikan: seg40 & v2 553-566 (nama penuh murid pada skrin), seg58 (nama murid), seg34 (close-up jurukamera), seg73 (logo CapCut)
V3_OFFSET = 2784.3

# Kolam cutaway (v2) — aktiviti murid/peranti tanpa wajah bercakap; digunakan apabila kamera induk terhalang
CUTAWAY = {
    "set_induksi": [(86.0, 90.6), (158.5, 169.5), (971.5, 978.2), (1026.5, 1032.4), (1012.0, 1025.8), (44.0, 52.8)],
    "langkah_1": [(228.5, 233.8), (234.2, 237.2), (282.8, 287.3), (1072.2, 1086.0), (1181.0, 1195.2), (1196.0, 1204.0),
                  (368.4, 375.2), (245.6, 250.3), (1110.6, 1150.0)],
    "langkah_2": [(452.0, 476.0), (500.0, 530.0), (570.0, 600.0), (1320.0, 1328.6), (1329.0, 1335.3), (1336.0, 1350.0)],
    "penutup": [(1437.6, 1451.0), (1451.4, 1460.4), (1460.8, 1466.5), (1466.9, 1473.8), (1486.4, 1492.2), (1492.6, 1497.8), (800.0, 840.0)],
}

# Pilihan framing kamera induk (x0, y0, lebar) dalam pecahan bingkai (nisbah 16:9 dikekalkan)
CROPS = {"wide": (0.02, 0.02, 0.96), "front": (0.15, 0.06, 0.74), "right": (0.30, 0.04, 0.70),
         "left": (0.06, 0.04, 0.70), "center": (0.20, 0.10, 0.64)}

# ------------------------------------------------------------------
# Data pengesanan orang -> penalti framing
# ------------------------------------------------------------------
_DET = None
def det():
    global _DET
    if _DET is None:
        _DET = {}
        for l in open(os.path.join(HERE, "det_v1.jsonl")):
            d = json.loads(l); _DET.setdefault(int(d["t"]), []).extend(d["b"])
    return _DET

def crop_penalty(sec, cname):
    x0, y0, w = CROPS[cname]; cx1, cy1 = x0 + w, y0 + w; area = w * w; pen = (0.96 - w) * 1.5
    for bx0, by0, bx1, by1, c in det().get(sec, []):
        h = by1 - by0; bw = bx1 - bx0
        ix = max(0, min(cx1, bx1) - max(x0, bx0)); iy = max(0, min(cy1, by1) - max(y0, by0)); inter = ix * iy / area
        if (h > 0.45 and by0 < 0.40) or bw > 0.30 or (by1 > 0.98 and h > 0.5):
            if inter > 0.003: pen += 30 * inter + 6.0         # orang dekat kamera / lalu depan kamera
        elif by0 < 0.40 and 0.18 < h <= 0.45 and c > 0.35:
            if inter > 0.003: pen += 0.9 + 3 * inter            # orang berdiri di tengah kelas (cth. jurukamera)
    return pen / 2.0  # 2 sampel sesaat

def frame_plan(p0, p1, bad_cost=2.6, switch=2.0):
    """Pilih framing terbaik setiap saat (DP). Pulang [(t0, t1, crop|None)] — None = terhalang (perlu cutaway)."""
    secs = list(range(int(math.floor(p0)), int(math.ceil(p1))))
    states = list(CROPS) + ["BAD"]
    cost = {s: 0.0 for s in states}; back = []
    for i, sec in enumerate(secs):
        pen = {c: crop_penalty(sec, c) for c in CROPS}; pen["BAD"] = bad_cost
        nc, bk = {}, {}
        for s in states:
            prev = min(states, key=lambda q: cost[q] + (switch if q != s and i > 0 else 0))
            nc[s] = cost[prev] + (switch if prev != s and i > 0 else 0) + pen[s]; bk[s] = prev
        cost = nc; back.append(bk)
    s = min(states, key=lambda q: cost[q]); path = [s]
    for bk in reversed(back[1:]): s = bk[s]; path.append(s)
    path.reverse()
    runs = []
    for sec, st in zip(secs, path):
        a, b = max(p0, sec), min(p1, sec + 1)
        if b <= a: continue
        if runs and runs[-1][2] == st: runs[-1][1] = b
        else: runs.append([a, b, st])
    # gabung larian < 1.2 s ke larian sebelumnya (elak kelipan)
    out = []
    for r in runs:
        if out and (r[1] - r[0] < 1.2): out[-1][1] = r[1]
        else: out.append(r)
    if len(out) > 1 and out[0][1] - out[0][0] < 1.2: out[1][0] = out[0][0]; out.pop(0)
    return [(a, b, None if st == "BAD" else st) for a, b, st in out]

# ------------------------------------------------------------------
# EDL
# ------------------------------------------------------------------
clips = []; markers = {}; _pool = {}
def nframes(): return sum(c["frames"] for c in clips)
def now(): return nframes() / FPS
def F(t): return int(round(t * FPS))
def add(src, start, frames, crop=None, audio="own", zoom=None, blur=False, tag="", label=""):
    if frames <= 0: return
    clips.append(dict(src=src, start=round(start, 4), frames=frames, crop=crop, audio=audio, zoom=zoom, blur=blur,
                      tag=tag, label=label, t_final=now()))
def mark(n): markers[n] = now()

def take_cutaway(tag, need):
    """Ambil cutaway daripada kolam fasa. Pulang senarai (v2_start, tempoh)."""
    pool = CUTAWAY[tag]; i, off = _pool.get(tag, (0, 0.0)); got = []
    tries = 0
    while need > 0.05 and tries < len(pool):
        a, b = pool[i % len(pool)]; avail = (b - a) - off
        if avail < 1.0: i += 1; off = 0.0; tries += 1; continue
        d = min(need, avail); got.append((a + off, d)); need -= d; off += d
        if off >= (b - a) - 1.0: i += 1; off = 0.0
    _pool[tag] = (i, off); return got

def v1_piece(p0, p1, tag):
    for a, b, cr in frame_plan(p0, p1):
        if cr is not None:
            add("v1", a, F(b) - F(a), crop=cr, tag=tag)
        else:  # kamera induk terhalang -> cutaway (audio induk diteruskan)
            t = a
            for vs, d in take_cutaway(tag, b - a):
                fr = F(t + d) - F(t)
                add("v2", vs, fr, audio=("v1", t), tag=tag, label=f"cutaway@v1:{t:.1f}"); t += d
            if b - t > 0.01:  # kolam cutaway habis -> framing terbaik
                best = min(CROPS, key=lambda c: sum(crop_penalty(x, c) for x in range(int(t), int(math.ceil(b)))))
                add("v1", t, F(b) - F(t), crop=best, tag=tag)

def span(a, b, inserts=(), tag=""):
    t = a
    for seg, x0, x1 in sorted(inserts, key=lambda z: z[1]):
        s0, s1, off = SYNC[seg]
        x0 = max(x0, off, a); x1 = min(x1, off + (s1 - s0) - 0.05, b)
        if 0 < x0 - t < 1.0: x0 = t if off <= t else t + 1.0
        if 0 < b - x1 < 1.0: x1 = b if off + (s1 - s0) - 0.05 >= b else b - 1.0
        if x1 - x0 < 1.0: continue
        if x0 > t: v1_piece(t, x0, tag)
        add("v2", s0 + (x0 - off), F(x1) - F(x0), tag=tag, label=f"seg{seg}@v1:{x0:.1f}")
        t = x1
    if b > t: v1_piece(t, b, tag)

# Rancangan kandungan (masa vid1). Fasa: Set Induksi (Guru 1) · Langkah 1 (Guru 2) · Langkah 2 + Penutup (Guru 3)
PLAN = [
    ("set_induksi", [
        (17.0, 108.0, [(1, 21.2, 35.4), (2, 63.9, 88.7), (3, 95.6, 104.9)]),
        (118.0, 245.0, [(4, 118.0, 129.4), (5, 140.3, 148.1), (44, 219.5, 226.6)]),
        (316.0, 357.0, [(8, 316.0, 340.0), (46, 345.0, 357.0)]),
        (366.0, 400.0, [(46, 366.0, 373.0), (9, 373.4, 390.0)]),
        (445.0, 520.0, [(12, 462.4, 476.5), (13, 489.6, 519.9)]),
        (520.0, 600.0, [(13, 520.0, 521.8), (14, 570.9, 582.6)]),
        (615.0, 700.0, [(47, 621.0, 635.7), (49, 678.4, 688.5), (17, 688.4, 696.3)]),
        (870.0, 911.0, [(50, 891.6, 910.0)]),
    ]),
    ("langkah_1", [
        (911.0, 1120.0, [(51, 915.9, 926.2), (19, 987.6, 996.9), (20, 1005.5, 1012.9), (22, 1048.1, 1055.5), (24, 1085.5, 1105.0)]),
        (1140.0, 1180.0, [(27, 1147.7, 1160.2)]),
        (1229.0, 1340.0, [(29, 1249.1, 1256.9), (30, 1260.3, 1268.6), (53, 1297.8, 1321.5), (54, 1323.9, 1340.0)]),
        (1400.0, 1470.0, [(55, 1407.0, 1421.5), (35, 1450.0, 1459.9), (56, 1468.7, 1470.0)]),
        (1625.0, 1706.0, []),
    ]),
    ("langkah_2", [
        (1735.0, 1830.0, [(39, 1762.0, 1830.0)]),
        (1860.0, 1910.0, [(59, 1871.2, 1903.5)]),
        (1960.0, 2025.0, [(39, 1960.0, 2025.0)]),
        (2190.0, 2260.0, [(62, 2190.0, 2205.7), (41, 2215.0, 2254.5)]),
        (2362.0, 2400.0, [(64, 2362.0, 2400.0)]),
        (2400.0, 2472.0, []),
    ]),
    ("penutup", [
        (2473.0, 2600.0, [(42, 2473.2, 2537.6), (66, 2537.8, 2551.0), (42, 2551.0, 2593.6), (70, 2593.8, 2600.0)]),
        (2716.0, 2770.0, []),
    ]),
]
FLEX = ("langkah_2", 5)  # span yang dipendekkan/dipanjangkan supaya jumlah tepat 30:00

def build_edl():
    clips.clear(); markers.clear(); _pool.clear()
    plan = json.loads(json.dumps(PLAN))
    # kira tempoh kandungan & laraskan span FLEX
    content = sum(b - a for _, sp in plan for a, b, _ in sp) + 28.6
    target = TOTAL - TITLE_DUR - CREDITS_DUR
    fp, fi = FLEX; ph = next(p for p in plan if p[0] == fp)
    ph[1][fi][1] += (target - content)
    # tajuk pembukaan legap
    add("black", 0, F(TITLE_DUR), audio="none", tag="title"); mark("title_end")
    for tag, sp in plan:
        mark(tag)
        for a, b, ins in sp: span(a, b, [tuple(x) for x in ins], tag)
        if tag == "penutup":
            mark("baca")
            add("v3", 0.0, F(TOTAL - CREDITS_DUR) - nframes(), tag="penutup", label="vid3")
    mark("credits")
    add("v1", 2836.0, TOTAL_FRAMES - nframes(), crop="wide", audio="amb", blur=True, tag="credits")
    assert nframes() == TOTAL_FRAMES, nframes()
    return clips, markers

def t_of_v1(v1t):
    for c in clips:
        d = c["frames"] / FPS
        if c["src"] == "v1" and c["audio"] == "own" and c["start"] <= v1t < c["start"] + d:
            return c["t_final"] + (v1t - c["start"])
        if c["src"] == "v2" and c["label"].startswith("seg"):
            seg = int(c["label"][3:].split("@")[0]); s0, s1, off = SYNC[seg]; v1s = off + (c["start"] - s0)
            if v1s <= v1t < v1s + d: return c["t_final"] + (v1t - v1s)
        if c["src"] == "v2" and isinstance(c["audio"], (list, tuple)):
            v1s = c["audio"][1]
            if v1s <= v1t < v1s + d: return c["t_final"] + (v1t - v1s)
    raise ValueError(v1t)

def fmt(s): return f"{int(s // 60):02d}:{int(s % 60):02d}"

def gfx_config():
    M = markers
    return {"teacher_mins": [f"{fmt(M['set_induksi'])} – {fmt(M['langkah_1'])}", f"{fmt(M['langkah_1'])} – {fmt(M['langkah_2'])}",
                             f"{fmt(M['langkah_2'])} – {fmt(M['credits'])}"], "title_dur": TITLE_DUR + 1.0, "end_dur": 14.0}

def overlay_events():
    M = markers; v3 = next(c for c in clips if c["src"] == "v3")["t_final"]
    return [
        ("title_open", 0.0),
        ("phase_set_induksi", M["set_induksi"] + 1.2),
        ("popup_guru1", t_of_v1(23.0)),
        ("phase_langkah_1", M["langkah_1"] + 0.3),
        ("popup_guru2", M["langkah_1"] + 1.8),
        ("steps_misi1", t_of_v1(988.5)),
        ("steps_misi2", t_of_v1(1261.0)),
        ("ayat_misi2", t_of_v1(1450.5)),
        ("phase_langkah_2", M["langkah_2"] + 0.3),
        ("popup_guru3", M["langkah_2"] + 1.8),
        ("steps_ar", t_of_v1(1872.0)),
        ("ayat_galeri", t_of_v1(2216.0)),
        ("phase_penutup", M["penutup"] + 0.3),
        ("ayat_rumusan", v3 + 7.4),
        ("credits_1", M["credits"] + 0.0), ("credits_2", M["credits"] + 10.0), ("credits_3", M["credits"] + 19.0),
        ("end_title", M["credits"] + 29.0),
    ]

# ------------------------------------------------------------------
# Rendering
# ------------------------------------------------------------------
GRADE_V1 = ("eq=contrast=1.07:brightness=-0.015:saturation=1.10:gamma=0.97,colorbalance=rs=-0.02:bs=0.02:rm=0.01:bm=-0.01:rh=-0.02,"
            "curves=master='0/0.02 0.5/0.49 1/0.96',vignette=angle=PI/6")
GRADE_V2 = "eq=contrast=1.04:brightness=-0.01:saturation=1.04:gamma=0.98,curves=master='0/0.02 0.5/0.49 1/0.96',vignette=angle=PI/6"
SHARP_V1 = "cas=strength=0.8,unsharp=5:5:0.6:5:5:0"
SHARP_V2 = "cas=strength=0.55"
AF_V1 = "highpass=f=90,lowpass=f=9000,afftdn=nr=10:nf=-30,dynaudnorm=f=300:g=21:p=0.8:m=12"
AF_V2 = "highpass=f=80,afftdn=nr=8:nf=-35,dynaudnorm=f=300:g=21:p=0.8:m=8"

def vfilter(c):
    # Gred warna pada resolusi sumber (pantas), kemudian skala Lanczos ke 1440p, kemudian penajaman pada resolusi akhir
    f = ["fps=30"]
    if c["src"] == "v1":
        x0, y0, w = CROPS[c["crop"] or "wide"]
        f.append(f"crop=trunc(iw*{w}/2)*2:trunc(ih*{w}/2)*2:trunc(iw*{x0}):trunc(ih*{y0})")
        f.append("hqdn3d=2:1.5:3:3")
    f.append(GRADE_V1 if c["src"] == "v1" else GRADE_V2)
    if c["blur"]:
        f.append(f"scale={OW // 4}:{OH // 4},boxblur=8:2,eq=brightness=-0.06,scale={OW}:{OH}:flags=bicubic")
    else:
        f.append(f"scale={OW}:{OH}:flags=lanczos")
        f.append(SHARP_V1 if c["src"] == "v1" else SHARP_V2)
    f.append("setsar=1,format=yuv420p")
    return ",".join(f)

def audio_src(c):
    """(fail, mula, penapis) untuk audio klip."""
    if c["audio"] == "none" or c["src"] == "black": return None
    if isinstance(c["audio"], (list, tuple)): return SRC["v1"], c["audio"][1], AF_V1, 1.0
    return SRC[c["src"]], c["start"], (AF_V1 if c["src"] == "v1" else AF_V2), (0.35 if c["audio"] == "amb" else 1.0)

def afilter(base, vol, d):
    fade = min(0.03, d / 4)
    return (f"aresample=48000,aformat=channel_layouts=stereo,{base},volume={vol},"
            f"afade=t=in:d={fade},afade=t=out:st={d - fade:.4f}:d={fade},apad,atrim=0:{d:.4f}")

def clip_path(i, kind="clips"): return os.path.join(WORK, kind, f"c{i:03d}." + ("mkv" if kind == "clips" else "wav"))

def render_audio(i, c, force=False):
    out = clip_path(i, "audio"); d = c["frames"] / FPS
    if os.path.exists(out) and not force: return out
    a = audio_src(c)
    if a is None: cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-t", f"{d:.4f}", "-i", "anullsrc=r=48000:cl=stereo"]
    else:
        f, st, base, vol = a
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{st:.4f}", "-i", f, "-vn", "-af", afilter(base, vol, d)]
    subprocess.run(cmd + ["-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out], check=True); return out

def render_clip(i, c, force=False):
    out = clip_path(i); d = c["frames"] / FPS
    if os.path.exists(out) and not force: return out
    aw = render_audio(i, c)
    if c["src"] == "black":
        vin = ["-f", "lavfi", "-i", f"color=c=0x06261c:s={OW}x{OH}:r=30"]; vf = "format=yuv420p"
    else:
        vin = ["-ss", f"{c['start']:.4f}", "-i", SRC[c["src"]]]; vf = vfilter(c)
    cmd = ["ffmpeg", "-v", "error", "-y"] + vin + ["-i", aw, "-map", "0:v:0", "-map", "1:a:0", "-vf", vf,
           "-frames:v", str(c["frames"]), "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-g", "30",
           "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out + ".tmp.mkv"]
    subprocess.run(cmd, check=True); os.replace(out + ".tmp.mkv", out); return out

def do_audio():
    build_edl(); os.makedirs(os.path.join(WORK, "audio"), exist_ok=True)
    with ThreadPoolExecutor(4) as ex: list(ex.map(lambda ic: render_audio(*ic), enumerate(clips)))
    lst = os.path.join(WORK, "audio.txt")
    with open(lst, "w") as f:
        for i in range(len(clips)): f.write(f"file '{clip_path(i, 'audio')}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", os.path.join(WORK, "dialog.wav")], check=True)
    print("dialog ->", os.path.join(WORK, "dialog.wav"))

def do_clips(force=False, jobs=3):
    build_edl(); os.makedirs(os.path.join(WORK, "clips"), exist_ok=True); os.makedirs(os.path.join(WORK, "audio"), exist_ok=True)
    order = sorted(range(len(clips)), key=lambda i: -clips[i]["frames"])  # klip panjang dahulu
    with ThreadPoolExecutor(jobs) as ex:
        list(ex.map(lambda i: (render_clip(i, clips[i], force), print("clip", i, flush=True)), order))

def do_rough():
    build_edl(); lst = os.path.join(WORK, "concat.txt")
    with open(lst, "w") as f:
        for i in range(len(clips)): f.write(f"file '{clip_path(i)}'\n")
    joined = os.path.join(WORK, "joined.mkv")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined], check=True)
    out = os.path.join(ROOT, "08_PREVIEW", "ROUGH_CUT_Hotel_Hijau_720p.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", joined, "-vf", "scale=1280:720", "-c:v", "libx264", "-preset", "fast",
                    "-crf", "26", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out], check=True)
    print("rough ->", out)

# ------------------------------------------------------------------
# Muzik & SFX
# ------------------------------------------------------------------
def music_plan():
    M = markers
    return [("mus_opening.wav", 0.0, M["set_induksi"] + 3.0, 0.0, -3.0),
            ("mus_intro.wav", M["set_induksi"] - 1.0, M["langkah_1"] + 1.0, 0.0, -18.0),
            ("mus_upbeat.wav", M["langkah_1"] - 1.0, M["langkah_2"] + 1.0, 0.0, -19.5),
            ("mus_tech.wav", M["langkah_2"] - 1.0, M["penutup"] + 1.0, 0.0, -19.0),
            ("mus_piano.wav", M["penutup"] - 1.0, M["credits"] + 1.0, 0.0, -18.0),
            ("mus_closing.wav", M["credits"] - 1.0, TOTAL, 0.0, -5.0)]

def sfx_plan():
    M = markers; ev = dict(overlay_events())
    return [("sfx_impact.wav", 0.5, -8.0), ("sfx_whoosh.wav", M["set_induksi"] - 0.6, -14.0),
            ("sfx_reveal.wav", ev["popup_guru1"], -15.0),
            ("sfx_whoosh.wav", M["langkah_1"] - 0.5, -12.0), ("sfx_reveal.wav", ev["popup_guru2"], -14.0),
            ("sfx_whoosh.wav", M["langkah_2"] - 0.5, -12.0), ("sfx_reveal.wav", ev["popup_guru3"], -14.0),
            ("sfx_whoosh.wav", M["penutup"] - 0.5, -13.0), ("sfx_whoosh.wav", M["credits"] - 0.5, -14.0),
            ("sfx_impact.wav", ev["end_title"] + 0.3, -11.0)]

# ------------------------------------------------------------------
# Sari kata
# ------------------------------------------------------------------
FIX = [(r"\b(pesif|pesip|pasip|pesi|pasi|pastry|pasih|basif)\b", "pasif"), (r"\b(atif|antif|aktip|actif|ektif|aktiv|lektik|aktip)\b", "aktif"),
       (r"\bpengawal (pasar|basah|bahsa)\b", "Pengawal Bahasa"), (r"\bhotel (jijau|hijauh|hijab)\b", "Hotel Hijau"),
       (r"\bjijau\b", "Hijau"), (r"\bsedia,? cikgu\b", "Sedia, cikgu!"), (r"\bcik ?gu\b", "cikgu"), (r"\bmine ?craft\b", "Minecraft")]
HALLU = re.compile(r"(terima kasih kerana menonton|sila langgan|subscribe|like dan share|tonton video|♪|www\.|\.com)", re.I)
KEYS = [  # (regex, warna BGR ASS)
    (r"ayat aktif", "&H37AFD4&"), (r"ayat pasif", "&H84D696&"), (r"\baktif\b", "&H37AFD4&"), (r"\bpasif\b", "&H84D696&"),
    (r"Pengawal Bahasa", "&H37AFD4&"), (r"Hotel Hijau", "&H84D696&"), (r"kata kerja", "&H37AFD4&"), (r"\bMisi \d\b", "&H37AFD4&"),
    (r"\bsituasi( \d)?\b", "&H84D696&"), (r"\bobjektif\b", "&H37AFD4&"), (r"\bciri-ciri\b", "&H37AFD4&"), (r"kitar semula", "&H84D696&"),
    (r"tiket refleksi", "&H37AFD4&"), (r"\b(di|me|mem|men|meng|meny)[a-z]+(kan|i)?\b(?=.*)", None),
    (r"\b(mengasingkan|diasingkan|memasang|dipasang|menuai|dituai|dipasifkan|diaktifkan|mempelajari|dipelajari)\b", "&H37AFD4&"),
    (r"\bBetul\b!?", "&H84D696&"), (r"Sedia, cikgu!", "&H37AFD4&"), (r"\bMinecraft\b", "&H84D696&"), (r"\bAR\b", "&H84D696&"),
]

def style_text(t):
    spans = []
    for rx, col in KEYS:
        if col is None: continue
        for m in re.finditer(rx, t, re.I):
            if not any(m.start() < e and s < m.end() for s, e, _ in spans): spans.append((m.start(), m.end(), col))
    out = []; last = 0
    for s, e, col in sorted(spans):
        out.append(t[last:s]); out.append("{\\b1\\c" + col + "}" + t[s:e] + "{\\b0\\c&HFFFFFF&}"); last = e
    out.append(t[last:]); return "".join(out)

def wrap2(text, n=46):
    if len(text) <= n: return [text]
    words = text.split(); best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:]); sc = abs(len(a) - len(b))
        if max(len(a), len(b)) <= n + 12 and (best is None or sc < best[0]): best = (sc, a, b)
    return [best[1], best[2]] if best else [text]

SUBS_EXTRA = [  # baris dikenal pasti daripada transkripsi mikrofon dekat (masa vid1)
    (1761.5, 1768.9, "Jadi, sekarang, tadi awak semua dah belajar\\Ntentang ayat aktif dengan ayat pasif, kan?"),
    (1769.5, 1770.6, "Ya!"),
]

def lines_of(t):
    return t.split("\\N") if "\\N" in t else wrap2(t)

def do_subs():
    build_edl()
    wav = os.path.join(WORK, "dialog.wav")
    raw = os.path.join(HERE, "transcript_raw.json")
    if not os.path.exists(raw):
        import numpy as np, wave
        from faster_whisper import WhisperModel
        w = wave.open(wav); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2).mean(1) / 32768
        a = a[::3]  # 48k -> 16k
        m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=4)
        segs, _ = m.transcribe(a, language="ms", beam_size=5, vad_filter=True, word_timestamps=True, condition_on_previous_text=False,
                               vad_parameters=dict(min_silence_duration_ms=500, speech_pad_ms=200))
        res = []
        for s in segs:
            res.append(dict(s=s.start, e=s.end, t=s.text.strip(), lp=s.avg_logprob, ns=s.no_speech_prob, cr=s.compression_ratio,
                            w=[(x.start, x.end, x.word) for x in s.words]))
            print(f"{s.start:7.1f} {s.text.strip()}", flush=True)
        json.dump(res, open(raw, "w"), ensure_ascii=False, indent=0)
    res = json.load(open(raw))
    edits = {}
    ep = os.path.join(HERE, "transcript_edits.json")  # semakan manual: {indeks: "teks dibetulkan" | null (buang)}
    if os.path.exists(ep): edits = json.load(open(ep))
    cues = []; prev = None; rep = 0
    for i, s in enumerate(res):
        txt = s["t"]; b = s["e"]
        if str(i) in edits:
            v = edits[str(i)]
            if v is None: continue
            if isinstance(v, list): txt, b = v[0], res[v[1]]["e"]
            else: txt = v
        else:
            if s["ns"] > 0.6 or s["lp"] < -1.0 or s["cr"] > 2.4 or HALLU.search(txt) or len(txt) < 2: continue
            for rx, rp in FIX: txt = re.sub(rx, rp, txt, flags=re.I)
        txt = re.sub(r"[ \t]+", " ", txt).strip()
        if txt == prev:
            rep += 1
            if rep >= 2: continue
        else: rep = 0
        prev = txt; a = s["s"]
        if a >= markers["credits"] or a < markers["set_induksi"]: continue
        cues.append([a, b, txt])
    for v1a, v1b, txt in SUBS_EXTRA:
        cues.append([t_of_v1(v1a), t_of_v1(v1b), txt])
    cues.sort(key=lambda c: c[0])
    for c in cues: c[1] = max(c[0] + 1.0, min(c[1], c[0] + min(7.0, 1.2 + 0.075 * len(c[2]))))  # tempoh ikut kelajuan bacaan
    for j in range(len(cues) - 1): cues[j][1] = min(cues[j][1], cues[j + 1][0] - 0.05)
    def ts_srt(x):
        ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    def ts_ass(x):
        cs = int(round(x * 100)); return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"
    srt = os.path.join(ROOT, "06_SUBTITLES", "MISI_PENGAWAL_BAHASA_Hotel_Hijau.ms.srt")
    with open(srt, "w", encoding="utf-8") as f:
        for k, (a, b, t) in enumerate(cues, 1): f.write(f"{k}\n{ts_srt(a)} --> {ts_srt(b)}\n" + "\n".join(lines_of(t)) + "\n\n")
    ass = os.path.join(ROOT, "06_SUBTITLES", "MISI_PENGAWAL_BAHASA_Hotel_Hijau.ms.ass")
    with open(ass, "w", encoding="utf-8") as f:
        f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 2560\nPlayResY: 1440\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n"
                "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
                "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
                "Style: Default,Inter SemiBold,64,&H00FFFFFF,&H000000FF,&H5A0E2A1F,&H96000000,0,0,0,0,100,100,0,0,3,16,0,2,160,160,64,1\n\n"
                "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        for a, b, t in cues:
            f.write(f"Dialogue: 0,{ts_ass(a)},{ts_ass(b)},Default,,0,0,0,,{'\\N'.join(style_text(x) for x in lines_of(t))}\n")
    print(len(cues), "cue ->", srt, ass)

# ------------------------------------------------------------------
# Akhir
# ------------------------------------------------------------------
def do_final(preview=False):
    build_edl(); M = markers
    joined = os.path.join(WORK, "joined.mkv")
    if not os.path.exists(joined): do_rough()
    man = json.load(open(os.path.join(GFX, "manifest.json")))
    inputs = ["-i", joined]; fc = []; last = "[0:v]"; k = 1
    for name, t0 in overlay_events():
        g = man[name]
        inputs += ["-itsoffset", f"{t0:.3f}", "-i", os.path.join(GFX, name + ".mov")]
        fc.append(f"[{k}:v]format=rgba[g{k}]")
        fc.append(f"{last}[g{k}]overlay={g['x']}:{g['y']}:eof_action=pass:repeatlast=0[o{k}]"); last = f"[o{k}]"; k += 1
    ass = os.path.join(ROOT, "06_SUBTITLES", "MISI_PENGAWAL_BAHASA_Hotel_Hijau.ms.ass")
    fc.append(f"{last}ass='{ass}':fontsdir=/usr/share/fonts/opentype/inter[subs]"); last = "[subs]"
    fc.append("[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[dlg][key]")
    mus = []
    for i, (fn, a, b, off, g) in enumerate(music_plan()):
        inputs += ["-i", os.path.join(AUD, fn)]; d = b - a
        fc.append(f"[{k}:a]atrim={off}:{off + d},asetpts=PTS-STARTPTS,volume={g}dB,afade=t=in:d=2,afade=t=out:st={d - 3}:d=3,"
                  f"adelay={int(a * 1000)}|{int(a * 1000)},apad[m{i}]"); mus.append(f"[m{i}]"); k += 1
    fc.append("".join(mus) + f"amix=inputs={len(mus)}:normalize=0:duration=longest,atrim=0:{TOTAL}[musraw]")
    fc.append("[musraw][key]sidechaincompress=threshold=0.04:ratio=5:attack=30:release=600:makeup=1[musd]")
    sf = []
    for i, (fn, t0, g) in enumerate(sfx_plan()):
        inputs += ["-i", os.path.join(AUD, fn)]
        fc.append(f"[{k}:a]volume={g}dB,adelay={int(t0 * 1000)}|{int(t0 * 1000)},apad[s{i}]"); sf.append(f"[s{i}]"); k += 1
    fc.append("[dlg][musd]" + "".join(sf) + f"amix=inputs={2 + len(sf)}:normalize=0:duration=first,"
              f"loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,afade=t=out:st={TOTAL - 3.5}:d=3.5,atrim=0:{TOTAL}[aout]")
    fc.append(f"{last}fade=t=out:st={TOTAL - 2}:d=2,format=yuv420p[vout]")
    fg = os.path.join(HERE, "final_filtergraph.txt"); open(fg, "w").write(";\n".join(fc))
    if preview:
        out = os.environ.get("HH_OUT") or os.path.join(ROOT, "08_PREVIEW", "PREVIEW_Hotel_Hijau_720p.mp4"); venc = ["-s", "1280x720", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24"]
    else:
        out = os.path.join(ROOT, "09_FINAL_EXPORT", "SIMULASI_PENGAJARAN_MIKRO_Hotel_Hijau_1440p.mp4")
        venc = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-profile:v", "high", "-level", "5.1", "-maxrate", "16M", "-bufsize", "32M"]
    cmd = ["ffmpeg", "-v", "error", "-stats", "-y"] + inputs + ["-filter_complex_script", fg, "-map", "[vout]", "-map", "[aout]",
           "-r", "30", "-frames:v", str(TOTAL_FRAMES)] + venc + ["-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-ac", "2", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True); print("final ->", out)

def do_edl():
    build_edl()
    with open(os.path.join(HERE, "edl.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["#", "masa_akhir_mula", "masa_akhir_tamat", "sumber", "masa_sumber_mula", "tempoh_s", "bingkai", "framing", "audio", "fasa", "nota"])
        names = {"v1": "vid sintaksis 1.MOV", "v2": "vid sintaksis 2.MOV", "v3": "vid3.mp4", "black": "(tajuk)"}
        mm = lambda s: f"{int(s // 60):02d}:{s % 60:06.3f}"
        for i, c in enumerate(clips):
            t0 = c["t_final"]; d = c["frames"] / FPS
            au = c["audio"] if isinstance(c["audio"], str) else f"vid1@{mm(c['audio'][1])}"
            w.writerow([i, mm(t0), mm(t0 + d), names[c["src"]], mm(c["start"]), f"{d:.3f}", c["frames"], c["crop"] or "", au, c["tag"], c["label"]])
    json.dump({k: round(v, 3) for k, v in markers.items()}, open(os.path.join(HERE, "markers.json"), "w"), indent=1)
    json.dump(gfx_config(), open(os.path.join(HERE, "gfx_config.json"), "w"), indent=1, ensure_ascii=False)
    cut = sum(1 for c in clips if "cutaway" in c["label"]); cutd = sum(c["frames"] for c in clips if "cutaway" in c["label"]) / FPS
    fr = {}
    for c in clips:
        if c["src"] == "v1" and c["audio"] == "own": fr[c["crop"]] = fr.get(c["crop"], 0) + c["frames"] / FPS
    print(len(clips), "klip; cutaway:", cut, f"({cutd:.0f}s); framing v1:", {k: round(v) for k, v in fr.items()})
    print({k: fmt(v) for k, v in markers.items()})
    for n, t in overlay_events(): print(f"  {n:18s} {fmt(t)}")

if __name__ == "__main__":
    sys.path.insert(0, HERE)
    step = sys.argv[1] if len(sys.argv) > 1 else "edl"
    {"edl": do_edl, "audio": do_audio, "subs": do_subs, "clips": lambda: do_clips("--force" in sys.argv), "rough": do_rough,
     "final": lambda: do_final("--preview" in sys.argv)}[step]()
