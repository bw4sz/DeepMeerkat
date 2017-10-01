# -*- mode: python -*-

block_cipher = None

a = Analysis(['/Users/Ben/Documents/DeepMeerkat/DeepMeerkat/main.py'],
             pathex=['/Users/ben/Documents/DeepMeerkat/DeepMeerkat/'],
             binaries=[],
             datas=[],
             hiddenimports=["tensorflow"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[ 'enchant', 'twisted'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='main',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe, Tree('/Users/ben/Documents/DeepMeerkat/DeepMeerkat'),
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Lib')
app = BUNDLE(coll,
             name='DeepMeerkat.app',
             icon='/Users/ben/Documents/DeepMeerkat/DeepMeerkat/images/thumbnail.png',
             bundle_identifier=None)