"""Action-trailer audio: original epic score (braams, taiko, string ostinato, risers, impacts) + real dialogue + lip-sync envelopes."""
import sys, json, subprocess, wave, numpy as np
sys.path.insert(0, '/home/user/work')
import music as M
SR, FPS = 48000, 30
W = '/home/user/work'
TOTAL = 39.0
rs = np.random.RandomState(11)

CLIPS = [  # speaker, src0, src1, out0
    ('AL', 446.70, 451.72, 8.50),    # Dalam kamus bahasa Inggeris, slay sebenarnya bermaksud membunuh?
    ('AM', 301.37, 304.25, 13.60),   # Semua orang faham, apa salahnya?
    ('IM', 304.40, 308.12, 16.55),   # Faham memang faham, tetapi mari kita analisis.
    ('IM', 357.22, 358.98, 20.40),   # Itulah campur kod pada peringkat frasa.
    ('AM', 647.92, 651.95, 22.40),   # Dia ni terpaling alim, semua orang dia tegur.
    ('AL', 619.46, 621.70, 28.20),   # Jawapannya jelas, iaitu salah!
    ('AM', 937.62, 941.00, 31.25),   # Ingat, santai boleh, rancu jangan!
]
BRAAMS = [1.80, 4.80, 8.30, 34.80]
HITS = [6.30, 12.79, 21.05, 24.45, 26.55, 27.05, 27.55, 29.87, 31.90, 37.6]
SILENCE = (30.45, 31.25)
def load_raw(a, b):
    out = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(a), '-t', str(b - a), '-i', f'{W}/src/raw1.mp4', '-vn', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(out, np.float32).reshape(-1, 2).mean(1)
def load_wav(p):
    w = wave.open(p); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a.reshape(-1, w.getnchannels())

N = int(TOTAL * SR); t = np.arange(N) / SR
# ---------------- dialogue ----------------
dia = np.zeros(N, np.float32)
for spk, a, b, o in CLIPS:
    x = load_raw(a, b).copy(); f = int(0.012 * SR); x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
    i = int(o * SR); dia[i:i + len(x)] += x[:N - i]
M.save('action2_dia_raw', dia)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{M.OUT}/action2_dia_raw.wav', '-af',
                'highpass=f=90,afftdn=nr=8:nf=-42,equalizer=f=250:t=q:w=1.2:g=-3,equalizer=f=3500:t=q:w=1.4:g=3,'
                'acompressor=threshold=-24dB:ratio=3.5:attack=5:release=120:makeup=3,loudnorm=I=-14:TP=-2:LRA=6', '-ar', str(SR), f'{M.OUT}/action2_dia.wav'], check=True)
dia2 = load_wav(f'{M.OUT}/action2_dia.wav')[:N, 0]; dia2 = np.pad(dia2, (0, N - len(dia2)))
mask = np.zeros(N)
for spk, a, b, o in CLIPS: mask[int(o * SR):int((o + b - a) * SR)] = 1
dia2 *= np.convolve(mask, np.ones(480) / 480, 'same')

# ---------------- score ----------------
mus = np.zeros((N + 3 * SR, 2))
def saw(f, dur, harm=24, detune=(0, 0.006, -0.007)):
    n = int(dur * SR); tt = np.arange(n) / SR; x = np.zeros(n)
    for d in detune:
        ff = f * (1 + d)
        for k in range(1, harm + 1):
            if ff * k > 9000: break
            x += np.sin(2 * np.pi * ff * k * tt + k * d * 50) / k
    return x / len(detune)
def braam(dur=3.2, vel=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = saw(36.7, dur, 40) + 0.8 * saw(73.4, dur, 30) + 0.5 * saw(110.0, dur, 20) + 0.35 * saw(146.8, dur, 14)   # D1 D2 A2 D3 (power chord)
    env = np.clip(tt / 0.04, 0, 1) * np.exp(-tt * 0.9)
    x = M.lowpass(np.stack([x, np.roll(x, 300)], 1), 900)
    sub = np.sin(2 * np.pi * np.cumsum(45 - 12 * np.clip(tt, 0, 1)) / SR) * np.exp(-tt * 1.4)
    return vel * (x * 0.55 + sub[:, None] * 0.9) * env[:, None]
def taiko(vel=1.0, f0=70):
    n = int(1.2 * SR); tt = np.arange(n) / SR
    f = f0 + 90 * np.exp(-tt * 25); body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 5.5)
    slap = M.lowpass(np.stack([rs.randn(n), rs.randn(n)], 1), 1500)[:, 0] * np.exp(-tt * 40) * 0.6
    x = vel * (body + slap); return np.stack([x, x], 1)
