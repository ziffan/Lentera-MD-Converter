# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata, collect_all

block_cipher = None

# Kumpulkan semua submodul + data + metadata paket yang tidak terdeteksi otomatis
all_datas, all_binaries, all_hiddenimports = [], [], []
for pkg in [
    'docling',        # submodul + entry points (docling.models.plugins)
    'docling_parse',  # pdf_resources/ — KRITIS untuk konversi PDF
    'docling_core',   # JSON schemas
    'pypdfium2',      # backend PDF alternatif
    'rapidocr',       # OCR engine (OcrAutoOptions)
    'cv2',            # OpenCV untuk image processing
    'lxml',           # XML/HTML parser
]:
    try:
        d, b, h = collect_all(pkg)
        all_datas += d
        all_binaries += b
        all_hiddenimports += h
    except Exception:
        pass

# Metadata untuk paket yang pakai importlib.metadata.version()
pkg_metadata = []
for pkg in ['docling', 'docling-core', 'docling-ibm-models', 'docling-parse',
            'huggingface-hub', 'transformers', 'tokenizers']:
    try:
        pkg_metadata += copy_metadata(pkg)
    except Exception:
        pass

a = Analysis(
    ['src/legal_md_converter/main.py'],
    pathex=[],
    binaries=[] + all_binaries,
    datas=[
        ('assets', 'assets'),
    ] + all_datas + pkg_metadata,
    hiddenimports=[
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtPrintSupport',
        'sqlite3',
        'importlib.metadata',
    ] + all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LenteraMD',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app_icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LenteraMD',
)

# macOS specific bundle
app = BUNDLE(
    coll,
    name='LenteraMD.app',
    icon='assets/icons/app_icon.icns',
    bundle_identifier='com.lenteramd.app',
    info_plist={
        'CFBundleDisplayName': 'Lentera MD',
        'LSMinimumSystemVersion': '10.15',
        'NSHumanReadableCopyright': 'Copyright 2026 Lentera MD',
    },
)
