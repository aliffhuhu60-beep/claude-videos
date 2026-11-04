#!/usr/bin/env python3
"""MISI PENGAWAL BAHASA: HOTEL HIJAU — skrip suntingan utama (FFmpeg).

Langkah:
  python3 build_video.py clips     # render setiap klip EDL -> _work/clips/*.mkv (gred warna + audio dialog)
  python3 build_video.py rough     # cantum klip -> 08_PREVIEW/ROUGH_CUT_*.mp4 (tanpa grafik/muzik)
  python3 build_video.py final     # grafik + muzik + SFX + ducking + loudnorm -> 09_FINAL_EXPORT/*.mp4
  python3 build_video.py edl       # cetak EDL (masa akhir <-> sumber) ke 07_PROJECT_FILES/edl.csv

Semua masa sumber merujuk kepada fail asal dalam 01_RAW_VIDEO (fail asal TIDAK diubah).
Panjang video akhir dikunci TEPAT 30:00 (54 000 bingkai @ 30 fps).
"""
import csv, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "01_RAW_VIDEO")
GFX = os.path.join(ROOT, "05_GRAPHICS")
AUD = os.path.join(ROOT, "02_AUDIO")
WORK = os.environ.get("HH_WORK", os.path.join(ROOT, "07_PROJECT_FILES", "_work"))
SRC = {
    "v1": os.path.join(RAW, "vid sintaksis 1.MOV"),   # kamera induk (wide), 854x480 HEVC 60p, 48:11
    "v2": os.path.join(RAW, "vid sintaksis 2.MOV"),   # himpunan B-roll (CapCut), 1280x720 30p, 25:00
    "v3": os.path.join(RAW, "vid3.mp4"),              # murid membaca ayat + tepukan, 1280x720 30p, 0:28
}
FPS = 30
TOTAL_FRAMES = 30 * 60 * FPS  # 30:00 tepat

# ------------------------------------------------------------------
# Offset penyegerakan B-roll (vid2 -> masa vid1), daripada sync_broll.py
# (korelasi silang sampul audio, margin keyakinan >= ~0.05 dan disemak secara visual)
# seg: (v2_start, v2_end, v1_offset)
# ------------------------------------------------------------------
SYNC = {
    1: (4.7, 18.9, 21.20), 2: (18.9, 43.7, 63.88), 3: (43.7, 53.1, 95.58), 4: (53.1, 64.6, 117.90),
    5: (64.6, 72.4, 140.27), 7: (85.9, 90.8, 218.95), 8: (90.8, 136.0, 294.95), 9: (136.0, 152.9, 373.32),
    10: (152.9, 158.1, 419.81), 12: (169.7, 184.0, 462.31), 13: (184.0, 216.4, 489.51), 14: (216.4, 228.2, 570.89),
    17: (237.4, 245.4, 688.36), 19: (250.5, 260.0, 987.54), 20: (260.0, 267.6, 1005.41), 22: (275.2, 282.6, 1048.06),
    24: (287.5, 307.2, 1085.41), 27: (316.0, 328.7, 1147.66), 29: (341.2, 349.0, 1249.04), 30: (349.0, 357.5, 1260.20),
    34: (375.4, 390.1, 1377.57), 35: (390.1, 400.0, 1449.94), 39: (410.2, 679.7, 1760.08), 40: (679.7, 715.9, 2151.28),
    41: (715.9, 764.9, 2205.70), 42: (764.9, 956.0, 2473.10), 44: (971.2, 978.4, 219.46), 46: (979.2, 1011.3, 353.88),
    47: (1011.3, 1026.2, 620.93), 49: (1032.6, 1042.8, 678.39), 50: (1042.8, 1061.4, 891.54), 51: (1061.4, 1071.9, 915.86),
    53: (1086.4, 1110.3, 1297.79), 54: (1110.3, 1180.7, 1323.83), 55: (1180.7, 1195.5, 1406.95), 56: (1195.5, 1204.3, 1468.63),
    59: (1287.3, 1319.8, 1871.16), 62: (1335.5, 1376.3, 2197.06), 64: (1377.3, 1422.5, 2361.67), 66: (1437.4, 1451.2, 2537.69),
    70: (1474.0, 1486.2, 2593.72),
}
V3_OFFSET = 2784.3  # vid3 bermula pada masa vid1 ini (korelasi audio)

