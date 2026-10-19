# TaskMahasiswa — Aplikasi Manajemen Tugas Kuliah

Proyek web sederhana untuk tugas individu mata kuliah **11S3133 Pengembangan Aplikasi Berbasis Web (PABWE)**. Aplikasi ini membantu mahasiswa mencatat tugas kuliah, menentukan tenggat dan prioritas, serta memantau status pengerjaan.

## Fitur
- Menambah tugas dengan nama, mata kuliah, tenggat, prioritas, dan catatan.
- Mengubah detail tugas.
- Menghapus tugas dengan dialog konfirmasi.
- Menandai tugas selesai atau belum selesai.
- Mencari tugas berdasarkan nama, mata kuliah, atau catatan.
- Memfilter status dan mengurutkan berdasarkan tenggat, prioritas, atau waktu penambahan.
- Ringkasan total tugas, tugas belum selesai, dan tugas selesai.
- Penyimpanan di browser menggunakan `localStorage`.
- Tampilan responsif untuk desktop dan perangkat seluler.

## Teknologi
- HTML5
- CSS3
- JavaScript murni (tanpa framework atau dependensi eksternal)

## Cara menjalankan
1. Ekstrak ZIP.
2. Buka folder `aplikasi_manajemen_tugas_mahasiswa`.
3. Buka `index.html` menggunakan browser modern.
4. Tambahkan beberapa tugas dan coba semua fitur.

Tidak perlu instalasi paket atau server backend. Untuk workflow pengembangan, folder ini dapat dibuka dengan VS Code dan dijalankan memakai ekstensi Live Server (opsional).

## Struktur berkas
```text
aplikasi_manajemen_tugas_mahasiswa/
├── index.html
├── style.css
├── app.js
└── README.md
```

## Penyimpanan dan batasan
Data disimpan pada `localStorage` di browser/perangkat yang sedang digunakan. Data tidak otomatis tersinkronisasi ke perangkat lain, tidak dikirim ke server, dan dapat hilang jika data situs browser dihapus. Aplikasi ini merupakan prototipe pembelajaran, bukan sistem akademik resmi.

## Skenario pengujian manual
| No. | Skenario | Hasil yang diharapkan |
|---|---|---|
| 1 | Tambah tugas dengan seluruh kolom wajib | Tugas muncul pada daftar dan angka ringkasan bertambah |
| 2 | Kirim formulir dengan kolom wajib kosong | Browser meminta kolom dilengkapi |
| 3 | Edit judul atau tenggat tugas | Daftar menampilkan nilai terbaru |
| 4 | Tandai tugas selesai | Status berubah dan ringkasan selesai bertambah |
| 5 | Hapus tugas lalu konfirmasi | Tugas hilang dari daftar |
| 6 | Cari kata kunci yang cocok | Hanya tugas yang cocok ditampilkan |
| 7 | Pilih filter “Belum selesai” | Tugas selesai tidak ditampilkan |
| 8 | Muat ulang halaman | Data yang sebelumnya disimpan tetap muncul di browser yang sama |
| 9 | Masukkan teks seperti `<script>` pada catatan | Teks tampil sebagai teks biasa, bukan dijalankan sebagai HTML |
| 10 | Gunakan tampilan layar sempit | Formulir dan daftar menyesuaikan lebar layar |

## Catatan penggunaan AI untuk laporan
Jika AI digunakan selama pengembangan, catat secara jujur:
- alat AI yang benar-benar digunakan;
- prompt yang benar-benar dikirim;
- bagian kode yang disarankan AI;
- hasil pemeriksaan dan pengujian yang dilakukan sendiri;
- kesalahan yang benar-benar ditemukan dan perbaikannya;
- tangkapan layar asli proses kerja dan hasil program.

Jangan mengklaim telah melakukan pengujian, menemukan bug, atau memperbaiki kode jika hal tersebut belum benar-benar dilakukan. Dokumentasikan bukti aktual dari proses pengembangan.
