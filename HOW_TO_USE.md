# Lentera MD — Panduan Penggunaan

> **Versi:** 1.0.0  
> **Platform:** Windows 10+, macOS 10.15+, Ubuntu 22.04+

---

## Daftar Isi

1. [Persyaratan Sistem](#1-persyaratan-sistem)
2. [Instalasi Windows (Installer .exe)](#2-instalasi-windows-installer-exe)
3. [Instalasi dari Kode Sumber](#3-instalasi-dari-kode-sumber)
4. [Menjalankan Aplikasi](#4-menjalankan-aplikasi)
5. [Panduan Penggunaan](#5-panduan-penggunaan)
6. [Pemeriksaan Ejaan](#6-pemeriksaan-ejaan)
7. [Menyimpan Hasil](#7-menyimpan-hasil)
8. [Pengaturan](#8-pengaturan)
9. [Tentang & Dukungan](#9-tentang--dukungan)
10. [Penyelesaian Masalah](#10-penyelesaian-masalah)

---

## 1. Persyaratan Sistem

| Komponen | Minimum | Rekomendasi |
|----------|---------|-------------|
| Sistem Operasi | Windows 10 / macOS 10.15 / Ubuntu 22.04 | Windows 11 / macOS 13 / Ubuntu 24.04 |
| Prosesor | 4 core x86_64 | 8 core |
| RAM | 4 GB | 8 GB |
| Penyimpanan | 2 GB kosong (+ ~500 MB model AI) | 4 GB kosong |
| Layar | 1280×720 | 1920×1080 |
| Internet | Diperlukan saat pertama kali memproses PDF | Tidak diperlukan setelahnya |

> **Catatan:** Saat pertama kali memproses PDF, Docling mengunduh model AI (~50–500 MB) dari HuggingFace. Proses ini hanya terjadi sekali dan disimpan di cache. Setelah itu aplikasi berjalan sepenuhnya offline.

---

## 2. Instalasi Windows (Installer .exe)

Cara termudah menggunakan Lentera MD di Windows adalah melalui installer yang sudah jadi.

### Langkah 1 — Unduh Installer

Unduh file `LenteraMD_Setup_1.0.0.exe` dari halaman [Releases](https://github.com/ziffan/Lentera-MD-Converter/releases).

### Langkah 2 — Jalankan Installer

1. Klik dua kali file installer
2. Ikuti petunjuk instalasi
3. Pilih lokasi instalasi (default: folder pengguna, tidak perlu hak admin)
4. Centang **"Buat ikon di Desktop"** jika ingin shortcut di Desktop
5. Klik **Install**

### Langkah 3 — Jalankan Aplikasi

Klik shortcut **Lentera MD** di Desktop atau Start Menu.

### Tentang Jendela Terminal

Saat aplikasi dibuka, sebuah **jendela terminal (command prompt) akan muncul** bersamaan dengan jendela utama aplikasi. Ini adalah hal **normal** — terminal menampilkan log aktivitas aplikasi.

> **Jangan tutup jendela terminal** selama aplikasi masih digunakan. Terminal akan tertutup otomatis saat aplikasi ditutup.
>
> Jika terjadi error, tutup dan buka kembali aplikasi. Jika masalah berlanjut, laporkan di [GitHub Issues](https://github.com/ziffan/Lentera-MD-Converter/issues).

### Pertama Kali Memproses PDF

Pada percobaan konversi PDF pertama, aplikasi akan mengunduh model AI layout (~170 MB) dari HuggingFace. Proses ini membutuhkan koneksi internet dan bisa memakan waktu beberapa menit tergantung kecepatan internet. Setelah selesai, model disimpan di cache dan tidak perlu diunduh lagi.

---

## 3. Instalasi dari Kode Sumber

Untuk pengembang atau pengguna yang ingin menjalankan dari source code.

### Prasyarat

- Python 3.10 atau lebih baru
- Git

### Langkah 1 — Clone Repository

```bash
git clone https://github.com/ziffan/Lentera-MD-Converter
cd Lentera-MD-Converter
```

### Langkah 2 — Buat Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### Langkah 3 — Install PyTorch (CPU-only)

Langkah ini penting untuk menghindari pengunduhan PyTorch versi CUDA (~2 GB).

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Langkah 4 — Install Semua Dependensi

```bash
pip install -e ".[dev]"
```

### Langkah 5 — Perbaiki torchvision (jika perlu)

Hanya jika muncul error `operator torchvision::nms does not exist`:

```bash
pip uninstall -y torchvision
pip install torchvision --index-url https://download.pytorch.org/whl/cpu
```

---

## 4. Menjalankan Aplikasi

### Dari Installer (Windows)

Klik shortcut **Lentera MD** di Desktop atau Start Menu.

### Dari Kode Sumber

```bash
# Windows
venv\Scripts\python src\legal_md_converter\main.py

# Linux / macOS
venv/bin/python src/legal_md_converter/main.py
```

Aplikasi akan terbuka dengan tampilan dua panel:
- **Panel kiri** — daftar file yang akan dikonversi
- **Panel kanan** — hasil konversi Markdown (dapat diedit langsung)

---

## 5. Panduan Penggunaan

### Menambahkan Dokumen

Ada tiga cara menambahkan file:

1. **Drag & Drop** — seret file dari Explorer langsung ke panel kiri
2. **Menu File → Open Files...** (Ctrl+O) — pilih satu atau beberapa file
3. **Menu File → Open Folder...** — pilih folder, semua dokumen yang didukung akan dimuat

**Format yang didukung:** PDF, DOCX, DOC, RTF, TXT

### Mengonversi Dokumen

1. Setelah file ditambahkan, klik **Convert to Markdown** di toolbar atau tekan **Ctrl+Enter**
2. Jendela progres terbuka dan menampilkan log konversi secara *live*
3. Setelah selesai, hasil konversi tampil di panel kanan

> **Pertama kali konversi PDF:** Aplikasi mengunduh model AI (~170–500 MB). Tunggu hingga selesai — proses berikutnya jauh lebih cepat.

### Jika Konversi Gagal

- Jendela progres menampilkan pesan error berwarna merah
- Klik tombol **Tutup** atau **Cancel** untuk menutup jendela progres
- Periksa apakah file tidak rusak dan format didukung
- Coba lagi — jika gagal karena download model terputus, coba sekali lagi

### Mengedit Hasil Konversi

Panel kanan adalah editor teks — kamu bisa:
- Mengetik dan mengedit langsung
- Memperbaiki kesalahan formatting
- Menghapus teks yang tidak diinginkan (header/footer, nomor halaman, dll.)

---

## 6. Pemeriksaan Ejaan

Setelah konversi selesai, panel **Pemeriksaan Ejaan** otomatis terbuka (jika diaktifkan di Pengaturan).

### Cara Menggunakan Panel Ejaan

1. Daftar kata bermasalah muncul di panel kanan (dock)
2. **Klik salah satu kata** → kursor di panel preview langsung melompat ke posisi kata tersebut
3. Pilih saran perbaikan dari dropdown **Saran Perbaikan**
4. Gunakan tombol:
   - **Ganti** — ganti dengan saran yang dipilih
   - **Abaikan** — lewati kata ini satu kali
   - **Abaikan Semua** — lewati semua kemunculan kata yang sama
   - **Tambah ke Kamus** — simpan ke kamus pengguna (tidak akan ditandai lagi)

### Menjalankan Ejaan Manual

- Menu **Tools → Spell Check**
- Atau aktifkan opsi *"Periksa ejaan otomatis"* di panel Pengaturan

> **Catatan:** Pemeriksaan ejaan menggunakan KBBI dengan 71.093 kata. Kata teknis, nama orang, atau singkatan mungkin ditandai — gunakan **Tambah ke Kamus** untuk menyimpannya.

---

## 7. Menyimpan Hasil

### Save Markdown (Ctrl+S)

1. Klik **File → Save Markdown...** atau tekan **Ctrl+S**
2. Pilih lokasi dan nama file
3. Klik Simpan

Tombol **Save Markdown** juga tersedia di bagian atas panel preview.

### Copy to Clipboard

Klik tombol **Copy to Clipboard** di panel preview untuk menyalin seluruh isi ke clipboard.

---

## 8. Pengaturan

Buka panel pengaturan melalui **View → Settings Panel**.

| Pengaturan | Keterangan |
|------------|------------|
| Aktifkan OCR | Hidupkan/matikan OCR untuk PDF hasil scan |
| Bahasa OCR | Indonesia + Inggris (default) |
| Template default | Legal / Akademik / Dasar |
| Periksa ejaan otomatis | Jalankan spellcheck otomatis setelah konversi |
| Lewati singkatan | Abaikan hlm., dst., dll. saat cek ejaan |
| Lewati bilangan tingkat | Abaikan ke-1, ke-2, dsb. |

---

## 9. Tentang & Dukungan

Buka **Help → About** untuk melihat:

- Logo dan versi aplikasi
- Tautan GitHub: https://github.com/ziffan/Lentera-MD-Converter
- Donasi via Saweria: https://saweria.co/kampusmerahdeveloper
- Donasi via Ko-fi: https://ko-fi.com/kampusmerahdev
- Peringatan penggunaan hasil OCR

---

## 10. Penyelesaian Masalah

### Konversi PDF sangat lambat (3+ menit pertama kali)

**Penyebab:** Docling mengunduh model AI (~170–500 MB) dari HuggingFace.  
**Solusi:** Tunggu hingga selesai. Run berikutnya jauh lebih cepat karena model sudah di-cache.

---

### Konversi gagal dengan error di jendela progres

**Langkah:**
1. Klik **Tutup** di jendela progres
2. Tutup aplikasi sepenuhnya
3. Buka kembali aplikasi
4. Coba konversi ulang

Jika masalah berlanjut, laporkan di: https://github.com/ziffan/Lentera-MD-Converter/issues

---

### `operator torchvision::nms does not exist`

```bash
pip uninstall -y torchvision
pip install torchvision --index-url https://download.pytorch.org/whl/cpu
```

---

### Spellcheck tidak berjalan

**Periksa:**
1. File `assets/kbbi/kbbi.db` harus ada (±4.3 MB)
2. Dokumen harus sudah dikonversi terlebih dahulu
3. Opsi *"Periksa ejaan otomatis"* aktif di Pengaturan

---

### Klik typo di panel ejaan tidak menavigasi ke teks

**Solusi:** Pastikan konversi sudah selesai dan hasil terlihat di panel kanan sebelum menggunakan panel ejaan.

---

### Jendela tidak muncul (Linux Wayland)

```bash
export QT_QPA_PLATFORM=wayland
python src/legal_md_converter/main.py
```

---

### Melihat Log Aplikasi

Log tersimpan otomatis di:

| OS | Lokasi |
|----|--------|
| Windows | `%LOCALAPPDATA%\Legal-MD-Team\LegalMDConverter\Logs\legal-md-converter.log` |
| macOS | `~/Library/Application Support/LegalMDConverter/Logs/legal-md-converter.log` |
| Linux | `~/.local/share/legal_md_converter/logs/legal-md-converter.log` |

---

## Peringatan Penggunaan

Mohon periksa kembali hasil olah kata/kalimat sebelum digunakan. Jika dokumen bersumber dari hasil OCR, kemungkinan akan banyak tipo dan pemenggalan kata/kalimat yang tidak sesuai. Hasil di luar tanggung jawab pengembang. Terima kasih.

---

*Dokumen ini diperbarui seiring perkembangan aplikasi.*
