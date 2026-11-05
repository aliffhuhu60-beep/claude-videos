# Keputusan Suntingan — Versi 4

## Perubahan versi 4 (maklum balas ke atas versi 3)
| # | Permintaan | Pelaksanaan |
|---|---|---|
| 1 | Babak berulang dua kali di awal sebelum pengenalan guru | Punca: `vid sintaksis 2.MOV` ialah kompilasi yang sudah dipotong (80 potongan babak), tetapi sebelum ini setiap segmen diselaraskan dengan **satu** offset → sesetengah cebisan terlari 6–17 s (salam "Baiklah, assalamualaikum" didengar dua kali). Kini **setiap babak** vid2 diselaraskan berasingan (`piecewise_sync.py`, `v2_cuts.txt` daripada `scdet`, `broll_sync_v2.csv`). Set Induksi bermula pada salam (vid1 00:15). Sari kata dipetakan semula ke garis masa baharu (`remap_cues`, rujukan `subs_timebase_edl.json`); baris berulang dibuang. |
| 2 | Tiada kaburan semasa Cikgu 3 menerangkan ayat murid | Kaburan Galeri Jawapan **dibuang** (`PRIVACY_MASKS = []`). ⚠️ Lajur nama murid pada skrin kini kelihatan — pastikan kebenaran. |
| 3 | Paparan ayat lebih tepat, jelas & lengkap | Panel ayat direka semula: lebih besar (font 42), ayat aktif **dan** pasif dipaparkan penuh (tidak terpotong), ayat pasif muncul **ketika disebut**. Panel Galeri kini mengikut perbincangan sebenar Cikgu 3: **22:10** *Amin menuai pokok jagung di ladang organik → Pokok jagung dituai oleh Amin di ladang organik* (semakan sistem: Salah — "Nyatakan objek…"); **23:00** *Amin memasang lampu di lobi hotel → Lampu dipasang di lobi hotel oleh Amin* (Betul). Teks disalin tepat daripada Galeri Jawapan. |
| 4 | Suara murid/jurukamera pada B-roll disenyapkan + muzik; tiada muzik semasa PdP | 12 selang B-roll murid (`STUDENT_BROLL_V2`, ≥5 s, jumlah ~3.7 min): audio asal **disenyapkan**, diganti muzik fasa (`build_music_bed`). Muzik **dibuang** sepenuhnya semasa guru mengajar; hanya tajuk pembukaan & kredit penutup mengekalkan muzik. |
| 5 | (semakan tambahan) | Shot muka jurukamera rapat ke lensa (vid2 1338.6–1341.1) & babak terhalang lain dikecualikan secara kekal (`EXCLUDE_V2`). |

# Keputusan Suntingan — Versi 3

## Perubahan versi 3 (maklum balas ke atas versi 2)
| # | Permintaan | Pelaksanaan |
|---|---|---|
| 1 | Pop-up guru jangan terlalu besar | Pop-up dikecilkan kepada **66%** saiz asal (≈1200×310 px pada 1440p, sudut bawah-kiri), dipaparkan **7 s**. |
| 2 | Pop-up Guru 2 & 3 tidak kelihatan | Pop-up dipindahkan ke **shot close-up** guru: Guru 1 **00:14**, Guru 2 **10:59** (sebelah skrin Minecraft), Guru 3 **18:47** (berdiri di hadapan kelas; sebelum ini 18:15 pada shot luas di mana Guru 3 kelihatan kecil). |
| 3 | Suara guru lebih kuat | Penguat suara (`VOICE`): high-pass 100 Hz, −2 dB @250 Hz, **+5 dB @3 kHz** (kejelasan), pemampat 3:1 + gandaan 5 dB; muzik latar **−4 dB**; ducking lebih kuat (ambang 0.02, nisbah 8:1); loudness akhir **−14 LUFS** (sebelum ini −16). |
| 4 | Sari kata semasa guru bercakap | Transkripsi padat baharu (`transcribe_dense.py`, tetingkap 30 s tanpa VAD) → **38 baris tambahan disemak manual** (`transcript_dense_edits.json`); jumlah **127 baris** (sebelum ini 89). Baris yang tidak jelas/halusinasi/nama murid tidak dimasukkan. |

