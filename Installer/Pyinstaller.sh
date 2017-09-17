#!/bin/bash
rm -rf C:/Users/Ben/Documents/DeepMeerkat/Installer/dist 

pyinstaller -y --clean --windowed DeepMeerkat.spec

#copy kivy .kv
cp -r C:/Users/Ben/Documents/DeepMeerkat/DeepMeerkat/DeepMeerkat.kv dist/

#test if it works
start C:/Users/ben/Documents/DeepMeerkat/Installer/dist/Lib/DeepMeerkat
