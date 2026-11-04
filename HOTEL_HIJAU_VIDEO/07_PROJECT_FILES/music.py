"""Penjana muzik instrumental & kesan bunyi ASLI (prosedur, numpy) — bebas hak cipta.
Semua bunyi disintesis dari awal; tiada sampel luar digunakan.

Output (48 kHz, stereo, WAV 16-bit) ke 02_AUDIO/:
  mus_opening.wav      Cinematic orchestral-style swell (pembukaan)
  mus_intro.wav        Corporate inspirational (pengenalan guru / set induksi)
  mus_upbeat.wav       Upbeat educational (aktiviti kumpulan / misi)
  mus_tech.wav         Modern technology ambient (aktiviti AR)
  mus_motiv.wav        Soft motivational (semakan jawapan)
  mus_piano.wav        Gentle piano (refleksi)
  mus_closing.wav      Inspirational cinematic (penutup & penghargaan)
  sfx_whoosh.wav, sfx_reveal.wav, sfx_impact.wav

Usage: python3 music.py <out_dir> [durations...]
"""
import numpy as np, wave, os, sys

SR = 48000
rng = np.random.default_rng(7)

def midi(n): return 440.0 * 2 ** ((n - 69) / 12)

def env_adsr(n, a, d, s, r, sr=SR):
    a, d, r = int(a * sr), int(d * sr), int(r * sr)
    e = np.full(n, s, np.float32)
    a = min(a, n); e[:a] = np.linspace(0, 1, a)
    d2 = min(d, n - a); e[a:a + d2] = np.linspace(1, s, d2)
    if r > 0: e[-min(r, n):] *= np.linspace(1, 0, min(r, n))
    return e

def piano(f, dur, vel=0.6):
    n = int(dur * SR); t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    for k, amp in enumerate([1, .55, .32, .2, .12, .07, .04], 1):
        fk = f * k * np.sqrt(1 + 0.0004 * k * k)
        if fk > 16000: break
        dec = np.exp(-t * (1.2 + 0.9 * k) * (f / 440) ** 0.3)
        out += amp * np.sin(2 * np.pi * fk * t + rng.random() * 6) * dec
    att = np.minimum(1, t / 0.004)
    rel = np.ones(n); rr = int(0.25 * SR); rel[-rr:] = np.linspace(1, 0, rr)
    return (out * att * rel * vel * 0.35).astype(np.float32)

def pad(freqs, dur, bright=0.5, attack=1.5, release=2.0):
    n = int(dur * SR); t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    for f in freqs:
        for det in (-0.07, 0, 0.07):
            ff = f * 2 ** (det / 12)
            for k in range(1, 8):
                amp = (1 / k) * (bright ** (k - 1))
                out += amp * np.sin(2 * np.pi * ff * k * t + rng.random() * 6)
    lfo = 1 + 0.15 * np.sin(2 * np.pi * 0.2 * t)
    e = env_adsr(n, attack, 0.5, 0.85, release)
    return (out * e * lfo / (len(freqs) * 3 * 2.2)).astype(np.float32)

def mallet(f, dur=0.6, vel=0.5):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + 0.3 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 18)
    return (s * np.minimum(1, t / 0.002) * vel * 0.4).astype(np.float32)

def kick(vel=0.6):
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 50 + 70 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * 9) * vel).astype(np.float32)

def shaker(vel=0.15):
    n = int(0.08 * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n); x = np.diff(np.concatenate([[0], x]))
    return (x * np.exp(-t * 60) * vel * 0.5).astype(np.float32)

def timpani(f=55, vel=0.8):
    n = int(3.0 * SR); t = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * dcy) for a, m, dcy in [(1, 1, 1.5), (.5, 1.5, 2.5), (.3, 1.98, 3.5)])
    nz = rng.standard_normal(n) * np.exp(-t * 40) * 0.2
    return ((s + nz) * vel * 0.5).astype(np.float32)

def add(buf, x, pos, pan=0.0):
    i = int(pos * SR)
    if i >= len(buf): return
    x = x[: len(buf) - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(x), 0] += x * l * 1.414 / 2 * 2 ** 0.5
    buf[i:i + len(x), 1] += x * r * 1.414 / 2 * 2 ** 0.5

def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    # one-pole IIR via cumulative trick (vectorised approx by FFT)
    X = np.fft.rfft(x, axis=0); fr = np.fft.rfftfreq(len(x), 1 / SR)
    H = 1 / np.sqrt(1 + (fr / fc) ** 2)
    return np.fft.irfft(X * H[:, None] if x.ndim == 2 else X * H, len(x), axis=0).astype(np.float32)

