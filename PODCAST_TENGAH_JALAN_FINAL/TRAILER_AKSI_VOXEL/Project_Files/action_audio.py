"""Action-trailer audio: original epic score (braams, taiko, string ostinato, risers, impacts) + real dialogue + lip-sync envelopes."""
import sys, json, subprocess, wave, numpy as np
sys.path.insert(0, '/home/user/work')
import music as M
SR, FPS = 48000, 30
W = '/home/user/work'
TOTAL = 29.9
rs = np.random.RandomState(11)

CLIPS = [  # speaker, src0, src1, out0
    ('AL', 446.70, 451.72, 7.70),    # Dalam kamus bahasa Inggeris, slay sebenarnya bermaksud membunuh?
    ('AM', 301.37, 304.25, 12.80),   # Semua orang faham, apa salahnya?
    ('IM', 304.40, 308.12, 15.75),   # Faham memang faham, tetapi mari kita analisis.
    ('AL', 619.46, 621.70, 21.00),   # Jawapannya jelas, iaitu salah!
    ('AM', 937.62, 941.00, 23.35),   # Ingat, santai boleh, rancu jangan!
]
BRAAMS = [1.60, 4.40, 7.50, 26.70]
HITS = [5.80, 19.50, 19.95, 20.40, 22.52, 23.98]

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
M.save('action_dia_raw', dia)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{M.OUT}/action_dia_raw.wav', '-af',
                'highpass=f=90,afftdn=nr=8:nf=-42,equalizer=f=250:t=q:w=1.2:g=-3,equalizer=f=3500:t=q:w=1.4:g=3,'
                'acompressor=threshold=-24dB:ratio=3.5:attack=5:release=120:makeup=3,loudnorm=I=-14:TP=-2:LRA=6', '-ar', str(SR), f'{M.OUT}/action_dia.wav'], check=True)
dia2 = load_wav(f'{M.OUT}/action_dia.wav')[:N, 0]; dia2 = np.pad(dia2, (0, N - len(dia2)))
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

# Act 1: rumble + tick pulse + braams
n = int(7.7 * SR); rumble = M.lowpass(np.stack([rs.randn(n), rs.randn(n)], 1), 120) * 0.8
rumble *= np.clip(np.arange(n) / SR / 1.0, 0, 1)[:, None]; put(rumble, 0.0, 0.6)
for k in range(int(7.4 / (60 / 140 / 2))): put(tick(0.18 if k % 2 else 0.28), 0.3 + k * 60 / 140 / 2)
put(revswell(1.5, 0.45), 0.1)
for b in BRAAMS: put(braam(3.4), b, 0.9); put(impact(0.9), b, 0.7)
put(revswell(1.2, 0.5), 4.4 - 1.2); put(revswell(1.0, 0.5), 7.5 - 1.0)
for tb in (5.0, 5.4, 5.8, 6.2, 6.6, 6.8, 7.0, 7.2): put(taiko(0.8 if tb < 6.6 else 0.6), tb)
# Act 2: driving ostinato + taiko groove under dialogue
strings_ostinato(7.6, 26.6)
beat = 60 / 140
for k in range(int((26.6 - 7.7) / beat)):
    tb = 7.7 + k * beat
    if k % 4 in (0, 3) or (k % 8 == 6): put(taiko(0.85, 60 if k % 4 == 0 else 80), tb)
for h in HITS: put(impact(0.75), h, 0.6); put(taiko(1.0, 55), h)
put(riser(2.8, 0.6), 26.7 - 2.8); put(braam(3.4), 26.7, 0.6); put(impact(1.0), 26.7, 0.5)
# final: big braam + ring-out chord (D minor) + last boom
fin = np.zeros_like(mus)
for kk, nn in enumerate([38, 45, 50, 53, 57, 62]):
    seg = saw(M.midi(nn), 3.0, 16) * np.exp(-np.arange(int(3.0 * SR)) / SR * 0.8) * 0.12
    i = int(26.7 * SR); fin[i:i + len(seg)] += np.stack([seg, np.roll(seg, 200 + kk * 50)], 1)
mus += M.reverb(M.lowpass(fin, 2500), 0.5)[:len(mus)]
put(impact(1.0), 29.0, 0.8)
mus = mus[:N]
# duck music under dialogue (action trailers keep music present: -9 dB)
env = np.convolve(mask, np.ones(int(0.2 * SR)) / int(0.2 * SR), 'same')
mus *= (10 ** (-6.5 * env / 20))[:, None]
mus *= np.clip((TOTAL - t) / 0.6, 0, 1)[:, None]
seg = mus[int(8 * SR):int(26 * SR)]; rms = np.sqrt((seg ** 2).mean()); mus *= 10 ** (-17 / 20) / rms
mus = np.tanh(mus * 1.3) / 1.3   # glue + soft-clip the big hits
mix = mus + np.stack([dia2, dia2], 1) * 1.0
M.save('action_mix_pre', mix)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{M.OUT}/action_mix_pre.wav', '-af', 'acompressor=threshold=-14dB:ratio=2:attack=10:release=200,loudnorm=I=-14:TP=-1.5:LRA=9,alimiter=limit=0.89:level=disabled',
                '-ar', str(SR), '-c:a', 'pcm_s16le', f'{W}/t3d/action_mix.wav'], check=True)

# envelopes
nf = int(round(TOTAL * FPS)); hop = SR // FPS
envs = {'AL': [0.0] * nf, 'IM': [0.0] * nf, 'AM': [0.0] * nf}
for spk, a, b, o in CLIPS:
    raw = load_raw(a, b)
    for fi in range(int(o * FPS), min(nf, int((o + b - a) * FPS))):
        s = int((fi / FPS - o) * SR); seg = raw[max(0, s - hop // 2): s + hop // 2]
        if len(seg): envs[spk][fi] = float(np.clip((20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9) + 42) / 26, 0, 1))
json.dump(dict(fps=FPS, total=TOTAL, env=envs, clips=CLIPS, braams=BRAAMS, hits=HITS), open(f'{W}/t3d/action_env.json', 'w'))
print('ok', nf)
