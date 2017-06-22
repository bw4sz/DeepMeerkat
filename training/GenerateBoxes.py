import cv2
import numpy as np
import csv
import glob
import os
import math
from collections import defaultdict
import heapq

#Find csv
csvs=glob.glob("C:/Users/Ben/Dropbox/HummingbirdProject/**/frames.csv",recursive=True)

def mult(p,x):
    return(int(p+p*x))

def check_bounds(img,axis,p):
    if p > img.shape[axis]:
        p=img.shape[axis]
    if p < 0:
        p=0
    return(p)

crop_counter=0
for f in csvs:
    
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
        
        print(frame_file.line_num)
        if frame_file.line_num in biggest:
    
            #read in image
            fname=os.path.split(f)[0] + "/" +row[1]+".jpg"
            img=cv2.imread(fname)
            if img is None:
                print(fname + " does not exist")
                continue
            
            #for image get the largest box
            
            #get bounding coordinates
            bbox=eval(row[2])
                        
            #expand box by multiplier m, limit to image edge
            m=(math.sqrt(2)-1)/2
            
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
            cv2.imwrite("G:/Crops/"+str(crop_counter) + ".jpg",resized_image) 
            crop_counter+=1