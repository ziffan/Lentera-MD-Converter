#!/bin/bash
# build_macos.sh — Build dan kemas Lentera MD untuk macOS
#
# Prasyarat:
#   - Xcode Command Line Tools: xcode-select --install
#   - create-dmg (opsional, untuk DMG): brew install create-dmg
#   - Developer ID Application certificate (opsional, untuk codesign + notarize)
#
# Cara pakai:
#   chmod +x build_macos.sh && ./build_macos.sh
#
# Output: dist/darwin/LenteraMD.app  dan  dist/LenteraMD.dmg (jika create-dmg tersedia)

set -e

APP_NAME="LenteraMD"
APP_DISPLAY="Lentera MD"
BUNDLE_ID="com.lenteramd.app"
VERSION="1.0.0"
DIST_DIR="dist/darwin"

echo "============================================================"
echo "Building ${APP_DISPLAY} untuk macOS"
echo "============================================================"

# Step 1: Build dengan PyInstaller menggunakan .spec file
echo ""
echo "[1/3] Building dengan PyInstaller..."
pyinstaller LegalMDConverter.spec \
    --distpath="${DIST_DIR}" \
    --workpath="build/darwin/temp" \
    --clean

# Verifikasi build
if [ ! -d "${DIST_DIR}/${APP_NAME}.app" ]; then
    echo "ERROR: ${APP_NAME}.app tidak ditemukan di ${DIST_DIR}/"
    exit 1
fi
echo "Build berhasil: ${DIST_DIR}/${APP_NAME}.app"

# Step 2: Buat DMG
echo ""
echo "[2/3] Membuat DMG..."
mkdir -p dist/dmg
rm -rf "dist/dmg/${APP_NAME}.app"
cp -r "${DIST_DIR}/${APP_NAME}.app" "dist/dmg/"

DMG_PATH="dist/${APP_NAME}-${VERSION}.dmg"

if command -v create-dmg &>/dev/null; then
    rm -f "${DMG_PATH}"
    create-dmg \
        --volname "${APP_DISPLAY}" \
        --volicon "assets/icons/app_icon.icns" \
        --window-pos 200 120 \
        --window-size 660 400 \
        --icon-size 100 \
        --icon "${APP_NAME}.app" 160 185 \
        --hide-extension "${APP_NAME}.app" \
        --app-drop-link 500 185 \
        "${DMG_PATH}" \
        "dist/dmg/"
    echo "DMG dibuat: ${DMG_PATH}"
else
    echo "PERINGATAN: create-dmg tidak terinstall. Lewati pembuatan DMG."
    echo "  Install dengan: brew install create-dmg"
    echo "  App bundle tersedia di: ${DIST_DIR}/${APP_NAME}.app"
fi

# Step 3: Code signing dan notarization (opsional)
echo ""
echo "[3/3] Code signing dan notarization..."

DEVELOPER_ID=$(security find-identity -v -p codesigning 2>/dev/null \
    | grep "Developer ID Application" | head -1 | awk -F'"' '{print $2}')

if [ -z "${DEVELOPER_ID}" ]; then
    echo "PERINGATAN: Tidak ada certificate Developer ID Application."
    echo "  App akan berjalan tapi mungkin muncul peringatan Gatekeeper."
    echo ""
    echo "Untuk mengaktifkan signing:"
    echo "  1. Daftar Apple Developer Program"
    echo "  2. Buat Developer ID Application certificate di Keychain Access"
    echo "  3. Set environment variable sebelum build:"
    echo "       export APPLE_ID='email@example.com'"
    echo "       export APPLE_APP_PASSWORD='xxxx-xxxx-xxxx-xxxx'"
else
    echo "Signing dengan: ${DEVELOPER_ID}"

    # Buat entitlements jika belum ada
    if [ ! -f "app.entitlements" ]; then
        cat > app.entitlements << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-jit</key>
    <false/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <false/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
</dict>
</plist>
PLIST
        echo "Entitlements dibuat: app.entitlements"
    fi

    codesign --force --deep --sign "${DEVELOPER_ID}" \
        --options runtime \
        --entitlements "app.entitlements" \
        "${DIST_DIR}/${APP_NAME}.app"
    echo "App signed"

    # Notarisasi (opsional — butuh APPLE_ID dan APPLE_APP_PASSWORD)
    if [ -n "${APPLE_ID}" ] && [ -n "${APPLE_APP_PASSWORD}" ]; then
        TEAM_ID=$(echo "${DEVELOPER_ID}" | grep -oP '\(\K[^)]+')
        echo "Mengirim untuk notarisasi..."
        xcrun notarytool submit "${DMG_PATH:-${DIST_DIR}/${APP_NAME}.app}" \
            --apple-id "${APPLE_ID}" \
            --password "${APPLE_APP_PASSWORD}" \
            --team-id "${TEAM_ID}" \
            --wait
        xcrun stapler staple "${DMG_PATH:-${DIST_DIR}/${APP_NAME}.app}"
        echo "Notarisasi selesai"
    else
        echo "PERINGATAN: APPLE_ID / APPLE_APP_PASSWORD tidak di-set. Lewati notarisasi."
        echo "  export APPLE_ID='email@example.com'"
        echo "  export APPLE_APP_PASSWORD='app-specific-password'"
    fi
fi

echo ""
echo "============================================================"
echo "Selesai!"
echo "  App:  ${DIST_DIR}/${APP_NAME}.app"
if [ -f "${DMG_PATH}" ]; then
    echo "  DMG:  ${DMG_PATH}"
fi
echo "============================================================"
