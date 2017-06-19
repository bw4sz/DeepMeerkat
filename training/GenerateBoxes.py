import cv2
import numpy as np
import csv
import glob

#Find csv
images=glob.glob("C:/Users/Ben/Dropbox/HummingbirdProject/Completed_Frames/**/*.csv",recursive=True)

def mult(p,x):
    return(int(p+(p*x)))

def check_bounds(img,axis,p):
    if p > img.shape[axis]:
        p=img.shape[axis]
    if p < 0:
        p=0
    return(p)

for f in csvs:
    
    #1. Read in frames.csv
    with open(f) as frames:
        frame_file=csv.reader(frames)
        for row in frame_file:
            
            #read in image
            try:
                img=cv2.imread(row[1])
            except:
                print(row[1] + "does not exist")
                break
            
            #create crops
            writer.writerow([x,bbox.x,bbox.y,bbox.h,bbox.w])
            
            bbox=row[2]
            
            ##The original motionmeerkat used the bottom left origin, numpy uses top left
            
            #expand box by multiplier m, limit to image edge
            m=2
            
            #bottom right height
            p1=bbox[1][1]
            p1=mult(p1,m)
            p1=check_bounds(img, 0, p1)
            
            #top left height
            p2=bbox[0][1]
            p2=check_bounds(img, 0, p2)            

            #bottom right width
            p3=bbox[0][0]
            p3=check_bounds(img, 1, p3)            
            
            #top left width
            p4=bbox[1][0]
            p4=check_bounds(img, 1, p4)            
            
            current_image=img.copy()
            cv2.rectangle(current_image,(p3,p1),(p4,p2),(0,0,255),thickness=3)
            
            #create a mask, in case its bigger than image            
            current_image=img[p1:p2,p3:p4]
            cv2.namedWindow("img")
            cv2.imshow("img", current_image)
            k=cv2.waitKey(0)



#3. Crop image

#4. Resize Image

#5  Save image for scoring