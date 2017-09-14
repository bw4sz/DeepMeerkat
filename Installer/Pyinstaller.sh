#!/bin/bash

cd /Users/Ben/Documents/DeepMeerkat/DeepMeerkat

#remove all previous installs
rm -rf dist/

pyinstaller -y --clean --windowed --name DeepMeerkat \
  --exclude-module _tkinter \
  --exclude-module Tkinter \
  --exclude-module enchant \
  --exclude-module twisted \
  /Users/Ben/Documents/DeepMeerkat/DeepMeerkat/main.py

#copy kivy .kv
cp -r /Users/Ben/Documents/DeepMeerkat/DeepMeerkat/DeepMeerkat.kv dist/main/

#Copy icon
cp /Users/Ben/Documents/DeepMeerkat/thumbnail.ico dist/main/

#Copy plotwatcher test file
cp /Users/Ben/Documents/DeepMeerkat/Hummingbird.avi dist/main/

#Copy FFmpeg binary?
#cp /Python27/opencv_ffmpeg310.dll dist/main/