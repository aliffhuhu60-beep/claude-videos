#!/usr/bin/env python3
"""Transkripsi padat trek dialog akhir (untuk menambah liputan sari kata).

Whisper cenderung "melangkau" bahagian panjang apabila mikrofon jauh. Skrip ini memproses audio
dalam tetingkap tetap 24 s (tanpa VAD, tanpa konteks segmen sebelumnya) supaya setiap bahagian
ditranskripsi secara bebas. Hasil disemak manual dalam transcript_dense_edits.json.

Usage: python3 transcribe_dense.py <dialog16k.wav> <out.json> [model] [win] [t0] [t1]
"""
import json, sys, wave
import numpy as np
from faster_whisper import WhisperModel

src, out = sys.argv[1], sys.argv[2]
model_name = sys.argv[3] if len(sys.argv) > 3 else "mobiuslabsgmbh/faster-whisper-large-v3-turbo"
WIN = float(sys.argv[4]) if len(sys.argv) > 4 else 24.0
w = wave.open(src); sr = w.getframerate(); audio = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
T = len(audio) / sr
t0 = float(sys.argv[5]) if len(sys.argv) > 5 else 8.0
t1 = float(sys.argv[6]) if len(sys.argv) > 6 else T
m = WhisperModel(model_name, device="cpu", compute_type="int8", cpu_threads=4)
res = []
t = t0
def quiet(x, span=4.0):
    """titik paling senyap (tenaga 50 ms) dalam ±span s — elak memotong perkataan di sempadan tetingkap"""
    lo, hi = int((x - span) * sr), int(min(T, x + span) * sr); hop = int(0.05 * sr)
    e = [float(np.mean(audio[i:i + hop] ** 2)) for i in range(lo, hi - hop, hop)]
    return (lo + int(np.argmin(e)) * hop) / sr if e else x
while t < t1:
    a = t; b = t1 if t + WIN + 4 >= t1 else quiet(t + WIN)
    chunk = audio[int(a * sr):int(b * sr)]
    segs, _ = m.transcribe(chunk, language="ms", beam_size=5, vad_filter=False, condition_on_previous_text=False,
                           word_timestamps=True, temperature=0.0, no_speech_threshold=0.7, compression_ratio_threshold=2.2)
    for s in segs:
        txt = s.text.strip()
        if not txt: continue
        res.append(dict(s=round(a + s.start, 2), e=round(a + s.end, 2), t=txt, lp=round(s.avg_logprob, 3),
                        ns=round(s.no_speech_prob, 3), cr=round(s.compression_ratio, 2),
                        w=[(round(a + x.start, 2), round(a + x.end, 2), x.word) for x in s.words]))
        print(f"{a + s.start:7.1f} [{s.avg_logprob:5.2f}] {txt}", flush=True)
    t = b
json.dump(res, open(out, "w"), ensure_ascii=False, indent=0)
print("segments:", len(res))
