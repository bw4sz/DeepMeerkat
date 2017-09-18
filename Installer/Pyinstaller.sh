#!/bin/bash
rm -rf C:/Users/Ben/Documents/DeepMeerkat/Installer/dist 

/c/Python35/Scripts/pyinstaller --onefile -y --clean --windowed DeepMeerkat.spec

#copy kivy .kv
cp -r C:/Users/Ben/Documents/DeepMeerkat/DeepMeerkat/DeepMeerkat.kv dist/

#test if it works
./dist/Lib/DeepMeerkat.exe
