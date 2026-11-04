# Keputusan Suntingan (Edit Decisions)

## 1. Bahan yang diperiksa
| Fail | Spesifikasi | Kandungan |
|---|---|---|
| `vid sintaksis 1.MOV` | 854×480 HEVC, 60 fps, 48:11, AAC 44.1 kHz | Kamera wide statik dari belakang kelas — keseluruhan PdP (ketiga-tiga guru) |
| `vid sintaksis 2.MOV` | 1280×720 H.264, 30 fps, 25:00, AAC 44.1 kHz | Himpunan 74 klip B-roll pegang tangan (eksport CapCut) |
| `vid3.mp4` | 1280×720 H.264, 30 fps, 0:28.6, AAC 48 kHz | Murid membaca ayat aktif → pasif + tepukan |

Fail asal **tidak diubah** — semua pemprosesan membaca terus dari `01_RAW_VIDEO/` dan menulis ke folder lain.

## 2. Pengenalan guru (siapa & bila)
Ketiga-tiga guru dikenal pasti secara visual daripada close-up B-roll dan dialog:
| Guru | Ciri visual | Mengajar dalam rakaman induk | Bukti pertukaran |
|---|---|---|---|
| 01 MOHAMAD ALIFF BIN AHMAD SHAHABUDDIN | baju polo maroon "Bmonetho", berkaca mata | 00:17 – ~10:55 | Membuka PdP: *"Baiklah, assalamualaikum semua"*, slaid *Selamat Datang ke Hotel Hijau* |
| 02 MUHAMMAD IMAN IRFAN BIN MOHD RAMZI | baju polo maroon "Bmonetho", berkaca mata, wajah lebih kurus | ~10:55 – ~28:25 | Guru 1 beredar ke kanan, Guru 2 ke skrin Minecraft *HOTEL HIJAU* (10:55–11:07) |
| 03 AMIN NAJMI BIN MOHYIDIN | jersi merah-hitam | ~28:30 – 48:11 | Guru 2: *"Semua suka tak? … Dah, terima kasih!"* (28:05–28:11); Guru 3: *"Jadi, sekarang, tadi awak semua dah belajar tentang ayat aktif dengan ayat pasif, kan?"* (29:21) |

Urutan dalam video mengikut arahan: orang pertama = Guru 1, kedua = Guru 2, ketiga = Guru 3.
> ⚠️ Sila sahkan padanan wajah ↔ nama (terutamanya Guru 1 vs Guru 2 yang memakai baju sama). Jika tertukar, ubah `TEACHERS` dalam `graphics.py` dan jana semula — tiada potongan lain perlu diubah.

## 3. Struktur 30 minit tepat
PdP sebenar berlangsung ~48 minit. Untuk mematuhi tempoh 30:00 dan RPH (3 × 10 minit):
- **Blok Guru 1 → 00:28–10:00**, **Guru 2 → 10:00–20:00**, **Guru 3 → 20:00–28:30**, penutup 28:30–30:00.
- Pop-up Guru 2 dan Guru 3 jatuh tepat pada **10:00** dan **20:00** — pada saat sebenar guru itu mengambil alih (dialog pertukaran sebenar dikekalkan penuh).
- Pemendekan dibuat dengan membuang **masa senyap/peralihan** (murid menulis tanpa dialog, pergerakan kumpulan, menunggu peranti), dan memilih bahagian kerja kumpulan yang berulang. Tiada dialog dipotong di tengah ayat secara sengaja; setiap potongan audio menggunakan crossfade 30 ms.
- Panjang dikunci oleh skrip: `assert nframes() == 54000`.

## 4. Kamera & B-roll
- **Penyegerakan automatik:** setiap klip B-roll dipadankan dengan masa rakaman induk melalui korelasi silang sampul audio (`sync_broll.py`). 41 klip berkeyakinan tinggi dikenal pasti dan 38 daripadanya digunakan sebagai *cutaway tersegerak* — gambar **dan** audio klip itu (mikrofon telefon lebih dekat, suara lebih jelas) menggantikan kamera induk pada saat yang sama. Hasilnya: rasa *multi-camera* dan dialog lebih jelas.
- Klip tanpa padanan yakin hanya digunakan dalam montaj pembukaan/penutup (tanpa mendakwa masa tertentu).
- **Framing kamera induk:** berselang-seli antara *wide* (96%) dan *medium* (74%, tumpuan hadapan kelas) supaya potongan pemendekan kelihatan seperti pertukaran kamera, bukan *jump cut*.
- **Dikecualikan:** seg58 (borang Ruang Guru memaparkan **nama penuh murid**), seg73 (logo CapCut), seg57 (klip menegak), seg32/43 (kabur). Nama murid dalam dialog vid3 tidak dipaparkan dalam sari kata.

