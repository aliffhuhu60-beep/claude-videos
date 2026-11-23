# Wallpaper Animasi Malam (2 versi)

Wallpaper hidup untuk telefon, gaya lukisan pastel/gouache, suasana malam.
Dilukis semula sepenuhnya dengan kod (tiada piksel dari gambar asal, jadi tiada watermark).

| Fail | Isi |
|---|---|
| `output/wallpaper_malam_1_kucing_bukit.mp4` (20 s) | Kucing putih di bukit. Telinga berpusing bila terdengar bunyi, kepala menoleh & dicondongkan (ingin tahu), menoleh ikut tahi bintang, bermain dengan kelip-kelip (mengekori, menggoyang punggung, menampar 2 kali), menggeleng kepala, kemudian menghidu angin. Awan bergerak merentas langit, angin bergelombang di rumput, benih dandelion terapung |
| `output/wallpaper_malam_2_kucing_tingkap.mp4` (30 s) | Kucing hitam di tingkap. Mengekori & menampar rama-rama malam, mendongak lihat tahi bintang, mengekori kelawar yang terbang melintasi bulan lalu mencondongkan kepala, menggeleng kepala, menghidu angin. Setiap helai daun bergetar ditiup angin, daun gugur, awan nipis bergerak, langsir beralun, lampu rumah jauh padam/menyala, kelip-kelip |
| `output/*_still.png` | Versi gambar statik (untuk wallpaper biasa) |

Spesifikasi: 1080 × 2400 (nisbah 20:9), 30 fps, 20 s / 30 s, gelung lancar (seamless loop), H.264.

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
