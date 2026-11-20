"""Shot plan, split-layout panels, overlays and subtitles (ASS + SRT) for the final render."""
import re, json, sys
sys.path.insert(0, '/home/user/work')
from timeline import timeline, subs, clips_out, seg_starts, TOTAL, FPS, q

TALK = [p for p in timeline if p['kind'] == 'talk']
def s2o(x):
    for p in TALK:
        if x < p['src0']: return p['out0']
        if x <= p['src1']: return p['out0'] + (x - p['src0'])
    return TALK[-1]['out1']

# ---------------- crop library (source pixel rects: x0, y0, w ; h = w*9/16) ----------------
CROPS = {
    'A-wide': ('A', 0, 0, 1920), 'B-wide': ('B', 0, 0, 1920),
    'B-med-AL': ('B', 0, 140, 1344), 'B-close-AL': ('B', 20, 190, 1152),
    'B-med-IM': ('B', 428, 150, 1344), 'B-close-IM': ('B', 524, 205, 1152),
    'B-med-AM': ('B', 576, 180, 1344), 'B-close-AM': ('B', 768, 235, 1152),
    'A-med-AL': ('A', 0, 20, 1344), 'A-close-AL': ('A', 0, 50, 1152),
    'A-two': ('A', 576, 20, 1344), 'A-close-AM': ('A', 740, 30, 1152),
}
ROT = {
    'AL': ['B-med-AL', 'A-med-AL', 'B-close-AL', 'A-wide', 'B-med-AL', 'A-close-AL'],
    'IM': ['B-med-IM', 'A-two', 'B-close-IM', 'B-wide', 'B-med-IM', 'A-two'],
    'AM': ['B-med-AM', 'A-two', 'B-close-AM', 'A-close-AM', 'B-med-AM', 'A-wide'],
}
SPLIT_ROT = {'AL': ['B-med-AL', 'A-med-AL'], 'IM': ['B-med-IM', 'A-two'], 'AM': ['B-med-AM', 'A-two']}

# ---------------- panels (split layout) : id, src_start, src_end, [cue src times], extra ----------------
PANELS = [
    ('RANCU', 159.00, 172.00, [159.97, 166.49], None),
    ('SP', 205.00, 222.00, [215.49, 218.29, 1e9], None),
    ('SP', 228.30, 237.90, [0, 0, 0], None),
    ('POV1', 284.55, 292.15, [1e9], None),
    ('POV3', 328.45, 338.10, [1e9, 1e9], None),
    ('POV3', 347.30, 362.00, [0, 359.05], None),
    ('POV4', 376.15, 390.85, [380.63, 386.20], None),
    ('SLAY1', 440.40, 451.75, [444.75], None),
    ('SLAY2', 470.00, 489.75, [475.85, 1e9, 1e9], None),
    ('SLAY2', 496.15, 512.00, [0, 0, 509.59], None),
    ('SLAY3', 531.19, 550.55, [0, 536.31, 547.35], None),
    ('SLAY4', 555.30, 565.70, [560.25], None),
    ('TER1', 645.23, 652.15, [1e9, 1e9, 1e9], None),
    ('TER2', 696.50, 712.25, [700.19, 702.01, 706.57], None),
    ('TER3', 727.50, 747.15, [734.35, 738.91], None),
    ('TER4', 764.10, 775.00, [768.01, 1e9], None),
    ('TER4', 792.20, 800.80, [0, 0], None),
    ('LARAS', 813.30, 829.50, [820.67, 825.29], None),
    ('DETEKTIF', 848.00, 862.90, [851.33, 854.60, 856.80, 859.90], None),
    ('RUMUSAN', 896.50, 920.45, [901.89, 906.77, 914.53], None),
]
panel_inst = []
for pid, a, b, cues, extra in PANELS:
    o0, o1 = q(s2o(a)), q(s2o(b))
    local = [(0.0 if c == 0 else round(s2o(c) - o0, 3)) if c < 1e8 else 1e9 for c in cues]
    panel_inst.append(dict(id=pid, out0=o0, out1=o1, dur=round(o1 - o0, 3), cues=local, lines=extra))

# split intervals (merge panels separated by < 1.5 s)
split = []
for p in panel_inst:
    if split and p['out0'] - split[-1][1] < 1.5: split[-1][1] = max(split[-1][1], p['out1'])
    else: split.append([p['out0'], p['out1']])
TR = 0.5  # layout transition seconds
def split_amount(t):
    for a, b in split:
        if a - TR <= t <= b + TR:
            if t < a: return (t - (a - TR)) / TR
            if t > b: return 1 - (t - b) / TR
            return 1.0
    return 0.0