def reverb(buf, size=2.6, mix=0.28):
    n = int(size * SR); t = np.arange(n) / SR
    ir = np.stack([rng.standard_normal(n) * np.exp(-t * 6.9 / size) for _ in range(2)], 1)
    ir = lowpass(ir, 6000); ir[: int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))[:, None]
    ir /= np.sqrt((ir ** 2).sum(0))
    L = len(buf) + n; N = 1 << int(np.ceil(np.log2(L)))
    wet = np.fft.irfft(np.fft.rfft(buf, N, axis=0) * np.fft.rfft(ir, N, axis=0), N, axis=0)[: len(buf)]
    return (buf * (1 - mix) + wet * mix * 2.0).astype(np.float32)

def finish(buf, fade_in=1.0, fade_out=3.0, peak_db=-3.0):
    buf = reverb(buf)
    n = len(buf)
    fi, fo = int(fade_in * SR), int(fade_out * SR)
    if fi: buf[:fi] *= np.linspace(0, 1, fi)[:, None]
    if fo: buf[-fo:] *= np.linspace(1, 0, fo)[:, None]
    buf = np.tanh(buf * 1.2) / np.tanh(1.2)  # soft limiter
    pk = np.abs(buf).max() + 1e-9
    return buf * (10 ** (peak_db / 20) / pk)

def write(path, buf):
    x = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(x.tobytes())

# Progresi akord (D major): I - V - vi - IV  /  vi - IV - I - V
CH = {"D": [62, 66, 69], "A": [61, 64, 69], "Bm": [59, 62, 66], "G": [59, 62, 67],
      "Em": [59, 64, 67], "F#m": [61, 66, 69]}
PROG1 = ["D", "A", "Bm", "G"]
PROG2 = ["Bm", "G", "D", "A"]
ROOT = {"D": 50, "A": 45, "Bm": 47, "G": 43, "Em": 40, "F#m": 42}

def track_pad_piano(dur, bpm, prog, arp=True, drums=False, mallets=False, bright=0.45, piano_vel=0.45, sparse=False):
    buf = np.zeros((int((dur + 4) * SR), 2), np.float32)
    beat = 60 / bpm; bar = beat * 4
    nb = int(np.ceil(dur / bar))
    for b in range(nb):
        c = prog[b % len(prog)]; t0 = b * bar
        add(buf, pad([midi(n - 12) for n in CH[c]] + [midi(ROOT[c])], bar + 1.5, bright, 0.8, 1.2) * 0.9, t0)
        if arp:
            notes = CH[c] + [CH[c][0] + 12]
            pattern = [0, 1, 2, 3, 2, 1, 0, 2] if not sparse else [0, 2, 3, 1]
            step = bar / len(pattern)
            for i, k in enumerate(pattern):
                v = piano_vel * (1.0 if i % 2 == 0 else 0.75)
                add(buf, piano(midi(notes[k] + 12), 1.8, v), t0 + i * step, pan=-0.3 + 0.6 * (i % 2))
        if mallets:
            for i in range(8):
                if i in (0, 3, 6):
                    add(buf, mallet(midi(CH[c][i % 3] + 24), 0.5, 0.35), t0 + i * beat / 2, pan=0.4)
        if drums:
            for i in range(4):
                add(buf, kick(0.45), t0 + i * beat)
            for i in range(8):
                add(buf, shaker(0.07 if i % 2 else 0.04), t0 + i * beat / 2, pan=0.5)
        add(buf, piano(midi(ROOT[c]), bar, 0.35), t0)  # bass note
    return buf[: int(dur * SR)]

def tech_ambient(dur):
    buf = np.zeros((int((dur + 4) * SR), 2), np.float32)
    bpm = 96; s16 = 60 / bpm / 4; bar = 16 * s16
    prog = ["Bm", "G", "D", "A"]
    for b in range(int(np.ceil(dur / bar))):
        c = prog[b % 4]; t0 = b * bar
        add(buf, pad([midi(n - 12) for n in CH[c]], bar + 2, 0.25, 1.5, 2) * 0.9, t0)
        seq = [0, 2, 1, 2, 0, 2, 1, 2, 0, 2, 1, 2, 0, 2, 1, 2]
        for i, k in enumerate(seq):
            f = midi(CH[c][k] + 24 + (12 if i % 8 == 7 else 0))
            n = int(0.25 * SR); tt = np.arange(n) / SR
            x = (np.sin(2 * np.pi * f * tt) * np.exp(-tt * 14) * 0.18).astype(np.float32)
            add(buf, x, t0 + i * s16, pan=0.6 * np.sin(i))
            add(buf, x * 0.35, t0 + i * s16 + 3 * s16 / 2, pan=-0.6 * np.sin(i))  # delay
        for i in range(4):
            add(buf, kick(0.25), t0 + i * 4 * s16)
    return buf[: int(dur * SR)]

