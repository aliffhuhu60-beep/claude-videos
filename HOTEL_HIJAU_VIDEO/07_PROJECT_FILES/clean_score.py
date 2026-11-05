"""Tukar hasil pengesanan (det_v1.jsonl) kepada skor per saat:
  occl  = 1 jika ada orang berdiri/lalu dekat kamera (kotak tinggi > 45% bingkai, kepala di atas 40%)
  crowd = bilangan purata orang berdiri di tengah kelas (selain murid duduk) — cth. jurukamera
Output: clean_v1.json {t: [occl, crowd]}  + jadual ringkas per 10 s.
Usage: clean_score.py det_v1.jsonl clean_v1.json"""
import json, sys, collections
per = collections.defaultdict(lambda: [0, 0.0, 0])
for line in open(sys.argv[1]):
    d = json.loads(line); s = int(d["t"]); occ = 0; st = 0
    for x0, y0, x1, y1, c in d["b"]:
        h = y1 - y0; w = x1 - x0
        if (h > 0.45 and y0 < 0.40) or w > 0.30 or (y1 > 0.98 and h > 0.5): occ = 1
        elif y0 < 0.40 and 0.18 < h <= 0.45 and c > 0.35: st += 1
    p = per[s]; p[0] = max(p[0], occ); p[1] += st; p[2] += 1
out = {s: [v[0], round(v[1] / v[2], 2)] for s, v in sorted(per.items())}
json.dump(out, open(sys.argv[2], "w"))
for s0 in range(0, max(out) + 1, 10):
    occ = sum(out.get(s, [0, 0])[0] for s in range(s0, s0 + 10)); cr = sum(out.get(s, [0, 0])[1] for s in range(s0, s0 + 10)) / 10
    print(f"{s0 // 60:02d}:{s0 % 60:02d} occl={occ:2d} crowd={cr:.1f} " + "#" * occ + "." * int(round(cr * 3)))