# Keputusan Suntingan — Versi 2

## Perubahan berbanding versi 1 (mengikut maklum balas)
| # | Permintaan | Pelaksanaan |
|---|---|---|
| 1 | Pengenalan Guru 2 pada bahagian yang ditunjukkan (Guru 2 di skrin Minecraft) | Pertukaran sebenar dikesan pada **15:11** rakaman induk: Guru 1 beredar ke kanan dan Guru 2 berdiri di hadapan skrin pada 15:13. Bahagian 10:55–15:11 ialah **masih Guru 1** (disahkan melalui close-up wajah). Kad fasa LANGKAH 1 muncul pada **09:42** (pertukaran guru); **pop-up Guru 02 muncul pada 10:59**, iaitu pada shot close-up Guru 2 berdiri di sebelah skrin Minecraft (bahagian yang ditunjukkan dalam maklum balas). |
| 2 | Babak ikut fasa: Set Induksi, Langkah 1, Langkah 2, Penutup (Refleksi) | Kad "BABAK 01–06" diganti **kad fasa PdP**: SET INDUKSI (Guru 1), LANGKAH 1 – Misi Minecraft (Guru 2), LANGKAH 2 – Aktiviti AR & Galeri Jawapan (Guru 3), PENUTUP (REFLEKSI) – tiket refleksi & rumusan (Guru 3). |
| 3 | Kurangkan shot yang ada 2 jurukamera dalam frame; buang orang lalu depan kamera | **Pengesanan orang automatik (YOLOv8n)** pada setiap 0.5 s rakaman induk. Untuk setiap saat, sistem memilih framing (wide / front / left / right / center) yang **mengelak orang berdiri & orang dekat kamera**. Jika tidak dapat dielakkan, gambar ditukar kepada **cutaway aktiviti murid** (suara cikgu diteruskan). Babak Guru 2 melintas depan kamera (28:26–28:55) **dibuang**. Semakan ketajaman B-roll menemui 3 lagi babak orang/objek lalu rapat di depan kamera atau kamera dihayun laju (awal Penutup, Galeri Jawapan, Misi 2); semuanya **dipotong**. Saat terhalang: 79 → 34 (baki ialah pertindihan kecil terpencil); saat dengan orang berdiri dalam frame: 267 → 108. Lebih banyak B-roll close-up guru digunakan. |
| 4 | Sari kata jelas, key point berwarna & bold | Sari kata **dibakar** ke dalam video (ASS, Inter SemiBold, kotak hijau gelap). **Ayat aktif / kata kerja / Pengawal Bahasa = emas bold**; **ayat pasif / Hotel Hijau / situasi / Betul = hijau bold**. Fail `.srt` dan `.ass` juga disertakan. |
| 5 | Video lebih tajam & resolusi tinggi | Eksport **2560×1440 (1440p)**. Rantaian: nyah-hingar `hqdn3d` → skala Lanczos → **penajaman adaptif CAS** + unsharp ringan (kamera induk); CAS ringan (B-roll). Bitrate maksimum 8 Mbps (fail < 2 GB supaya boleh disimpan dalam GitHub LFS). |
| 6 | Motion grafik menerangkan langkah aktiviti | Panel **Langkah Aktiviti** (langkah muncul satu demi satu): *Misi 1 · Stesen Minecraft*, *Misi 2 · Tukar Ayat*, *Aktiviti AR*. Kandungan disalin daripada teks sebenar pada skrin Minecraft & aplikasi AR. |
| 7 | Motion grafik untuk ayat yang dibina murid | Panel **Ayat Murid (AKTIF → PASIF)** dengan kata kerja diserlahkan: arahan Misi 2, 3 pasangan ayat daripada **Galeri Jawapan** (Google Sheet di skrin), dan ayat rumusan murid. |
| 8 | Tajuk awal: SIMULASI PENGAJARAN MIKRO (MICRO TEACHING), tiada preview | Tajuk 8 s pada latar hijau legap — **tiada montaj/preview rakaman**. |
| 9 | Buang label GURU 01/02/03 di bawah video | Bar kemajuan & label **dibuang sepenuhnya**. |

