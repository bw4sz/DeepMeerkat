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

def mult(p,x):
    return(int(p+p*x))

def check_bounds(img,axis,p):
    if p > img.shape[axis]:
        p=img.shape[axis]
    if p < 0:
        p=0
    return(p)

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
    
    ##get the largest box for each image
    image_areas=defaultdict(list)
    
    for row in frame_file:
        if isinstance(eval(row[2]),float):
            continue
        bbox=eval(row[2])
        area=(bbox[0][1]-bbox[1][1])*(bbox[1][0]-bbox[0][0])
        image_areas[row[1]].append([frame_file.line_num,area])
    
    #get top 2 boxes 
    biggest=[]
    for key, value in image_areas.items():
        if len(value)==0:
            continue
        
        #get areas
        a=[x[1] for x in value]
        if len(a) > 1:
            #find indices
            top2=np.argpartition(a,-2)[-2:]
            for ind in top2:
                biggest.append(value[ind][0])
        else:
            biggest.append(value[0][0])

    frames.close()

    second_file=open(f)
    frame_file=csv.reader(second_file)

    #skip header
    next(frame_file,None)
    
    #just proccess those line numbers
    #start at first data row
    
    for row in frame_file:
        
        if frame_file.line_num in biggest:
    
            #read in image
            fname=os.path.split(f)[0] + "/" +row[1]+".jpg"
            img=cv2.imread(fname)
            if img is None:
                continue
            
            #score if background or foreground?
            
            #for image get the largest box
            
            #get bounding coordinates
            bbox=eval(row[2])
                        
            #expand box by multiplier m, limit to image edge
            m=(math.sqrt(2)-1)
            
            #min height
            p1=mult(bbox[1][1],-m)
            p1=check_bounds(img, 0, p1)
            
            #max height
            p2=mult(bbox[0][1],m)            
            p2=check_bounds(img, 0, p2)            
    
            #min width
            p3=mult(bbox[0][0],-m)            
            p3=check_bounds(img, 1, p3)            
            
            #max width
            p4=mult(bbox[1][0],m)                        
            p4=check_bounds(img, 1, p4)            
        
            #create a mask, in case its bigger than image            
            current_image=img[p1:p2,p3:p4]
    
            #4. Resize Image
            resized_image = cv2.resize(current_image, (299, 299))             
            #cv2.namedWindow("img")
            #cv2.imshow("img", resized_image)
            #k=cv2.waitKey(0)
            
            #Save image for scoring
            cv2.imwrite("/Users/Ben/Dropbox/GoogleCloud/TestCrops/"+str(crop_counter) + ".jpg",resized_image) 
            crop_counter+=1