def opening(dur=40.0):
    buf = np.zeros((int((dur + 4) * SR), 2), np.float32)
    # swell strings
    seq = [("Bm", 0), ("G", 6), ("D", 12), ("A", 18), ("Bm", 24), ("G", 30), ("D", 34)]
    for i, (c, t0) in enumerate(seq):
        ln = (seq[i + 1][1] - t0 + 2.5) if i + 1 < len(seq) else dur - t0
        br = 0.35 + 0.1 * min(i, 4)
        add(buf, pad([midi(n - 12) for n in CH[c]] + [midi(n) for n in CH[c]] + [midi(ROOT[c] - 12)], ln, br, 2.5, 2.5) * (0.6 + 0.12 * i), t0)
    # timpani hits on title reveal
    add(buf, timpani(46.25, 0.9), 0.2); add(buf, timpani(46.25, 1.0), 12.0); add(buf, timpani(41.2, 0.8), 24.0)
    # piano melody (sederhana, asli)
    mel = [(74, 12.5), (73, 13.5), (71, 14.5), (69, 16.0), (71, 18.5), (73, 19.5), (74, 20.5), (78, 22.0),
           (76, 24.5), (74, 25.5), (73, 26.5), (71, 28.0), (74, 30.5), (73, 31.5), (69, 32.5), (74, 34.0)]
    for n, t0 in mel:
        add(buf, piano(midi(n), 3.0, 0.55), t0, pan=0.15)
    return buf[: int(dur * SR)]

def closing(dur):
    buf = track_pad_piano(dur, 72, ["G", "A", "Bm", "D", "G", "A", "D", "D"], arp=True, bright=0.5, piano_vel=0.45, sparse=True)
    mel = [74, 76, 78, 81, 78, 76, 74, 73]
    bar = 60 / 72 * 4
    for b in range(int(dur / bar)):
        if b >= 2:
            add(buf, piano(midi(mel[b % 8]), bar * 0.9, 0.5), b * bar + 0.02, pan=0.1)
    return buf

def sfx_whoosh(d=1.4):
    n = int(d * SR); t = np.arange(n) / SR
    x = rng.standard_normal((n, 2)).astype(np.float32)
    # sweep band: emulate with FFT-based time-varying filter in chunks
    out = np.zeros_like(x); ch = 2048
    for i in range(0, n, ch):
        p = i / n; fc = 300 + 5000 * np.sin(np.pi * p) ** 2
        seg = x[i:i + ch]; out[i:i + ch] = lowpass(seg, fc)
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    pan = np.linspace(-0.8, 0.8, n)
    out[:, 0] *= e * (1 - pan) / 2; out[:, 1] *= e * (1 + pan) / 2
    return out / (np.abs(out).max() + 1e-9) * 0.5

def sfx_reveal(d=2.0):
    buf = np.zeros((int(d * SR), 2), np.float32)
    for i, n in enumerate([81, 86, 88, 93]):
        add(buf, mallet(midi(n), 1.2, 0.35), 0.06 * i, pan=-0.4 + 0.27 * i)
    sh = sfx_whoosh(0.6) * 0.25; buf[: len(sh)] += sh
    return reverb(buf, 1.5, 0.35)

def sfx_impact(d=3.0):
    buf = np.zeros((int(d * SR), 2), np.float32)
    add(buf, timpani(41.2, 1.0), 0); add(buf, kick(0.9), 0)
    return reverb(buf, 2.5, 0.3)

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    d = dict(opening=40, intro=200, upbeat=420, tech=360, motiv=240, piano=420, closing=120)
    for a in sys.argv[2:]:
        k, v = a.split("="); d[k] = float(v)
    jobs = {
        "mus_opening": lambda: finish(opening(d["opening"]), 2.0, 4.0),
        "mus_intro": lambda: finish(track_pad_piano(d["intro"], 92, PROG1, mallets=True, bright=0.45), 2, 4),
        "mus_upbeat": lambda: finish(track_pad_piano(d["upbeat"], 112, PROG1, drums=True, mallets=True, piano_vel=0.4), 2, 4),
        "mus_tech": lambda: finish(tech_ambient(d["tech"]), 2, 4),
        "mus_motiv": lambda: finish(track_pad_piano(d["motiv"], 84, PROG2, bright=0.4, piano_vel=0.4), 2, 4),
        "mus_piano": lambda: finish(track_pad_piano(d["piano"], 66, ["G", "D", "Em", "A"], bright=0.3, piano_vel=0.42, sparse=True), 2, 5),
        "mus_closing": lambda: finish(closing(d["closing"]), 2, 6),
        "sfx_whoosh": lambda: finish(sfx_whoosh(), 0.01, 0.2, -6),
        "sfx_reveal": lambda: finish(sfx_reveal(), 0.0, 0.5, -6),
        "sfx_impact": lambda: finish(sfx_impact(), 0.0, 1.0, -4),
    }
    for k, fn in jobs.items():
        print("render", k, flush=True); write(os.path.join(out, k + ".wav"), fn())
