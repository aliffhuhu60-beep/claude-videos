"""Trailer audio: real podcast dialogue clips + original trailer music + SFX, and per-frame mouth envelopes."""
import sys, json, subprocess, wave, numpy as np
sys.path.insert(0, '/home/user/work')
import music as M          # reuses synth helpers (regenerates podcast music deterministically)
SR, FPS = 48000, 30
W = '/home/user/work'
TOTAL = 29.6

# (speaker, src_start, src_end, out_start)
CLIPS = [
    ('AL', 446.70, 451.72, 2.80),    # Dalam kamus bahasa Inggeris, slay sebenarnya bermaksud membunuh?
    ('AM', 301.37, 304.25, 8.10),    # Semua orang faham, apa salahnya?
    ('IM', 304.40, 308.12, 11.15),   # Faham memang faham, tetapi mari kita analisis.
    ('AL', 615.42, 622.60, 16.40),   # di TikTok mungkin slay. Tetapi dari segi tatabahasa, jawapannya jelas, iaitu salah! (+ketawa)
    ('AM', 937.62, 941.00, 23.70),   # Ingat, santai boleh, rancu jangan!
]
LAUGH = (16.40 + (621.70 - 615.42), 16.40 + (622.60 - 615.42))

def load_raw(a, b):
    out = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(a), '-t', str(b - a), '-i', f'{W}/src/raw1.mp4', '-vn', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(out, np.float32).reshape(-1, 2).mean(1)

N = int(TOTAL * SR)
dia = np.zeros(N, np.float32)
for spk, a, b, o in CLIPS:
    x = load_raw(a, b).copy(); f = int(0.015 * SR)
    x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
    i = int(o * SR); dia[i:i + len(x)] += x[:N - i]
M.save('trailer_dia_raw', dia)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{M.OUT}/trailer_dia_raw.wav', '-af',
                'highpass=f=85,afftdn=nr=8:nf=-42,equalizer=f=250:t=q:w=1.2:g=-2.5,equalizer=f=3600:t=q:w=1.5:g=2.5,'
                'acompressor=threshold=-22dB:ratio=3:attack=6:release=140:makeup=2,loudnorm=I=-15:TP=-2:LRA=7',
                '-ar', str(SR), f'{M.OUT}/trailer_dia.wav'], check=True)
def load_wav(p):
    w = wave.open(p); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a.reshape(-1, w.getnchannels())
dia2 = load_wav(f'{M.OUT}/trailer_dia.wav')[:N, 0]
dia2 = np.pad(dia2, (0, N - len(dia2)))
# silence outside clips (loudnorm tails)
mask = np.zeros(N)
for spk, a, b, o in CLIPS: mask[int(o * SR):int((o + b - a) * SR)] = 1
dia2 *= np.convolve(mask, np.ones(480) / 480, 'same')

# ---------------- music ----------------
mus = np.zeros((N + SR, 2))
BPM = 112; beat = 60 / BPM
PROG = [[50, 62, 66, 69, 73], [47, 62, 66, 69, 74], [43, 59, 62, 66, 71], [45, 61, 64, 69, 73]]
def impact(vel=1.0):
    n = int(1.6 * SR); t = np.arange(n) / SR
    f = 30 + 70 * np.exp(-t * 9); ph = 2 * np.pi * np.cumsum(f) / SR
    boom = np.sin(ph) * np.exp(-t * 2.6)
    nz = M.lowpass(np.stack([M.rs.randn(n), M.rs.randn(n)], 1), 1800)[:, 0] * np.exp(-t * 12) * 0.5
    return vel * (boom + nz)
def riser(dur, vel=0.4):
    n = int(dur * SR); t = np.arange(n) / SR
    nz = M.rs.randn(n); sw = (t / dur) ** 2
    hp = nz - np.convolve(nz, np.ones(40) / 40, 'same')
    tone = np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / dur) ** 2) / SR) * 0.25
    return vel * (hp * 0.6 + tone) * sw
def whoosh(vel=0.5):
    n = int(0.55 * SR); t = np.arange(n) / SR
    env = np.sin(np.pi * t / 0.55) ** 2
    return vel * M.lowpass(np.stack([M.rs.randn(n) * env, M.rs.randn(n) * env], 1), 2500)[:, 0]
