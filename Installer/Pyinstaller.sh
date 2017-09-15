#!/bin/bash
rm -rf /Users/Ben/Documents/DeepMeerkat/Installer/dist 

pyinstaller -y --clean --windowed DeepMeerkat.spec

#Somehow the wrong libpng gets pulled, replace it
rm /Users/ben/Documents/DeepMeerkat/Installer/dist/DeepMeerkat.app/Contents/MacOS/libpng16.16.dylib

#grab from homebrew
cp /usr/local/Cellar/libpng/ /Users/ben/Documents/DeepMeerkat/Installer/dist/DeepMeerkat.app/Contents/MacOS/

#copy kivy .kv
cp -r /Users/Ben/Documents/DeepMeerkat/DeepMeerkat/DeepMeerkat.kv dist/

pushd dist

hdiutil create ./DeepMeerkat.dmg -srcfolder DeepMeerkat.app -ov

popd

#test if it works
open /Users/ben/Documents/DeepMeerkat/Installer/dist/Lib/DeepMeerkat
