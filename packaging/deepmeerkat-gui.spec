# PyInstaller spec for `deepmeerkat-gui` (PySide6 window).
# Build: pyinstaller --noconfirm packaging/deepmeerkat-gui.spec

import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files

root = Path(os.path.dirname(os.path.abspath(SPEC))).parent

# Bundled PNG (logo) for importlib.resources
datas = collect_data_files("deepmeerkat", include_py_files=False)

block_cipher = None

a = Analysis(
    [str(root / "packaging" / "run_gui.py")],
    pathex=[str(root / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "PySide6",
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
    name="deepmeerkat-gui",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
