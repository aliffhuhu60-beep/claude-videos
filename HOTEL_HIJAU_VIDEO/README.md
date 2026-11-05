# SIMULASI PENGAJARAN MIKRO (MICRO TEACHING) — Misi Pengawal Bahasa: Hotel Hijau

Bahasa Melayu Tahun 5 · Ayat Aktif dan Ayat Pasif (SP 5.3.3) · 3 guru · **30:00 tepat**

| Guru | Nama | Jawatan | Blok dalam video |
|---|---|---|---|
| 01 | MOHAMAD ALIFF BIN AHMAD SHAHABUDDIN | PENGURUS HOTEL HIJAU | 00:08 – 09:42 · Set Induksi |
| 02 | MUHAMMAD IMAN IRFAN BIN MOHD RAMZI | KETUA PEMANTAU ZON | 09:42 – 18:13 · Langkah 1 |
| 03 | AMIN NAJMI BIN MOHYIDIN | KETUA PENGAWAL BAHASA | 18:13 – 29:17 · Langkah 2 & Penutup (Refleksi) |

Penutup mengandungi penghargaan kepada **DR. RASIDAYANTY BINTI SAION (Pensyarah Kursus Pedagogi)** dan **KELUARGA BMONETHO**, diikuti slogan **JAGA ALAM, JAGA BAHASA**.

## Hasil
| # | Hasil | Lokasi |
|---|---|---|
| 1 | Storyboard lengkap | `storyboard.md` |
| 2 | Senarai semua klip & aset | `asset_inventory.csv`, `07_PROJECT_FILES/edl.csv` (133 potongan, masa akhir ↔ masa sumber, framing) |
| 3 | Video rough cut (tanpa grafik/muzik, 720p) | `08_PREVIEW/ROUGH_CUT_Hotel_Hijau_720p.mp4` |
| 4 | **Video akhir MP4** (1440p30, H.264, AAC 48 kHz stereo, sari kata dibakar) | `09_FINAL_EXPORT/SIMULASI_PENGAJARAN_MIKRO_Hotel_Hijau_1440p_v4.mp4` |
| 5 | Sari kata (SRT + ASS berwarna) | `06_SUBTITLES/` — semakan manual: `07_PROJECT_FILES/transcript_edits.json` |
| 6 | Skrip penyuntingan FFmpeg/Python | `07_PROJECT_FILES/*.py` |
| 7 | Aset motion graphics | `05_GRAPHICS/` (*.mov ber-alpha + *_still.png) |
| 8 | Keputusan suntingan & senarai semak | `edit_decisions.md` |

> Fail video besar (>100 MB) disimpan menggunakan **Git LFS** atau dipecah kepada beberapa bahagian — lihat bahagian *Muat turun video* di bawah.

## Struktur folder
```
HOTEL_HIJAU_VIDEO/
├── 01_RAW_VIDEO/      fail asal (TIDAK diubah; tidak disimpan dalam git — muat turun dari Google Drive)
├── 02_AUDIO/          muzik & SFX asli (dijana oleh music.py)
├── 03_IMAGES/         (kosong — tiada gambar dibekalkan)
├── 04_BROLL/          (B-roll dibaca terus dari 01_RAW_VIDEO/vid sintaksis 2.MOV)
├── 05_GRAPHICS/       pop-up guru, tajuk babak, lower third, tajuk pembukaan/penutup, kredit
├── 06_SUBTITLES/      fail SRT
├── 07_PROJECT_FILES/  skrip, EDL, data penyegerakan, filtergraph akhir
├── 08_PREVIEW/        rough cut & preview
├── 09_FINAL_EXPORT/   video akhir
├── storyboard.md · asset_inventory.csv · edit_decisions.md · README.md
```

## Cara menghasilkan semula video
Keperluan: Linux/macOS, **FFmpeg ≥ 6**, **Python ≥ 3.10** dengan `numpy` dan `Pillow`, font **Inter** (`/usr/share/fonts/opentype/inter/`). Pilihan: `faster-whisper` (hanya untuk transkripsi).

