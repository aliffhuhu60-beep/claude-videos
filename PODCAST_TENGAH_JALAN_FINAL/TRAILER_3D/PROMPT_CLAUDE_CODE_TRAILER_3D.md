# MASTER PROMPT CLAUDE CODE — TRAILER ANIMASI 3D
## PODCAST TENGAH JALAN · "SLAY ATAU SALAH?" (≤ 30 saat)

---

### 1. PERANAN & OBJEKTIF

Bertindak sebagai **3D Animation Director, Character Artist, Technical Animator dan Motion Designer**.

Hasilkan **trailer animasi 3D penuh berdurasi 29–30 saat (maksimum 30 saat)** untuk mempromosikan episod podcast *"Slay atau Salah? Bila Bahasa Kita Terpaling Rancu di TikTok"*.

Gunakan bahan berikut **sebagai rujukan sahaja** (jangan salin piksel demi piksel — bina semula dalam 3D dengan kualiti lebih tinggi):

| Fail | Kegunaan |
|---|---|
| `Trailer_3D_Reference.mp4` | **Rujukan utama**: susunan babak, masa, pergerakan kamera, grafik teks, rentak muzik |
| `Trailer_Storyboard.jpg` | Satu bingkai bagi setiap babak |
| `Character_Sheet.jpg` | Rupa tiga watak (warna kulit, baju, cermin mata, rambut) |
| `trailer_mix.wav` | **Audio akhir siap** (dialog sebenar + muzik + SFX) — WAJIB digunakan tanpa diubah masa |
| `trailer_env.json` | Sampul suara setiap penutur bagi setiap bingkai (30 fps) untuk lip-sync |
| `Podcast_Final_10-11_Minutes.mp4` | Rakaman sebenar hos (rujukan rupa, pakaian, lokasi) |

Objektif: trailer yang **menarik, kemas, lucu sedikit tetapi profesional**, mendorong penonton menonton episod penuh.

---

### 2. SPESIFIKASI OUTPUT

- Resolusi **1920 × 1080**, 16:9, **30 fps**, MP4 (H.264 + AAC 48 kHz).
- Durasi **29.6 s** (mesti sama dengan `trailer_mix.wav`).
- Simpan dalam folder `TRAILER_3D_FINAL/`:
  - `Trailer_3D_Final.mp4`
  - `Trailer_3D_Final_Vertical_9x16.mp4` (pilihan, 1080×1920 untuk TikTok/Reels — reframe, bukan crop buta)
  - `Project_Files/` (skrip, fail .blend atau kod Three.js, tekstur)
  - `Stills/` (satu PNG bagi setiap babak)

---

### 3. GAYA VISUAL

**Stylized 3D** — gaya animasi moden seperti filem animasi 3D keluarga (watak bulat, mesra, ekspresif), **bukan realistik** dan **bukan low-poly kasar**.

- Bahan (material) lembut: kulit dengan *subsurface* ringan, kain jersi matte, kereta berkilat.
- Pencahayaan **petang Malaysia**: cahaya matahari hangat dari kiri-belakang, langit biru → jingga di ufuk, bayang lembut.
- Akhir trailer (25–29.6 s): langit beransur jingga senja.
- Palet identiti podcast untuk grafik: **merah marun `#6E1E2B`**, **krim `#F7EDE0`**, **merah jambu lembut `#F4B6C6`**, hitam `#141012`, kuning sari kata `#FFD54A`.
- Fon: **Poppins** (ExtraBold untuk tajuk, Bold untuk sari kata).
- Bar letterbox sinematik (70 px atas & bawah) dari 2.4 s hingga 27.1 s.

---

### 4. WATAK (3 ORANG — WAJIB)

Semua lelaki muda (~20 tahun), duduk di atas **kerusi plastik bulat kelabu muda**, seluar panjang hitam, kasut gelap. Susunan dari kiri ke kanan kamera: **ALIFF – IMAN – AMMAR**.

