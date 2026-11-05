"""Ukur ketajaman (varians Laplacian) & goyangan per 0.5 s bagi video B-roll.
Usage: sharpness.py <video> <out.jsonl>"""
import sys, json, subprocess, numpy as np, cv2
v, out = sys.argv[1:3]; W, H = 640, 360; fps = 2
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", v, "-vf", f"fps={fps},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
f = open(out, "w"); prev = None; i = 0
while True:
    b = p.stdout.read(W * H)
    if len(b) < W * H: break
    g = np.frombuffer(b, np.uint8).reshape(H, W)
    sh = float(cv2.Laplacian(g, cv2.CV_64F).var())
    mot = float(np.abs(g.astype(np.int16) - prev).mean()) if prev is not None else 0.0
    prev = g.astype(np.int16)
    f.write(json.dumps({"t": i / fps, "sharp": round(sh, 1), "motion": round(mot, 2)}) + "\n"); i += 1
print("frames", i)
