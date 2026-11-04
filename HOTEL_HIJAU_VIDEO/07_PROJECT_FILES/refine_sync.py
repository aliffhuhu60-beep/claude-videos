"""Perhalusi offset B-roll (ketepatan ~1 ms) dengan korelasi silang audio 8 kHz di sekitar
anggaran kasar. Usage: refine_sync.py v1.wav v2.wav broll_sync.csv out.csv [v3.wav]"""
import sys, wave, csv, numpy as np
def load(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
    x = x[: len(x) // 2 * 2].reshape(-1, 2).mean(1)  # 16k -> 8k
    return x
def bp(x):  # emphasise speech band
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / 8000)
    X[(f < 200) | (f > 3500)] = 0; return np.fft.irfft(X, len(x))
SR = 8000
a = load(sys.argv[1]); b = load(sys.argv[2])
def refine(seg, guess, search=1.5):
    s0 = int((guess - search) * SR); s0 = max(0, s0)
    ref = bp(a[s0: s0 + len(seg) + int(2 * search * SR)])
    seg = bp(seg); n = len(ref) + len(seg); N = 1 << int(np.ceil(np.log2(n)))
    c = np.fft.irfft(np.fft.rfft(ref, N) * np.conj(np.fft.rfft(seg, N)), N)[: len(ref) - len(seg)]
    cs = np.concatenate([[0], np.cumsum(ref ** 2)])
    en = np.sqrt(cs[len(seg):len(ref)] - cs[:len(ref) - len(seg)] + 1e-9)[: len(c)]
    ncc = c / (en * np.linalg.norm(seg) + 1e-9); j = int(np.argmax(ncc))
    return (s0 + j) / SR, float(ncc[j])
rows = list(csv.DictReader(open(sys.argv[3])))
out = []
for r in rows:
    if not r["v1_offset"]: continue
    s, e, g = float(r["v2_start"]), float(r["v2_end"]), float(r["v1_offset"])
    seg = b[int(s * SR): int(e * SR)]
    off, sc = refine(seg, g)
    out.append(dict(seg=r["seg"], v2_start=s, v2_end=e, v1_offset=round(off, 3), ncc=round(sc, 3), coarse_margin=r["margin"]))
    print(out[-1], flush=True)
with open(sys.argv[4], "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
