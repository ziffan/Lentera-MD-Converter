#!/bin/bash
# build_appimage.sh — Build AppImage untuk Lentera MD (Linux x86_64)
#
# Prasyarat:
#   1. Build PyInstaller terlebih dahulu:
#        python build_app.py --onedir
#      Output ada di: dist/linux/LenteraMD/
#   2. appimagetool tersedia di PATH atau di folder ini
#        Unduh: https://github.com/AppImage/AppImageKit/releases
#        chmod +x appimagetool-x86_64.AppImage
#
# Cara pakai:
#   chmod +x installer/linux/build_appimage.sh
#   ./installer/linux/build_appimage.sh
#
# Output: dist/LenteraMD-1.0.0-x86_64.AppImage

set -e

APP_NAME="LenteraMD"
APP_LOWER="lentera-md"
VERSION="1.0.0"
ARCH="x86_64"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BUILD_DIR="${ROOT_DIR}/dist/linux/${APP_NAME}"
APPDIR="${ROOT_DIR}/dist/${APP_NAME}.AppDir"

echo "============================================================"
echo "Building ${APP_NAME} AppImage v${VERSION}"
echo "============================================================"

# --- Cek build PyInstaller ---
if [ ! -d "${BUILD_DIR}" ]; then
    echo "ERROR: Build PyInstaller tidak ditemukan di: ${BUILD_DIR}"
    echo "Jalankan terlebih dahulu:"
    echo "  python build_app.py --onedir"
    exit 1
fi

# --- Cek appimagetool ---
if command -v appimagetool &>/dev/null; then
    APPIMAGETOOL="appimagetool"
elif [ -f "${SCRIPT_DIR}/appimagetool-x86_64.AppImage" ]; then
    APPIMAGETOOL="${SCRIPT_DIR}/appimagetool-x86_64.AppImage"
elif [ -f "${ROOT_DIR}/appimagetool-x86_64.AppImage" ]; then
    APPIMAGETOOL="${ROOT_DIR}/appimagetool-x86_64.AppImage"
else
    echo "ERROR: appimagetool tidak ditemukan."
    echo "Unduh dari: https://github.com/AppImage/AppImageKit/releases"
    echo "Lalu letakkan di folder ini atau di PATH:"
    echo "  ${SCRIPT_DIR}/appimagetool-x86_64.AppImage"
    exit 1
fi

# --- Buat AppDir ---
echo ""
echo "[1/4] Membuat AppDir..."
rm -rf "${APPDIR}"
mkdir -p "${APPDIR}/usr/bin"
mkdir -p "${APPDIR}/usr/share/applications"
mkdir -p "${APPDIR}/usr/share/icons/hicolor/256x256/apps"

# Salin seluruh build PyInstaller
cp -r "${BUILD_DIR}/." "${APPDIR}/usr/bin/"

# --- Salin aset ---
echo "[2/4] Menyalin aset..."

# Icon
if [ -f "${ROOT_DIR}/assets/icons/app_icon.png" ]; then
    cp "${ROOT_DIR}/assets/icons/app_icon.png" \
       "${APPDIR}/usr/share/icons/hicolor/256x256/apps/${APP_LOWER}.png"
    cp "${ROOT_DIR}/assets/icons/app_icon.png" "${APPDIR}/${APP_LOWER}.png"
fi

# Desktop file AppImage (harus ada di root AppDir)
cat > "${APPDIR}/${APP_LOWER}.desktop" << EOF
[Desktop Entry]
Name=Lentera MD
Comment=Konversi dokumen hukum Indonesia ke Markdown
Exec=${APP_NAME}
Icon=${APP_LOWER}
Terminal=false
Type=Application
Categories=Office;Utility;
MimeType=application/pdf;text/plain;application/vnd.openxmlformats-officedocument.wordprocessingml.document;
Keywords=legal;document;markdown;converter;indonesia;hukum;lentera;
StartupWMClass=LenteraMD
EOF

cp "${APPDIR}/${APP_LOWER}.desktop" \
   "${APPDIR}/usr/share/applications/${APP_LOWER}.desktop"

# AppRun — entry point AppImage
cat > "${APPDIR}/AppRun" << 'APPRUN'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/LenteraMD" "$@"
APPRUN
chmod +x "${APPDIR}/AppRun"

# --- Build AppImage ---
echo "[3/4] Membangun AppImage..."
OUTPUT="${ROOT_DIR}/dist/${APP_NAME}-${VERSION}-${ARCH}.AppImage"

ARCH=${ARCH} "${APPIMAGETOOL}" "${APPDIR}" "${OUTPUT}"

# --- Selesai ---
echo ""
echo "[4/4] Membersihkan AppDir sementara..."
rm -rf "${APPDIR}"

echo ""
echo "============================================================"
echo "Selesai!"
echo "  AppImage: ${OUTPUT}"
echo ""
echo "Cara pakai:"
echo "  chmod +x ${APP_NAME}-${VERSION}-${ARCH}.AppImage"
echo "  ./${APP_NAME}-${VERSION}-${ARCH}.AppImage"
echo "============================================================"