# ------------------------------------------------------------------
# EDL
# ------------------------------------------------------------------
clips = []      # dict(src, start, frames, frame, audio, zoom, blur, tag, label)
markers = {}    # nama -> masa akhir (s)

def nframes():
    return sum(c["frames"] for c in clips)

def now():
    return nframes() / FPS

def add(src, start, dur=None, frames=None, frame="full", audio="own", zoom=None, blur=False, tag="", label=""):
    f = frames if frames is not None else int(round(dur * FPS))
    if f <= 0: return
    clips.append(dict(src=src, start=round(start, 4), frames=f, frame=frame, audio=audio, zoom=zoom, blur=blur,
                      tag=tag, label=label, t_final=now()))

def span(a, b, inserts=(), frame="wide", tag=""):
    """Rakaman induk v1 dari a..b (s). inserts: [(seg, v1_from, v1_to)] B-roll yang disegerakkan
    menggantikan gambar DAN audio (mikrofon telefon lebih dekat) pada julat itu."""
    t = a
    fa = int(round(a * FPS))
    for seg, x0, x1 in sorted(inserts, key=lambda z: z[1]):
        s0, s1, off = SYNC[seg]
        x0 = max(x0, off, a); x1 = min(x1, off + (s1 - s0) - 0.05, b)
        # elak 'flash cut' < 1 s antara sisipan dan rakaman induk
        if 0 < x0 - t < 1.0:
            x0 = t if off <= t else t + 1.0
        if 0 < b - x1 < 1.0:
            x1 = b if off + (s1 - s0) - 0.05 >= b else b - 1.0
        if x1 - x0 < 1.0: continue
        if x0 > t:
            add("v1", t, frames=int(round(x0 * FPS)) - int(round(t * FPS)), frame=frame, tag=tag)
        add("v2", s0 + (x0 - off), frames=int(round(x1 * FPS)) - int(round(x0 * FPS)), tag=tag, label=f"seg{seg}@v1:{x0:.1f}")
        t = x1
    if b > t:
        add("v1", t, frames=int(round(b * FPS)) - int(round(t * FPS)), frame=frame, tag=tag)

def mark(name):
    markers[name] = now()