| Watak | Peranan | Rupa |
|---|---|---|
| **ALIFF** (kiri) | Hos utama | Kulit sawo matang; muka sedikit bulat; **cermin mata berbingkai hitam**; rambut hitam pendek kemas; **jersi polo HITAM** dengan tulisan putih besar **"BIG"** di dada, jalur putih di lengan, kolar putih. Duduk sedikit menyerong ke arah dua rakan. |
| **IMAN** (tengah) | "Detektif sintaksis" | Kulit cerah sederhana; muka bujur; **cermin mata berbingkai nipis gelap**; rambut hitam disikat ke tepi; **jersi biru tua/ungu gelap "IPGMKTHO"** tulisan putih, kolar & jalur lengan putih. |
| **AMMAR** (kanan) | "Suara warganet" | Kulit sawo matang; muka lebih kurus; **tiada cermin mata**; rambut hitam dengan jambul depan; senyuman lebar; **jersi biru tua/ungu gelap "IPGMKTHO"** sama seperti Iman. Duduk menyerong ke kiri. |

Keperluan animasi watak:
- **Lip-sync**: buka mulut berdasarkan `trailer_env.json` (`env.AL`, `env.IM`, `env.AM`, nilai 0–1 setiap bingkai). Tambah bentuk mulut (viseme) asas A/E/O/M jika boleh.
- **Kelip mata** rawak setiap 3–5 s; **pandangan**: pendengar memandang penutur; penutur memandang rakan/kamera.
- **Gerak isyarat tangan** sederhana semasa bercakap (bukan melambai berlebihan); tangan berehat di atas paha bila diam.
- **Ketawa** (`env.laugh` = 1) pada 22.7–23.6 s: ketiga-tiga ketawa, bahu bergerak, kepala sedikit ke belakang.
- Pernafasan & goyangan badan halus sepanjang masa (watak tidak pernah kaku sepenuhnya).

---

### 5. SET & LATAR (lengkap)

Berdasarkan lokasi rakaman sebenar — **tepi jalan taman perumahan pada waktu petang**:

- **Jalan tar** kelabu dengan garisan putih putus-putus, bahu jalan & bebendul konkrit.
- **Kereta hatchback MERAH** (gaya kompak tempatan, logo generik — **jangan guna logo/nombor plat sebenar**) diparkir di belakang hos, bahagian hadapan menghadap kamera.
- **Meja lipat kecil putih** di hadapan Aliff & Iman dengan **dua tablet** bersandar.
- **Deretan rumah teres dua tingkat** (dinding putih/krim, bumbung genting merah bata, tingkap, pintu, pagar besi, unit penghawa dingin) di sebelah kiri, beransur jauh.
- **Pokok kelapa sawit** dengan pelepah besar melengkung, rumput hijau & pokok renek di sebelah kanan/belakang.
- Tiang lampu jalan, langit dengan awan nipis, matahari rendah.
- Babak telefon (0–2.4 s): **telefon pintar 3D** terapung di latar gelap marun dengan antara muka media sosial generik (tanpa logo TikTok rasmi) — komen sedang ditaip.

---

### 6. STORYBOARD & MASA (ikut audio — jangan ubah masa)

| Masa | Babak | Kamera | Audio / Teks |
|---|---|---|---|
| **0.0–2.4** | **HOOK TELEFON** — telefon 3D berputar perlahan; komen ditaip: *"Outfit dia hari ni slay gila, confirm ramai yang jealous!"*; kata `Outfit/slay/confirm/jealous` diserlahkan merah jambu | Dolly-in perlahan ke telefon | Teks kiri atas: **"PERNAH TULIS MACAM NI?"**; 1.75 s: slam **"SLAY ATAU SALAH?"** (kotak marun). Bunyi taip + riser |
| **2.4–4.4** | **ESTABLISHING** — set penuh dari atas | Crane turun dari tinggi (belakang kanan, atas pokok) ke paras mata | Impak muzik pada 2.4 s. Aliff mula bercakap 2.8 s |
| **4.4–7.9** | **ALIFF CU** | Close-up 3/4 kanan, push-in perlahan | *"Dalam kamus bahasa Inggeris, slay sebenarnya bermaksud membunuh?"* · Kad nama **ALIFF – Hos Utama** · 7.05 s slam **"MEMBUNUH?!"** (merah jambu) |
| **7.9–11.1** | **AMMAR CU** | Close-up dari kiri | *"Semua orang faham, apa salahnya?"* · Kad nama **AMMAR – Suara Warganet** |
| **11.1–14.9** | **IMAN CU** | Close-up hadapan sedikit kanan | *"Faham memang faham, tetapi mari kita analisis."* · Kad nama **IMAN – Detektif Sintaksis** |
| **14.9–16.4** | **MONTAJ** — tiga kad kata 3D muncul mengikut rentak: **POV** (14.9) · **SLAY** (15.4) · **TERPALING** (15.9) | Orbit pantas mengelilingi meja, paras rendah | Muzik sahaja, 3 impak. Kad di bahagian bawah bingkai (jangan tutup muka) |
| **16.4–19.6** | **ALIFF MCU** | Medium close-up dari kanan | *"…di TikTok, mungkin slay. Tetapi dari segi tatabahasa…"* |
| **19.6–23.5** | **WIDE 3 ORANG** | Dolly-in perlahan dari hadapan | *"…jawapannya jelas, iaitu salah!"* · 22.1 s slam **"SALAH!"** (kotak merah) · 22.7 s ketiga-tiga **ketawa** |
| **23.5–27.1** | **AMMAR CU** | Close-up, push-in | *"Ingat, santai boleh, rancu jangan!"* · 24.35 s slam **"SANTAI BOLEH, RANCU JANGAN!"** (kotak marun) · langit mula jingga |
| **27.1–29.6** | **END CARD** | Pull-back & naik tinggi menampakkan set waktu senja | **AUDIO SIAR AKADEMIK** · **PODCAST TENGAH JALAN** · **SLAY ATAU SALAH?** · *Bila Bahasa Kita Terpaling Rancu di TikTok* · butang kuning **EPISOD PENUH · TONTON SEKARANG** · fade ke hitam 0.5 s terakhir |

