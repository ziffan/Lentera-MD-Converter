# Panduan Rilis Lentera MD

Dokumen ini menjelaskan cara membangun installer/paket distribusi Lentera MD untuk setiap platform.

---

## Persiapan (semua platform)

```bash
# Clone dan masuk ke direktori proyek
git clone https://github.com/ziffan/Lentera-MD-Converter
cd Lentera-MD-Converter

# Aktifkan virtual environment
python -m venv venv
source venv/bin/activate          # Linux / macOS
venv\Scripts\activate             # Windows

# Install PyTorch CPU-only
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install semua dependensi termasuk PyInstaller
pip install -e ".[dev]"
pip install pyinstaller
```

---

## Windows — Installer (.exe via Inno Setup)

### Langkah 1: Build executable dengan PyInstaller

```bat
python build_app.py --onedir
```

Output: `dist\windows\LenteraMD\`

### Langkah 2: Install Inno Setup 6

Unduh dari: https://jrsoftware.org/isdl.php

### Langkah 3: Compile installer

```bat
:: Dari command line (iscc harus di PATH)
iscc installer\windows\lentera_md_setup.iss

:: Atau buka lentera_md_setup.iss di Inno Setup IDE → Compile (Ctrl+F9)
```

Output: `installer\windows\Output\LenteraMD_Setup_1.0.0.exe`

### Catatan

- Installer mendukung install per-user (tanpa hak admin) maupun system-wide
- Membuat shortcut Start Menu dan opsional Desktop
- Uninstaller sudah termasuk
- Untuk signing dengan certificate: beli code signing certificate dari CA terpercaya (Sectigo, DigiCert, dll.) lalu set di bagian `[Setup]` pada file `.iss`

---

## macOS — DMG (via PyInstaller + create-dmg)

### Prasyarat

```bash
# Xcode Command Line Tools
xcode-select --install

# create-dmg (opsional, untuk membuat DMG)
brew install create-dmg
```

### Build

```bash
chmod +x build_macos.sh
./build_macos.sh
```

Output:
- `dist/darwin/LenteraMD.app` — bundle aplikasi
- `dist/LenteraMD-1.0.0.dmg` — disk image (jika create-dmg tersedia)

### Code Signing dan Notarisasi (opsional)

Diperlukan agar tidak muncul peringatan Gatekeeper:

1. Daftar [Apple Developer Program](https://developer.apple.com/programs/) ($99/tahun)
2. Buat **Developer ID Application** certificate
3. Buat app-specific password di appleid.apple.com
4. Set environment variable sebelum build:

```bash
export APPLE_ID="email@example.com"
export APPLE_APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"
./build_macos.sh
```

Script otomatis mendeteksi certificate dan melakukan signing + notarisasi + stapling.

---

## Linux — Paket .deb (Debian/Ubuntu)

### Prasyarat

```bash
sudo apt install dpkg-dev fakeroot
```

### Build

```bash
# Step 1: Build executable
python build_app.py --onedir

# Step 2: Kemas ke .deb
chmod +x build_debian.sh
./build_debian.sh
```

Output: `dist/lentera-md_1.0.0_amd64.deb`

### Install paket

```bash
sudo dpkg -i dist/lentera-md_1.0.0_amd64.deb
sudo apt-get install -f    # perbaiki dependensi jika ada
```

---

## Linux — AppImage (portable, semua distro)

AppImage berjalan di semua distro Linux tanpa instalasi.

### Prasyarat

```bash
# Unduh appimagetool
wget -O installer/linux/appimagetool-x86_64.AppImage \
    https://github.com/AppImage/AppImageKit/releases/latest/download/appimagetool-x86_64.AppImage
chmod +x installer/linux/appimagetool-x86_64.AppImage
```

### Build

```bash
# Step 1: Build executable
python build_app.py --onedir

# Step 2: Buat AppImage
chmod +x installer/linux/build_appimage.sh
./installer/linux/build_appimage.sh
```

Output: `dist/LenteraMD-1.0.0-x86_64.AppImage`

### Distribusi

```bash
chmod +x LenteraMD-1.0.0-x86_64.AppImage
./LenteraMD-1.0.0-x86_64.AppImage
```

---

## Struktur Output

```
dist/
├── windows/
│   └── LenteraMD/              ← hasil PyInstaller (Windows)
├── darwin/
│   └── LenteraMD.app/          ← hasil PyInstaller (macOS)
├── linux/
│   └── LenteraMD/              ← hasil PyInstaller (Linux)
├── LenteraMD_Setup_1.0.0.exe   ← installer Windows (Inno Setup)
├── LenteraMD-1.0.0.dmg         ← disk image macOS
├── lentera-md_1.0.0_amd64.deb  ← paket Debian/Ubuntu
└── LenteraMD-1.0.0-x86_64.AppImage  ← AppImage Linux portable
```

---

## Checklist Rilis GitHub

- [ ] Update `version` di `pyproject.toml`
- [ ] Update `AppVersion` di `installer/windows/lentera_md_setup.iss`
- [ ] Update `VERSION` di `build_macos.sh`, `build_debian.sh`, `installer/linux/build_appimage.sh`
- [ ] Jalankan tests: `pytest tests/ -v` → semua harus pass
- [ ] Build semua platform
- [ ] Buat Git tag: `git tag v1.0.0 && git push origin v1.0.0`
- [ ] Buat GitHub Release, upload semua artefak build
- [ ] Update README jika ada perubahan fitur
