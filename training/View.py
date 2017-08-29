import os
import cv2
import csv

with open("/Users/Ben/Documents/DeepMeerkat/Training/Negatives.csv","r") as f:
    reader=csv.reader(f)
    for line in reader:     
        if line[1]=="Positive":
            img=cv2.imread(line[0])
            cv2.putText(img,str(line[2]),(20,20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)        
            cv2.imshow("image",img)
            cv2.waitKey(0)    

