#!/bin/bash

rm -rf /Users/Ben/Documents/DeepMeerkat/Installer/Mac/dist 
rm -rf /Users/Ben/Documents/DeepMeerkat/Installer/Mac/build 

pyinstaller  --windowed --onedir DeepMeerkat.spec

#Somehow the wrong libpng gets pulled, replace it
#grab from homebrew
cp -f /usr/local/Cellar/libpng/1.6.32/lib/libpng16.16.dylib /Users/ben/Documents/DeepMeerkat/Installer/Mac/dist/DeepMeerkat.app/Contents/MacOS/libpng16.16.dylib

#copy model across
cp -r /Users/ben/Dropbox/GoogleCloud/DeepMeerkat_20180109_090611/model dist/DeepMeerkat.app/Contents/Resources

#sign it (may need to remove .DS_store files)
codesign --deep -f -s "Ben Weinstein" DeepMeerkat.app
codesign --deep -f -s "Ben Weinstein" DeepMeerkat.dmg

pushd dist

hdiutil create ./DeepMeerkat.dmg -srcfolder DeepMeerkat.app -ov

popd

#test if it works
open /Users/ben/Documents/DeepMeerkat/Installer/Mac/dist/DeepMeerkat.app