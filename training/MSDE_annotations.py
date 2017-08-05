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

def MSDE(frame,bg_image,bounding_box):

    current=resize_box(frame,bounding_box)
    background=resize_box(bg_image,bounding_box)

    #convert to luminance
    current_gray=cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)                    
    background_grey=cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)                    

    #absolute diff
    current_diff=cv2.absdiff(current_gray,background_grey)
    
    #substract mean
    mean,_ = cv2.meanStdDev(current_diff)
    mean_diff=current_diff - mean
    
    #set all negative values to 0
    mean_diff[np.where(mean_diff<0)] = 0
    
    #strech to 255
    msde_image=cv2.normalize(mean_diff, mean_diff,alpha=0,beta=255,norm_type=cv2.NORM_MINMAX)
    
    return [current,msde_image]

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
for root, dirnames, filenames in os.walk("C:/Users/Ben/Dropbox/HummingbirdProject/"):
    for filename in fnmatch.filter(filenames, '*frames.csv'):
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
    if filedate > '2017-07-30 00:00:00':
        new_csvs.append(csvfile)

print(len(new_csvs))

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
        
        print(frame_file.line_num)
        if frame_file.line_num in biggest:
    
            #read in image
            fname=os.path.split(f)[0] + "/" +row[1]+".jpg"
            img=cv2.imread(fname)
            if img is None:
                print(fname + " does not exist")
                continue
            
            #score if background or foreground?
            
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