# Wallpaper Animasi Malam (2 versi)

Wallpaper hidup untuk telefon, gaya lukisan pastel/gouache, suasana malam.
Dilukis semula sepenuhnya dengan kod (tiada piksel dari gambar asal, jadi tiada watermark).

| Fail | Isi |
|---|---|
| `output/wallpaper_malam_1_kucing_bukit.mp4` | Kucing putih di atas bukit, bulan penuh, awan bergerak perlahan, bintang berkelip, tahi bintang, kelip-kelip, rumput beralun, ekor kucing bergerak |
| `output/wallpaper_malam_2_kucing_tingkap.mp4` | Kucing hitam di tepi tingkap, taman malam bercahaya bulan, rumah jauh dengan lampu tingkap, kelip-kelip, daun bergoyang, cahaya lampu bilik berkelip lembut |
| `output/*_still.png` | Versi gambar statik (untuk wallpaper biasa) |

Spesifikasi: 1080 × 2400 (nisbah 20:9), 30 fps, 20 saat, gelung lancar (seamless loop), H.264.

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
