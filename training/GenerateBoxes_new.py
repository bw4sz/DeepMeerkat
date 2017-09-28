import cv2
import csv
import glob
import os
import fnmatch
import os
import pandas

class BoundingBox:
    def __init__(self,x,y,h,w,label,score):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.label=label
        self.score=score
        
csvs=[]        
for root, dirnames, filenames in os.walk("/Users/ben/Dropbox/HummingbirdProject/Data/"):
    for filename in fnmatch.filter(filenames, 'annotations.csv'):
        csvs.append(os.path.join(root, filename))

#Get list of all ready saved images
training_data=glob.glob("/Users/Ben/Dropbox/GoogleCloud/Training/Positives/*.jpg") + glob.glob("/Users/Ben/Dropbox/GoogleCloud/Training/Negatives/*.jpg")
testing_data=glob.glob("/Users/Ben/Dropbox/GoogleCloud/Testing/Positives/*.jpg") + glob.glob("/Users/Ben/Dropbox/GoogleCloud/Testing/Negatives/*.jpg")
to_be_scored=glob.glob("/Users/Ben/Dropbox/GoogleCloud/TestCrops/Positives/*.jpg") + glob.glob("/Users/Ben/Dropbox/GoogleCloud/TestCrops/Negatives/*.jpg")

processed_images=[]

for image in training_data + testing_data + to_be_scored:
    processed_images.append(os.path.basename(image))

#counter for new images
new_images=0

#Loop through annotation files

for f in csvs:
    
    #Read in frames.csv
    df=pandas.read_csv(f)
    
    #add in counter column for same image, different bounding box
    counter=0
    
    for x in range(1,df.shape[0]):
        if df.loc[x,"Frame"]==df.loc[x-1,"Frame"]:
            counter+=1            
            df.loc[x,"Clip"]=counter
        else:
            df.loc[x,"Clip"]=counter        
            counter=0
    
    for index,row in df.iterrows():
        
        #read in image
        fname=os.path.split(f)[0] + "/" +str(row.Frame)+".jpg"
        img=cv2.imread(fname)
        
        if img is None:
            continue
        
        #set box parameters
        box=BoundingBox(x=row.x,y=row.y,h=row.h,w=row.w,label=row.label,score=row.score)
        cropped_image=img[box.y:box.y+box.h,box.x:box.x+box.w]
                                
        #Save image for scoring
        frame_number=os.path.splitext(fname)[0].split("/")[-1]
        
        #video
        video_name=f.split("/")[-2]
        
        ##only review Positive scores or low negative scores
        #if box.label=="Negative":
            #if float(box.score) > 0.95:
                #print(str(box.label) + " " +  str(box.score) + " skipped")
                #continue
                
        clipname=video_name+  "_" + frame_number + "_" + str(row.Clip) + ".jpg"
                
        #write the clip if it hasn't been written
        
        if clipname in processed_images:
            print("skipping")
            continue
        
        else:
    
            if box.label == "Positive":
                cv2.imwrite("/Users/Ben/Dropbox/GoogleCloud/TestCrops/Positives/"+ clipname, cropped_image) 
            else:
                cv2.imwrite("/Users/Ben/Dropbox/GoogleCloud/TestCrops/Negatives/"+ clipname, cropped_image) 
            new_images+=1

print("%s new images added" %(new_images))