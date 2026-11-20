"""Procedural, original (copyright-free) music + SFX for the podcast edit."""
import numpy as np, wave, os
SR = 48000
OUT = '/home/user/work/audio/gen'
os.makedirs(OUT, exist_ok=True)
rs = np.random.RandomState(3)

def save(name, x):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1: x = np.stack([x, x], 1)
    pk = np.abs(x).max()
    if pk > 0.98: x = x * 0.98 / pk
    with wave.open(f'{OUT}/{name}.wav', 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())

def midi(n): return 440.0 * 2 ** ((n - 69) / 12)
def env_adsr(n, a, d, s, r, sus_len):
    a, d, r = int(a*SR), int(d*SR), int(r*SR); sl = max(0, int(sus_len*SR) - a - d)
    e = np.concatenate([np.linspace(0,1,max(a,1)), np.linspace(1,s,max(d,1)), np.full(sl, s), np.linspace(s,0,max(r,1))])
    return e[:n] if len(e) >= n else np.pad(e, (0, n-len(e)))

def epiano(f, dur, vel=0.5):
    n = int((dur + 1.2) * SR); t = np.arange(n) / SR
    tone = (np.sin(2*np.pi*f*t) + 0.35*np.sin(2*np.pi*2*f*t)*np.exp(-t*3) + 0.12*np.sin(2*np.pi*3*f*t)*np.exp(-t*6)
            + 0.05*np.sin(2*np.pi*7*f*t)*np.exp(-t*20))
    trem = 1 + 0.08*np.sin(2*np.pi*4.5*t)
    return vel * tone * trem * env_adsr(n, 0.005, 0.6, 0.45, 1.0, dur) * np.exp(-t*0.6)

def pad(f, dur, vel=0.2):
    n = int((dur + 1.5) * SR); t = np.arange(n) / SR
    x = sum(np.sin(2*np.pi*f*(1+dt)*t + p) for dt, p in ((0,0),(0.003,1),(-0.004,2)))
    x += 0.3*sum(np.sin(2*np.pi*2*f*(1+dt)*t) for dt in (0.002,-0.002))
    return vel * x / 3 * env_adsr(n, 0.6, 0.5, 0.8, 1.4, dur)

def pluck(f, vel=0.4, dur=0.5):
    n = int((dur+0.4)*SR); t = np.arange(n)/SR
    x = np.sign(np.sin(2*np.pi*f*t))*0.25 + np.sin(2*np.pi*f*t)
    k = np.exp(-t*9)
    # simple one-pole lowpass with decaying cutoff
    y = np.zeros(n); a = 0.0
    for i in range(0, n, 64):
        c = 0.08 + 0.5*np.exp(-i/SR*12)
        seg = x[i:i+64]; out = np.empty_like(seg)
        for j, v in enumerate(seg): a += c*(v-a); out[j] = a
        y[i:i+64] = out
    return vel * y * k

def bass(f, dur, vel=0.5):
    n = int((dur+0.2)*SR); t = np.arange(n)/SR
    x = np.sin(2*np.pi*f*t) + 0.2*np.sin(2*np.pi*2*f*t)
    return vel * x * env_adsr(n, 0.01, 0.2, 0.7, 0.15, dur)

def kick(vel=0.9):
    n = int(0.45*SR); t = np.arange(n)/SR
    f = 50 + 90*np.exp(-t*30)
    ph = 2*np.pi*np.cumsum(f)/SR
    return vel*np.sin(ph)*np.exp(-t*7)

def snare(vel=0.35):
    n = int(0.3*SR); t = np.arange(n)/SR
    nz = rs.randn(n); nz = np.convolve(nz, [1,-0.6], 'same')
    return vel*(0.6*nz*np.exp(-t*18) + 0.5*np.sin(2*np.pi*190*t)*np.exp(-t*25))

def snap(vel=0.25):
    n = int(0.12*SR); t = np.arange(n)/SR
    nz = np.convolve(rs.randn(n), [1,-0.9], 'same')
    return vel*nz*np.exp(-t*45)

def hat(vel=0.12, open_=False):
    n = int((0.25 if open_ else 0.06)*SR); t = np.arange(n)/SR
    nz = np.diff(np.concatenate([[0], rs.randn(n)]))
    return vel*nz*np.exp(-t*(12 if open_ else 70))

def reverb(x, wet=0.25, length=1.8, seed=1):
    r = np.random.RandomState(seed); n = int(length*SR); t = np.arange(n)/SR
    irL = r.randn(n)*np.exp(-t*3.2); irR = r.randn(n)*np.exp(-t*3.2)
    irL /= np.sqrt((irL**2).sum()); irR /= np.sqrt((irR**2).sum())
    from numpy.fft import rfft, irfft
    N = 1 << int(np.ceil(np.log2(len(x)+n)))
    m = x if x.ndim == 1 else x.mean(1)
    L = irfft(rfft(m, N)*rfft(irL, N), N)[:len(x)]; R = irfft(rfft(m, N)*rfft(irR, N), N)[:len(x)]
    dry = np.stack([m, m], 1) if x.ndim == 1 else x
    return dry*(1-wet) + np.stack([L, R], 1)*wet*3

def place(buf, x, t, pan=0.0):
    i = int(t*SR)
    if i >= len(buf): return
    x = x[:len(buf)-i]
    l, r = np.cos((pan+1)*np.pi/4), np.sin((pan+1)*np.pi/4)
    buf[i:i+len(x), 0] += x*l*1.41; buf[i:i+len(x), 1] += x*r*1.41