def impact(vel=1.0):
    n = int(2.5 * SR); tt = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(28 + 80 * np.exp(-tt * 8)) / SR) * np.exp(-tt * 1.8)
    crack = M.lowpass(np.stack([rs.randn(n), rs.randn(n)], 1), 5000) * np.exp(-tt * 18)[:, None] * 0.5
    tail = M.reverb(np.stack([boom, boom], 1) * 0.3, 0.6, 2.0)[:n]
    return vel * (boom[:, None] * 0.9 + crack + tail)
def riser(dur, vel=0.5):
    n = int(dur * SR); tt = np.arange(n) / SR; p = tt / dur
    nz = rs.randn(n); hp = nz - np.convolve(nz, np.ones(30) / 30, 'same')
    tone = sum(np.sin(2 * np.pi * np.cumsum(f0 * (1 + 3 * p ** 2)) / SR) for f0 in (220, 330, 440)) / 3
    x = vel * (hp * 0.5 + tone * 0.5) * p ** 2.5; return np.stack([x, np.roll(x, 200)], 1)
def revswell(dur, vel=0.5):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = M.lowpass(np.stack([rs.randn(n), rs.randn(n)], 1), 7000) * ((tt / dur) ** 3)[:, None]; return vel * x
def tick(vel=0.25):
    n = int(0.05 * SR); tt = np.arange(n) / SR; x = vel * np.sin(2 * np.pi * 2400 * tt) * np.exp(-tt * 120); return np.stack([x, x], 1)
def put(x, t0, g=1.0):
    i = int(t0 * SR); x = x[:len(mus) - i]; mus[i:i + len(x)] += x * g
def strings_ostinato(t0, t1, bpm=140, notes=(50, 50, 53, 50, 55, 50, 53, 52), vel=0.32):
    s16 = 60 / bpm / 4; k = 0; tt = t0
    while tt < t1:
        n = notes[k % len(notes)]; d = s16 * 0.9; seg = saw(M.midi(n), d, 18) + 0.5 * saw(M.midi(n + 12), d, 10)
        e = np.exp(-np.arange(len(seg)) / SR * 14); x = seg * e * vel
        put(M.lowpass(np.stack([x, np.roll(x, 120)], 1), 3200), tt); tt += s16; k += 1

def heartbeat(vel=0.9):
    n = int(0.5 * SR); tt = np.arange(n) / SR
    f = 48 + 30 * np.exp(-tt * 30); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 14)
    x2 = np.roll(x, int(0.17 * SR)) * 0.7; y = vel * (x + x2); return np.stack([y, y], 1)
def tremolo(t0, t1, notes=(50, 53, 57), vel=0.12):
    d = t1 - t0; n = int(d * SR); tt = np.arange(n) / SR; x = np.zeros(n)
    for nn in notes: x += saw(M.midi(nn), d, 14)[:n]
    x *= (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 12 * tt))) * np.clip(tt / 1.5, 0, 1) * vel
    put(M.lowpass(np.stack([x, np.roll(x, 300)], 1), 2600), t0)
