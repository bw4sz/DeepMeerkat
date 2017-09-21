#!/bin/bash
rm -rf C:/Users/Ben/Documents/DeepMeerkat/Installer/dist 
rm -rf C:/Users/Ben/Documents/DeepMeerkat/Installer/build 
rm -rf C:/Users/Ben/Documents/DeepMeerkat/Installer/Output 

/c/Python35/Scripts/pyinstaller --onefile -y --clean --windowed DeepMeerkat.spec

#copy kivy .kv
cp -r C:/Users/Ben/Documents/DeepMeerkat/DeepMeerkat/DeepMeerkat.kv dist/

#copy model
cp -r C:/Users/ben/Dropbox/GoogleCloud/DeepMeerkat_20170920_211010/model dist/Lib/

