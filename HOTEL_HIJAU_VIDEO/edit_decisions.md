# Keputusan Suntingan — Versi 2

## Perubahan berbanding versi 1 (mengikut maklum balas)
| # | Permintaan | Pelaksanaan |
|---|---|---|
| 1 | Pengenalan Guru 2 pada bahagian yang ditunjukkan (Guru 2 di skrin Minecraft) | Pertukaran sebenar dikesan pada **15:11** rakaman induk: Guru 1 beredar ke kanan dan Guru 2 berdiri di hadapan skrin pada 15:13. Bahagian 10:55–15:11 ialah **masih Guru 1** (disahkan melalui close-up wajah). Pop-up Guru 02 kini muncul pada **09:43** video. |
| 2 | Babak ikut fasa: Set Induksi, Langkah 1, Langkah 2, Penutup (Refleksi) | Kad "BABAK 01–06" diganti **kad fasa PdP**: SET INDUKSI (Guru 1), LANGKAH 1 – Misi Minecraft (Guru 2), LANGKAH 2 – Aktiviti AR & Galeri Jawapan (Guru 3), PENUTUP (REFLEKSI) – tiket refleksi & rumusan (Guru 3). |
| 3 | Kurangkan shot yang ada 2 jurukamera dalam frame; buang orang lalu depan kamera | **Pengesanan orang automatik (YOLOv8n)** pada setiap 0.5 s rakaman induk. Untuk setiap saat, sistem memilih framing (wide / front / left / right / center) yang **mengelak orang berdiri & orang dekat kamera**. Jika tidak dapat dielakkan, gambar ditukar kepada **cutaway aktiviti murid** (suara cikgu diteruskan). Babak Guru 2 melintas depan kamera (28:26–28:55) **dibuang**. Saat terhalang: 79 → 34 (baki ialah pertindihan kecil terpencil); saat dengan orang berdiri dalam frame: 267 → 108. Lebih banyak B-roll close-up guru digunakan. |
| 4 | Sari kata jelas, key point berwarna & bold | Sari kata **dibakar** ke dalam video (ASS, Inter SemiBold, kotak hijau gelap). **Ayat aktif / kata kerja / Pengawal Bahasa = emas bold**; **ayat pasif / Hotel Hijau / situasi / Betul = hijau bold**. Fail `.srt` dan `.ass` juga disertakan. |
| 5 | Video lebih tajam & resolusi tinggi | Eksport **2560×1440 (1440p)**. Rantaian: nyah-hingar `hqdn3d` → skala Lanczos → **penajaman adaptif CAS** + unsharp ringan (kamera induk); CAS ringan (B-roll). Bitrate sehingga 16 Mbps. |
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
- Wajah murid masih kelihatan — sila pastikan kebenaran penerbitan sebelum tayangan awam.

## Audio & warna
Sama seperti versi 1: dialog (high-pass, `afftdn`, `dynaudnorm`), muzik asli bebas hak cipta (`music.py`) mengikut fasa (pembukaan orkestra → intro korporat → upbeat Minecraft → tech ambient AR → piano refleksi → penutup inspirasi), ducking sidechain, `loudnorm` −16 LUFS / −1.5 dBTP. Gred warna semula jadi.
