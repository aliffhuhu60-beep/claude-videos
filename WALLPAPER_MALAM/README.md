# Wallpaper Animasi Malam (2 versi)

Wallpaper hidup untuk telefon, gaya lukisan pastel/gouache, suasana malam.
Dilukis semula sepenuhnya dengan kod (tiada piksel dari gambar asal, jadi tiada watermark).

| Fail | Isi |
|---|---|
| `output/wallpaper_malam_1_kucing_bukit.mp4` (20 s) | Kucing putih di bukit. Telinga berpusing bila terdengar bunyi, kepala menoleh & dicondongkan, menoleh ikut tahi bintang, mengekori kelip-kelip (telinga tegak, merendah badan, menggoyang punggung, hujung ekor bergetar), menggeleng kepala, menghidu angin. Awan bergerak, angin di rumput, benih dandelion terapung |
| `output/wallpaper_malam_2_kucing_tingkap.mp4` (30 s) | Kucing hitam di tingkap. Mengekori rama-rama malam (merendah badan, menggoyang punggung), mendongak lihat tahi bintang, mengekori kelawar lalu mencondongkan kepala, menggeleng kepala, menghidu angin. Daun bergetar, daun gugur, awan nipis, langsir beralun, lampu rumah jauh padam/menyala |
| `output/*_still.png` | Versi gambar statik (untuk wallpaper biasa) |

Spesifikasi: 1080 × 2400 (nisbah 20:9), 30 fps, 20 s / 30 s, gelung lancar (seamless loop), H.264.

## Versi tablet (Samsung Galaxy Tab S9 FE, 2304 × 1440)
Kedua-dua kucing duduk bersebelahan di ambang tingkap, memandang bukit bercahaya bulan.
Ayat: *"The night is softer / when we share it."*
Mereka menoleh ikut tahi bintang, berpandangan sambil mencondongkan kepala, kemudian sama-sama mengekori seekor kelip-kelip.
Juga: awan bergerak, daun bergetar, langsir beralun, lilin berkelip, lampu kelip-kelip di bawah ambang.

| Fail (`output/tablet/`) | Guna |
|---|---|
| `wallpaper_tablet_duo_square.mp4` / `_still.png` (2304 × 2304) | Satu fail untuk melintang **dan** menegak — semua elemen penting di tengah 1440 × 1440 |
| `wallpaper_tablet_duo_landscape.mp4` / `.png` (2304 × 1440) | Potongan siap untuk melintang |
| `wallpaper_tablet_duo_portrait.mp4` / `.png` (1440 × 2304) | Potongan siap untuk menegak |

Video 15 saat (had video wallpaper skrin kunci Samsung).

## Cara pasang
- **Android**: kebanyakan telefon (Samsung, Xiaomi, Oppo, dll.) boleh terus guna video sebagai wallpaper:
  Galeri → pilih video → *Tetapkan sebagai kertas dinding*. Jika tiada pilihan itu, guna aplikasi
  "Video Live Wallpaper" dari Play Store.
- **iPhone**: iOS tidak boleh guna MP4 terus. Tukar ke Live Photo dengan aplikasi seperti *intoLive*,
  kemudian Tetapan → Kertas Dinding.

## Jana semula
```
node render.cjs still bukit output/wallpaper_malam_1_kucing_bukit_still.png 3
node render.cjs video bukit output/wallpaper_malam_1_kucing_bukit.mp4 30
node render.cjs video tingkap output/wallpaper_malam_2_kucing_tingkap.mp4 30
# tambah argumen akhir 0 untuk versi tanpa teks, cth: node render.cjs video bukit out.mp4 30 0
```
Fon: Gaegu (SIL Open Font License).