```bash
cd HOTEL_HIJAU_VIDEO
# 0. Letakkan fail asal dalam 01_RAW_VIDEO/: "vid sintaksis 1.MOV", "vid sintaksis 2.MOV", "vid3.mp4"
#    Keperluan tambahan: pip install faster-whisper opencv-python-headless onnxruntime

# 1. (Pilihan) Pengesanan orang — sudah disimpan dalam 07_PROJECT_FILES/det_v1.jsonl
python3 07_PROJECT_FILES/detect.py yolov8n.onnx "01_RAW_VIDEO/vid sintaksis 1.MOV" 07_PROJECT_FILES/det_v1.jsonl 2

# 2. EDL (framing automatik, cutaway, fasa) + konfigurasi grafik
python3 07_PROJECT_FILES/build_video.py edl

# 3. Grafik 1440p & muzik asli
python3 07_PROJECT_FILES/graphics.py 05_GRAPHICS 07_PROJECT_FILES/gfx_config.json
python3 07_PROJECT_FILES/music.py 02_AUDIO intro=600 upbeat=540 tech=480 motiv=60 piano=240 closing=60 opening=40

# 4. Trek dialog -> sari kata (transkripsi + semakan manual transcript_edits.json)
python3 07_PROJECT_FILES/build_video.py audio
python3 07_PROJECT_FILES/build_video.py subs

# 5. Klip 1440p -> rough cut -> video akhir
python3 07_PROJECT_FILES/build_video.py clips
python3 07_PROJECT_FILES/build_video.py rough
python3 07_PROJECT_FILES/build_video.py final            # -> 09_FINAL_EXPORT (1440p)
python3 07_PROJECT_FILES/build_video.py final --preview  # -> 08_PREVIEW (720p)

# 6. Semakan kualiti
python3 07_PROJECT_FILES/qc_check.py 09_FINAL_EXPORT/SIMULASI_PENGAJARAN_MIKRO_Hotel_Hijau_1440p_v4.mp4 08_PREVIEW/qc
```
Fail sementara klip disimpan dalam `07_PROJECT_FILES/_work/` (atau `$HH_WORK`).

### (Pilihan) Menjana semula data penyegerakan B-roll
```bash
ffmpeg -i "01_RAW_VIDEO/vid sintaksis 1.MOV" -ac 1 -ar 16000 v1.wav
ffmpeg -i "01_RAW_VIDEO/vid sintaksis 2.MOV" -ac 1 -ar 16000 v2.wav
python3 07_PROJECT_FILES/sync_broll.py v1.wav v2.wav 07_PROJECT_FILES/broll_cuts.txt 07_PROJECT_FILES/broll_sync.csv
```

## Mengubah suai
- **Nama/jawatan guru, fasa, langkah aktiviti, ayat murid:** `TEACHERS`, `PHASES`, `STEPS`, `SENTENCES` dalam `graphics.py`.
- **Sari kata:** betulkan/buang baris dalam `07_PROJECT_FILES/transcript_edits.json`, kemudian `build_video.py subs` + `final`.
- **Teks penghargaan:** `credits_1` / `credits_2` / `credits_3` dalam `graphics.py`.
- **Potongan / susunan:** `PLAN` dalam `build_video.py` (masa saat fail sumber); span `FLEX` dilaraskan automatik supaya tepat 30:00.
- **Masa grafik:** `overlay_events()`; **muzik:** `music_plan()`; **SFX:** `sfx_plan()`.

## Muat turun video
Video akhir ~1.8 GB (1440p, ≤ 8 Mbps). Jika repositori menggunakan Git LFS, `git lfs pull` akan memuat turun fail MP4. Jika fail dipecahkan kepada bahagian (`*.mp4.part-aa`, `-ab`, …), cantumkan semula:
```bash
cat 09_FINAL_EXPORT/*.mp4.part-* > video.mp4
```

## Bahan yang belum mencukupi (tidak direka)
- Tiada establishing shot luaran / bangunan "hotel" → digunakan wide shot kelas dan slaid Hotel Hijau.
- Tiada shot ketiga-tiga guru bersama → kad penutup menyenaraikan ketiga-tiga guru.
- Tiada rakaman "empat skrin kumpulan" serentak atau close-up kad warna/nombor giliran yang jelas.
- Tiada muzik dibekalkan → muzik asli bebas hak cipta dijana.
- Audio kamera induk direkam dari belakang kelas (jauh) → sesetengah dialog (terutama kerja kumpulan) tidak dapat disarikatakan dengan yakin.
- Sumber 480p/720p → dinaikkan ke 1440p dengan nyah-hingar + penajaman adaptif (bukan AI upscaling; tiada GPU).
- **Kebenaran penerbitan wajah murid** perlu disahkan oleh pihak sekolah/guru sebelum tayangan awam.
