import sys, json
from faster_whisper import WhisperModel
src, out, model = sys.argv[1], sys.argv[2], sys.argv[3]
m = WhisperModel(model, device="cpu", compute_type="int8", cpu_threads=4)
prompt = "Podcast Tengah Jalan. Aliff, Ammar, Iman. Kerancuan bahasa, sintaksis, subjek, predikat, POV, first time, slay, outfit, confirm, jealous, terpaling, kelewahan, ayat pasif, ditegurnya, laras bahasa, Detektif Kapsyen, TikTok, pantun."
import numpy as np, wave
w=wave.open(src); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768; a=a[:16000*1016]
segs, info = m.transcribe(a, language="ms", word_timestamps=True, initial_prompt=prompt, vad_filter=True, beam_size=5, condition_on_previous_text=False)
res=[]
with open(out+".txt","w") as f:
    for s in segs:
        d={"start":s.start,"end":s.end,"text":s.text,"words":[[w.start,w.end,w.word,w.probability] for w in (s.words or [])]}
        res.append(d)
        f.write(f"[{s.start:7.2f}-{s.end:7.2f}] {s.text}\n"); f.flush(); json.dump(res, open(out+".json","w"), ensure_ascii=False)
json.dump(res, open(out+".json","w"), ensure_ascii=False)
print("done")
