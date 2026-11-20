import numpy as np, subprocess, wave, json, sys
sys.path.insert(0, '/home/user/work')
from timeline import timeline, clips_out, seg_starts, TOTAL, AZAN_LEAD, AZAN_SRC_END, EN
SR = 48000
W = '/home/user/work'

def load(path, ss=None, t=None, mono=True):
    cmd = ['ffmpeg', '-v', 'error']
    if ss is not None: cmd += ['-ss', str(ss)]
    if t is not None: cmd += ['-t', str(t)]
    cmd += ['-i', path, '-vn', '-ac', '1' if mono else '2', '-ar', str(SR), '-f', 'f32le', '-']
    x = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)
    return x if mono else x.reshape(-1, 2)

def save(path, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1: x = np.stack([x, x], 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x*32767).astype(np.int16).tobytes())

def lufs(path):
    out = subprocess.run(['ffmpeg', '-v', 'info', '-i', path, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float([l for l in out.splitlines() if l.strip().startswith('I:')][-1].split()[1])

N = int(round(TOTAL*SR)) + SR
# ---------------- dialogue stem ----------------
raw = load(f'{W}/src/raw1.mp4', 0, 1020, mono=False).mean(1)
dia = np.zeros(N, np.float32)
# per-clip gain leveling (active speech RMS)
levels = []
for c in clips_out:
    i0, i1 = int(c['src0']*100), int(c['src1']*100)
    act = EN[i0:i1][EN[i0:i1] > -35]
    levels.append(np.mean(act) if len(act) else -20)
target = np.median(levels)
FADE = int(0.012*SR)
for c, lv in zip(clips_out, levels):
    g = 10 ** (np.clip(target - lv, -4, 4) / 20)
    for p in c['pieces']:
        s0, s1 = int(round(p['src0']*SR)), int(round(p['src1']*SR))
        o0 = int(round(p['out0']*SR))
        seg = raw[s0:s1].copy() * g
        L = len(seg); f = min(FADE, L//4)
        seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
        dia[o0:o0+L] += seg
save(f'{W}/audio/dia_raw.wav', dia)
# processing chain (gentle): declip, HPF, denoise, EQ, de-ess, compression, loudness
chain = ('adeclip=w=55:o=75,highpass=f=85,afftdn=nr=8:nf=-42:tn=1,'
         'equalizer=f=250:t=q:w=1.2:g=-2.5,equalizer=f=3600:t=q:w=1.5:g=2,equalizer=f=8500:t=h:w=1:g=-1,'
         'deesser=i=0.35,acompressor=threshold=-21dB:ratio=2.8:attack=8:release=160:makeup=2,'
         'loudnorm=I=-16:TP=-2:LRA=8')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{W}/audio/dia_raw.wav', '-af', chain, '-ar', str(SR), f'{W}/audio/dia_proc.wav'], check=True)
dia = load(f'{W}/audio/dia_proc.wav', mono=False)[:N, 0]
dia = np.pad(dia, (0, N-len(dia)))
# kill any residual processing tails outside talk pieces
mask = np.zeros(N, np.float32)
for p in timeline:
    if p['kind'] == 'talk':
        mask[int(p['out0']*SR):int(p['out1']*SR)] = 1
k = np.ones(int(0.01*SR))/int(0.01*SR); mask = np.convolve(mask, k, 'same')
dia *= mask
print('dialogue LUFS', lufs(f'{W}/audio/dia_proc.wav'))

mix = np.zeros((N, 2), np.float32)
mix += dia[:, None]

def gen(name): return load(f'{W}/audio/gen/{name}.wav', mono=False)
def put(x, t0, gain_db=0.0, fade_in=0.0, fade_out=0.0):
    x = x.copy() * 10**(gain_db/20)
    if x.ndim == 1: x = np.stack([x, x], 1)
    if fade_in: f = int(fade_in*SR); x[:f] *= np.linspace(0, 1, f)[:, None]
    if fade_out: f = int(fade_out*SR); x[-f:] *= np.linspace(1, 0, f)[:, None]
    i = int(round(t0*SR)); x = x[:max(0, N-i)]
    mix[i:i+len(x)] += x

kinds = {p['kind']: p for p in timeline if p['kind'] != 'talk'}
# opening ad music (-16 LUFS-ish source ~ -14) -> -2 dB
put(gen('music_opening'), 0.0, -2.5)
# soft bed under the first ~14 s of the intro, then fade out before pantun
bed = gen('music_bed')
t_intro = seg_starts['intro']
put(bed[:int(16*SR)], t_intro, -21, fade_in=1.0, fade_out=4.0)
# azan: original audio, muezzin portion only, no music
az = kinds['azan']
azan = load(f'{W}/src/azan.mp4', 0, AZAN_SRC_END, mono=False)
save(f'{W}/audio/azan_part.wav', azan)
g = -18 - lufs(f'{W}/audio/azan_part.wav')
put(azan, az['out0'] + AZAN_LEAD, g, fade_in=0.08, fade_out=0.6)
print('azan gain', g)
# axia ad music
ax = kinds['axia']
put(gen('music_axia'), ax['out0'], -3.0)
# closing bed: from start of last clip of s7 (farewell) through credits
last = clips_out[-1]
cr = kinds['credits']
dur = cr['out1'] - last['out0']
b2 = bed[int(20*SR):int(20*SR)+int(dur*SR)].copy()
env = np.ones(len(b2)); i_cr = int((cr['out0']-last['out0'])*SR)
env[:i_cr] = 10**(-21/20); env[i_cr:] = 10**(-6/20)
ramp = int(1.0*SR); env[i_cr-ramp//2:i_cr+ramp//2] = np.linspace(10**(-21/20), 10**(-6/20), ramp)
b2 *= env[:, None]
put(b2, last['out0'], 0.0, fade_in=1.5, fade_out=2.5)
# SFX: "ting" at chapter starts of the three sentence segments
ting = gen('sfx_ting')
for s in ('s3', 's4', 's5'):
    put(ting, seg_starts[s] + 0.05, -10)
json.dump({'whoosh_times': []}, open(f'{W}/audio/sfx_meta.json', 'w'))
# final safety limiter
save(f'{W}/audio/mix_pre.wav', mix)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{W}/audio/mix_pre.wav', '-af',
                'alimiter=limit=0.89:attack=3:release=60:level=disabled', '-ar', str(SR), '-c:a', 'pcm_s16le', f'{W}/audio/mix_final.wav'], check=True)
print('mix LUFS', lufs(f'{W}/audio/mix_final.wav'), 'dur', N/SR)
