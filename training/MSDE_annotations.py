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
import random
        
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

def resize_box(img,bbox,m=math.sqrt(2)-1):

    #expand box by multiplier m, limit to image edge

    #min height
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
    cropped_image=img[p1:p2,p3:p4]

    #Resize Image
    resized_image = cv2.resize(cropped_image, (299, 299))  
    return(resized_image)

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

def mult(p,x):
    return(int(p+p*x))

def check_bounds(img,axis,p):
    if p > img.shape[axis]:
        p=img.shape[axis]
    if p < 0:
        p=0
    return(p)



#####Main Entry####

csvs = []
for root, dirnames, filenames in os.walk("/Users/Ben/Dropbox/HummingbirdProject/"):
    for filename in fnmatch.filter(filenames, '*Frames.csv'):
        csvs.append(os.path.join(root, filename))
        
#remove csv already done sort by date
new_csvs=[]
for csvfile in csvs:
    #convert time
    filedate=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(creation_date(csvfile)))
    if filedate > '2017-07-30 00:00:00':
        new_csvs.append(csvfile)

print("CSV files to process:  +  %d" % len(new_csvs))

label={}


for f in new_csvs:
    
    ####Set background images###
    
    #get images in folder
    jpgs=glob.glob(os.path.split(f)[0] + "/*.jpg")
    
    #sanity check
    if len(jpgs) < 5:
        continue
    
    #show image and get foreground or background
    #hit f for foreground, b for background
    labels={}
    for jpg in jpgs:
        img=cv2.imread(jpg)
        cv2.imshow("image",img)
        labels[jpg]=cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    ###Create background image####
    '''
    On my OSX keyboard 102 == 'f' and '98' == 'b'
    '''

    bg_sequence=[]
    for path,key in labels.items():
        if key ==98:
            image=cv2.imread(path)
            bg_sequence.append(image)
    
    Y = np.vstack((x.ravel() for x in bg_sequence))
    Z = np.median(Y,axis = 0)
    bg_model = np.uint8(Z.reshape(image.shape))    
    
    cv2.namedWindow("background",cv2.WINDOW_FULLSCREEN)
    cv2.imshow("background",bg_model)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

###Save bounding boxes###
            
    #Read in frames.csv
    frames=open(f)
    frame_file=csv.reader(frames)
    
    #skip header
    next(frame_file,None)
    
    #2) Assign Bounding Box and Labels
    for row in frame_file:
        
        print(frame_file.line_num)

        #read in image
        fname=os.path.split(f)[0] + "/" +row[1]+".jpg"
        img=cv2.imread(fname)
        if img is None:
            print(fname + " does not exist")
            continue
        
        ##assign bounding box
        bbox=eval(row[2])
        
        #Background subtraction
        clip,subtract=MSDE(img, bg_model, bbox)
        cv2.imshow("subtraction",subtract)
        cv2.waitKey(0)
        
        #create random file number
        h=random.randint(0,1000000)
        #if foreground, save
        if labels[fname] == "f":
            cv2.imwrite("/User/Ben/Dropbox/GoogleCloud/Positives/"+str(h)+"_original.jpg",clip)                
            cv2.imwrite("/User/Ben/Dropbox/GoogleCloud/Positives/"+str(h)+".jpg",subtract)
        else:
            cv2.imwrite("/User/Ben/Dropbox/GoogleCloud/Negatives/"+str(h)+"_original.jpg",clip)                                
            cv2.imwrite("/User/Ben/Dropbox/GoogleCloud/Negatives/"+str(h)+".jpg",subtract)
                
                
        
        
        
