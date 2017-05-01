import cv2
from datetime import datetime, timedelta
import os
import numpy as np
from Geometry import *
import csv
import time
import Crop

class Video:
    def __init__(self,vid,args):
                
        #start time
        self.start_time=time.time()
        
        #store args from MotionMeerkat
        self.args=args
        self.args.video=vid
        
        #set descriptors
        self.frame_count=0
        
        #Annotations dictionary
        self.annotations={}
        
        #create output directory
        normFP=os.path.normpath(self.args.input)
        (filepath, filename)=os.path.split(normFP)
        (shortname, extension) = os.path.splitext(filename)
        (_,IDFL) = os.path.split(filepath) 
        self.file_destination=os.path.join(self.args.output,shortname)        
        
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
 
        #load tensorflow model?
        if self.args.tensorflow:
            import tensorflow as tf
            import predict
            sess=tf.Session()
            tf.saved_model.loader.load(sess,[tf.saved_model.tag_constants.SERVING], self.args.path_to_model)                
            self.tensorflow_instance=predict.tensorflow()
        
        if self.args.show: cv2.namedWindow("Motion_Event")            
            
        while True:

            #read frame
            ret,self.original_image=self.read_frame()
            
            if not ret:
                #end time
                self.end_time=time.time()
                break
            
            self.frame_count+=1
            
            #skip the first frame
            if self.IS_FIRST_FRAME:
                print("Skipping first frame")
                self.IS_FIRST_FRAME=False
                continue
            
            #background subtraction
            self.background_apply()
            
            #contour analysis
            self.countours=self.find_contour()
            
            #Next frame if no contours
            if len(self.contours) == 0 :
                continue
              
            #bounding boxes
            bounding_boxes = self.cluster_bounding_boxes(self.contours)
            
            #Next frame if no bounding boxes
            if len(bounding_boxes) == 0 :
                continue

            #minimum box size
            width = np.size(self.original_image, 1)
            height = np.size(self.original_image, 0)
            area = width * height
            
            #remove if smaller than min size
            remaining_bounding_box=[]
            
            for bounding_box in bounding_boxes:
                if area * self.args.size < bounding_box.h * bounding_box.w:
                    remaining_bounding_box.append(bounding_box)
            
            if self.args.tensorflow:
                self.tensorflow_label=self.tensorflow_instance.predict(sess=sess,read_from="numpy",image_array=[self.original_image],numpy_name=self.frame_count)
            
                #next frame if negative label
                if self.tensorflow_label[self.frame_count]=="negative":
                        continue
                
            #Write bounding box time event, depends on proper frame rate
            sec = timedelta(seconds=int(self.frame_count/float(self.frame_rate)))             
            d = datetime(1,1,1) + sec                        
            for box in remaining_bounding_box:
                box.time = d

            self.annotations[self.frame_count] = remaining_bounding_box
            
            if self.args.show:
                for bounding_box in remaining_bounding_box:
                    if self.args.draw: cv2.rectangle(self.original_image, (bounding_box.x, bounding_box.y), (bounding_box.x+bounding_box.w, bounding_box.y+bounding_box.h), (0,0,255), 2)
                    cv2.imshow("Motion_Event", self.original_image)
                    cv2.waitKey(5)
        cv2.destroyAllWindows()            
    
    def read_frame(self):
        
        #read frame
        ret,image=self.cap.read()
        
        if not ret:
            return((ret,image))
        
        #set crop settings if first frame
        if self.IS_FIRST_FRAME:
            if self.args.crop:
                self.roi=Crop.Crop(image,"Crop")            
        if self.args.crop:
            cropped_image=image[self.roi[1]:self.roi[3], self.roi[0]:self.roi[2]]
            return((ret,cropped_image))
        else:
            return((ret,image))
    
    def create_background(self):
        
        self.fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=False,varThreshold=float(self.args.mogvariance))
        self.fgbg.setBackgroundRatio(0.95)
    
    #Frame Subtraction
    def background_apply(self):
        
        #Apply Subtraction
        self.image = self.fgbg.apply(self.original_image,learningRate=self.args.moglearning)
        
        #Erode to remove noise, dilate the areas to merge bounded objects
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15))
        self.image= cv2.morphologyEx(self.image, cv2.MORPH_OPEN, kernel)

    def find_contour(self):
            _,self.contours,hierarchy = cv2.findContours(self.image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
            self.contours = [contour for contour in self.contours if cv2.contourArea(contour) > 50]
        
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
                    if distance < 20:
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

        def __init__(self, rect):
            self.update_rect(rect)
            self.members = []    
    
    def write(self):      
        
        #write parameter logs
        
        self.output_args=self.file_destination + "/parameters.csv"
        with open(self.output_args, 'w',newline="") as f:  
            writer = csv.writer(f,)
            writer.writerows(self.args.__dict__.items())
            
            #Total time
            self.total_min=(self.start_time-self.end_time)/60
            writer.writerow(["Minutes",self.total_min])
            
            #Frames in file
            writer.writerow(["Total Frames",self.frame_count])
            
            #Frames returned to file
            writer.writerow(["Motion Events",len(self.annotations)])
            
            #Hit rate
            len(self.annotations)
            writer.writerow(["Return rate",float(len(self.annotations)/self.frame_count)])
            
            #Frames per second
            writer.writerow(["Frame processing rate",round(float(self.frame_count)/(self.total_min*60),2)])
        
        #Write frame annotations
        self.output_annotations=self.file_destination + "/annotations.csv"
        with open(self.output_annotations, 'w',newline="") as f:  
            writer = csv.writer(f,)
            writer.writerow(["Frame","x","y","h","w"])
            for x in self.annotations.keys():   
                bboxes=self.annotations[x]
                for bbox in bboxes: 
                    writer.writerow([x,bbox.x,bbox.y,bbox.h,bbox.w])
            
            
            