"""Frame compositor: two-camera shots + crops/zoom, split layout, graphics, inserts. Writes one chunk with burnt subtitles."""
import json, subprocess, sys, os, numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, '/home/user/work')
W, H, FPS = 1920, 1080, 30
WK = '/home/user/work'
P = json.load(open(f'{WK}/out/plan.json'))
from plan import CROPS
CAM_B_OFFSET = 20.42
SRC = {'A': f'{WK}/src/raw1.mp4', 'B': f'{WK}/src/cam2.mov'}
G = f'{WK}/out/gfx'

def ease(t): t = min(1, max(0, t)); return 4*t*t*t if t < .5 else 1 - (-2*t+2)**3/2

class Reader:
    def __init__(self, path, start, scale=None, nframes=None):
        vf = 'fps=30' + (f',scale={scale}' if scale else '')
        self.w, self.h = (W, H) if not scale else tuple(int(x) for x in scale.split(':'))
        cmd = ['ffmpeg', '-v', 'error', '-ss', f'{max(0, start):.4f}', '-i', path, '-vf', vf, '-an']
        if nframes: cmd += ['-frames:v', str(nframes)]
        cmd += ['-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=10**8)
        self.n = self.w*self.h*3; self.last = None
    def read(self):
        b = self.p.stdout.read(self.n)
        if len(b) == self.n: self.last = np.frombuffer(b, np.uint8).reshape(self.h, self.w, 3)
        return self.last
    def close(self):
        try: self.p.stdout.close(); self.p.kill(); self.p.wait()
        except Exception: pass

def fr(t): return int(round(t*FPS))
NF = fr(P['total'])
shots = [dict(s, f0=fr(s['out0']), f1=fr(s['out1'])) for s in P['shots']]
segs = [dict(s, f0=fr(s['out0']), f1=fr(s['out1'])) for s in P['segments']]
talk_segs = {}
for p in P['talk']:
    a, b = talk_segs.get(p['seg'], (1e9, -1)); talk_segs[p['seg']] = (min(a, p['out0']), max(b, p['out1']))
panels = [dict(p, f0=fr(p['out0']), n=fr(p['dur'])) for p in P['panels']]
for i, p in enumerate(panels): p['dir'] = f'{G}/panel_{i:02d}'
ovs = [dict(o, f0=fr(o['out0']), n=fr(o['dur'])) for o in P['overlays']]
for i, o in enumerate(ovs): o['dir'] = f'{G}/ov_{i:02d}'
split = P['split']; TR = 0.5
def split_amount(t):
    for a, b in split:
        if a - TR <= t <= b + 0.15:
            if t < a: return (t - (a - TR)) / TR
            if t > b - 0.35: return 1 - (t - (b - 0.35)) / TR
            return 1.0
    return 0.0

BUG = Image.open(f'{G}/bug/00000.png').convert('RGBA')
SPLITBG = Image.open(f'{G}/splitbg/00000.png').convert('RGB')
SR = (50, 150, 1100, 619)
shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(shadow)
d.rounded_rectangle((SR[0], SR[1]+12, SR[0]+SR[2], SR[1]+SR[3]+12), 26, fill=(0, 0, 0, 150))
shadow = shadow.filter(ImageFilter.GaussianBlur(22))
border = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(border).rounded_rectangle((SR[0]-2, SR[1]-2, SR[0]+SR[2]+1, SR[1]+SR[3]+1), 26, outline=(247, 237, 224, 150), width=2)
mask_cache = {}
def rmask(w, h, r):
    k = (w, h, r)
    if k not in mask_cache:
        m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w-1, h-1), r, fill=255)
        if len(mask_cache) > 200: mask_cache.clear()
        mask_cache[k] = m
    return mask_cache[k]

def png(dirp, i):
    p = f'{dirp}/{i:05d}.png'
    return Image.open(p).convert('RGBA') if os.path.exists(p) else None

def shot_frame(arr, s, f):
    cam, x0, y0, w = CROPS[s['crop']]
    h = w*9/16
    if s['zoom']:
        u = (f - s['f0']) / max(1, s['f1'] - s['f0'])
        z = 1 + 0.045*ease(u)
        cx, cy = x0 + w/2, y0 + h*0.42
        w, h = w/z, h/z
        x0, y0 = cx - w/2, cy - h*0.42
    x0 = min(max(0, x0), W - w); y0 = min(max(0, y0), H - h)
    im = Image.fromarray(arr)
    if w >= W - 0.5 and not s['zoom']: return im
    return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))