def build_edl():
    clips.clear(); markers.clear()
    # ================= A. PEMBUKAAN SINEMATIK (00:00 - 00:28) =================
    mark("open")
    add("v1", 2.0, 12.0, frame="wide", audio="none", zoom=(1.0, 1.08), tag="open")          # suasana kelas Hotel Hijau
    add("v2", 0.2, 4.4, audio="none", zoom=(1.0, 1.06), tag="open")                          # papan putih: SP 5.3.3
    add("v2", 53.4, 7.0, audio="none", zoom=(1.0, 1.06), tag="open")                         # gambar HOTEL HIJAU
    add("v2", 86.0, 4.6, audio="none", zoom=(1.04, 1.0), tag="open")                         # murid bersedia
    # ================= B. GURU 1 (00:28 - 10:00) =================
    mark("g1")
    span(17.0, 278.5, [(1, 21.2, 35.4), (2, 63.9, 88.7), (3, 95.6, 104.9), (4, 117.9, 129.4), (5, 140.3, 148.1),
                       (44, 219.5, 226.6)], frame="wide", tag="g1")
    mark("papan")
    span(316.0, 357.0, [(8, 316.0, 340.0), (46, 345.0, 357.0)], frame="med", tag="g1")
    span(366.0, 426.0, [(46, 366.0, 373.0), (9, 373.4, 390.0), (10, 419.9, 425.0)], frame="wide", tag="g1")
    span(445.5, 520.0, [(12, 462.4, 476.5), (13, 489.6, 519.9)], frame="med", tag="g1")
    mark("kumpulan")
    span(520.0, 655.0, [(13, 520.0, 521.8), (14, 570.9, 582.6), (47, 621.0, 635.7)], frame="wide", tag="g1")
    # ================= C. GURU 2 (10:00 - 20:00) =================
    mark("g2")
    span(655.0, 728.0, [(49, 678.4, 688.5), (17, 688.4, 696.3)], frame="med", tag="g2")
    span(815.0, 1110.0, [(50, 891.6, 910.0), (51, 915.9, 926.2), (19, 987.6, 996.9), (20, 1005.5, 1012.9),
                         (22, 1048.1, 1055.5), (24, 1085.5, 1105.0)], frame="wide", tag="g2")
    mark("ar")
    span(1229.0, 1300.0, [(29, 1249.1, 1256.9), (30, 1260.3, 1268.6), (53, 1297.8, 1300.0)], frame="med", tag="g2")
    mark("ar_typing")
    span(1330.0, 1366.0, [(54, 1330.0, 1366.0)], tag="g2")
    span(1400.0, 1470.0, [(55, 1407.0, 1421.5), (35, 1450.0, 1459.9), (56, 1468.7, 1470.0)], frame="wide", tag="g2")
    mark("h2")
    span(1680.0, 1735.0, [], frame="med", tag="g2")
    # ================= D. GURU 3 (20:00 - 28:30) =================
    mark("g3")
    span(1735.0, 1830.0, [(39, 1762.0, 1830.0)], frame="med", tag="g3")
    span(1860.0, 1910.0, [(59, 1871.2, 1903.5)], frame="wide", tag="g3")
    span(1960.0, 2025.0, [(39, 1960.0, 2025.0)], tag="g3")
    mark("galeri")
    span(2150.0, 2260.0, [(40, 2151.3, 2187.4), (62, 2190.0, 2205.7), (41, 2205.7, 2254.5)], frame="wide", tag="g3")
    span(2362.0, 2400.0, [(64, 2362.0, 2400.0)], tag="g3")
    mark("refleksi")
    span(2473.0, 2596.5, [(42, 2473.2, 2537.6), (66, 2537.8, 2551.0), (42, 2551.0, 2593.6), (70, 2593.8, 2596.5)], tag="g3")
    mark("baca")
    add("v3", 0.0, frames=int(round(1710 * FPS)) - nframes(), tag="g3")   # vid3 penuh (~28.5 s) hingga 28:30
    # ================= E. PENUTUP (28:30 - 30:00) =================
    mark("close")
    add("v2", 940.0, 6.0, audio="amb", tag="close")      # murid tersenyum dengan tiket refleksi
    add("v2", 1381.0, 6.0, audio="amb", tag="close")     # interaksi guru-murid
    add("v1", 1753.0, 6.0, frame="med", audio="amb", tag="close")   # murid mengangkat tangan
    add("v2", 24.0, 6.0, audio="amb", tag="close")       # Guru 1
    add("v2", 251.0, 5.0, audio="amb", tag="close")      # Guru 2
    add("v2", 1294.0, 6.0, audio="amb", tag="close")     # Guru 3
    mark("credits")
    add("v1", 2836.0, frames=TOTAL_FRAMES - nframes(), frame="wide", audio="amb", blur=True, tag="close")  # kelas bersurai
    assert nframes() == TOTAL_FRAMES, nframes()
    return clips, markers

# ------------------------------------------------------------------
# Rendering klip
# ------------------------------------------------------------------
GRADE_V1 = ("hqdn3d=1.5:1.5:4:4,eq=contrast=1.07:brightness=-0.015:saturation=1.10:gamma=0.97,"
            "colorbalance=rs=-0.02:bs=0.02:rm=0.01:bm=-0.01:rh=-0.02,curves=master='0/0.02 0.5/0.49 1/0.96',vignette=angle=PI/6")
GRADE_V2 = ("eq=contrast=1.04:brightness=-0.01:saturation=1.04:gamma=0.98,"
            "curves=master='0/0.02 0.5/0.49 1/0.96',vignette=angle=PI/6")
AF_V1 = "highpass=f=90,lowpass=f=9000,afftdn=nr=10:nf=-30,dynaudnorm=f=300:g=21:p=0.8:m=12"
AF_V2 = "highpass=f=80,afftdn=nr=8:nf=-35,dynaudnorm=f=300:g=21:p=0.8:m=8"

