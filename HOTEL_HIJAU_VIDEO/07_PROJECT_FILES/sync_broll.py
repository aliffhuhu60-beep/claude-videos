"""Cari kedudukan setiap klip B-roll (vid sintaksis 2) dalam rakaman induk (vid sintaksis 1)
menggunakan korelasi silang audio. Output: 07_PROJECT_FILES/broll_sync.csv
Usage: python3 sync_broll.py <v1.wav 16k> <v2.wav 16k> <cuts.txt> <out.csv>
"""
import sys, wave, numpy as np, csv
def load(p, sr_out=2000):
    w = wave.open(p); sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
    f = sr // sr_out
    x = x[: len(x) // f * f].reshape(-1, f).mean(1)          # downsample (box)
    return x, sr_out
def env(x, sr, hop=20):
    # log-energy envelope at sr/hop Hz, high-pass in time -> robust to gain differences
    n = len(x) // hop * hop
    e = np.log(np.square(x[:n]).reshape(-1, hop).mean(1) + 1e-3)
    k = 50
    e = e - np.convolve(e, np.ones(k) / k, 'same')
    return e
a, sr = load(sys.argv[1]); b, _ = load(sys.argv[2])
ea, eb = env(a, sr), env(b, sr)
R = sr / 20  # envelope rate (100 Hz)
cuts = [float(c) for c in open(sys.argv[3]).read().split()]
N = 1 << int(np.ceil(np.log2(len(ea) * 2)))
FA = np.fft.rfft(ea, N)
csq = np.concatenate([[0], np.cumsum(ea ** 2)])
rows = []
for i in range(len(cuts) - 1):
    s, e = cuts[i], cuts[i + 1]
    if e - s < 2.5:
        rows.append([i, s, e, '', '', '']); continue
    seg = eb[int(s * R): int(e * R)]
    seg = seg - seg.mean(); L = len(seg)
    c = np.fft.irfft(FA * np.conj(np.fft.rfft(seg, N)), N)[: len(ea) - L]
    energy = np.sqrt(csq[L:len(ea)] - csq[:len(ea) - L] + 1e-6)[: len(c)]
    ncc = c / (energy * np.linalg.norm(seg) + 1e-6)
    j = int(np.argmax(ncc)); score = float(ncc[j])
    # second best (outside +-3s) to measure confidence
    m = ncc.copy(); m[max(0, j - 300): j + 300] = -1
    rows.append([i, s, e, round(j / R, 2), round(score, 3), round(score - float(m.max()), 3)])
    print(rows[-1], flush=True)
with open(sys.argv[4], 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['seg', 'v2_start', 'v2_end', 'v1_offset', 'ncc', 'margin']); w.writerows(rows)
