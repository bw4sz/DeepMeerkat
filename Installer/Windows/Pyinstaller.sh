#!/bin/bash
rm -rf C:/Users/Ben/Documents/DeepMeerkat/Installer/Windows/dis
rm -rf C:/Users/Ben/Documents/DeepMeerkat/Installer/Windows/build 
rm -rf C:/Users/Ben/Documents/DeepMeerkat/Installer/Windows/Output 

/c/Python35/Scripts/pyinstaller -c --windowed -y DeepMeerkat.spec

#copy model
cp -r C:/Users/ben/Dropbox/GoogleCloud/DeepMeerkat_20170924_105144/model dist/Lib/

#Copy FFmpeg binary
cp C:/Python35/Lib/site-packages/opencv_ffmpeg320_64.dll dist/Lib/