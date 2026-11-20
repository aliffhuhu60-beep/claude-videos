# PODCAST TENGAH JALAN — Slay atau Salah?

Suntingan akhir audio siar akademik *"Slay atau Salah? Bila Bahasa Kita Terpaling Rancu di TikTok"*.

## Fail hasil

| Fail | Keterangan |
|---|---|
| `Podcast_Final_10-11_Minutes.mp4` | Video akhir **10:58.1** · 1920×1080 · 30 fps · H.264 + AAC 48 kHz · sari kata dibakar |
| `Podcast_Subtitles.srt` | Sari kata Bahasa Melayu berasingan (termasuk baris pantun) |
| `Opening_Animated_Ad.mp4` | Iklan pembukaan animasi (10 s) |
| `Azan_Section.mp4` | Bahagian azan seperti dalam video akhir |
| `VQY_Axia_Black_Animated_Ad.mp4` | Iklan animasi VQY Grab Service, Axia hitam (10 s) |
| `Project_Files/` | Skrip suntingan (EDL, timeline, pelan syot, compositor, audio), sumber grafik HTML/Canvas, fail ASS, transkripsi |
| `Assets/` | Fon Poppins, muzik latar asli & kesan bunyi |

## Struktur video (masa sebenar dalam fail akhir)

| # | Bahagian | Masa | Tempoh |
|---|---|---|---|
| 1 | Iklan pembukaan animasi | 0:00.0 – 0:10.0 | 10 s |
| 2 | Intro, pengenalan hos & 2 pantun | 0:10.0 – 1:32.2 | 82 s |
| 3 | Kerancuan bahasa & sintaksis | 1:32.2 – 2:57.8 | 86 s |
| 4 | Ayat 1: POV | 2:57.8 – 4:32.9 | 95 s |
| 5 | Ayat 2: SLAY | 4:32.9 – 6:48.2 | 135 s |
| 6 | Ayat 3: TERPALING | 6:48.2 – 8:38.9 | 111 s |
| 7 | Bahagian azan (muazin sahaja) | 8:38.9 – 8:49.8 | 11 s |
| 8 | Salah atau kreatif? | 8:49.8 – 9:39.0 | 49 s |
| 9 | Iklan VQY Grab Service (Axia hitam) | 9:39.0 – 9:49.0 | 10 s |
| 10 | Penutup, rumusan, pantun | 9:49.0 – 10:52.1 | 63 s |
| 11 | Kredit | 10:52.1 – 10:58.1 | 6 s |

## Keputusan suntingan utama

- **Dua sudut kamera**: `video real 1.mp4` (sudut sisi; fail ini mengandungi rakaman yang sama dua kali, hanya separuh pertama digunakan) dan `IMG_6885.MOV` (sudut depan). Kedua-duanya diselaraskan melalui korelasi audio (offset 20.42 s, ralat < 1 bingkai).
- **Syot**: wide (penubuhan setiap segmen & reaksi pendek), medium & close-up (crop 1.4–1.7× daripada sumber 1080p) mengikut penutur; pertukaran sudut pada setiap potongan jeda supaya tiada *jump cut*; zoom perlahan (4.5%) hanya pada ~1/3 syot panjang.
- **Audio**: audio mikrofon klip (sudut sisi) digunakan; *declip*, high-pass 85 Hz, pengurangan hingar ringan, EQ sederhana, de-esser, kompresor, penyamaan aras setiap penutur, loudness −16 LUFS (puncak −1.7 dBFS).
- **Potongan**: kiraan & arahan pengarah sebelum setiap babak, ulang ambil, gurauan "bukan bertiga", "bye", serta jeda lebih 0.55 s dipendekkan kepada ~0.3 s. Untuk mencapai 10–11 minit, beberapa baris ulasan berulang dibuang (contoh: senarai bentuk kerancuan dalam Segmen 2, ringkasan semula Iman & Ammar selepas Ayat 2, baris "sebab dan akibat" Iman, "Malah guru boleh…", disclaimer lisan & "like/share" — disclaimer kini dipaparkan dalam kredit). **Semua analisis teras tiga ayat, ayat asal, pembetulan gramatis dan perbandingan aktif/pasif dikekalkan.**
- **Sari kata**: ditranskripsi dengan Whisper, kemudian **disemak dan dibetulkan secara manual** berpandukan skrip PDF (audio sebenar diutamakan). Kata kunci akademik = kuning, istilah TikTok/Inggeris = merah jambu lembut. Pantun dipaparkan sebagai rangkap dua baris.
- **Grafik**: 20 panel akademik dalam susun atur skrin-belah (video kekal besar di kiri) — definisi rancu, SUBJEK + PREDIKAT = AYAT, ayat tunggal/majmuk, analisis & pembetulan POV/SLAY/TERPALING, TER- + PALING = kelewahan, ayat pasif (diri pertama/kedua vs ketiga), aktif vs pasif, laras bahasa, Detektif Kapsyen, rumusan. Skrin-belah digunakan ~42% masa perbualan; selebihnya skrin penuh pada wajah hos.
- **Azan**: mengikut arahan terkini — hanya **bunyi awal azan dengan visual muazin** (0–8.83 s klip asal, tanpa diubah kelajuan/pic), tiada muzik, dibingkaikan dengan latar langit petang & siluet masjid serta teks *"Berhenti Sebentar, Menghayati Seruan Ilahi."*
- **Muzik**: muzik latar dijana khas (asli, bebas hak cipta) — hanya pada iklan, 14 s awal intro dan penutup/kredit; **tiada muzik semasa perbualan atau azan**. Bunyi "ting" lembut pada permulaan setiap analisis ayat (seperti dalam skrip).

## Perkara untuk disahkan sebelum penerbitan

1. **Dakwaan "10% lebih murah berbanding Grab\*"** dalam iklan Axia — ditandakan `*` dengan nota "Berdasarkan tawaran yang diberikan. Tertakluk pada pengesahan." Tiada logo Grab rasmi atau nombor telefon digunakan.
2. Video rujukan gaya `1000405693.mp4` **tidak terdapat** dalam folder Google Drive yang diberikan, jadi gaya sari kata/grafik direka berdasarkan penerangan dalam arahan.
3. Beberapa baris audio berbeza sedikit daripada skrip (cth. "masuk ke dalam kelas", "kami bertiga"); sari kata mengikut audio sebenar.

## Bina semula

Skrip dalam `Project_Files/scripts/` (Python 3 + FFmpeg + Playwright/Chromium): `timeline.py` → `audio_build.py` → `plan.py` → `render_gfx.py` → `finalize.sh`. Fail sumber mentah tidak disertakan (simpan di Google Drive).
