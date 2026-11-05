"""Pengesanan orang (YOLOv8n ONNX) pada rakaman induk untuk mencari:
  - orang lalu/berdiri dekat kamera (oklusi)
  - orang berdiri di dalam kelas selain guru (cth. jurukamera)
Usage: detect.py <model.onnx> <video> <out.jsonl> [fps] [start] [dur]"""
import sys, json, subprocess, numpy as np, onnxruntime as ort
model, video, out = sys.argv[1:4]
fps = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0
ss = sys.argv[5] if len(sys.argv) > 5 else "0"
dur = sys.argv[6] if len(sys.argv) > 6 else None
W, H = 854, 480
sess = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
cmd = ["ffmpeg", "-v", "error", "-ss", ss] + (["-t", dur] if dur else []) + ["-i", video, "-vf", f"fps={fps},scale={W}:{H}",
       "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
S = 640 / W; nh = int(H * S); pad = (640 - nh) // 2
f = open(out, "w"); i = 0
while True:
    buf = p.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    import cv2
    x = cv2.resize(img, (640, nh), interpolation=cv2.INTER_AREA)
    canvas = np.full((640, 640, 3), 114, np.uint8); canvas[pad:pad + nh] = x
    inp = canvas.transpose(2, 0, 1)[None].astype(np.float32) / 255.0
    pr = sess.run(None, {"images": inp})[0][0]          # (84, 8400)
    conf = pr[4]; keep = conf > 0.30
    b = pr[:4, keep].T; c = conf[keep]
    boxes = []
    if len(c):
        xy = np.stack([b[:, 0] - b[:, 2] / 2, b[:, 1] - b[:, 3] / 2, b[:, 0] + b[:, 2] / 2, b[:, 1] + b[:, 3] / 2], 1)
        xy[:, [1, 3]] -= pad; xy /= 640  # normalised to width (x) ; y in units of width
        xy[:, [1, 3]] *= 640 / nh        # y normalised to height
        idx = cv2.dnn.NMSBoxes(xy[:, :4].tolist(), c.tolist(), 0.30, 0.5)
        for k in np.array(idx).flatten():
            boxes.append([round(float(v), 3) for v in xy[k]] + [round(float(c[k]), 2)])
    t = float(ss) + i / fps
    f.write(json.dumps({"t": round(t, 2), "b": boxes}) + "\n"); i += 1
f.close(); print("frames", i)
