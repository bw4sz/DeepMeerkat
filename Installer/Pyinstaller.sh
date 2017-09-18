#!/bin/bash
rm -rf /Users/Ben/Documents/DeepMeerkat/Installer/dist 

pyinstaller -y --clean --windowed DeepMeerkat.spec

#Somehow the wrong libpng gets pulled, replace it
#grab from homebrew
cp -f /usr/local/Cellar/libpng/1.6.32/lib/libpng16.16.dylib /Users/ben/Documents/DeepMeerkat/Installer/dist/Lib/libpng16.16.dylib

pushd dist

hdiutil create ./DeepMeerkat.dmg -srcfolder DeepMeerkat.app -ov

popd

#test if it works
open /Users/ben/Documents/DeepMeerkat/Installer/dist/Lib/main
