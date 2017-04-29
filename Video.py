import cv2
from Geometry import *

class Video:
    def __init__(self,vid,args):
        
        #store args from MotionMeerkat
        self.args=args
        self.args.video=vid
        
        #set descriptors
        self.frame_count=0
        
        #Annotations dictionary
        self.annotations={}
        
        #read video
        self.cap=cv2.VideoCapture(self.args.video)
        
        #background subtraction
        self.background_instance=self.create_background() 


    def read_frame(self):
        self.cap.read()
        #ROI settings
        
    def analyze(self):
 
        while True:
            
            #read frame
            ret,self.original_image=self.cap.read()
            
            if not ret:
                break
            
            self.frame_count+=1
            
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
            
            #Write bounding box events
            self.annotations[self.frame_count] = bounding_boxes

    def show(self):
        
        cv2.namedWindow("Motion_Event")            
        show_count=0
        cap=cv2.VideoCapture(self.args.video)
        
        while True:
            show_count+=1

            #read frame
            ret,image=cap.read()
            if not ret:
                break
            if show_count in self.annotations:
                                
                #draw
                if True:
                    for bounding_box in self.annotations[show_count]:
                        cv2.rectangle(image, (bounding_box.x, bounding_box.y), (bounding_box.x+bounding_box.w, bounding_box.y+bounding_box.h), (0,0,255), 2)
                        
                cv2.imshow("Motion_Event", image)
                cv2.waitKey(0)
            else:
                continue
                
        cv2.destroyAllWindows()            
        
    #Lower level functions
    
    def create_background(self):
        
        self.fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=False,varThreshold=float(self.args.mogvariance))
        self.fgbg.setBackgroundRatio(0.95)
    
    #Frame Subtraction
    def background_apply(self):
        
        #Apply Subtraction
        self.image = self.fgbg.apply(self.original_image,learningRate=self.args.moglearning)
        
        #Erode to remove noise, dilate the areas to merge bounded objects
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))
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

        def __init__(self, rect):
            self.update_rect(rect)
            self.members = []    