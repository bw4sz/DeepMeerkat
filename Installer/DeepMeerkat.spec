# -*- mode: python -*-
import cv2
import numpy

from kivy.tools.packaging.pyinstaller_hooks import (
    hookspath,
    runtime_hooks
)


block_cipher = None

a = Analysis(['C:/Users/Ben/Documents/DeepMeerkat/DeepMeerkat/main.py'],
             pathex=['C:/Users/ben/Documents/DeepMeerkat/DeepMeerkat',"C:/Program Files (x86)/Windows Kits/10/Redist/ucrt/DLLs/x64/"],
             binaries=[],
             datas=[],
             hiddenimports=['win32timezone',"cv2","numpy","multiprocessing"],
             hookspath=[],
             runtime_hooks=[],
             excludes=['Tkinter', 'enchant', 'twisted'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='DeepMeerkat',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe, Tree('C:/Users/ben/Documents/DeepMeerkat/DeepMeerkat'),
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Lib')
app = BUNDLE(coll,
             name='DeepMeerkat.app',
             icon='C:/Users/ben/Documents/DeepMeerkat/DeepMeerkat/images/thumbnail.png',
             bundle_identifier=None)
