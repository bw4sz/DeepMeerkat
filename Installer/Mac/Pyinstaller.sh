#!/bin/bash

rm -rf /Users/Ben/Documents/DeepMeerkat/Installer/Mac/dist 
rm -rf /Users/Ben/Documents/DeepMeerkat/Installer/Mac/build 

pyinstaller  --windowed --onedir DeepMeerkat.spec

#Somehow the wrong libpng gets pulled, replace it
#grab from homebrew
cp -f /usr/local/Cellar/libpng/1.6.32/lib/libpng16.16.dylib /Users/ben/Documents/DeepMeerkat/Installer/Mac/dist/DeepMeerkat.app/Contents/MacOS/libpng16.16.dylib

#copy model across
cp -r /Users/ben/Dropbox/GoogleCloud/DeepMeerkat_20171011_134826/model dist/DeepMeerkat.app/Contents/Resources

pushd dist

hdiutil create ./DeepMeerkat.dmg -srcfolder DeepMeerkat.app -ov

popd

#test if it works
open /Users/ben/Documents/DeepMeerkat/Installer/Mac/dist/DeepMeerkat.app