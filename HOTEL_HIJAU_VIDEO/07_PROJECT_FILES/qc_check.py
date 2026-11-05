#!/usr/bin/env python3
"""Semakan kualiti (Langkah 9) untuk video akhir.
- Tempoh tepat 30:00, spesifikasi (H.264, 1920x1080, 30 fps, AAC 48 kHz stereo)
- Skrin hitam tidak disengajakan (blackdetect)
- Loudness (EBU R128) & true peak
- Lembaran semakan visual pada saat penting (pop-up guru, tajuk, kredit)
Usage: python3 qc_check.py <video.mp4> <out_dir>
"""
import json, re, subprocess, sys, os
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
rep = []
j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
    "format=duration,size,bit_rate:stream=codec_name,width,height,r_frame_rate,sample_rate,channels,nb_frames",
    "-of", "json", src], capture_output=True, text=True).stdout)
rep.append("## Spesifikasi\n```\n" + json.dumps(j, indent=1) + "\n```")
dur = float(j["format"]["duration"])
rep.append(f"- Tempoh: **{dur:.3f} s** ({int(dur // 60)}:{dur % 60:06.3f}) — {'✅ 30:00' if abs(dur - 1800) < 0.1 else '❌'}")
r = subprocess.run(["ffmpeg", "-v", "info", "-i", src, "-vf", "blackdetect=d=0.5:pix_th=0.08", "-af", "ebur128=peak=true",
                    "-f", "null", "-"], capture_output=True, text=True).stderr
blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)", r)
rep.append("- Segmen hitam (≥0.5 s): " + (", ".join(f"{float(a):.1f}–{float(b):.1f}s" for a, b, _ in blacks) or "tiada"))
summ = r[r.rfind("Summary:"):]
I = re.search(r"I:\s+(-?[\d.]+) LUFS", summ); LRA = re.search(r"LRA:\s+([\d.]+) LU", summ); TP = re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ)
rep.append(f"- Loudness bersepadu: **{I.group(1)} LUFS**, LRA {LRA.group(1)} LU, true peak **{TP.group(1)} dBTP**")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_video as bv
bv.build_edl(); ev = dict(bv.overlay_events())
moments = {k: ev[k] + (2.5 if not k.startswith(("title", "credits", "end")) else 4.5) for k in
           ["title_open", "phase_set_induksi", "popup_guru1", "popup_guru2", "steps_misi1", "steps_misi2", "ayat_misi2", "popup_guru3",
            "steps_ar", "ayat_galeri1", "ayat_galeri2", "phase_penutup", "ayat_rumusan", "credits_1", "credits_2", "credits_3", "end_title"]}
for k, t in moments.items():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", src, "-frames:v", "1", "-vf", "scale=640:-2",
                    os.path.join(out, f"qc_{t:07.1f}_{k}.jpg")], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-pattern_type", "glob", "-i", os.path.join(out, "qc_*.jpg"),
                "-vf", "tile=4x5", "-frames:v", "1", os.path.join(out, "qc_contact_sheet.jpg")], check=True)
open(os.path.join(out, "qc_report.md"), "w").write("# Laporan QC\n\n" + "\n".join(rep) + "\n")
print("\n".join(rep[1:]))
