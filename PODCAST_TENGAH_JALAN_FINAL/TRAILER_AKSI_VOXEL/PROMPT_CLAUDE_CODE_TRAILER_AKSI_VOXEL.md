# MASTER PROMPT CLAUDE CODE — TRAILER AKSI 3D GAYA BLOK (VOXEL)
## PODCAST TENGAH JALAN · "SLAY ATAU SALAH?" (≤ 40 saat)

---

### 1. PERANAN & OBJEKTIF

Bertindak sebagai **3D Animation Director, Voxel Artist, Technical Animator dan Trailer Editor**.

Hasilkan **trailer gaya filem aksi (action movie trailer)** berdurasi **39.0 saat** dalam **gaya 3D blok/voxel** (dunia dibina daripada kiub bertekstur piksel, inspirasi permainan sandbox blok). Ia mesti **rekaan asli**: jangan guna logo, watak, tekstur atau aset rasmi mana-mana permainan.

Bahan rujukan (letak dalam folder yang sama):

| Fail | Kegunaan |
|---|---|
| `Trailer_Aksi_Voxel_v2_Reference.mp4` | **Rujukan utama**: susunan babak, masa potongan, pergerakan kamera, kad tajuk, kilatan, gegaran |
| `Trailer_Aksi_Storyboard.jpg` | Satu bingkai bagi setiap babak |
| `Character_Sheet_Voxel.jpg` | Rupa tiga watak blok berbanding rakaman sebenar |
| `action2_mix.wav` | **Audio akhir siap**: muzik aksi asli + dialog sebenar + SFX. **Wajib guna tanpa ubah masa** |
| `action2_env.json` | Sampul suara setiap penutur bagi setiap bingkai (30 fps) untuk lip-sync |
| `Podcast_Final_10-11_Minutes.mp4` | Rakaman sebenar (rujukan rupa hos & lokasi) |

---

### 2. SPESIFIKASI OUTPUT

- **1920 × 1080**, 16:9, **30 fps**, MP4 (H.264 + AAC 48 kHz), durasi **39.0 s** (sama dengan `action2_mix.wav`).
- Folder `TRAILER_AKSI_FINAL/`: `Trailer_Aksi_Final.mp4`, `Stills/` (satu PNG bagi setiap babak), `Project_Files/`.
- Pilihan: versi menegak 9:16 (1080×1920) yang di-reframe dengan kemas.

---

### 3. GAYA VISUAL