def vfilter(c):
    src = c["src"]; f = []
    if src == "v1":
        f.append("fps=30")
        if c["frame"] == "med":   # 'medium shot' — tumpuan hadapan kelas (guru + skrin)
            f.append("crop=iw*0.74:ih*0.74:iw*0.15:ih*0.06")
        else:
            f.append("crop=iw*0.96:ih*0.96")
    else:
        f.append("fps=30")
    if c["zoom"]:
        z0, z1 = c["zoom"]; d = c["frames"] / FPS
        n = max(1, c["frames"] - 1)
        f.append("scale=3840:2160:flags=lanczos,"
                 f"zoompan=z='{z0}+({z1}-{z0})*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30")
    else:
        f.append("scale=1920:1080:flags=lanczos")
    f.append(GRADE_V1 if src == "v1" else GRADE_V2)
    if c["blur"]:
        f.append("boxblur=24:2,eq=brightness=-0.06")
    f.append("setsar=1,format=yuv420p")
    return ",".join(f)

def afilter(c):
    d = c["frames"] / FPS
    base = AF_V1 if c["src"] == "v1" else AF_V2
    vol = "volume=0.35," if c["audio"] == "amb" else ""
    fade = min(0.03, d / 4)
    return (f"aresample=48000,aformat=channel_layouts=stereo,{base},{vol}"
            f"afade=t=in:d={fade},afade=t=out:st={d - fade:.4f}:d={fade},apad,atrim=0:{d:.4f}")

def clip_path(i):
    return os.path.join(WORK, "clips", f"c{i:03d}.mkv")

def render_clip(i, c, force=False):
    out = clip_path(i)
    if os.path.exists(out) and not force: return out
    d = c["frames"] / FPS
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{c['start']:.4f}", "-i", SRC[c["src"]]]
    if c["audio"] == "none":
        cmd += ["-f", "lavfi", "-t", f"{d + 0.5:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
        amap = ["-map", "1:a"]; af = f"atrim=0:{d:.4f}"
    else:
        amap = ["-map", "0:a:0"]; af = afilter(c)
    cmd += ["-map", "0:v:0"] + amap + ["-vf", vfilter(c), "-af", af, "-frames:v", str(c["frames"]),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", "-g", "30",
            "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out + ".tmp.mkv"]
    subprocess.run(cmd, check=True)
    os.replace(out + ".tmp.mkv", out)
    return out

def do_clips(force=False):
    os.makedirs(os.path.join(WORK, "clips"), exist_ok=True)
    build_edl()
    with ThreadPoolExecutor(2) as ex:
        list(ex.map(lambda ic: (render_clip(ic[0], ic[1], force), print("clip", ic[0], flush=True)), enumerate(clips)))

def do_rough():
    build_edl()
    lst = os.path.join(WORK, "concat.txt")
    with open(lst, "w") as f:
        for i in range(len(clips)): f.write(f"file '{clip_path(i)}'\n")
    joined = os.path.join(WORK, "joined.mkv")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined], check=True)
    out = os.path.join(ROOT, "08_PREVIEW", "ROUGH_CUT_Hotel_Hijau_720p.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", joined, "-vf", "scale=1280:720", "-c:v", "libx264", "-preset", "fast",
                    "-crf", "26", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out], check=True)
    print("rough ->", out)

# ------------------------------------------------------------------
# Grafik, muzik & SFX (masa akhir, dikira daripada penanda EDL)
# ------------------------------------------------------------------
def t_of_v1(v1t):
    """Masa akhir bagi masa sumber vid1 (mengambil kira sisipan B-roll yang disegerakkan)."""
    for c in clips:
        d = c["frames"] / FPS
        if c["src"] == "v1" and c["start"] <= v1t < c["start"] + d and c["audio"] == "own":
            return c["t_final"] + (v1t - c["start"])
        if c["src"] == "v2" and c["label"].startswith("seg"):
            seg = int(c["label"][3:].split("@")[0]); s0, s1, off = SYNC[seg]
            v1s = off + (c["start"] - s0)
            if v1s <= v1t < v1s + d: return c["t_final"] + (v1t - v1s)
    raise ValueError(v1t)

