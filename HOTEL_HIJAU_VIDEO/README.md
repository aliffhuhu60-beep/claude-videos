# MISI PENGAWAL BAHASA: HOTEL HIJAU — Projek Video Dokumentasi PdP

Bahasa Melayu Tahun 5 · Ayat Aktif dan Ayat Pasif (SP 5.3.3) · 3 guru · **30:00 tepat**

| Guru | Nama | Jawatan | Blok dalam video |
|---|---|---|---|
| 01 | MOHAMAD ALIFF BIN AHMAD SHAHABUDDIN | PENGURUS HOTEL HIJAU | 00:00 – 10:00 |
| 02 | MUHAMMAD IMAN IRFAN BIN MOHD RAMZI | KETUA PEMANTAU ZON | 10:00 – 20:00 |
| 03 | AMIN NAJMI BIN MOHYIDIN | KETUA PENGAWAL BAHASA | 20:00 – 30:00 |

Penutup mengandungi penghargaan kepada **DR. RASIDAYANTY BINTI SAION (Pensyarah Kursus Pedagogi)** dan **KELUARGA BMONETHO**, diikuti slogan **JAGA ALAM, JAGA BAHASA**.

## Hasil
| # | Hasil | Lokasi |
|---|---|---|
| 1 | Storyboard lengkap | `storyboard.md` |
| 2 | Senarai semua klip & aset | `asset_inventory.csv`, `07_PROJECT_FILES/edl.csv` (95 potongan, masa akhir ↔ masa sumber) |
| 3 | Video rough cut (tanpa grafik/muzik, 720p) | `08_PREVIEW/ROUGH_CUT_Hotel_Hijau_720p.mp4` |
| 4 | **Video akhir MP4** (1080p30, H.264, AAC 48 kHz stereo) | `09_FINAL_EXPORT/MISI_PENGAWAL_BAHASA_Hotel_Hijau_1080p.mp4` |
| 5 | Sari kata SRT (dialog yang dapat dikenal pasti) | `06_SUBTITLES/MISI_PENGAWAL_BAHASA_Hotel_Hijau.ms.srt` |
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

# 1. Grafik (≈10 min)
python3 07_PROJECT_FILES/graphics.py 05_GRAPHICS

# 2. Muzik & SFX asli (≈5 min)
python3 07_PROJECT_FILES/music.py 02_AUDIO intro=280 upbeat=450 tech=260 motiv=380 piano=200 closing=95

# 3. EDL + sari kata
python3 07_PROJECT_FILES/build_video.py edl
python3 07_PROJECT_FILES/build_video.py subs

# 4. Render klip (gred warna + audio dialog) → rough cut
python3 07_PROJECT_FILES/build_video.py clips
python3 07_PROJECT_FILES/build_video.py rough

# 5. Video akhir (grafik + muzik + ducking + loudnorm)
python3 07_PROJECT_FILES/build_video.py final            # 1080p → 09_FINAL_EXPORT
python3 07_PROJECT_FILES/build_video.py final --preview  # 720p pantas → 08_PREVIEW

# 6. Semakan kualiti (tempoh, skrin hitam, loudness, lembaran visual)
python3 07_PROJECT_FILES/qc_check.py 09_FINAL_EXPORT/MISI_PENGAWAL_BAHASA_Hotel_Hijau_1080p.mp4 08_PREVIEW/qc
```
Fail sementara klip disimpan dalam `07_PROJECT_FILES/_work/` (atau `$HH_WORK`).

### (Pilihan) Menjana semula data penyegerakan B-roll
```bash
ffmpeg -i "01_RAW_VIDEO/vid sintaksis 1.MOV" -ac 1 -ar 16000 v1.wav
ffmpeg -i "01_RAW_VIDEO/vid sintaksis 2.MOV" -ac 1 -ar 16000 v2.wav
python3 07_PROJECT_FILES/sync_broll.py v1.wav v2.wav 07_PROJECT_FILES/broll_cuts.txt 07_PROJECT_FILES/broll_sync.csv
```

## Mengubah suai
- **Nama/jawatan/aktiviti guru:** `TEACHERS` dalam `graphics.py` → jalankan semula langkah 1 dan 5.
- **Teks penghargaan:** `credits_1` / `credits_2` / `credits_3` dalam `graphics.py`.
- **Potongan / susunan babak:** `build_edl()` dalam `build_video.py` (masa dalam saat fail sumber). Skrip akan menolak sebarang EDL yang tidak tepat 30:00.
- **Masa grafik:** `overlay_events()`; **muzik:** `music_plan()`; **SFX:** `sfx_plan()`.

## Muat turun video
Video akhir ~1 GB. Jika repositori menggunakan Git LFS, `git lfs pull` akan memuat turun fail MP4. Jika fail dipecahkan kepada bahagian (`*.mp4.part-aa`, `-ab`, …), cantumkan semula:
```bash
cat 09_FINAL_EXPORT/MISI_PENGAWAL_BAHASA_Hotel_Hijau_1080p.mp4.part-* > MISI_PENGAWAL_BAHASA_Hotel_Hijau_1080p.mp4
```

## Bahan yang belum mencukupi (tidak direka)
- Tiada establishing shot luaran / bangunan "hotel" → digunakan wide shot kelas dan slaid Hotel Hijau.
- Tiada shot ketiga-tiga guru bersama → penutup memaparkan setiap guru berturutan + kad nama.
- Tiada rakaman "empat skrin kumpulan" serentak atau close-up kad warna/nombor giliran yang jelas.
- Tiada muzik dibekalkan → muzik asli bebas hak cipta dijana.
- Audio kamera induk direkam dari belakang kelas (jauh) → kejelasan dialog terhad; sari kata hanya untuk dialog yang pasti.
- Sumber 480p/720p → eksport 1080p (4K tidak bermakna).
- **Kebenaran penerbitan wajah murid** perlu disahkan oleh pihak sekolah/guru sebelum tayangan awam.
