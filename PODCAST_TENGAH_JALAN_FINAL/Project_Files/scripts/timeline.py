"""Build the output timeline from the EDL: cut points, pause trimming, subtitle timing, shots, inserts."""
import json, wave, re, numpy as np
from edl import EDL

FPS = 30
CAM_B_OFFSET = 20.42           # cam2 time = raw1 time - offset
OPENING_DUR = 10.0
AXIA_DUR = 10.0
AZAN_SRC_END = 8.83            # muezzin shot only
AZAN_LEAD = 1.4                # title card before azan audio
AZAN_TAIL = 0.7
CREDITS_DUR = 6.0

# ---------- audio energy (10 ms) ----------
w = wave.open('/home/user/work/audio/raw1_16k.wav')
a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
HOP = 160
n = len(a) // HOP
EN = 20 * np.log10(np.sqrt((a[:n*HOP].reshape(n, HOP) ** 2).mean(1)) + 1e-9)
SIL_DB = -38.0

def en_at(t): return EN[min(n-1, max(0, int(t*100)))]

def snap_start(s):
    lo, hi = int((s-0.22)*100), int((s+0.04)*100)
    seg = EN[lo:hi]
    # latest index that is near the minimum (prefer close to s)
    m = seg.min(); idx = [i for i, v in enumerate(seg) if v <= m + 3]
    return (lo + idx[-1]) / 100

def snap_end(e):
    lo, hi = int((e-0.04)*100), int((e+0.22)*100)
    seg = EN[lo:hi]
    m = seg.min(); idx = [i for i, v in enumerate(seg) if v <= m + 3]
    return (lo + idx[0]) / 100 + 0.03

def silent_runs(s, e, min_len=0.55):
    i0, i1 = int(s*100), int(e*100)
    sil = EN[i0:i1] < SIL_DB
    runs, st = [], None
    for k, v in enumerate(sil):
        if v and st is None: st = k
        if (not v) and st is not None:
            if (k-st)/100 >= min_len: runs.append(((i0+st)/100, (i0+k)/100))
            st = None
    return runs

# ---------- whisper words ----------
WD = json.load(open('/home/user/work/audio/w_tr.json'))
WORDS = [(x[0], x[1], x[2].strip()) for sg in WD for x in sg['words']]

def q(t): return round(t * FPS) / FPS

# ---------- build ----------
items = []          # ordered list of timeline items
cur_seg = None
for e in EDL:
    if e[0] == 'SEG': cur_seg = e[1]; items.append(('SEG', e[1])); continue
    if e[0] in ('AZAN', 'AXIA', 'END'): items.append((e[0],)); continue
    s, en_, spk, txt = e
    items.append(('CLIP', cur_seg, s, en_, spk, txt))

timeline = []       # pieces: dict(kind, out0, out1, ...)
subs = []           # dict(out0, out1, text, spk, pantun)
clips_out = []      # per EDL clip: dict(spk, out0, out1, pieces)
t = 0.0
# opening ad
timeline.append(dict(kind='opening', out0=0.0, out1=OPENING_DUR)); t = OPENING_DUR
seg_starts = {}
prev_seg = None
for it in items:
    if it[0] == 'SEG':
        seg_starts[it[1]] = q(t); prev_seg = it[1]; continue
    if it[0] == 'AZAN':
        d = AZAN_LEAD + AZAN_SRC_END + AZAN_TAIL
        timeline.append(dict(kind='azan', out0=q(t), out1=q(t+d))); t = q(t+d); continue
    if it[0] == 'AXIA':
        timeline.append(dict(kind='axia', out0=q(t), out1=q(t+AXIA_DUR))); t = q(t+AXIA_DUR); continue
    if it[0] == 'END':
        timeline.append(dict(kind='credits', out0=q(t), out1=q(t+CREDITS_DUR))); t = q(t+CREDITS_DUR); continue
    _, seg, s, e, spk, txt = it
    s2, e2 = snap_start(s), snap_end(e)
    # source sub-ranges after removing long pauses
    ranges = []; cs = s2
    for (r0, r1) in silent_runs(s2 + 0.15, e2 - 0.15):
        keep = 0.30
        ranges.append((cs, r0 + keep/2)); cs = r1 - keep/2
    ranges.append((cs, e2))
    # never leave a tiny island of speech between two trimmed pauses: merge short ranges with a neighbour
    merged = True
    while merged and len(ranges) > 1:
        merged = False
        for k in range(len(ranges)):
            if ranges[k][1] - ranges[k][0] < 1.3:
                if k + 1 < len(ranges): ranges[k:k+2] = [(ranges[k][0], ranges[k+1][1])]
                else: ranges[k-1:k+1] = [(ranges[k-1][0], ranges[k][1])]
                merged = True; break
    pieces = []
    for (r0, r1) in ranges:
        r0, r1 = q(r0), q(r1)
        if r1 - r0 < 2/FPS: continue
        p = dict(kind='talk', seg=seg, spk=spk, src0=r0, src1=r1, out0=q(t), out1=q(t + (r1-r0)))
        t = p['out1']; pieces.append(p); timeline.append(p)
    # mapping src->out within this clip
    def s2o(x, pieces=pieces):
        for p in pieces:
            if x <= p['src1']: return p['out0'] + max(0.0, x - p['src0'])
        return pieces[-1]['out1']
    # subtitle chunks
    pantun = txt.startswith('PANTUN:')
    body = txt[7:] if pantun else txt
    chunks = [c.strip() for c in body.split('|') if c.strip()]
    ws = [wd for wd in WORDS if wd[0] >= s - 0.3 and wd[0] < e - 0.05]
    nw = [len(re.sub(r'[*~]', '', c).split()) for c in chunks]
    tot = sum(nw); acc = 0
    starts = []
    for k, c in enumerate(chunks):
        frac = acc / tot
        wi = min(len(ws)-1, int(round(frac * len(ws)))) if ws else 0
        st = ws[wi][0] if (ws and k > 0) else s2
        starts.append(max(st, s2)); acc += nw[k]
    for k, c in enumerate(chunks):
        a0 = starts[k]; a1 = starts[k+1] if k+1 < len(chunks) else e2
        o0, o1 = s2o(a0), s2o(a1)
        subs.append(dict(out0=round(o0, 3), out1=round(o1, 3), text=c, spk=spk, pantun=pantun, seg=seg))
    clips_out.append(dict(spk=spk, seg=seg, out0=pieces[0]['out0'], out1=pieces[-1]['out1'], pieces=pieces, src0=s2, src1=e2, text=txt))

TOTAL = t

if __name__ == '__main__':
    print('TOTAL', round(TOTAL, 2), 's =', f"{int(TOTAL//60)}:{TOTAL%60:05.2f}")
    talk = sum(p['out1']-p['out0'] for p in timeline if p['kind'] == 'talk')
    print('talk', round(talk, 1), 'pieces', sum(1 for p in timeline if p['kind'] == 'talk'), 'subs', len(subs))
    for k, v in seg_starts.items(): print(k, v)
    for p in timeline:
        if p['kind'] != 'talk': print(p)