- **Dunia voxel**: setiap objek dibina daripada kiub; tekstur piksel 16×16 (NearestFilter, tiada blur). Kiub tanah 0.5 m; perincian kecil (kereta, meja) 0.25 m atau kurang.
- **Suasana INTENS & DRAMATIK**: senja gelap (langit ungu-jingga), matahari rendah **di belakang** set (cahaya latar/siluet, *rim light* jingga), cahaya pengisi biru sejuk, **kabus** tebal, **lampu jalan & lampu kereta menyala**, **zarah bara** terapung, vignette kuat, **butiran filem**, letterbox 2.39:1 (136 px), sudut kamera condong (*dutch angle*) pada babak tegang, gerak perlahan pada barisan hero.
- **Bahasa trailer aksi** (seperti contoh video pengguna): babak gelap, **potongan pantas**, **kad tajuk metalik** berlatar gelap berasap dengan **bara api** naik, **kilatan putih** dan **gegaran kamera** pada setiap hentakan (*braam*/*hit*), bar letterbox 96 px.
- **TIADA babak telefon/TikTok.**
- Fon: **Poppins** (ExtraBold untuk kad tajuk & slam, Bold untuk sari kata). Sari kata putih dengan outline hitam; kata kunci kuning `#FFD54A`, istilah TikTok merah jambu `#F4B6C6`. Warna identiti: marun `#6E1E2B`, krim `#F7EDE0`.

---

### 4. WATAK BLOK (WAJIB SERUPA RAKAMAN SEBENAR)

Badan blok: kepala 0.5 m kiub, badan, lengan, peha + betis berasingan (supaya boleh duduk dengan lutut bengkok). Tinggi ±1.75 m. Muka tekstur piksel 16×16 dengan perincian.

| Watak | Kedudukan | Rupa (ikut rakaman) |
|---|---|---|
| **ALIFF**, Hos Utama | Kiri | Kulit sawo matang sederhana `#C99673`; **muka berisi**; **cermin mata berbingkai NIPIS LUT SINAR/PERAK** (bukan hitam); **rambut LURUS, KEMAS & RATA, belah tepi, juntaian pendek yang lurus — BUKAN berjambul/tegak**; **polo HITAM** dengan tulisan putih **"BIG"**, jalur lengan & kolar putih. |
| **IMAN**, Detektif Sintaksis | Tengah | Kulit **cerah** `#E3BB98`; muka bujur; **cermin mata berbingkai LOGAM NIPIS gelap** (bulat); **rambut TEBAL dengan juntaian depan menutup dahi** hingga ke paras kening; **polo biru tua** "IPGMKTHO", kolar & jalur putih. |
| **AMMAR**, Suara Warganet | Kanan | Kulit sawo matang **cerah** `#D2A07A` (**jangan terlalu gelap**); **TIADA cermin mata**; **TIADA misai**; rambut hitam **belah tepi**; **senyuman lebar** bila diam; **polo biru tua** "IPGMKTHO". |

Animasi watak:
- **Lip-sync** daripada `action_env.json` (`env.AL`, `env.IM`, `env.AM`, nilai 0–1 setiap bingkai). Mulut piksel: tertutup = garis, terbuka = segi empat gelap + lidah merah jambu.
- **Kelip mata** setiap 3–4 s, **pandangan** ke arah penutur, kepala mengangguk kecil semasa bercakap, tangan bergerak sederhana.
- Babak "lineup": ketiga-tiga **berdiri** sebaris dengan gaya hero (sudut rendah, matahari di belakang).

---

### 5. SET (lengkap & terperinci)

- **Jalan tar** blok gelap dengan garisan putih putus-putus, bebendul konkrit kedua-dua tepi.
- **Deretan rumah teres dua tingkat** di kiri (fasad blok plaster krim/putih/pic, tingkap kaca berbingkai, pintu kayu, beranda tingkat 1, **bumbung genting bertingkat**, unit penghawa dingin, **pagar besi**, pokok renek & bunga).
- **Pokok kelapa sawit blok** (batang kayu, pelepah daun melengkung) & semak di kanan/belakang.
- **Tiang lampu jalan** (lampu bercahaya), **awan blok**.
- **Kereta hatchback merah blok** (kaca gelap, lampu hadapan putih bercahaya, lampu belakang merah, tayar hitam + rim kelabu) di belakang hos. **Tiada logo/nombor plat sebenar.**
- **Meja putih** + **2 tablet** (skrin menyala biru muda), **kerusi plastik kelabu**.

---

### 6. STORYBOARD & MASA (ikut audio, toleransi ±1 bingkai)

| Masa (s) | Babak | Kamera / Visual | Audio & Teks |
|---|---|---|---|
| 0.00–1.80 | **Pembukaan gelap** | Skrin hitam | **PODCAST TENGAH JALAN / MEMPERSEMBAHKAN** · degupan jantung + gegaran |
| 1.80–3.80 | **Dron senja** | Terbang laju dari tinggi ke arah set; lampu jalan menyala | **BRAAM 1** + kilatan |
| 3.80–4.80 | **Kad 1** | Latar gelap berasap + bara | *DI TENGAH JALAN...* / **BAHASA KITA** |
| 4.80–5.40 | **Kereta** | Sudut rendah 3/4 hadapan, lampu menyala | **BRAAM 2** |
| 5.40–6.30 | **Kad 2** | — | **SEDANG DIRANCU** |
| 6.30–7.30 | **Lineup hero** | Sudut rendah, gerak perlahan, siluet senja | hentakan taiko |
| 7.30–8.30 | **Kad 3** | — | *TIGA HOS.* / **SATU MISI.** |
| 8.30–8.50 | Hitam | — | **BRAAM 3** |
| 8.50–13.60 | **ALIFF CU** | Push-in | *"Dalam kamus bahasa Inggeris, slay sebenarnya bermaksud membunuh?"* · slam **MEMBUNUH?!** (12.79) |
| 13.60–16.55 | **AMMAR CU** | Close-up bersih | *"Semua orang faham, apa salahnya?"* |
| 16.55–20.35 | **IMAN CU** | Push-in | *"Faham memang faham, tetapi mari kita analisis."* |
| 20.35–22.35 | **IMAN CU 2** (babak tambahan) | Lebih dekat, dutch angle | *"Itulah campur kod pada peringkat frasa."* · slam **CAMPUR KOD!** kuning (21.05) |
| 22.35–26.50 | **AMMAR baca ayat 3** (babak tambahan) | Push-in perlahan, dutch angle | *"Dia ni terpaling alim, semua orang dia tegur."* · slam **TERPALING?!** merah (24.45) |
| 26.50–28.15 | **Montaj** | Orbit sekeliling meja | Kad blok 3D **satu demi satu di TENGAH skrin, penuh & tidak bertindih**: **POV** (26.55) → **SLAY** (27.05) → **TERPALING** (27.55) |
| 28.15–30.45 | **ALIFF medium** | Dolly-in | *"Jawapannya jelas, iaitu salah!"* · slam **SALAH!** (29.87) |
| 30.45–31.25 | **JEDA SENYAP** (babak tambahan) | Syot lebar tiga hos, gelap, hampir pegun | Muzik terhenti, hanya degupan jantung |
| 31.25–34.80 | **AMMAR CU** | Push-in | *"Ingat, santai boleh, rancu jangan!"* · slam **SANTAI BOLEH, RANCU JANGAN!** (31.90) |
| 34.80–39.00 | **Tajuk akhir** | Latar gelap berasap + bara | **BRAAM akhir** · **SLAY ATAU SALAH?** · *Bila Bahasa Kita Terpaling Rancu di TikTok* · **EPISOD PENUH · TONTON SEKARANG** · hentakan 37.6 · pudar ke hitam |

### 7. AUDIO

- Guna **`action2_mix.wav`** sebagai audio akhir. Ia mengandungi muzik aksi asli (braam, taiko, ostinato tali, riser), dialog sebenar daripada rakaman dan kesan hentakan. **Jangan jana suara AI dan jangan ubah kelajuan/pic.**
- Masa dialog (s): Aliff 8.50–13.52 · Ammar 13.60–16.48 · Iman 16.55–20.27 · Iman 20.40–22.16 · Ammar 22.40–26.43 · Aliff 28.20–30.44 · Ammar 31.25–34.63.
- Hentakan visual (kilatan + gegaran) mesti tepat pada: 1.80, 4.80, 6.30, 8.30, 12.79, 21.05, 24.45, 26.55, 27.05, 27.55, 29.87, 31.90, 34.80, 37.60.

---

### 8. CADANGAN TEKNIKAL

1. **Blender (bpy)** + Eevee/Cycles: bina voxel melalui skrip (instancing), tekstur piksel `Closest` interpolation, rig watak blok (kepala/leher, bahu, pinggul, lutut), shape/scale untuk mulut, render PNG → FFmpeg + `action_mix.wav`. Tambah *bloom*, *depth of field* pada close-up dan *motion blur* ringan pada babak dron/montaj.
2. **Three.js (WebGL) + Playwright** seperti video rujukan, naik taraf dengan *post-processing* (bloom, SSAO, color grading teal-orange, vignette).

Jika ada kekangan teknikal, selesaikan berperingkat dan **jangan dakwa render berjaya tanpa menyemak fail output**.

---

### 9. PERATURAN PENTING

- Tiga watak **mesti dikenali** mengikut jadual di atas. Perhatian: Aliff memakai cermin mata **lut sinar** dengan rambut **lurus & kemas (tiada jambul)**; Iman memakai cermin mata **logam nipis** dengan rambut **berjuntai**; Ammar **tanpa misai** dan **kulit tidak terlalu gelap**.
- **Tiada babak TikTok/telefon**, tiada logo TikTok/Grab/permainan/jenama kereta, tiada nombor plat sebenar.
- Kesan aksi (kilatan, gegaran) hanya pada titik hentakan, bukan sepanjang masa.
- Grafik/slam tidak menutup muka watak.
- Sari kata tepat dengan audio; ejaan Bahasa Melayu betul.
- Durasi akhir **≤ 40 saat**.
- Kad montaj POV/SLAY/TERPALING mesti **kelihatan penuh**, satu demi satu, tidak bertindih.

---

### 10. SEMAKAN SEBELUM SERAH

- [ ] 39.0 s, 1920×1080, 30 fps, audio selari, lip-sync tepat.
- [ ] Semua potongan & slam tepat pada masa storyboard.
- [ ] Rupa tiga watak konsisten & menepati rakaman sebenar.
- [ ] Set lengkap & terperinci (jalan, rumah teres, pagar, pokok sawit, lampu jalan, awan, kereta merah, meja + tablet, kerusi).
- [ ] Tiada bingkai rosak; fail dimainkan dari awal hingga akhir.
- [ ] Simpan still PNG setiap babak dalam `Stills/`.

**KEUTAMAAN: tegang & gempak dalam 8 saat pertama, kemudian perbincangan isu rancu yang jelas, diakhiri tajuk yang kuat.**
