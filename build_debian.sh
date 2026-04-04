#!/bin/bash
# build_debian.sh - Build .deb package for Lentera MD
# Requires: dpkg-dev, fakeroot

set -e

APP_NAME="lentera-md"
VERSION="1.0.0"
DEBIAN_DIR="debian/${APP_NAME}"

echo "============================================================"
echo "Building ${APP_NAME} ${VERSION} .deb package"
echo "============================================================"

# Clean previous build
rm -rf debian/

# Create directory structure
echo ""
echo "[1/4] Creating package structure..."
mkdir -p "${DEBIAN_DIR}/DEBIAN"
mkdir -p "${DEBIAN_DIR}/usr/bin"
mkdir -p "${DEBIAN_DIR}/usr/share/applications"
mkdir -p "${DEBIAN_DIR}/usr/share/icons/hicolor/256x256/apps"
mkdir -p "${DEBIAN_DIR}/usr/share/doc/${APP_NAME}"

# Copy executable
echo "[2/4] Copying files..."
if [ -d "dist/linux" ]; then
    cp -r dist/linux/* "${DEBIAN_DIR}/usr/"
else
    # Fallback: copy source for pip install
    echo "⚠️  No dist/linux found. Building with pip first..."
    pip install . --target "${DEBIAN_DIR}/usr/lib/python3/dist-packages/${APP_NAME}"
    cat > "${DEBIAN_DIR}/usr/bin/${APP_NAME}" << 'WRAPPER'
#!/bin/bash
exec python3 -m legal_md_converter.main "$@"
WRAPPER
    chmod +x "${DEBIAN_DIR}/usr/bin/${APP_NAME}"
fi

# Copy desktop file
cp legal-md-converter.desktop "${DEBIAN_DIR}/usr/share/applications/${APP_NAME}.desktop"

# Copy icon
if [ -f "assets/icons/app_icon.png" ]; then
    cp assets/icons/app_icon.png "${DEBIAN_DIR}/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"
fi

# Copy assets
cp -r assets "${DEBIAN_DIR}/usr/share/${APP_NAME}/" 2>/dev/null || true

# Create control file
echo "[3/4] Creating control file..."
cat > "${DEBIAN_DIR}/DEBIAN/control" << EOF
Package: ${APP_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: amd64
Depends: libc6, libstdc++6, libglib2.0-0, libgl1, fontconfig
Maintainer: Lentera MD Team <team@lenteramd.app>
Description: Convert Indonesian legal documents to Markdown
 A desktop application for converting Indonesian legal PDFs and
 TXT documents to structured Markdown format with built-in
 KBBI spellchecking.
EOF

# Create postinst script
cat > "${DEBIAN_DIR}/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e
if [ "$1" = "configure" ]; then
    update-desktop-database -q 2>/dev/null || true
    gtk-update-icon-cache -q /usr/share/icons/hicolor 2>/dev/null || true
fi
EOF
chmod 755 "${DEBIAN_DIR}/DEBIAN/postinst"

# Create postrm script
cat > "${DEBIAN_DIR}/DEBIAN/postrm" << 'EOF'
#!/bin/bash
set -e
if [ "$1" = "remove" ]; then
    update-desktop-database -q 2>/dev/null || true
    gtk-update-icon-cache -q /usr/share/icons/hicolor 2>/dev/null || true
fi
EOF
chmod 755 "${DEBIAN_DIR}/DEBIAN/postrm"

# Build package
echo "[4/4] Building .deb package..."
mkdir -p dist
dpkg-deb --build "${DEBIAN_DIR}" "dist/${APP_NAME}_${VERSION}_amd64.deb"

echo ""
echo "============================================================"
echo "Build complete!"
echo "  Package: dist/${APP_NAME}_${VERSION}_amd64.deb"
echo "  Install: sudo dpkg -i dist/${APP_NAME}_${VERSION}_amd64.deb"
echo "============================================================"
