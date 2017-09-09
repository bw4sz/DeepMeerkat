import cv2
import numpy as np
import csv
import glob
import os
import math
from collections import defaultdict
import time
import fnmatch
import os
import platform
import datetime
import argparse

parser = argparse.ArgumentParser(description='Create bounding boxes for the machine learning model')
parser.add_argument('--date', help='Date Since Last Run',default="2017-08-27")
args, _ = parser.parse_known_args()

class BoundingBox:
    def __init__(self,x,y,h,w,label,score):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.label=label
        self.score=score
        
def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime

csvs = []
for root, dirnames, filenames in os.walk("/Users/ben/DeepMeerkat/"):
    for filename in fnmatch.filter(filenames, 'annotations.csv'):
        csvs.append(os.path.join(root, filename))

crop_counter=0
        
#remove csv already done sort by date
new_csvs=[]
for csvfile in csvs:
    #convert time
    filedate=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(creation_date(csvfile)))
    if filedate > args.date + '00:00:00':
        new_csvs.append(csvfile)

print(len(new_csvs))
print(new_csvs)

for f in new_csvs:
    
    #Read in frames.csv
    frames=open(f)
    frame_file=csv.reader(frames)
    
    #skip header
    next(frame_file,None)
    
    for row in frame_file:
            
        #read in image
        fname=os.path.split(f)[0] + "/" +row[0]+".jpg"
        img=cv2.imread(fname)
        if img is None:
            continue
        
        box=BoundingBox(x=int(row[1]),y=int(row[2]),h=int(row[3]),w=int(row[4]),label=row[5],score=float(row[6]))
        cropped_image=img[box.y:box.y+box.h,box.x:box.x+box.w]
                                
        #Save image for scoring
        frame_number=os.path.splitext(fname)[0].split("/")[-1]
        
        #video
        video_name=f.split("/")[-2]
        
        #only review Positive scores or low negative scores
        if box.label=="Negative":
            if float(box.score) > 0.95:
                print(str(box.label) + " " +  str(box.score) + " skipped")
                continue
            
        if box.label == "Positive":
            cv2.imwrite("/Users/Ben/Dropbox/GoogleCloud/TestCrops/Positives/"+ video_name+  "_" + frame_number + "_" + str(crop_counter) + ".jpg",cropped_image) 
        else:
            cv2.imwrite("/Users/Ben/Dropbox/GoogleCloud/TestCrops/Negatives/"+ video_name+  "_" + frame_number + "_" + str(crop_counter) + ".jpg",cropped_image) 
        crop_counter+=1