def overlay_events(M):
    ev = [
        ("opening_title", 0.8),
        ("chapter_01", M["g1"] + 0.2),
        ("popup_guru1", t_of_v1(23.0)),             # Guru 1 kelihatan (B-roll seg1: slaid "Selamat Datang ke Hotel Hijau")
        ("lt_video", t_of_v1(141.0)),
        ("lt_papan", M["papan"] + 0.5),
        ("chapter_02", M["kumpulan"] + 0.3),
        ("popup_guru2", M["g2"] + 1.0),             # sejurus Guru 2 mengambil alih di hadapan kelas
        ("chapter_03", M["g2"] + 7.0),
        ("chapter_04", M["ar"] + 0.3),
        ("lt_ar", M["ar_typing"] + 1.0),
        ("popup_guru3", M["g3"] + 1.0),
        ("chapter_05", M["g3"] + 7.0),
        ("lt_galeri", M["galeri"] + 2.0),
        ("chapter_06", M["refleksi"] + 0.5),
        ("lt_baca", M["baca"] + 1.0),
        ("credits_1", M["credits"] + 0.0),
        ("credits_2", M["credits"] + 11.0),
        ("credits_3", M["credits"] + 21.0),
        ("end_title", M["credits"] + 32.0),
    ]
    return ev

def music_plan(M):
    # (fail, mula_akhir, tamat_akhir, offset_dalam_fail, gain_dB_asas)
    return [
        ("mus_opening.wav", 0.0, M["g1"] + 3.0, 0.0, -2.0),
        ("mus_intro.wav", M["g1"] - 1.0, M["papan"] + 2.0, 0.0, -17.0),
        ("mus_upbeat.wav", M["papan"], M["g2"] - 1.0, 0.0, -19.0),
        ("mus_upbeat.wav", M["g2"] + 1.0, M["ar"] + 1.0, 60.0, -19.0),
        ("mus_tech.wav", M["ar"] - 1.0, M["g3"] - 1.0, 0.0, -18.0),
        ("mus_motiv.wav", M["g3"] + 1.0, M["refleksi"] + 1.0, 0.0, -18.0),
        ("mus_piano.wav", M["refleksi"] - 1.0, M["close"] + 1.0, 0.0, -17.0),
        ("mus_closing.wav", M["close"] - 1.0, 1800.0, 0.0, -4.0),
    ]

def sfx_plan(M):
    return [
        ("sfx_impact.wav", 0.6, -6.0), ("sfx_whoosh.wav", 11.6, -14.0), ("sfx_whoosh.wav", M["g1"] - 0.7, -14.0),
        ("sfx_whoosh.wav", M["g2"] - 0.6, -12.0), ("sfx_reveal.wav", M["g2"] + 1.0, -14.0),
        ("sfx_whoosh.wav", M["g3"] - 0.6, -12.0), ("sfx_reveal.wav", M["g3"] + 1.0, -14.0),
        ("sfx_reveal.wav", t_of_v1(23.0), -14.0),
        ("sfx_whoosh.wav", M["close"] - 0.6, -14.0), ("sfx_impact.wav", M["credits"] + 32.3, -10.0),
    ]

