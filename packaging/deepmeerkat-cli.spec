# PyInstaller spec for the `deepmeerkat` CLI (console).
# Build from repo root:
#   pip install pyinstaller
#   pyinstaller --noconfirm packaging/deepmeerkat-cli.spec
#
# MegaDetector pulls PyTorch; bundles are large.

import os
from pathlib import Path

root = Path(os.path.dirname(os.path.abspath(SPEC))).parent

block_cipher = None

a = Analysis(
    [str(root / "packaging" / "run_cli.py")],
    pathex=[str(root / "src")],
    binaries=[],
    datas=[],
    hiddenimports=[
        "megadetector",
        "megadetector.detection",
        "megadetector.detection.run_detector",
        "torch",
        "cv2",
    ],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="deepmeerkat",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
