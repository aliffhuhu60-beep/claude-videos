"""Jana asset_inventory.csv (semua fail + kegunaan). Usage: python3 07_PROJECT_FILES/make_inventory.py <v2cuts.txt>"""
import csv, os, subprocess, json, sys
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, "07_PROJECT_FILES"); import build_video as b
rows = [["jenis", "fail", "segmen/julat", "resolusi", "fps", "tempoh_s", "audio", "kandungan", "sync_ke_vid1_s", "kegunaan_dalam_video"]]
def probe(p):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels", "-of", "json", p], capture_output=True, text=True).stdout)
    v = [s for s in j["streams"] if s["codec_type"] == "video"][0]; a = [s for s in j["streams"] if s["codec_type"] == "audio"][0]
    return f'{v["width"]}x{v["height"]} {v["codec_name"]}', v["r_frame_rate"], float(j["format"]["duration"]), f'{a["codec_name"]} {a["sample_rate"]}Hz {a["channels"]}ch'
info = {"vid sintaksis 1.MOV": "Kamera wide statik (belakang kelas) - keseluruhan PdP 48 min, 3 guru; audio induk",
        "vid sintaksis 2.MOV": "Himpunan B-roll pegang tangan (eksport CapCut, 74 klip; logo CapCut 2 s di hujung)",
        "vid3.mp4": "Murid membaca ayat aktif -> pasif, 'Betulkah, kelas?' 'Betul!', tepukan"}
use = {"vid sintaksis 1.MOV": "Rakaman induk + audio dialog semua babak; latar kredit",
       "vid sintaksis 2.MOV": "Cutaway/B-roll tersegerak (gambar + audio mikrofon dekat)", "vid3.mp4": "Babak 9 rumusan (28:01-28:30)"}
for f in ["vid sintaksis 1.MOV", "vid sintaksis 2.MOV", "vid3.mp4"]:
    r, fps, d, a = probe("01_RAW_VIDEO/" + f)
    rows.append(["video_asal", f, "penuh", r, fps, round(d, 2), a, info[f], {"vid3.mp4": str(b.V3_OFFSET)}.get(f, "rujukan" if "1" in f else "lihat segmen"), use[f]])
desc = {0: "Papan putih: SP 5.3.3, objektif", 1: "Guru 1 + slaid Selamat Datang ke Hotel Hijau", 2: "Guru 1 panggil-sahut Pengawal Bahasa / Sedia cikgu",
        3: "Wide kelas, slaid kuning", 4: "Gambar HOTEL HIJAU di skrin", 5: "Murid menonton", 6: "Guru menulis di papan putih", 7: "Murid (reaksi)",
        8: "Murid menulis jawapan di papan putih", 9: "Guru 1 di papan putih", 10: "Wide kelas", 11: "Murid menulis di papan putih", 12: "Guru 1 + slaid kuning",
        13: "Guru 1 menerangkan objektif", 14: "Kumpulan murid", 15: "Close-up tablet", 16: "Close-up tablet (Minecraft)", 17: "Guru 2 di skrin HOTEL HIJAU (Minecraft)",
        18: "Kumpulan", 19: "Guru 2 di skrin Minecraft", 20: "Wide kelas", 21: "Guru 2 di skrin", 22: "Close-up tablet Minecraft", 23: "Close-up tablet Minecraft",
        24: "Guru 2 di skrin", 25: "Wide kumpulan", 26: "Guru 2 membimbing kumpulan", 27: "Guru 2 membimbing kumpulan", 28: "Wide kelas", 29: "Wide kelas",
        30: "Guru 2 di skrin Minecraft", 31: "Skrin Minecraft (teks)", 32: "Kabur", 33: "Murid dengan tablet", 34: "Close-up wajah tersenyum",
        35: "Guru 2 menerangkan teks situasi", 36: "Guru 2 membimbing kumpulan", 37: "Guru 2 berjalan", 38: "Wide kelas",
        39: "Guru 3 + Ruang Guru, murid menghantar jawapan, perbincangan ayat (4.5 min)", 40: "Galeri jawapan (hamparan) di skrin", 41: "Close-up galeri jawapan",
        42: "Tiket refleksi (3 min)", 43: "Kabur", 44: "Murid berbincang", 45: "Wide", 46: "Murid menulis di papan putih", 47: "Kumpulan dengan tablet", 48: "Kumpulan",
        49: "Kumpulan dengan tablet", 50: "Kumpulan dengan tablet", 51: "Murid menggunakan tablet", 52: "Close-up tablet", 53: "Kumpulan", 54: "Close-up menaip ayat dalam Minecraft",
        55: "Close-up tablet Minecraft", 56: "Kumpulan", 57: "Klip menegak", 58: "Borang Ruang Guru - NAMA MURID kelihatan", 59: "Guru 3 di skrin Ruang Guru",
        60: "Close-up menaip", 61: "Komputer riba", 62: "Kelas wide", 63: "Kelas", 64: "Interaksi guru-murid", 65: "Wajah tersenyum", 66: "Tiket refleksi",
        67: "Tiket refleksi + tablet", 68: "Tiket refleksi", 69: "Tiket refleksi", 70: "Tiket refleksi", 71: "Kumpulan", 72: "Tiket refleksi", 73: "Logo CapCut"}
EXCL = {32: "kabur", 43: "kabur", 57: "klip menegak", 58: "privasi: nama murid", 73: "logo CapCut"}
cuts = [float(x) for x in open(sys.argv[1]).read().split()]
b.build_edl(); used = {}
for c in b.clips:
    t = f'{int(c["t_final"] // 60):02d}:{c["t_final"] % 60:04.1f}'
    if c["label"].startswith("seg"): used.setdefault(int(c["label"][3:].split("@")[0]), []).append(t)
    elif c["src"] == "v2": used.setdefault(next(i for i in range(len(cuts) - 1) if cuts[i] <= c["start"] < cuts[i + 1]), []).append(t + " (montaj)")
for i in range(len(cuts) - 1):
    s, e = cuts[i], cuts[i + 1]; sy = b.SYNC.get(i)
    if i in EXCL: u = "DIKECUALIKAN (" + EXCL[i] + ")"
    elif i in used: u = "Masa akhir (v2): " + "; ".join(used[i])
    else: u = "simpanan (tidak digunakan)"
    rows.append(["broll_segmen", "vid sintaksis 2.MOV", f"seg{i}: {s:.1f}-{e:.1f}", "1280x720", "30", round(e - s, 1), "aac", desc.get(i, ""), f"{sy[2]:.2f}" if sy else "tidak pasti", u])
for f in sorted(os.listdir("05_GRAPHICS")):
    if f.endswith(".mov") or (f.endswith(".png") and f.startswith("progress")):
        rows.append(["grafik", f, "", "1920x1080 RGBA", "30", "", "", "Motion graphics (graphics.py)", "", "overlay"])
for f in sorted(os.listdir("02_AUDIO")):
    rows.append(["audio", f, "", "", "", "", "48kHz stereo", "Muzik/SFX asli dijana (music.py) - bebas hak cipta", "", "muzik latar / kesan bunyi"])
csv.writer(open("asset_inventory.csv", "w", newline="")).writerows(rows)
print(len(rows), "baris")