def click(vel=0.25):
    n = int(0.03 * SR); t = np.arange(n) / SR
    return vel * np.diff(np.concatenate([[0], M.rs.randn(n)])) * np.exp(-t * 200)

# phone intro: muted arpeggio + riser
for i in range(int(2.4 / (beat / 2))):
    n = PROG[0][1 + (i % 4)] + 12
    M.place(mus, M.pluck(M.midi(n), 0.10, 0.25), i * beat / 2, 0.3 * ((i % 2) * 2 - 1))
M.place(mus, riser(2.3, 0.35), 0.1)
# typing clicks
for k in range(26): M.place(mus, click(0.22), 0.25 + k * 0.05 + (0.02 if k % 3 == 0 else 0), 0.0)
# groove under the whole trailer (ducked later)
g = M.groove(TOTAL - 2.4 + 1.0, BPM, PROG, drums=True, density=1.0, bright=1.1)
gi = int(2.4 * SR); mus[gi:gi + len(g)] += g[:len(mus) - gi] * 0.9
# hits
for t0, v in ((2.4, 1.0), (14.9, 0.7), (15.4, 0.7), (15.9, 0.9), (22.1, 0.6), (25.0, 0.6), (27.1, 1.0)):
    M.place(mus, impact(v * 0.55), t0)
for t0 in (4.35, 7.9, 11.1, 14.85, 16.35, 19.55, 23.45, 27.05):
    M.place(mus, whoosh(0.35), t0 - 0.3, 0.0)
# final chord ring-out
fin = np.zeros_like(mus)
for k, n in enumerate([62, 66, 69, 73, 78, 81]): M.place(fin, M.epiano(M.midi(n), 2.2, 0.12), 27.1 + 0.03 * k, (k - 2.5) * 0.25)
mus += M.reverb(fin, 0.45)[:len(mus)]
mus = mus[:N]
t = np.arange(N) / SR
# stop the groove after the final hit, fade out at the end
gate = np.where(t < 27.1, 1.0, np.clip(1 - (t - 27.1) / 0.25, 0.25, 1))
mus *= gate[:, None] * np.clip((TOTAL - t) / 1.2, 0, 1)[:, None]
# ducking under dialogue
env = np.abs(dia2); k = int(0.25 * SR)
duck_env = np.convolve(env > 0.02, np.ones(k) / k, 'same')
duck = 10 ** ((-13 * np.clip(duck_env * 3, 0, 1)) / 20)
mus *= duck[:, None]
mus = M.lowpass(mus, 12000)
# level: music -> about -17 LUFS before ducking region
mix = mus * 0.55 + np.stack([dia2, dia2], 1)
M.save('trailer_mix_pre', mix)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{M.OUT}/trailer_mix_pre.wav', '-af', 'alimiter=limit=0.89:level=disabled',
                '-c:a', 'pcm_s16le', f'{W}/t3d/trailer_mix.wav'], check=True)

# ---------------- mouth envelopes per frame ----------------
nf = int(round(TOTAL * FPS))
envs = {'AL': [0.0] * nf, 'IM': [0.0] * nf, 'AM': [0.0] * nf, 'laugh': [0.0] * nf}
hop = SR // FPS
for spk, a, b, o in CLIPS:
    raw = load_raw(a, b)
    for fi in range(int(o * FPS), min(nf, int((o + b - a) * FPS))):
        s = int((fi / FPS - o) * SR); seg = raw[max(0, s - hop // 2): s + hop // 2]
        if len(seg) == 0: continue
        db = 20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9)
        envs[spk][fi] = float(np.clip((db + 42) / 26, 0, 1))
for fi in range(nf):
    tt = fi / FPS
    if LAUGH[0] <= tt < LAUGH[1] + 0.4: envs['laugh'][fi] = 1.0
    if LAUGH[0] <= tt < LAUGH[1]: envs['AL'][fi] = 0.0     # handled by laugh animation
json.dump(dict(fps=FPS, total=TOTAL, env=envs, clips=CLIPS, laugh=LAUGH), open(f'{W}/t3d/trailer_env.json', 'w'))
print('ok', nf)
