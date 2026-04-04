#!/bin/bash
# build_macos.sh - Build and package Lentera MD for macOS
# Requires: Xcode Command Line Tools, Developer ID certificate (for notarization)

set -e

APP_NAME="LenteraMD"
BUNDLE_ID="com.lenteramd.app"
VERSION="1.0.0"

echo "============================================================"
echo "Building ${APP_NAME} for macOS"
echo "============================================================"

# Step 1: Build with PyInstaller
echo ""
echo "[1/3] Building with PyInstaller..."
pyinstaller LenteraMD.spec

# Verify build
if [ ! -d "dist/macos/${APP_NAME}.app" ]; then
    echo "❌ Build failed: ${APP_NAME}.app not found"
    exit 1
fi
echo "✅ Build successful"

# Step 2: Create DMG
echo ""
echo "[2/3] Creating DMG..."
mkdir -p dist/dmg
cp -r "dist/macos/${APP_NAME}.app" "dist/dmg/"

if command -v create-dmg &> /dev/null; then
    create-dmg \
        --volname "${APP_NAME}" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "${APP_NAME}.app" 150 185 \
        --hide-extension "${APP_NAME}.app" \
        "dist/${APP_NAME}.dmg" \
        "dist/dmg/"
    echo "✅ DMG created: dist/${APP_NAME}.dmg"
else
    echo "⚠️  create-dmg not installed. Skipping DMG creation."
    echo "    Install with: brew install create-dmg"
    echo "    App bundle is available at: dist/macos/${APP_NAME}.app"
fi

# Step 3: Code signing and notarization (optional)
echo ""
echo "[3/3] Code signing and notarization..."

# Check if Developer ID is available
DEVELOPER_ID=$(security find-identity -v -p codesigning | grep "Developer ID Application" | head -1 | awk -F'"' '{print $2}')

if [ -z "$DEVELOPER_ID" ]; then
    echo "⚠️  No Developer ID Application certificate found."
    echo "    Skipping code signing and notarization."
    echo "    App will work but may show Gatekeeper warnings."
    echo ""
    echo "To enable signing, you need:"
    echo "  1. Apple Developer Program membership"
    echo "  2. Developer ID Application certificate"
    echo "  3. App-specific password for notarization"
else
    echo "Signing with: ${DEVELOPER_ID}"
    
    # Sign the app
    codesign --force --sign "${DEVELOPER_ID}" \
        --options runtime \
        --entitlements "app.entitlements" \
        "dist/macos/${APP_NAME}.app"
    
    echo "✅ App signed"
    
    # Notarize (requires Apple ID and app-specific password)
    if [ -n "$APPLE_ID" ] && [ -n "$APPLE_APP_PASSWORD" ]; then
        echo "Submitting for notarization..."
        xcrun notarytool submit "dist/macos/${APP_NAME}.app" \
            --apple-id "${APPLE_ID}" \
            --password "${APPLE_APP_PASSWORD}" \
            --team-id "$(echo ${DEVELOPER_ID} | cut -d'(' -f2 | cut -d')' -f1)" \
            --wait
        
        # Staple the ticket
        xcrun stapler staple "dist/macos/${APP_NAME}.app"
        echo "✅ Notarized and stapled"
    else
        echo "⚠️  APPLE_ID and APPLE_APP_PASSWORD not set."
        echo "    Skipping notarization."
        echo "    Set environment variables to enable:"
        echo "      export APPLE_ID='your@email.com'"
        echo "      export APPLE_APP_PASSWORD='app-specific-password'"
    fi
fi

echo ""
echo "============================================================"
echo "Build complete!"
echo "  App: dist/macos/${APP_NAME}.app"
if [ -f "dist/${APP_NAME}.dmg" ]; then
    echo "  DMG: dist/${APP_NAME}.dmg"
fi
echo "============================================================"