## 5. Tiada rekaan kandungan
- Semua babak menggunakan rakaman sebenar. Tiada dialog/aksi/reaksi direka.
- **Bahan yang tiada dalam rakaman** (tidak direka; diganti dengan alternatif jujur):
  - Establishing shot luaran "hotel" → digantikan wide shot kelas + gambar/slaid *Hotel Hijau* pada skrin.
  - Ketiga-tiga guru dalam satu shot → penutup memaparkan Guru 1, 2, 3 berturutan + kad kredit nama.
  - "Empat skrin kumpulan" serentak → tidak dirakam; tidak dibina PiP palsu.
  - Close-up kad warna & nombor giliran → tidak jelas dalam rakaman; dirujuk hanya sebagai "empat kumpulan".
  - Lagu/muzik → tiada dibekalkan; **muzik asli dijana secara prosedur** (lihat §7).

## 6. Warna
- Kamera induk (480p HEVC): `hqdn3d` ringan (kurangkan hingar), kontras +7%, saturasi +10%, gamma 0.97, imbangan warna sedikit sejuk di highlight untuk meneutralkan lampu kalimantang, lengkung "highlight roll-off" (putih → 96%), vignette halus.
- B-roll iPhone: kontras +4%, saturasi +4%, lengkung & vignette yang sama supaya tona seragam.
- Tiada *sharpening* tiruan. Skala naik ke 1080p dengan Lanczos.
- **Resolusi akhir 1920×1080** (sumber tidak menyokong 4K). **30 fps** (kamera induk 60 fps diturunkan secara bersih; B-roll asal 30 fps).

## 7. Audio
- **Dialog:** high-pass 80–90 Hz, `afftdn` (pengurangan hingar sederhana 8–10 dB), `dynaudnorm` untuk meratakan suara guru/murid antara kamera.
- **Muzik:** semua muzik dan SFX **dicipta dari awal** oleh `music.py` (sintesis numpy: pad, piano, mallet, timpani, whoosh) — tiada bahan berhak cipta:
  | Bahagian | Mood | Fail |
  |---|---|---|
  | Pembukaan | Cinematic orchestral (swell + timpani + melodi piano) | `mus_opening.wav` |
  | Pengenalan / set induksi | Corporate inspirational | `mus_intro.wav` |
  | Aktiviti kumpulan / Misi | Upbeat educational | `mus_upbeat.wav` |
  | Aktiviti AR | Modern technology ambient | `mus_tech.wav` |
  | Semakan jawapan | Soft motivational | `mus_motiv.wav` |
  | Refleksi | Gentle piano | `mus_piano.wav` |
  | Penutup | Inspirational cinematic | `mus_closing.wav` |
  | Pertukaran guru | whoosh lembut + chime "digital reveal" | `sfx_whoosh.wav`, `sfx_reveal.wav` |
- **Ducking:** `sidechaincompress` dikunci oleh trek dialog — muzik turun automatik apabila guru/murid bercakap.
- **Loudness akhir:** `loudnorm` I = −16 LUFS, true peak −1.5 dBTP (tiada clipping). Fade-in/out bagi setiap muzik.

## 8. Senarai semak (Langkah 9)
| Perkara | Status |
|---|---|
| Nama & jawatan guru tepat | ✅ disalin tepat dari arahan, huruf besar, susunan sama |
| Tempoh 30:00 | ✅ dikunci 54 000 bingkai |
| Dialog terpotong | ✅ potongan pada jeda; crossfade 30 ms |
| Aktiviti direka | ✅ tiada |
| Audio terlalu kuat / clipping | ✅ loudnorm −16 LUFS, TP −1.5 dB |
| Ejaan teks | ✅ disemak (BM) |
| Transition agresif | ✅ potongan bersih + fade; tiada transition berlebihan |
| Skrin hitam tidak sengaja | ✅ hanya fade-out penutup yang disengajakan |
| Wajah / maklumat murid | ⚠️ nama murid pada skrin dikecualikan; **wajah murid kelihatan** — sila pastikan kebenaran penerbitan sebelum tayangan awam |