# Act 1: heartbeat + rumble + braams + taiko build
n = int(8.5 * SR); rumble = M.lowpass(np.stack([rs.randn(n), rs.randn(n)], 1), 110) * 0.9
rumble *= np.clip(np.arange(n) / SR / 1.0, 0, 1)[:, None]; put(rumble, 0.0, 0.7)
for k, tb in enumerate([0.15, 0.95, 1.6]): put(heartbeat(0.9 + 0.1 * k), tb)
for k in range(int(6.5 / (60 / 140 / 2))): put(tick(0.15 if k % 2 else 0.25), 2.0 + k * 60 / 140 / 2)
put(revswell(1.6, 0.5), 0.2)
for b in BRAAMS: put(braam(3.6), b, 1.0); put(impact(1.0), b, 0.8)
put(revswell(1.2, 0.55), 4.8 - 1.2); put(revswell(1.0, 0.55), 8.3 - 1.0)
for tb in (5.6, 5.9, 6.3, 6.7, 7.0, 7.3, 7.6, 7.8, 8.0, 8.15): put(taiko(0.95 if tb < 7.5 else 0.75), tb)
tremolo(2.0, 8.3, vel=0.10)
# Act 2: driving ostinato + taiko + tension tremolo; full drop-out during the silence beat
strings_ostinato(8.4, SILENCE[0])
strings_ostinato(SILENCE[1] + 0.05, 34.8, notes=(50, 50, 53, 50, 57, 50, 55, 53))
tremolo(8.4, SILENCE[0], notes=(38, 45, 50), vel=0.08)
beat = 60 / 140
for k in range(int((34.8 - 8.5) / beat)):
    tb = 8.5 + k * beat
    if SILENCE[0] - 0.05 <= tb < SILENCE[1]: continue
    if k % 4 in (0, 3) or (k % 8 == 6): put(taiko(0.9, 60 if k % 4 == 0 else 80), tb)
for h in HITS: put(impact(0.85), h, 0.65); put(taiko(1.0, 55), h)
put(riser(2.5, 0.6), SILENCE[0] - 2.5 + 0.02)
put(heartbeat(1.0), SILENCE[0] + 0.1)
put(riser(2.8, 0.65), 34.8 - 2.8); put(braam(3.6), 34.8, 0.7); put(impact(1.0), 34.8, 0.6)
fin = np.zeros_like(mus)
for kk, nn in enumerate([38, 45, 50, 53, 57, 62]):
    seg = saw(M.midi(nn), 3.6, 16) * np.exp(-np.arange(int(3.6 * SR)) / SR * 0.7) * 0.12
    i = int(34.8 * SR); fin[i:i + len(seg)] += np.stack([seg, np.roll(seg, 200 + kk * 50)], 1)
mus += M.reverb(M.lowpass(fin, 2500), 0.5)[:len(mus)]
put(impact(1.0), 37.6, 0.85)
mus = mus[:N]
# duck music under dialogue (action trailers keep music present: -9 dB)
env = np.convolve(mask, np.ones(int(0.2 * SR)) / int(0.2 * SR), 'same')
mus *= (10 ** (-6.5 * env / 20))[:, None]
mus *= np.clip((TOTAL - t) / 0.6, 0, 1)[:, None]
g = np.ones(N); i0, i1 = int((SILENCE[0] + 0.12) * SR), int((SILENCE[1] - 0.02) * SR); g[i0:i1] = 0.12
g = np.convolve(g, np.ones(2400) / 2400, 'same'); mus *= g[:, None]
seg = mus[int(9 * SR):int(30 * SR)]; rms = np.sqrt((seg ** 2).mean()); mus *= 10 ** (-17 / 20) / rms
mus = np.tanh(mus * 1.3) / 1.3   # glue + soft-clip the big hits
mix = mus + np.stack([dia2, dia2], 1) * 1.0
M.save('action2_mix_pre', mix)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{M.OUT}/action2_mix_pre.wav', '-af', 'acompressor=threshold=-14dB:ratio=2:attack=10:release=200,loudnorm=I=-14:TP=-1.5:LRA=9,alimiter=limit=0.89:level=disabled',
                '-ar', str(SR), '-c:a', 'pcm_s16le', f'{W}/t3d/action2_mix.wav'], check=True)

# envelopes
nf = int(round(TOTAL * FPS)); hop = SR // FPS
envs = {'AL': [0.0] * nf, 'IM': [0.0] * nf, 'AM': [0.0] * nf}
for spk, a, b, o in CLIPS:
    raw = load_raw(a, b)
    for fi in range(int(o * FPS), min(nf, int((o + b - a) * FPS))):
        s = int((fi / FPS - o) * SR); seg = raw[max(0, s - hop // 2): s + hop // 2]
        if len(seg): envs[spk][fi] = float(np.clip((20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9) + 42) / 26, 0, 1))
json.dump(dict(fps=FPS, total=TOTAL, env=envs, clips=CLIPS, braams=BRAAMS, hits=HITS, silence=SILENCE), open(f'{W}/t3d/action2_env.json', 'w'))
print('ok', nf)
