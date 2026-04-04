# Lentera MD — Panduan Penggunaan / User Guide

> **Versi:** 1.0.0
> **Platform:** Windows 10+, macOS 10.15+, Ubuntu 22.04+
> **Bahasa / Language:** English 🇬🇧 & Bahasa Indonesia 🇮🇩

---

## Table of Contents / Daftar Isi

1. [System Requirements / Persyaratan Sistem](#1-system-requirements--persyaratan-sistem)
2. [Prerequisites / Prasyarat](#2-prerequisites--prasyarat)
3. [Installation Guide / Panduan Instalasi](#3-installation-guide--panduan-instalasi)
4. [Using the Application / Menggunakan Aplikasi](#4-using-the-application--menggunakan-aplikasi)
5. [Troubleshooting / Penyelesaian Masalah](#5-troubleshooting--penyelesaian-masalah)

---

## 1. System Requirements / Persyaratan Sistem

### English 🇬🇧

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10 / macOS 10.15 / Ubuntu 22.04 | Windows 11 / macOS 13 / Ubuntu 24.04 |
| **CPU** | 4 cores (x86_64) | 8 cores (x86_64 or Apple Silicon) |
| **RAM** | 4 GB | 8 GB |
| **Disk Space** | 2 GB free | 4 GB free |
| **Python** | 3.10 | 3.12 |
| **Display** | 1280×720 | 1920×1080 |
| **Network** | Required (first run only, for model download) | — |

> **Note:** First run downloads OCR models (~50 MB). Subsequent runs work offline.

### Bahasa Indonesia 🇮🇩

| Komponen | Minimum | Rekomendasi |
|----------|---------|-------------|
| **Sistem Operasi** | Windows 10 / macOS 10.15 / Ubuntu 22.04 | Windows 11 / macOS 13 / Ubuntu 24.04 |
| **Prosesor** | 4 core (x86_64) | 8 core (x86_64 atau Apple Silicon) |
| **RAM** | 4 GB | 8 GB |
| **Penyimpanan** | 2 GB kosong | 4 GB kosong |
| **Python** | 3.10 | 3.12 |
| **Layar** | 1280×720 | 1920×1080 |
| **Jaringan** | Diperlukan (hanya pertama kali, untuk unduh model) | — |

> **Catatan:** Pertama kali menjalankan aplikasi akan mengunduh model OCR (~50 MB). Setelahnya bisa berjalan offline.

---

## 2. Prerequisites / Prasyarat

### English 🇬🇧

**Required System Packages (Linux only):**

```bash
# Ubuntu/Debian
sudo apt install python3-venv python3-pip

# Fedora/RHEL
sudo dnf install python3-pip python3-devel

# Optional (for better OCR results)
sudo apt install tesseract-ocr tesseract-ocr-ind
```

**Python Version Check:**
```bash
python3 --version
# Must show Python 3.10 or higher
```

### Bahasa Indonesia 🇮🇩

**Paket Sistem yang Diperlukan (hanya Linux):**

```bash
# Ubuntu/Debian
sudo apt install python3-venv python3-pip

# Fedora/RHEL
sudo dnf install python3-pip python3-devel

# Opsional (untuk hasil OCR lebih baik)
sudo apt install tesseract-ocr tesseract-ocr-ind
```

**Cek Versi Python:**
```bash
python3 --version
# Harus menunjukkan Python 3.10 atau lebih tinggi
```

---

## 3. Installation Guide / Panduan Instalasi

### Method A: From Source / Dari Sumber (Developer)

#### English 🇬🇧

**Step 1: Clone the Repository**
```bash
git clone <repository-url>
cd lentera-md
```

**Step 2: Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate    # Linux/macOS
# or
venv\Scripts\activate       # Windows
```

**Step 3: Install PyTorch (CPU-only to avoid 2GB+ CUDA download)**
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

**Step 4: Install Dependencies**
```bash
# Production only
pip install -e .

# Production + development tools
pip install -e ".[dev]"
```

**Step 5: Fix torchvision if needed**
```bash
# Only if you get "operator torchvision::nms does not exist"
pip uninstall -y torchvision
pip install torchvision --index-url https://download.pytorch.org/whl/cpu
```

**Step 6: Run the Application**
```bash
python -m legal_md_converter.main
```

#### Bahasa Indonesia 🇮🇩

**Langkah 1: Clone Repository**
```bash
git clone <repository-url>
cd lentera-md
```

**Langkah 2: Buat Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate    # Linux/macOS
# atau
venv\Scripts\activate       # Windows
```

**Langkah 3: Install PyTorch (versi CPU-only agar tidak unduh CUDA ~2GB)**
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

**Langkah 4: Install Dependensi**
```bash
# Hanya produksi
pip install -e .

# Produksi + alat pengembangan
pip install -e ".[dev]"
```

**Langkah 5: Perbaiki torchvision jika perlu**
```bash
# Hanya jika muncul error "operator torchvision::nms does not exist"
pip uninstall -y torchvision
pip install torchvision --index-url https://download.pytorch.org/whl/cpu
```

**Langkah 6: Jalankan Aplikasi**
```bash
python -m legal_md_converter.main
```

---

### Method B: From Executable / Dari File Eksekusi

#### English 🇬🇧

**Linux (.deb):**
```bash
sudo dpkg -i lentera-md_1.0.0_amd64.deb
lentera-md
```

**macOS (.dmg):**
1. Open `LenteraMD.dmg`
2. Drag `LenteraMD.app` to Applications folder
3. Launch from Applications (or Spotlight)

**Windows (.exe):**
1. Run the installer or executable
2. Launch from Start Menu or Desktop shortcut

---

## 4. Using the Application / Menggunakan Aplikasi

### English 🇬🇧

**Convert a Document:**
1. Launch Lentera MD
2. Drag & drop a PDF/DOCX/TXT file onto the left panel (or click "Add Files...")
3. Click "Convert to Markdown" in the toolbar
4. Wait for parsing to complete (progress bar shows status)
5. View the converted markdown in the right panel
6. Click "Save Markdown" to export, or "Copy to Clipboard"

**Check Spelling:**
1. After conversion, the spell check panel opens automatically
2. Select a typo from the list
3. Choose a suggestion from the dropdown
4. Click "Ganti" (Replace), "Abaikan" (Ignore), or "Tambah ke Kamus" (Add to Dictionary)

**Export with Template:**
1. Click "Export Markdown..." in the File menu
2. Choose format (Markdown, HTML, or Plain Text)
3. Choose template (Legal, Academic, or Basic)
4. Select output location
5. Click "Ekspor"

#### Bahasa Indonesia 🇮🇩

**Mengonversi Dokumen:**
1. Buka Lentera MD
2. Drag & drop file PDF/DOCX/TXT ke panel kiri (atau klik "Add Files...")
3. Klik "Convert to Markdown" di toolbar
4. Tunggu proses parsing selesai (progress bar menunjukkan status)
5. Lihat hasil konversi markdown di panel kanan
6. Klik "Save Markdown" untuk ekspor, atau "Copy to Clipboard"

**Memeriksa Ejaan:**
1. Setelah konversi, panel pemeriksaan ejaan terbuka otomatis
2. Pilih salah satu typo dari daftar
3. Pilih saran dari dropdown
4. Klik "Ganti" (Replace), "Abaikan" (Ignore), atau "Tambah ke Kamus" (Add to Dictionary)

**Ekspor dengan Template:**
1. Klik "Export Markdown..." di menu File
2. Pilih format (Markdown, HTML, atau Plain Text)
3. Pilih template (Legal, Akademik, atau Dasar)
4. Pilih lokasi output
5. Klik "Ekspor"

---

## 5. Troubleshooting / Penyelesaian Masalah

### English 🇬🇧

#### Problem: `InputFormat has no attribute TXT`

**Cause:** Old version of code or outdated installation.
**Solution:**
```bash
# Reinstall from source
pip install -e . --force-reinstall --no-deps
```

---

#### Problem: `PdfPipelineOptions object has no attribute 'ocr_lang'`

**Cause:** Using old code with new docling version.
**Solution:** Update to the latest version. The fix changes `ocr_lang` → `ocr_options.lang`.

---

#### Problem: `torchvision::nms does not exist`

**Cause:** `torchvision` version doesn't match `torch` version (CUDA vs CPU).
**Solution:**
```bash
pip uninstall -y torchvision
pip install torchvision --index-url https://download.pytorch.org/whl/cpu
```

---

#### Problem: `AttributeError: 'PdfPipelineOptions' object has no attribute 'backend'`

**Cause:** Docling API changed — `format_options` must use `PdfFormatOption`.
**Solution:** Update to the latest code. The fix wraps options with `PdfFormatOption(pipeline_options=...)`.

---

#### Problem: `Unsupported format: .docx`

**Cause:** Missing handler for DOCX files.
**Solution:** Update to the latest code. The fix adds `parse_generic()` method for non-PDF formats.

---

#### Problem: Table export crashes with `TypeError: sequence item 1: expected str instance, list found`

**Cause:** PDF contains tables with nested/merged cells.
**Solution:** Update to the latest code. The fix adds `cell_str()` helper to flatten nested values.

---

#### Problem: Template output contains literal `{{ title }}` instead of actual values

**Cause:** Template rendering engine mismatch.
**Solution:** Update to the latest code. The fix replaces `string.Template` with direct `str.replace()`.

---

#### Problem: Spellcheck shows thousands of "Bloom filter library not available" messages

**Cause:** `bloom_filter2` package not installed, causing log spam.
**Solution:** Fixed in latest version. Now logs only once at DEBUG level. To install the library (optional, for faster spellcheck):
```bash
pip install bloom_filter2
```

---

#### Problem: Application window doesn't appear

**Check:**
```bash
# 1. Is Python running?
python3 --version

# 2. Is PySide6 installed?
python3 -c "from PySide6.QtWidgets import QApplication; print('OK')"

# 3. Run with verbose logging
python -m legal_md_converter.main 2>&1 | head -20
```

**Common fixes:**
- On Wayland: `export QT_QPA_PLATFORM=wayland`
- On headless server: Requires X11/Wayland display

---

#### Problem: Parsing is very slow (3+ minutes)

**Cause:** First run downloads OCR models (~50 MB). Subsequent runs are faster.
**Solution:** Wait for first run to complete. Models are cached for future use. For text-based PDFs (not scanned), parsing should be under 5 seconds.

---

#### Problem: Spellcheck doesn't find any errors

**Possible causes:**
1. KBBI database not found → Check `assets/kbbi/kbbi.db` exists (should be 4.3 MB, 71,093 words)
2. Document not converted yet → Spellcheck only works on converted markdown
3. Text is already correct → No typos to find!

**Verify:**
```bash
python3 -c "
from legal_md_converter.engine.document_service import DocumentService
svc = DocumentService()
print(f'Spellchecker ready: {svc.is_spell_checker_ready()}')
svc.close()
"
```

---

### Bahasa Indonesia 🇮🇩

#### Masalah: `InputFormat tidak punya atribut TXT`

**Penyebab:** Versi kode lama atau instalasi usang.
**Solusi:**
```bash
# Install ulang dari sumber
pip install -e . --force-reinstall --no-deps
```

---

#### Masalah: `PdfPipelineOptions tidak punya field 'ocr_lang'`

**Penyebab:** Menggunakan kode lama dengan versi docling baru.
**Solusi:** Perbarui ke versi terbaru. Fix mengubah `ocr_lang` → `ocr_options.lang`.

---

#### Masalah: `torchvision::nms does not exist`

**Penyebab:** Versi `torchvision` tidak cocok dengan `torch` (CUDA vs CPU).
**Solusi:**
```bash
pip uninstall -y torchvision
pip install torchvision --index-url https://download.pytorch.org/whl/cpu
```

---

#### Masalah: `AttributeError: 'PdfPipelineOptions' object has no attribute 'backend'`

**Penyebab:** API Docling berubah — `format_options` harus pakai `PdfFormatOption`.
**Solusi:** Perbarui ke kode terbaru. Fix membungkus options dengan `PdfFormatOption(pipeline_options=...)`.

---

#### Masalah: `Unsupported format: .docx`

**Penyebab:** Handler untuk file DOCX belum ada.
**Solusi:** Perbarui ke kode terbaru. Fix menambahkan method `parse_generic()` untuk format non-PDF.

---

#### Masalah: Ekspor tabel crash dengan `TypeError: sequence item 1: expected str instance, list found`

**Penyebab:** PDF mengandung tabel dengan sel bertingkat/gabung.
**Solusi:** Perbarui ke kode terbaru. Fix menambahkan helper `cell_str()` untuk meratakan nested values.

---

#### Masalah: Template output mengandung `{{ title }}` literal, bukan nilai sebenarnya

**Penyebab:** Ketidakcocokan engine rendering template.
**Solusi:** Perbarui ke kode terbaru. Fix mengganti `string.Template` dengan `str.replace()` langsung.

---

#### Masalah: Spellcheck menampilkan ribuan pesan "Bloom filter library not available"

**Penyebab:** Paket `bloom_filter2` tidak terinstall, menyebabkan log spam.
**Solusi:** Sudah diperbaiki di versi terbaru. Sekarang log hanya sekali di level DEBUG. Untuk install library (opsional, agar spellcheck lebih cepat):
```bash
pip install bloom_filter2
```

---

#### Masalah: Jendela aplikasi tidak muncul

**Periksa:**
```bash
# 1. Apakah Python berjalan?
python3 --version

# 2. Apakah PySide6 terinstall?
python3 -c "from PySide6.QtWidgets import QApplication; print('OK')"

# 3. Jalankan dengan logging verbose
python -m legal_md_converter.main 2>&1 | head -20
```

**Perbaikan umum:**
- Di Wayland: `export QT_QPA_PLATFORM=wayland`
- Di server tanpa layar: Memerlukan display X11/Wayland

---

#### Masalah: Parsing sangat lambat (3+ menit)

**Penyebab:** Pertama kali menjalankan akan mengunduh model OCR (~50 MB). Setelahnya lebih cepat.
**Solusi:** Tunggu sampai pertama kali selesai. Model akan di-cache untuk penggunaan selanjutnya. Untuk PDF berbasis teks (bukan scan), parsing harus di bawah 5 detik.

---

#### Masalah: Spellcheck tidak menemukan kesalahan apa pun

**Kemungkinan penyebab:**
1. Database KBBI tidak ditemukan → Cek `assets/kbbi/kbbi.db` ada (harusnya 4.3 MB, 71,093 kata)
2. Dokumen belum dikonversi → Spellcheck hanya bekerja pada markdown yang sudah dikonversi
3. Teks sudah benar → Tidak ada typo yang ditemukan!

**Verifikasi:**
```bash
python3 -c "
from legal_md_converter.engine.document_service import DocumentService
svc = DocumentService()
print(f'Spellchecker siap: {svc.is_spell_checker_ready()}')
svc.close()
"
```

---

## Getting Help / Mendapatkan Bantuan

**English:** If you encounter an issue not covered here, please:
- Check the log file: `~/.local/share/LegalMDConverter/Logs/legal-md-converter.log`
- Open an issue on GitHub with the error message and log output

**Bahasa Indonesia:** Jika menemui masalah yang tidak tercakup di sini, silakan:
- Periksa file log: `~/.local/share/LegalMDConverter/Logs/legal-md-converter.log`
- Buka issue di GitHub dengan pesan error dan output log

---

*Dokumen ini akan diperbarui seiring perkembangan aplikasi.*
