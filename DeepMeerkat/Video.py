import cv2
import sys
if sys.version_info >= (3, 0):
    from urllib.parse import urlparse
else:
    from urlparse import urlparse
import math
from datetime import datetime, timedelta
import os
import numpy as np
from Geometry import *
import csv
import time
import Crop
import predict

#general functions
class FixedlenList(list):
    '''
subclass from list, providing all features list has
the list size is fixed. overflow items will be discarded

    '''
    def __init__(self,l=0):
        super(FixedlenList,self).__init__()
        self.__length__=l #fixed length

    def pop(self,index=-1):
        super(FixedlenList, self).pop(index)

    def remove(self,item):
        self.__delitem__(item)

    def __delitem__(self,item):
        super(FixedlenList, self).__delitem__(item)
        #self.__length__-=1

    def append(self,item):
        if len(self) >= self.__length__:
            super(FixedlenList, self).pop(0)
        super(FixedlenList, self).append(item)

    def extend(self,aList):
        super(FixedlenList, self).extend(aList)
        self.__delslice__(0,len(self)-self.__length__)

    def insert(self):
        pass

def mult(p,x):
    return(int(p+p*x))

def check_bounds(img,axis,p):
    if p > img.shape[axis]:
        p=img.shape[axis]
    if p < 0:
        p=0
    return(p)

def resize_box(img,bbox,m=math.sqrt(2)-1):

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

        #Frame Padding
        self.padding_frames=FixedlenList(l=self.args.buffer)

        #create output directory
        normFP=os.path.normpath(vid)
        (filepath, filename)=os.path.split(normFP)
        (shortname, extension) = os.path.splitext(filename)
        (_,IDFL) = os.path.split(filepath)

        self.file_destination=os.path.join(self.args.output,shortname)

        #create if directory does not exist
        if not os.path.exists(self.file_destination):
            os.makedirs(self.file_destination)

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

    def analyze(self):

        if self.args.show:
            print(self.args.show)
            cv2.namedWindow("Motion_Event")
            #cv2.namedWindow("Background")

        while True:

            #Reset padding frames, for debugging.
            WritePadding=False

            #read frame
            ret,self.read_image=self.read_frame()

            if not ret:
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

            #Gather clips and compute hog features for new background
            self.bg_image=self.fgbg.getBackgroundImage()

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

            if self.args.tensorflow:
                labels=[]
                for bounding_box in remaining_bounding_box:
                    clip=resize_box(self.original_image,bounding_box,m=0)
                    
                    #Tensorflow prediction
                    pred=predict.TensorflowPredict(sess=self.tensorflow_session,read_from="numpy",image_array=[clip],label_lines=["Positive","Negative"])                    
                    
                    #Assign output
                    bounding_box.label=pred
                    labels.append(pred)                    
                    
                for index,label in enumerate(labels):
                    cv2.putText(self.original_image,str(label),(30,30+20*index),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,0,255),2)
                                 
                #next frame if negative label that has score greater than 0.9
                for box in labels:
                    for label,score in box:
                        if label == 'Positive':
                            WritePadding=True
                        else:
                            WritePadding=False
                            
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
                self.end_sequence(Motion=True,WritePadding=WritePadding)

        cv2.destroyAllWindows()

    def read_frame(self):

        #read frame
        ret,self.original_image=self.cap.read()

        if not ret:
            return((ret,self.original_image))

        #set crop settings if first frame
        if self.IS_FIRST_FRAME:
            if self.args.crop:
                self.roi=Crop.Crop(self.original_image,"Crop")
            return((ret,self.original_image))
        if self.args.crop:
            image=self.original_image[self.roi[1]:self.roi[3], self.roi[0]:self.roi[2]]
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

    def end_sequence(self,Motion,WritePadding=False):        #When frame hits the end of processing

        #write history
        self.MotionHistory.append(Motion)

        if not Motion:
            #Capture Frame
            self.padding_frames.append(self.original_image)

        else:

            #write current frame
            fname=self.file_destination + "/"+str(self.frame_count)+".jpg"
            cv2.imwrite(fname,self.original_image)

            ##write padding frames, if they don't exist
            #if WritePadding:
                #for x in range(0,len(self.padding_frames)):
                    #filenm=self.file_destination + "/"+str(self.frame_count-(x+1))+".jpg"
                    #if not os.path.exists(filenm):
                        #cv2.imwrite(filenm,self.padding_frames[x])

            ##write post-motion frames
            #for x in range(self.args.buffer):
                ##read frame, check if its the last frame in video
                #ret,self.read_image=self.read_frame()
                #if not ret:
                    #self.end_time=time.time()
                    #break
                ##add to frame count and apply background
                #self.frame_count+=1
                #self.background_apply()

                ##write frame
                #fname=self.file_destination + "/"+str(self.frame_count)+".jpg"
                #if not os.path.exists(fname):
                    #cv2.imwrite(fname,self.original_image)

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
            self.label=None

        def __init__(self, rect):
            self.update_rect(rect)
            self.members = []

    def write(self):

        #write parameter logs
        self.output_args=self.file_destination + "/parameters.csv"
        if sys.version_info >= (3, 0):
            with open(self.output_args, 'w',newline="") as f:
                writer = csv.writer(f,)
                writer.writerows(self.args.__dict__.items())

                #Total time
                self.total_min=(self.end_time-self.start_time)/60.0
                writer.writerow(["Minutes",self.total_min])

                #Frames in file
                writer.writerow(["Total Frames",self.frame_count])

                #Frames returned to file
                writer.writerow(["Motion Events",len(self.annotations)])

                #Hit rate
                len(self.annotations)
                writer.writerow(["Return rate",float(len(self.annotations))/self.frame_count])

                #Frames per second
                writer.writerow(["Frame processing rate",round(float(self.frame_count)/(self.total_min*60),2)])
        else:
            with open(self.output_args, 'wb') as f:
                writer = csv.writer(f,)
                writer.writerows(self.args.__dict__.items())

                #Total time
                self.total_min=round((self.end_time-self.start_time)/60,3)
                writer.writerow(["Minutes",self.total_min])

                #Frames in file
                writer.writerow(["Total Frames",self.frame_count])

                #Frames returned to file
                writer.writerow(["Motion Events",len(self.annotations)])

                #Hit rate
                len(self.annotations)
                writer.writerow(["Return rate",float(len(self.annotations))/self.frame_count])

                #Frames per second
                writer.writerow(["Frame processing rate",round(float(self.frame_count)/(self.total_min*60),2)])
                
        #Write frame annotations
        self.output_annotations=self.file_destination + "/annotations.csv"
        if sys.version_info >= (3, 0):
            with open(self.output_annotations, 'w',newline="") as f:
                writer = csv.writer(f,)
                writer.writerow(["Frame","x","y","h","w","label"])
                for x in self.annotations.keys():
                    bboxes=self.annotations[x]
                    for bbox in bboxes:
                        writer.writerow([x,bbox.x,bbox.y,bbox.h,bbox.w,bbox.label])
        else:
            with open(self.output_annotations, 'wb') as f:
                writer = csv.writer(f,)
                writer.writerow(["Frame","x","y","h","w","label"])
                for x in self.annotations.keys():
                    bboxes=self.annotations[x]
                    for bbox in bboxes:
                        writer.writerow([x,bbox.x,bbox.y,bbox.h,bbox.w,bbox.label])

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
