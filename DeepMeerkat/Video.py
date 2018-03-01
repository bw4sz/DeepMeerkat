import cv2
import sys
import math
from datetime import datetime, timedelta
import os
import numpy as np
from Geometry import *
import csv
import time
import Crop
import predict

def mult(p,x):
    return(int(p+p*x))

def check_bounds(img,axis,p):
    if p > img.shape[axis]:
        p=img.shape[axis]
    if p < 0:
        p=0
    return(p)
    
def resize_box(img,bbox,m=(math.sqrt(2)-1)/2):

    #expand box by multiplier m, limit to image edge

    #min height
    p1=mult(bbox.y,-m)
    p1=check_bounds(img, 0, p1)

    #max height
    p2=mult(bbox.y+bbox.h,m)
    p2=check_bounds(img, 0, p2)

    #min width
    p3=mult(bbox.x,-m)
    p3=check_bounds(img, 1, p3)

    #max width
    p4=mult(bbox.x+bbox.w,m)
    p4=check_bounds(img, 1, p4)

    #create a mask, in case its bigger than image
    cropped_image=img[p1:p2,p3:p4]

    #Resize Image
    resized_image = cv2.resize(cropped_image, (299, 299))
    return(resized_image)

class Video:
    def __init__(self,vid,args,tensorflow_session=None):

        #start time
        self.start_time=time.time()

        #store args from DeepMeerkat.py
        self.args=args
        self.args.video=vid
        self.tensorflow_session=tensorflow_session

        #set descriptors
        self.frame_count=0

        #Annotations dictionary
        self.annotations={}

        #MotionHistory
        self.MotionHistory=[]

        #create output directory
        normFP=os.path.normpath(vid)
        (filepath, filename)=os.path.split(normFP)
        (self.shortname, extension) = os.path.splitext(filename)
        (_,IDFL) = os.path.split(filepath)
        
        #if output is path add a container folder
        if os.path.isdir(self.args.input):
            self.file_destination=os.path.join(self.args.output,IDFL)
            self.file_destination=os.path.join(self.file_destination,self.shortname)            
        else:
            self.file_destination=os.path.join(self.args.output,self.shortname)

        #create if directory does not exist
        if not os.path.exists(self.file_destination):
            try: 
                os.makedirs(self.file_destination)
            except:
                pass

        #read video
        self.cap=cv2.VideoCapture(self.args.video)
        
        #set frame frate
        self.frame_rate=round(self.cap.get(5))

        #This seems to misinterpret just .tlv files
        if extension in ['.tlv','.TLV']:
            self.frame_rate=1
            print("File type is .tlv, setting frame rate to 1 fps")

        #background subtraction
        self.background_instance=self.create_background()

        #Detector almost always returns first frame
        self.IS_FIRST_FRAME = True
        
        #Analyze Video
        self.analyze()
        
        #Write Video Files
        self.write()

    def analyze(self):
        if self.args.show:
            print(self.args.show)
            cv2.namedWindow("Motion_Event")

        while True:

            #read frame
            ret,self.read_image=self.read_frame()

            if not ret:
                
                #Check if video was corrupted
                if self.frame_count==0:
                    raise ValueError("DeepMeerkat was unable to read the supplied file. Check if the file is corrupt and can be opened on your computer. You may need to download the proper video codecs for your machine.")
                #end time
                self.end_time=time.time()
                break

            self.frame_count+=1

            #skip the first frame after adding it to the background.
            if self.IS_FIRST_FRAME:
                print("Skipping first frame")
                self.IS_FIRST_FRAME=False
                self.width = np.size(self.read_image, 1)
                self.height = np.size(self.read_image, 0)
                self.image_area = self.width * self.height
                
                continue

            #adapt settings of mogvariance to keep from running away
            self.adapt()

            #background subtraction
            self.background_apply()

            #contour analysis
            self.countours=self.find_contour()

            #Next frame if no contours
            if len(self.contours) == 0 :
                self.end_sequence(Motion=False)
                continue

            #bounding boxes
            bounding_boxes = self.cluster_bounding_boxes(self.contours)

            #Next frame if no bounding boxes
            if len(bounding_boxes) == 0 :
                self.end_sequence(Motion=False)
                continue

            #remove if smaller than min size
            remaining_bounding_box=[]

            for bounding_box in bounding_boxes:
                if self.image_area * self.args.size < bounding_box.h * bounding_box.w:
                    remaining_bounding_box.append(bounding_box)

            #next frame is no remaining bounding boxes
            if len(remaining_bounding_box)==0:
                self.end_sequence(Motion=False)
                continue
            
            #if training, just spit out clips
            if self.args.training:
                clip_counter=0    
                self.annotations[self.frame_count] = remaining_bounding_box                    
                
                for box in remaining_bounding_box:
                    clip_to_write=resize_box(self.original_image, box)
                    fname=self.file_destination + "/"+str(self.shortname) +"_"+str(self.frame_count) + "_" + str(clip_counter)+".jpg"                            
                    cv2.imwrite(fname, clip_to_write)   
                    clip_counter+=1
                
                #don't write full frames
                continue                

            if self.args.tensorflow:
                labels=[]
                for bounding_box in remaining_bounding_box:
                    clip=resize_box(self.original_image,bounding_box,m=0)
                    
                    #Tensorflow prediction
                    pred=predict.TensorflowPredict(sess=self.tensorflow_session,read_from="numpy",image_array=[clip],label_lines=["Positive","Negative"])                    
                    
                    #Assign output
                    bounding_box.label=pred[0]
                    labels.append(pred)                    
                
                if self.args.write_text:
                    for index,label in enumerate(labels):
                        cv2.rectangle(self.original_image,(20,0+20*index),(330,40+25*index),(255,255,255),thickness=-1)
                        cv2.putText(self.original_image,str(label[0]),(30,30+20*index),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,0,255),2)
                                 
                #next frame if negative label that has score greater than user threshold
                for box in labels:
                    for label,score in box:
                        if label == 'Positive':
                            tensorflow_check=True
                        else:
                            if score > float(self.args.tensorflow_threshold):
                                tensorflow_check=False
                            else:
                                tensorflow_check=True
                                
                ##Tensorflow check
                if tensorflow_check:
                    pass
                else:
                    self.end_sequence(Motion=False)                
                    continue
            
            self.annotations[self.frame_count] = remaining_bounding_box

            if self.args.draw_box:
                for bounding_box in remaining_bounding_box:
                    cv2.rectangle(self.original_image, (bounding_box.x, bounding_box.y),
                                  (bounding_box.x+bounding_box.w, bounding_box.y+bounding_box.h), (0,0,255), 2)
            if self.args.show:
                cv2.imshow("Motion_Event", self.original_image)
                cv2.waitKey(0)

            #Motion Frame! passed all filters.
            else:
                self.end_sequence(Motion=True)

        cv2.destroyAllWindows()

    def read_frame(self):

        #read frame
        ret,self.original_image=self.cap.read()

        if not ret:
            return((ret,self.original_image))
        
        if self.args.resize:
            image=cv2.resize(self.original_image, (0,0), fx=0.75, fy=0.75) 
        else:
            image=self.original_image
            
        return((ret,image))

    def create_background(self):
        self.fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=False,varThreshold=float(self.args.mogvariance))
        self.fgbg.setBackgroundRatio(0.95)

    #Frame Subtraction
    def background_apply(self):

        #Apply Subtraction
        self.image = self.fgbg.apply(self.read_image,learningRate=self.args.moglearning)

        #Erode to remove noise, dilate the areas to merge bounded objects
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))
        self.image= cv2.morphologyEx(self.image, cv2.MORPH_OPEN, kernel)

    def find_contour(self):
            _,self.contours,hierarchy = cv2.findContours(self.image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
            self.contours = [contour for contour in self.contours if cv2.contourArea(contour) > 50]

    def end_sequence(self,Motion):        #When frame hits the end of processing

        #write history
        self.MotionHistory.append(Motion)

        if Motion:
            #write current frame
            fname=self.file_destination + "/"+str(self.frame_count)+".jpg"
            cv2.imwrite(fname,self.original_image)

    def cluster_bounding_boxes(self, contours):
        bounding_boxes = []
        for i in range(len(contours)):
            x1,y1,w1,h1 = cv2.boundingRect(contours[i])

            parent_bounding_box = self.get_parent_bounding_box(bounding_boxes, i)
            if parent_bounding_box is None:
                parent_bounding_box = self.BoundingBox(Rect(x1, y1, w1, h1))
                parent_bounding_box.members.append(i)
                bounding_boxes.append(parent_bounding_box)

            for j in range(i+1, len(contours)):
                if self.get_parent_bounding_box(bounding_boxes, j) is None:
                    x2,y2,w2,h2 = cv2.boundingRect(contours[j])
                    rect = Rect(x2, y2, w2, h2)
                    distance = parent_bounding_box.rect.distance_to_rect(rect)
                    if distance < 50:
                        parent_bounding_box.update_rect(self.extend_rectangle(parent_bounding_box.rect, rect))
                        parent_bounding_box.members.append(j)
        return bounding_boxes

    def get_parent_bounding_box(self, bounding_boxes, index):
        for bounding_box in bounding_boxes:
            if index in bounding_box.members:
                return bounding_box
        return None

    def extend_rectangle(self, rect1, rect2):
        x = min(rect1.l_top.x, rect2.l_top.x)
        y = min(rect1.l_top.y, rect2.l_top.y)
        w = max(rect1.r_top.x, rect2.r_top.x) - x
        h = max(rect1.r_bot.y, rect2.r_bot.y) - y
        return Rect(x, y, w, h)

    class BoundingBox:
        def update_rect(self, rect):
            self.rect = rect
            self.x = rect.l_top.x
            self.y = rect.l_top.y
            self.w = rect.width
            self.h = rect.height
            self.time=None
            self.label=(None,None)

        def __init__(self, rect):
            self.update_rect(rect)
            self.members = []

    def write(self):

        #write parameter logs
        self.output_args=self.file_destination + "/parameters.csv"
            
        #report statistics
        try:
            self.total_min=(self.end_time-self.start_time)/60.0
        except:
            self.total_min=1
        
        if os.name=="nt":
            with open(self.output_args, 'w',newline="") as f:
                writer = csv.writer(f,)
                writer.writerows(self.args.__dict__.items())
    
                #Total time
                writer.writerow(["Minutes",self.total_min])
    
                #Frames in file
                writer.writerow(["Total Frames",self.frame_count])
    
                #Frames returned to file
                writer.writerow(["Motion Events",len(self.annotations)])
    
                #Hit rate
                if not self.frame_count==0:
                    writer.writerow(["Return rate",float(len(self.annotations))/self.frame_count])
                
                #Frames per second
                writer.writerow(["Frame processing rate",round(float(self.frame_count)/(self.total_min*60),2)])

                f.flush()
             
            #Write frame annotations
            self.output_annotations=self.file_destination + "/annotations.csv"
            with open(self.output_annotations, 'w',newline="") as f:
                writer = csv.writer(f,)
                writer.writerow(["Frame","x","y","h","w","label","score"])
                for x in sorted(self.annotations.keys()):
                    bboxes=self.annotations[x]
                    for bbox in bboxes:
                        writer.writerow([x,bbox.x,bbox.y,bbox.h,bbox.w,bbox.label[0],bbox.label[1]])
                f.flush()
        else:

            with open(self.output_args, 'wb') as f:
                writer = csv.writer(f,)
                writer.writerows(self.args.__dict__.items())
    
                #Total time
                writer.writerow(["Minutes",self.total_min])
    
                #Frames in file
                writer.writerow(["Total Frames",self.frame_count])
    
                #Frames returned to file
                writer.writerow(["Motion Events",len(self.annotations)])
    
                #Hit rate
                writer.writerow(["Return rate",float(len(self.annotations))/self.frame_count])
    
                #Frames per second
                writer.writerow(["Frame processing rate",round(float(self.frame_count)/(self.total_min*60),2)])
                
                #Ensure write
                f.flush()
                
            #Write frame annotations
            self.output_annotations=self.file_destination + "/annotations.csv"
            with open(self.output_annotations, 'wb') as f:
                writer = csv.writer(f,)
                writer.writerow(["Frame","x","y","h","w","label","score"])
                for x in sorted(self.annotations.keys()):
                    bboxes=self.annotations[x]
                    for bbox in bboxes:
                        writer.writerow([x,bbox.x,bbox.y,bbox.h,bbox.w,bbox.label[0],bbox.label[1]])
                f.flush()
                
                
    def adapt(self):

            #If current frame is a multiple of the 1000 frames
            if self.frame_count % 1000 == 0:
                #get the percent of frames returned in the last 10 minutes
                if (sum([x < self.frame_count-1000 for x in self.annotations.keys()])/1000) > 0.05:

                    #increase tolerance rate
                    self.args.mogvariance+=5

                    #add a ceiling
                    if self.args.mogvariance > 60:
                        self.args.mogvariance = 60
                    print("Adapting to video conditions: increasing MOG variance tolerance to %d" % self.args.mogvariance)
