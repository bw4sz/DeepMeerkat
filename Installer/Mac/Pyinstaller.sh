#!/bin/bash

rm -rf /Users/Ben/Documents/DeepMeerkat/Installer/Mac/dist 
rm -rf /Users/Ben/Documents/DeepMeerkat/Installer/Mac/build 

pyinstaller -c --onedir DeepMeerkat.spec

#Somehow the wrong libpng gets pulled, replace it
#grab from homebrew
cp -f /usr/local/Cellar/libpng/1.6.32/lib/libpng16.16.dylib /Users/ben/Documents/DeepMeerkat/Installer/Mac/dist/Lib/libpng16.16.dylib

#copy model across
cp -r /Users/ben/Dropbox/GoogleCloud/DeepMeerkat_20170924_105144/model dist/Lib/

#copy tensorflow across?
cp -R /Library/Python/2.7/site-packages/tensorflow dist/Lib/

pushd dist

hdiutil create ./DeepMeerkat.dmg -srcfolder main.app -ov

popd

#test if it works
open /Users/ben/Documents/DeepMeerkat/Installer/Mac/dist/Lib/main