# ---------------- full-frame overlays ----------------
overlays = []
def ov(kind, src_or_out, dur, out=False, **kw):
    t0 = q(src_or_out if out else s2o(src_or_out))
    overlays.append(dict(kind=kind, out0=t0, dur=dur, **kw))
ov('name', 39.4, 4.2, t1='ALIFF', t2='Hos Utama')
ov('name', 71.95, 4.2, t1='AMMAR', t2='Suara Warganet')
ov('name', 101.70, 4.0, t1='IMAN', t2='Detektif Sintaksis')
ov('title', 109.40, 4.6)
chap = {'s2': ('SEGMEN 2', 'KERANCUAN BAHASA & SINTAKSIS'), 's3': ('SEGMEN 3 · AYAT 1', 'POV'), 's4': ('SEGMEN 4 · AYAT 2', 'SLAY'),
        's5': ('SEGMEN 5 · AYAT 3', 'TERPALING'), 's6': ('SEGMEN 6', 'SALAH ATAU KREATIF?'), 's7': ('SEGMEN 7', 'PENUTUP')}
for s, (a, b) in chap.items():
    ov('chapter', seg_starts[s] + 0.35, 3.8, out=True, t1=a, t2=b)
ov('stamp', 936.85, 4.4)

# ---------------- shot plan ----------------
def has_kw(t): return '*' in t
shots = []   # dict(out0, out1, crop, cam, src0, zoom)
rot_i = {'AL': 0, 'IM': 0, 'AM': 0}
last = None
sub_by_clip = {}
for s in subs: sub_by_clip.setdefault((s['seg'], s['spk']), []).append(s)
seg_first = set()
for ci, c in enumerate(clips_out):
    spk = c['spk']; first_in_seg = c['seg'] not in seg_first; seg_first.add(c['seg'])
    cs = [s for s in subs if c['out0'] - 1e-6 <= s['out0'] < c['out1'] - 1e-6]
    for pi, p in enumerate(c['pieces']):
        # candidate cut points inside piece (subtitle starts)
        cand = sorted(set(q(s['out0']) for s in cs if p['out0'] + 1.8 < s['out0'] < p['out1'] - 1.8))
        bounds = [p['out0']]
        while True:
            remaining = p['out1'] - bounds[-1]
            if remaining <= 8.0: break
            target = bounds[-1] + 5.5
            opts = [x for x in cand if bounds[-1] + 3.0 <= x <= p['out1'] - 2.5]
            if not opts: break
            bounds.append(min(opts, key=lambda x: abs(x - target)))
        bounds.append(p['out1'])
        for k in range(len(bounds) - 1):
            o0, o1 = bounds[k], bounds[k + 1]
            mid = (o0 + o1) / 2
            in_split = split_amount(mid) > 0.5
            d = o1 - o0
            if in_split:
                lst = SPLIT_ROT[spk]; key = lst[(rot_i[spk]) % len(lst)]; rot_i[spk] += 1
                if last and CROPS[last][0] == CROPS[key][0] and last == key: key = lst[(rot_i[spk]) % len(lst)]; rot_i[spk] += 1
            elif first_in_seg and pi == 0 and k == 0:
                key = 'A-wide' if last != 'A-wide' else 'B-wide'
            elif d < 2.2:
                key = 'B-wide' if last != 'B-wide' else 'A-wide'
            else:
                lst = ROT[spk]; key = lst[rot_i[spk] % len(lst)]; rot_i[spk] += 1
                # avoid same camera + same framing back-to-back; at pause cuts (k==0, pi>0) force camera change
                force_cam = (k == 0 and pi > 0)
                tries = 0
                while tries < 6 and last and ((key == last) or (force_cam and CROPS[key][0] == CROPS[last][0])):
                    key = lst[rot_i[spk] % len(lst)]; rot_i[spk] += 1; tries += 1
            cam = CROPS[key][0]
            src0 = p['src0'] + (o0 - p['out0'])
            zoom = (not in_split) and d >= 4.0 and ('med' in key or 'close' in key or 'two' in key) and (len(shots) % 3 == 0)
            shots.append(dict(out0=round(o0, 4), out1=round(o1, 4), crop=key, cam=cam, src0=round(src0, 4), zoom=zoom, spk=spk))
            last = key

# ---------------- subtitles ----------------
def fmt_ass(t):
    cs = int(round(t * 100)); h = cs // 360000; m = (cs // 6000) % 60; s = (cs // 100) % 60; c = cs % 100
    return f"{h}:{m:02d}:{s:02d}.{c:02d}"
def fmt_srt(t):
    ms = int(round(t * 1000)); h = ms // 3600000; m = (ms // 60000) % 60; s = (ms // 1000) % 60; r = ms % 1000
    return f"{h:02d}:{m:02d}:{s:02d},{r:03d}"