def compose_split(base, e):
    x = SR[0]*e; y = SR[1]*e; w = W + (SR[2]-W)*e; h = H + (SR[3]-H)*e
    wi, hi = int(round(w)), int(round(h))
    canvas = SPLITBG.copy().convert('RGBA')
    if e > 0.05:
        sh = shadow.copy(); sh.putalpha(sh.getchannel('A').point(lambda v: int(v*e))); canvas.alpha_composite(sh)
    small = base.resize((wi, hi), Image.BILINEAR if e < 0.999 else Image.LANCZOS)
    canvas.paste(small, (int(round(x)), int(round(y))), rmask(wi, hi, int(26*e)))
    if e > 0.999: canvas.alpha_composite(border)
    return canvas

def main(fa, fb, out):
    start = fa / FPS
    vf = f"setpts=PTS+{start:.6f}/TB,ass={WK}/out/Podcast_Subtitles.ass:fontsdir={WK}/fonts,setpts=PTS-STARTPTS"
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-framerate', '30', '-i', '-',
                            '-vf', vf, '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-g', '60',
                            '-threads', '2', out], stdin=subprocess.PIPE, bufsize=10**8)
    reader = None; rkey = None
    azan_frames = None
    for f in range(fa, fb):
        t = f / FPS
        seg = next((s for s in segs if s['f0'] <= f < s['f1']), None)
        if seg is not None:
            kind = seg['kind']; lf = f - seg['f0']
            if kind in ('opening', 'axia'):
                key = (kind,)
                if rkey != key:
                    if reader: reader.close()
                    reader = Reader(f'{WK}/out/{kind}_v.mp4', lf / FPS); rkey = key
                arr = reader.read(); img = Image.fromarray(arr) if arr is not None else Image.new('RGB', (W, H))
            elif kind == 'credits':
                im = png(f'{G}/credits', lf); img = im.convert('RGB') if im else Image.new('RGB', (W, H))
            elif kind == 'azan':
                if azan_frames is None:
                    rd = Reader(f'{WK}/src/azan.mp4', 0, scale='486:864', nframes=int(8.83*FPS)+1)
                    azan_frames = []
                    while True:
                        b = rd.p.stdout.read(486*864*3)
                        if len(b) < 486*864*3: break
                        azan_frames.append(Image.fromarray(np.frombuffer(b, np.uint8).reshape(864, 486, 3)))
                    rd.close()
                tl = lf / FPS; LEAD = 1.4
                vi = 0 if tl < LEAD else min(len(azan_frames)-1, int((tl - LEAD)*FPS))
                canvas = Image.new('RGBA', (W, H), (0, 0, 0, 255)); canvas.paste(azan_frames[vi], (1170, 110))
                bg = png(f'{G}/azan', lf)
                if bg: canvas.alpha_composite(bg)
                img = canvas.convert('RGB')
                dur = (seg['f1'] - seg['f0'])/FPS
                fade = min(1, tl/0.5, (dur - tl)/0.6)
                if fade < 1: img = Image.fromarray((np.asarray(img)*max(0, fade)).astype(np.uint8))
            enc.stdin.write(img.tobytes()); continue
        # ---------------- talk ----------------
        s = next((s for s in shots if s['f0'] <= f < s['f1']), None)
        if s is None: s = min(shots, key=lambda x: abs(x['f0'] - f))
        key = ('shot', s['f0'])
        if rkey != key:
            if reader: reader.close()
            src_t = s['src0'] + (f - s['f0'])/FPS
            if s['cam'] == 'B': src_t -= CAM_B_OFFSET
            reader = Reader(SRC[s['cam']], src_t); rkey = key
        arr = reader.read()
        base = shot_frame(arr, s, f)
        sp = split_amount(t)
        e = ease(sp)
        canvas = compose_split(base, e) if e > 0.001 else base.convert('RGBA')
        for p in panels:
            if p['f0'] <= f < p['f0'] + p['n']:
                im = png(p['dir'], f - p['f0'])
                if im: canvas.alpha_composite(im)
        for o in ovs:
            if o['f0'] <= f < o['f0'] + o['n']:
                im = png(o['dir'], f - o['f0'])
                if im: canvas.alpha_composite(im)
        canvas.alpha_composite(BUG)
        img = canvas.convert('RGB')
        # dips at talk-segment boundaries
        fade = 1.0
        for name, (a, b) in talk_segs.items():
            if a - 0.01 <= t < b + 0.01:
                din = 0.5 if name == 'intro' else 0.3
                fade = min(1, (t - a)/din + 1/FPS, (b - t)/0.3)
        if fade < 1: img = Image.fromarray((np.asarray(img)*max(0, fade)).astype(np.uint8))
        enc.stdin.write(img.tobytes())
        if f % 300 == 0: print(out, f, '/', fb, flush=True)
    if reader: reader.close()
    enc.stdin.close(); enc.wait()
    print('done', out, flush=True)

if __name__ == '__main__':
    fa, fb, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    main(fa, min(fb, NF), out)