## Pengenalan guru
| Guru | Ciri | Tempoh dalam rakaman induk | Bukti |
|---|---|---|---|
| 01 MOHAMAD ALIFF | polo maroon, wajah lebih berisi, berkaca mata | 00:17 – 15:11 | membuka PdP, slaid Selamat Datang, dunia Minecraft Hotel Hijau |
| 02 MUHAMMAD IMAN IRFAN | polo maroon, wajah lebih kurus, berkaca mata | 15:11 – 28:26 | Misi 1 & 2 di Minecraft; buku Minecraft tertulis "Nama: Iman" |
| 03 AMIN NAJMI | jersi merah-hitam | 28:55 – 47:30 | aplikasi AR, Galeri Jawapan, tiket refleksi |

## Kandungan grafik (hanya daripada rakaman — tiada rekaan)
- **Misi 1:** "STESEN 1: Baca SOALAN di papan, pijak petak HIJAU untuk jawab."
- **Misi 2:** "Tukar kepada ayat aktif: 'Sayur-sayuran dituai oleh tukang kebun di ladang organik.' Tulis NAMA dan jawapan kamu dalam buku. Letak buku di lectern." + aktiviti "Tuai 3 lobak merah dengan cangkul".
- **Aplikasi AR:** borang *Selamat datang, Pengawal Bahasa!* (nama, kelas, Mula Kamera) → Situasi 1–4 → "Perhatikan animasi, kemudian bina satu ayat aktif dan satu ayat pasif menggunakan kata kerja itu" → Hantar.
- **Galeri Jawapan:** lajur Situasi · Kata Kerja · Ayat Aktif · Sistem · Sebab · Ayat Pasif (contoh: *Amin mengasingkan sampah mengikut tong warna kitar semula → Sampah diasingkan oleh Amin mengikut tong warna kitar semula*).

## Sari kata — kaedah & had
- Transkripsi Whisper *large-v3-turbo* pada trek dialog akhir, kemudian **disemak manual baris demi baris** (`07_PROJECT_FILES/transcript_edits.json`): dibetulkan dengan rujukan silang kepada papan putih, skrin dan transkripsi mikrofon dekat; baris yang tidak pasti **dibuang** (lebih baik tiada sari kata daripada sari kata salah).
- Mikrofon kamera induk berada di belakang kelas, jadi sesetengah bahagian (terutama semasa kerja kumpulan) tidak cukup jelas untuk disarikatakan.
- Nama murid dibuang daripada sari kata.

## Privasi
- Dikecualikan: skrin borang AR & Galeri Jawapan yang memaparkan **nama penuh murid** (B-roll seg40, seg58, v2 553–566).
- **Lajur "Nama" pada skrin Galeri Jawapan dikaburkan** (`PRIVACY_MASKS` dalam `build_video.py`).
- Wajah murid masih kelihatan — sila pastikan kebenaran penerbitan sebelum tayangan awam.

## Audio & warna
Sama seperti versi 1: dialog (high-pass, `afftdn`, `dynaudnorm`), muzik asli bebas hak cipta (`music.py`) mengikut fasa (pembukaan orkestra → intro korporat → upbeat Minecraft → tech ambient AR → piano refleksi → penutup inspirasi), ducking sidechain, `loudnorm` −16 LUFS / −1.5 dBTP. Gred warna semula jadi.
