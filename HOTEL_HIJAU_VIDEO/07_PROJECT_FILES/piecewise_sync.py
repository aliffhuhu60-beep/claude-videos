#!/usr/bin/env python3
"""Penyelarasan cebisan demi cebisan vid2 -> vid1.
vid2 ialah kompilasi yang telah dipotong (banyak potongan dalaman), jadi satu offset bagi setiap segmen tidak tepat.
Setiap tetingkap 4 s (langkah 1 s) vid2 dipadankan dengan sampul tenaga ucapan vid1 (korelasi FFT ternormal),
kemudian tetingkap berturutan yang offsetnya sama digabungkan menjadi cebisan berterusan.
Usage: piecewise_sync.py v1_16k.wav v2_16k.wav v2_cuts.txt out.csv
(v2_cuts.txt: masa potongan babak vid2 daripada ffmpeg scdet)"""
import sys, wave, csv, numpy as np
def load(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
    return x[: len(x) // 2 * 2].reshape(-1, 2).mean(1)
SR = 8000; FR = 50
def env(x):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < 250) | (f > 3000)] = 0; y = np.fft.irfft(X, len(x))
    h = SR // FR; e = np.log(np.add.reduceat(y ** 2, np.arange(0, len(y) - h, h)) + 1e3); return (e - e.mean()) / e.std()
EA = env(load(sys.argv[1])); EB = env(load(sys.argv[2]))
L = 4 * FR; N = 1 << int(np.ceil(np.log2(len(EA) + L)))
FA = np.fft.rfft(EA, N); cs = np.concatenate([[0], np.cumsum(EA)]); cs2 = np.concatenate([[0], np.cumsum(EA ** 2)])
def best(w):
    L = len(w); w = w - w.mean(); nw = np.linalg.norm(w)
    if nw < 1e-6 or L < 2 * FR: return None
    N = 1 << int(np.ceil(np.log2(len(EA) + L)))
    c = np.fft.irfft(np.fft.rfft(EA, N) * np.conj(np.fft.rfft(w, N)), N)[: len(EA) - L]
    s = cs[L:len(EA)] - cs[:len(EA) - L]; s2 = cs2[L:len(EA)] - cs2[:len(EA) - L]
    r = c / (np.sqrt(np.maximum(s2 - s * s / L, 1e-9))[: len(c)] * nw); j = int(np.argmax(r))
    m = r.copy(); m[max(0, j - FR):j + FR] = -1
    return j / FR, float(r[j]), float(m.max())
cuts = [0.0] + [float(x) for x in open(sys.argv[3]).read().split()] + [len(EB) / FR]
with open(sys.argv[4], "w", newline="") as f:
    wr = csv.writer(f); wr.writerow(["seg", "v2_start", "v2_end", "v1_offset", "r", "r2", "consistency"])
    for k in range(len(cuts) - 1):
        a, b = cuts[k] + 0.1, cuts[k + 1] - 0.1
        if b - a < 2.0: continue
        res = best(EB[int(a * FR):int(b * FR)])  # seluruh babak sebagai satu tetingkap
        if res is None: continue
        v1a, r, r2 = res
        # semakan konsistensi: tetingkap 4 s dalam babak harus memberi offset yang sama
        offs = [bb[0] - t for t in np.arange(a, b - 4, 2.0) if (bb := best(EB[int(t * FR):int((t + 4) * FR)])) and bb[1] > 0.5]
        cons = float(np.mean([abs(o - (v1a - a)) < 0.15 for o in offs])) if offs else float("nan")
        wr.writerow([k, round(cuts[k], 3), round(cuts[k + 1], 3), round(v1a - (a - cuts[k]), 3), round(r, 3), round(r2, 3), round(cons, 2)])
print("ok")