YEL, PNK = '&H004AD5FF&', '&H00C6B6F4&'
def ass_text(t):
    out = ''; i = 0
    for m in re.finditer(r'\*([^*]+)\*|~([^~]+)~', t):
        out += t[i:m.start()].replace('~', '')
        if m.group(1) is not None:
            inner = m.group(1)
            # nested pink inside yellow -> keep yellow, strip tildes
            out += '{\\c' + YEL + '}' + inner.replace('~', '').upper() + '{\\c&H00FFFFFF&}'
        else:
            out += '{\\c' + PNK + '}' + m.group(2).upper() + '{\\c&H00FFFFFF&}'
        i = m.end()
    out += t[i:].replace('~', '')
    return out
def plain(t): return re.sub(r'[*~]', '', t)

S = [s for s in subs if not s['pantun']]
S.sort(key=lambda s: s['out0'])
for k, s in enumerate(S):
    nxt = S[k + 1]['out0'] if k + 1 < len(S) else None
    end = s['out1']
    if nxt is not None:
        if nxt - end < 0.35: end = nxt          # close tiny gaps (less flicker)
        end = min(end, nxt)
    if end - s['out0'] < 0.6 and nxt is not None: end = min(nxt, s['out0'] + 0.6)
    s['e'] = end

ASS_HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Poppins,58,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,4,2.5,2,160,160,62,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
PANTUN_STYLE = "Style: Pantun,Poppins,54,&H00E0EDF7,&H00FFFFFF,&H00000000,&H96000000,-1,-1,0,0,100,100,0,0,1,4,2.5,8,160,160,0,1\n"
ASS_HEAD = ASS_HEAD.replace("\n[Events]", PANTUN_STYLE + "\n[Events]")
pantun_events = []
P_lines = [s for s in subs if s['pantun']]
groups = {}
for s in P_lines: groups.setdefault((s['seg'], s['spk']), []).append(s)
for g in groups.values():
    g = sorted(g, key=lambda s: s['out0'])
    if g[0]['text'].startswith('Dengarkan'): g = g[1:]
    for k, s in enumerate(g):
        pair_start = k - (k % 2)
        txt = '\\N'.join(x['text'] for x in g[pair_start:k+1])
        if k % 2 == 1: txt = g[pair_start]['text'] + '\\N' + s['text']
        end = g[k+1]['out0'] if k+1 < len(g) else s['out1'] + 0.25
        fad = '{\\fad(150,0)}' if k % 2 == 0 else '{\\fad(0,0)}'
        if k % 2 == 1 or k == len(g)-1: fad = fad.replace('(0,0)', '(0,200)').replace('(150,0)', '(150,200)')
        pantun_events.append((s['out0'], end, '{\\pos(960,850)}' + fad + txt))
with open('/home/user/work/out/Podcast_Subtitles.ass', 'w') as f:
    f.write(ASS_HEAD)
    for a0, a1, tx in pantun_events:
        f.write(f"Dialogue: 1,{fmt_ass(a0)},{fmt_ass(a1)},Pantun,,0,0,0,,{tx}\n")
    for s in S:
        anim = '{\\fad(90,70)\\fscx94\\fscy94\\t(0,140,\\fscx100\\fscy100)}'
        f.write(f"Dialogue: 0,{fmt_ass(s['out0'])},{fmt_ass(s['e'])},Sub,,0,0,0,,{anim}{ass_text(s['text'])}\n")
# SRT: dialogue + pantun lines
SR = sorted(subs, key=lambda s: s['out0'])
with open('/home/user/work/out/Podcast_Subtitles.srt', 'w') as f:
    for k, s in enumerate(SR, 1):
        e = s.get('e', s['out1'])
        f.write(f"{k}\n{fmt_srt(s['out0'])} --> {fmt_srt(e)}\n{plain(s['text'])}\n\n")

json.dump(dict(shots=shots, panels=panel_inst, split=split, overlays=overlays, total=TOTAL,
               segments=[dict(kind=p['kind'], out0=p['out0'], out1=p['out1']) for p in timeline if p['kind'] != 'talk'],
               talk=[dict(out0=p['out0'], out1=p['out1'], seg=p['seg']) for p in TALK], seg_starts=seg_starts),
          open('/home/user/work/out/plan.json', 'w'), indent=1)
if __name__ == '__main__':
    from collections import Counter
    print('shots', len(shots), Counter(s['crop'] for s in shots).most_common())
    import statistics
    print('shot len median', statistics.median(s['out1'] - s['out0'] for s in shots), 'min', min(s['out1'] - s['out0'] for s in shots))
    print('panels', len(panel_inst), 'split intervals', len(split), 'overlays', len(overlays), 'subs', len(S))
    print('split time', sum(b - a for a, b in split))