def lowpass(x, fc):
    from numpy.fft import rfft, irfft, rfftfreq
    X = rfft(x, axis=0); f = rfftfreq(len(x), 1/SR)
    X *= (1/np.sqrt(1+(f/fc)**4))[:, None]
    return irfft(X, len(x), axis=0)

# chord progression (D major): Dmaj9, Bm9, Gmaj7, A6sus
PROG = [[50, 62, 66, 69, 73, 76], [47, 62, 66, 69, 73], [43, 59, 62, 66, 69], [45, 61, 64, 66, 71]]

def groove(total, bpm, bars_prog, drums=True, density=1.0, bright=1.0, seed=0):
    beat = 60/bpm; bar = 4*beat
    buf = np.zeros((int((total+2)*SR), 2)); keys = np.zeros_like(buf)
    nbars = int(np.ceil(total/bar))
    for b in range(nbars):
        ch = bars_prog[b % len(bars_prog)]; t0 = b*bar
        # chords: e-piano stabs
        for k, n in enumerate(ch[1:]):
            place(keys, epiano(midi(n), beat*1.5, 0.16), t0 + 0.012*k, pan=(k-2)*0.25)
            place(keys, epiano(midi(n), beat*1.0, 0.11), t0 + 2.5*beat + 0.01*k, pan=(k-2)*0.25)
        place(keys, pad(midi(ch[1]), bar, 0.10), t0, -0.3); place(keys, pad(midi(ch[3]), bar, 0.08), t0, 0.3)
        # bass
        place(buf, bass(midi(ch[0]-12+12), beat*1.6, 0.42), t0)
        place(buf, bass(midi(ch[0]-12+12), beat*0.6, 0.30), t0 + 2.5*beat)
        place(buf, bass(midi(ch[0]-12+19), beat*0.6, 0.22), t0 + 3.5*beat)
        if drums:
            for q in range(4):
                tq = t0 + q*beat
                if q in (0,) or (q == 2 and density > 0.8): place(buf, kick(0.75), tq)
                if q in (1, 3): place(buf, snap(0.22*density) + 0, tq, 0.1)
                place(buf, hat(0.07*bright), tq + beat/2 + 0.012, 0.35)
                if density > 0.9: place(buf, hat(0.045*bright), tq + 0.006, 0.35)
    keys = reverb(keys, 0.3)
    return buf[:len(keys)] + keys

# 1) Opening ident (10s): soft build, resolve at 9s
op = groove(10.5, 96, PROG, drums=True, density=0.9)
t = np.arange(len(op))/SR
fade_in = np.clip(t/1.2, 0, 1); fade_out = np.clip((10.0 - t)/1.2, 0, 1)
# riser swell + final chord
op *= (fade_in*fade_out)[:, None]
fin = np.zeros_like(op)
for k, n in enumerate([62, 66, 69, 73, 78]): place(fin, epiano(midi(n), 1.5, 0.12), 8.7 + 0.03*k, (k-2)*0.3)
fin = reverb(fin, 0.45)[:len(op)]
op = op + fin*np.clip((10.4-t)/1.0, 0, 1)[:, None]
save('music_opening', lowpass(op[:int(10.0*SR)], 9000))

# 2) Bed (loopable 4 bars x 8 = ~80 s), gentle: no kick, light snaps
bed = groove(80.0, 92, PROG, drums=True, density=0.5, bright=0.6)
save('music_bed', lowpass(bed[:int(80*SR)], 7000))

# 3) Axia ad (10s, upbeat, 118 bpm, plucks)
PROG2 = [[48, 64, 67, 71, 74], [45, 60, 64, 67, 72], [41, 60, 65, 69, 72], [43, 62, 65, 67, 71]]  # Cmaj7 Am7 Fmaj7 G7sus
ax = groove(10.5, 118, PROG2, drums=True, density=1.0, bright=1.2)
mel = np.zeros_like(ax); beat = 60/118
notes = [76, 79, 81, 79, 76, 74, 72, 74, 76, 79, 84, 81, 79, 76, 79, 81, 84, 83, 79, 76]
for i, n in enumerate(notes): place(mel, pluck(midi(n), 0.16, 0.35), 0.0 + i*beat/2 + 4*beat*0.0, 0.2*((i % 2)*2-1))
mel = reverb(mel, 0.25)[:len(ax)]
ax = ax + mel
t = np.arange(len(ax))/SR
ax *= (np.clip(t/0.3, 0, 1)*np.clip((10.0-t)/0.9, 0, 1))[:, None]
save('music_axia', lowpass(ax[:int(10.0*SR)], 11000))

# 4) SFX: soft "ting" (bell) and soft whoosh
n = int(1.6*SR); t = np.arange(n)/SR
ting = sum(a*np.sin(2*np.pi*f*t)*np.exp(-t*d) for f, a, d in ((1568, 1, 3.5), (3136*1.003, .35, 6), (4704*0.998, .15, 9), (2349, .25, 5)))
ting *= np.clip(t/0.003, 0, 1)
save('sfx_ting', reverb(ting*0.35, 0.3, 1.5))
n = int(0.7*SR); t = np.arange(n)/SR
nz = rs.randn(n); sw = np.sin(np.pi*np.clip(t/0.7, 0, 1))**2
wh = lowpass(np.stack([nz*sw, np.roll(nz, 200)*sw], 1), 2200)*0.18
save('sfx_whoosh', wh)
print('ok')
