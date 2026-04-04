#!/bin/bash
# build_debian.sh — Build paket .deb untuk Lentera MD (Debian/Ubuntu)
#
# Prasyarat:
#   - dpkg-dev, fakeroot: sudo apt install dpkg-dev fakeroot
#   - Build PyInstaller terlebih dahulu:
#       python build_app.py --onedir
#     Output ada di: dist/linux/LenteraMD/
#
# Cara pakai:
#   chmod +x build_debian.sh && ./build_debian.sh
#
# Output: dist/lentera-md_1.0.0_amd64.deb

set -e

APP_NAME="lentera-md"
APP_DISPLAY="Lentera MD"
APP_EXE="LenteraMD"
VERSION="1.0.0"
DEBIAN_DIR="debian/${APP_NAME}"
BUILD_DIR="dist/linux/${APP_EXE}"

echo "============================================================"
echo "Building ${APP_DISPLAY} ${VERSION} — paket .deb"
echo "============================================================"

# --- Cek build PyInstaller ---
if [ ! -d "${BUILD_DIR}" ]; then
    echo "ERROR: Build PyInstaller tidak ditemukan di: ${BUILD_DIR}"
    echo "Jalankan terlebih dahulu:"
    echo "  python build_app.py --onedir"
    exit 1
fi

# --- Bersihkan build sebelumnya ---
rm -rf debian/

# --- Buat struktur direktori paket ---
echo ""
echo "[1/4] Membuat struktur paket..."
mkdir -p "${DEBIAN_DIR}/DEBIAN"
mkdir -p "${DEBIAN_DIR}/opt/${APP_NAME}"
mkdir -p "${DEBIAN_DIR}/usr/bin"
mkdir -p "${DEBIAN_DIR}/usr/share/applications"
mkdir -p "${DEBIAN_DIR}/usr/share/icons/hicolor/256x256/apps"
mkdir -p "${DEBIAN_DIR}/usr/share/doc/${APP_NAME}"

# --- Salin file aplikasi ---
echo "[2/4] Menyalin file aplikasi..."

# Salin seluruh build PyInstaller ke /opt/lentera-md/
cp -r "${BUILD_DIR}/." "${DEBIAN_DIR}/opt/${APP_NAME}/"

# Buat symlink di /usr/bin agar bisa dijalankan dari terminal
cat > "${DEBIAN_DIR}/usr/bin/${APP_NAME}" << EOF
#!/bin/bash
exec /opt/${APP_NAME}/${APP_EXE} "\$@"
EOF
chmod 755 "${DEBIAN_DIR}/usr/bin/${APP_NAME}"

# Desktop file
if [ -f "legal-md-converter.desktop" ]; then
    sed "s|Exec=lentera-md|Exec=/opt/${APP_NAME}/${APP_EXE}|g" \
        legal-md-converter.desktop \
        > "${DEBIAN_DIR}/usr/share/applications/${APP_NAME}.desktop"
else
    cat > "${DEBIAN_DIR}/usr/share/applications/${APP_NAME}.desktop" << EOF
[Desktop Entry]
Name=${APP_DISPLAY}
Comment=Konversi dokumen hukum Indonesia ke Markdown
Exec=/opt/${APP_NAME}/${APP_EXE} %F
Icon=${APP_NAME}
Terminal=false
Type=Application
Categories=Office;Utility;
MimeType=application/pdf;text/plain;application/vnd.openxmlformats-officedocument.wordprocessingml.document;
Keywords=legal;document;markdown;converter;indonesia;hukum;lentera;
StartupWMClass=LenteraMD
EOF
fi

# Icon
if [ -f "assets/icons/app_icon.png" ]; then
    cp "assets/icons/app_icon.png" \
       "${DEBIAN_DIR}/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"
fi

# Dokumentasi
if [ -f "README.md" ]; then
    cp "README.md" "${DEBIAN_DIR}/usr/share/doc/${APP_NAME}/"
fi

# --- Buat control file ---
echo "[3/4] Membuat metadata paket..."

# Hitung ukuran paket
INSTALLED_SIZE=$(du -sk "${DEBIAN_DIR}/opt/${APP_NAME}" | cut -f1)

cat > "${DEBIAN_DIR}/DEBIAN/control" << EOF
Package: ${APP_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: amd64
Installed-Size: ${INSTALLED_SIZE}
Depends: libc6 (>= 2.17), libstdc++6 (>= 9), libglib2.0-0, libgl1, fontconfig, libxcb-xinerama0, libxcb-icccm4, libxcb-image0, libxcb-keysyms1, libxcb-render-util0
Maintainer: Lentera MD Team <team@lenteramd.app>
Homepage: https://github.com/ziffan/Lentera-MD-Converter
Description: Konversi dokumen hukum Indonesia ke Markdown
 Aplikasi desktop untuk mengonversi dokumen hukum Indonesia
 (PDF, DOCX, DOC, TXT, RTF) ke format Markdown, dilengkapi
 pemeriksaan ejaan berbasis KBBI dengan 71.093 kata.
 .
 Fitur utama:
  - Multi-format: PDF, DOCX, DOC, TXT, RTF
  - Drag & Drop
  - Pemeriksaan ejaan KBBI
  - Preview dapat diedit
  - Cross-platform (Windows, macOS, Linux)
EOF

# postinst — update cache setelah install
cat > "${DEBIAN_DIR}/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e
if [ "$1" = "configure" ]; then
    update-desktop-database -q 2>/dev/null || true
    gtk-update-icon-cache -qf /usr/share/icons/hicolor 2>/dev/null || true
fi
EOF
chmod 755 "${DEBIAN_DIR}/DEBIAN/postinst"

# postrm — update cache setelah hapus
cat > "${DEBIAN_DIR}/DEBIAN/postrm" << 'EOF'
#!/bin/bash
set -e
if [ "$1" = "remove" ] || [ "$1" = "purge" ]; then
    update-desktop-database -q 2>/dev/null || true
    gtk-update-icon-cache -qf /usr/share/icons/hicolor 2>/dev/null || true
fi
EOF
chmod 755 "${DEBIAN_DIR}/DEBIAN/postrm"

# --- Build paket .deb ---
echo "[4/4] Membangun paket .deb..."
mkdir -p dist
DEB_PATH="dist/${APP_NAME}_${VERSION}_amd64.deb"
dpkg-deb --build "${DEBIAN_DIR}" "${DEB_PATH}"

echo ""
echo "============================================================"
echo "Selesai!"
echo "  Paket: ${DEB_PATH}"
echo ""
echo "Cara install:"
echo "  sudo dpkg -i ${DEB_PATH}"
echo "  sudo apt-get install -f   # jika ada dependensi yang kurang"
echo ""
echo "Cara hapus:"
echo "  sudo apt remove ${APP_NAME}"
echo "============================================================"
