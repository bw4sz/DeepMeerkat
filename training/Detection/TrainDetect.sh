#!/bin/bash 

#start virtual env
source detection/bin/activate

#Converted labeled records to TFrecords format

# this should be your array of image data dictionaries. 
# Don't forget that you'll want to separate your training and testing data.
python PrepareData.py