def do_final(preview=False):
    build_edl(); M = markers
    joined = os.path.join(WORK, "joined.mkv")
    if not os.path.exists(joined): do_rough()
    import graphics
    gx0, gx1, gy = graphics.progress_assets(GFX, [M["g2"] - M["g1"], M["g3"] - M["g2"], M["close"] - M["g3"]])
    wb = gx1 - gx0
    # strip berganda untuk bar kemajuan (separuh kiri emas, separuh kanan lut sinar)
    from PIL import Image
    strip = Image.new("RGBA", (wb * 2, 4), (0, 0, 0, 0)); strip.paste(Image.new("RGBA", (wb, 4), (212, 175, 55, 235)), (0, 0))
    strip.save(os.path.join(WORK, "progress_strip.png"))
    ev = overlay_events(M)
    inputs = ["-i", joined]
    fc = []; last = "[0:v]"; k = 1
    p0, p1 = M["g1"], M["close"]
    inputs += ["-loop", "1", "-framerate", "30", "-i", os.path.join(GFX, "progress_track.png")]
    inputs += ["-loop", "1", "-framerate", "30", "-i", os.path.join(WORK, "progress_strip.png")]
    fc.append(f"[1:v]format=rgba,fade=t=in:st={p0 + 6}:d=1:alpha=1,fade=t=out:st={p1 - 1}:d=1:alpha=1[trk]")
    fc.append(f"[2:v]format=rgba,crop=w={wb}:h=4:x='{wb}*(1-min(1,max(0,(t-{p0})/{p1 - p0})))':y=0,"
              f"fade=t=in:st={p0 + 6}:d=1:alpha=1,fade=t=out:st={p1 - 1}:d=1:alpha=1[fil]")
    fc.append(f"{last}[trk]overlay=0:0:shortest=1:enable='between(t,{p0 + 6},{p1})'[pb0]")
    fc.append(f"[pb0][fil]overlay={gx0}:{gy}:shortest=1:enable='between(t,{p0 + 6},{p1})'[pb1]")
    last = "[pb1]"; k = 3
    for name, t0 in ev:
        inputs += ["-i", os.path.join(GFX, name + ".mov")]
        fc.append(f"[{k}:v]setpts=PTS-STARTPTS+{t0:.3f}/TB[g{k}]")
        fc.append(f"{last}[g{k}]overlay=0:0:eof_action=pass:repeatlast=0[o{k}]")
        last = f"[o{k}]"; k += 1
    # ---- audio ----
    dlg = "[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[dlg][key]"
    fc.append(dlg)
    mus = []
    for i, (fn, a, b, off, g) in enumerate(music_plan(M)):
        inputs += ["-i", os.path.join(AUD, fn)]
        d = b - a
        fc.append(f"[{k}:a]atrim={off}:{off + d},asetpts=PTS-STARTPTS,volume={g}dB,"
                  f"afade=t=in:d=2,afade=t=out:st={d - 3}:d=3,adelay={int(a * 1000)}|{int(a * 1000)},apad[m{i}]")
        mus.append(f"[m{i}]"); k += 1
    fc.append("".join(mus) + f"amix=inputs={len(mus)}:normalize=0:duration=longest,atrim=0:1800[musraw]")
    # ducking: muzik diperlahankan apabila ada dialog
    fc.append("[musraw][key]sidechaincompress=threshold=0.04:ratio=5:attack=30:release=600:makeup=1[musd]")
    sf = []
    for i, (fn, t0, g) in enumerate(sfx_plan(M)):
        inputs += ["-i", os.path.join(AUD, fn)]
        fc.append(f"[{k}:a]volume={g}dB,adelay={int(t0 * 1000)}|{int(t0 * 1000)},apad[s{i}]")
        sf.append(f"[s{i}]"); k += 1
    fc.append("[dlg][musd]" + "".join(sf) + f"amix=inputs={2 + len(sf)}:normalize=0:duration=first,"
              "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,atrim=0:1800[aout]")
    fc.append(f"{last}fade=t=out:st=1798:d=2,format=yuv420p[vout]")
    fcs = ";\n".join(fc)
    with open(os.path.join(ROOT, "07_PROJECT_FILES", "final_filtergraph.txt"), "w") as f: f.write(fcs)
    if preview:
        out = os.path.join(ROOT, "08_PREVIEW", "PREVIEW_Hotel_Hijau_720p.mp4")
        venc = ["-s", "1280x720", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24"]
    else:
        out = os.path.join(ROOT, "09_FINAL_EXPORT", "MISI_PENGAWAL_BAHASA_Hotel_Hijau_1080p.mp4")
        venc = ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-profile:v", "high", "-level", "4.1",
                "-maxrate", "8M", "-bufsize", "16M"]
    cmd = ["ffmpeg", "-v", "error", "-stats", "-y"] + inputs + ["-filter_complex_script", os.path.join(ROOT, "07_PROJECT_FILES", "final_filtergraph.txt"),
           "-map", "[vout]", "-map", "[aout]", "-r", "30", "-frames:v", str(TOTAL_FRAMES)] + venc + \
          ["-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print("final ->", out)


# ------------------------------------------------------------------
# Sari kata (SRT): HANYA dialog yang dapat dikenal pasti dengan yakin
# (transkripsi Whisper 'medium' + semakan manual). Nama murid tidak dipaparkan.
# (sumber, mula, tamat, teks) — masa dalam fail sumber
# ------------------------------------------------------------------
SUBS = [
    ("v2", 4.7 + 2.4, 4.7 + 4.9, "Baiklah, assalamualaikum semua."),
    ("v2", 4.7 + 5.0, 4.7 + 7.4, "Waalaikumussalam."),
    ("v2", 4.7 + 17.0, 4.7 + 22.4, "Misi hari ini, menjadi Pengawal Bahasa."),
    ("v2", 4.7 + 27.6, 4.7 + 31.0, "Dan kalian semua akan menjadi Pengawal Bahasa."),
    ("v2", 4.7 + 31.2, 4.7 + 36.0, "Jadi, bila Cikgu sebut \"Pengawal Bahasa\",\nkamu kena sebut \"Sedia, cikgu!\""),
    ("v2", 4.7 + 36.4, 4.7 + 37.4, "Boleh."),
    ("v1", 1755 + 6.5, 1755 + 14.0, "Jadi, sekarang, tadi awak semua dah belajar\ntentang ayat aktif dengan ayat pasif, kan?"),
    ("v1", 1755 + 14.5, 1755 + 15.4, "Ya."),
    ("v3", 7.9, 11.9, "Saya mempelajari tajuk ayat aktif dan pasif."),
    ("v3", 12.2, 14.9, "Okey, boleh ke … pasifkan ayat tersebut?"),
    ("v3", 15.7, 23.0, "Kalau dipasifkan, ayatnya akan menjadi:\nTajuk ayat aktif dan pasif saya pelajari."),
    ("v3", 23.4, 24.7, "Betulkah, kelas?"),
    ("v3", 25.1, 26.1, "Betul!"),
]

def v2_to_v1(t):
    for seg, (s0, s1, off) in SYNC.items():
        if s0 <= t < s1: return off + (t - s0)
    raise ValueError(t)

def do_subs():
    build_edl()
    def to_final(src, t):
        if src == "v3":
            c = next(c for c in clips if c["src"] == "v3"); return c["t_final"] + (t - c["start"])
        return t_of_v1(v2_to_v1(t) if src == "v2" else t)
    def ts(x):
        ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    out = os.path.join(ROOT, "06_SUBTITLES", "MISI_PENGAWAL_BAHASA_Hotel_Hijau.ms.srt")
    with open(out, "w", encoding="utf-8") as f:
        for i, (src, a, b, txt) in enumerate(SUBS, 1):
            fa, fb = to_final(src, a), to_final(src, b)
            f.write(f"{i}\n{ts(fa)} --> {ts(fb)}\n{txt}\n\n")
    print("srt ->", out)

def do_edl():
    build_edl()
    path = os.path.join(ROOT, "07_PROJECT_FILES", "edl.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["#", "masa_akhir_mula", "masa_akhir_tamat", "sumber", "masa_sumber_mula", "tempoh_s", "bingkai", "framing", "audio", "babak", "nota"])
        for i, c in enumerate(clips):
            t0 = c["t_final"]; d = c["frames"] / FPS
            fmt = lambda s: f"{int(s // 60):02d}:{s % 60:06.3f}"
            name = {"v1": "vid sintaksis 1.MOV", "v2": "vid sintaksis 2.MOV", "v3": "vid3.mp4"}[c["src"]]
            w.writerow([i, fmt(t0), fmt(t0 + d), name, fmt(c["start"]), f"{d:.3f}", c["frames"], c["frame"], c["audio"], c["tag"], c["label"]])
    json.dump({k: round(v, 3) for k, v in markers.items()}, open(os.path.join(ROOT, "07_PROJECT_FILES", "markers.json"), "w"), indent=1)
    print(path, len(clips), "klip;", {k: f"{int(v // 60):02d}:{v % 60:05.2f}" for k, v in markers.items()})

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    step = sys.argv[1] if len(sys.argv) > 1 else "edl"
    {"clips": lambda: do_clips("--force" in sys.argv), "rough": do_rough, "final": lambda: do_final("--preview" in sys.argv),
     "edl": do_edl, "subs": do_subs}[step]()