Sari kata: putih, Poppins Bold ~60 px, outline hitam, di tengah bawah (di atas bar letterbox); kata kunci kuning, istilah TikTok merah jambu (rujuk video rujukan untuk teks tepat).

---

### 7. AUDIO

- **Gunakan `trailer_mix.wav` sedia ada sebagai audio akhir** (dialog sebenar daripada rakaman podcast + muzik asli bebas hak cipta + SFX). Jangan jana suara AI, jangan ubah kelajuan/pic.
- Semua potongan kamera dan slam teks mesti tepat pada masa dalam jadual di atas (±1 bingkai).
- Masa dialog (s): Aliff 2.80–7.82 · Ammar 8.10–10.98 · Iman 11.15–14.87 · Aliff 16.40–23.58 (ketawa 22.68–23.58) · Ammar 23.70–27.08.

---

### 8. CADANGAN TEKNIKAL

Pilih salah satu (utamakan kualiti):

1. **Blender (bpy) + Eevee/Cycles** — disyorkan. Model watak dengan subdivision surface, rig ringkas (kepala, rahang/mulut shape key, mata, lengan), animasi dipacu Python daripada `trailer_env.json`, render PNG → FFmpeg + `trailer_mix.wav`.
2. **Three.js (WebGL) + Playwright** — seperti video rujukan, tetapi naik taraf: `MeshPhysicalMaterial`, HDRI langit, *ambient occlusion* (SSAO), *depth of field* pada close-up, anti-aliasing tinggi, model watak lebih halus.

Jika ada kekangan teknikal, selesaikan secara berperingkat dan **jangan dakwa render berjaya tanpa menyemak fail output**.

---

### 9. PERATURAN PENTING

- Ketiga-tiga watak mesti **mudah dikenali** (Aliff baju hitam "BIG" + cermin mata; Iman tengah + cermin mata; Ammar kanan tanpa cermin mata).
- **Jangan** guna logo TikTok/Grab/jenama kereta rasmi atau nombor plat sebenar.
- **Jangan** guna glitch, flash berlebihan, shake kamera kasar atau terlalu banyak teks serentak.
- Grafik tidak menutup muka watak.
- Sari kata tepat dengan audio, ejaan Bahasa Melayu betul.
- Durasi akhir **≤ 30 saat**.

---

### 10. SEMAKAN SEBELUM SERAH

- [ ] Durasi 29.6 s, 1920×1080, 30 fps, audio selari (lip-sync tepat).
- [ ] Setiap babak sepadan dengan masa storyboard.
- [ ] Tiga watak konsisten rupa sepanjang trailer.
- [ ] Set lengkap: jalan, kereta merah, meja + tablet, kerusi plastik, rumah teres, pokok sawit, langit.
- [ ] Teks slam & kad nama muncul pada masa yang betul, tidak menutup muka.
- [ ] Tiada bingkai rosak/hitam yang tidak disengajakan; fail dimainkan dari awal hingga akhir.
- [ ] Simpan satu still PNG bagi setiap babak dalam `Stills/`.

**KEUTAMAAN: menarik dalam 3 saat pertama, watak ekspresif, kemas dan profesional.**
