import sys
import tensorflow as tf
import os
import glob
import numpy as np
import argparse
import cv2
from collections import defaultdict
import csv
import itertools

def TensorflowPredict(read_from,sess,image_array=None,imagedir=None,wait_time=10,label_lines=None):
    
    #frames to be analyzed
    tfimages=[]     
    
    # Read in the image_data
    if read_from=="file":
        if os.path.isdir(imagedir):
            find_photos=glob.glob(imagedir+"*.jpg")            
            for x in find_photos:
                image_data = tf.gfile.FastGFile(x, 'rb').read()    
                tfimages.append(image_data)
        else:
            image_data = tf.gfile.FastGFile(imagedir, 'rb').read()                    
            tfimages.append(image_data)
             
    if read_from=="numpy":
        for x in image_array:
            bimage=cv2.imencode(".jpg", x)[1].tostring()
            tfimages.append(bimage)
            
    # Feed the image_data as input to the graph and get first prediction
    softmax_tensor = sess.graph.get_tensor_by_name('final_ops/softmax:0')
    predictions = sess.run(softmax_tensor, {'Placeholder:0': tfimages})
    
    #output results
    results_frame=[ ]
    
    for x in range(0,len(predictions)):
        # Sort to show labels of first prediction in order of confidence
        top_k = predictions[x].argsort()[-len(predictions[x]):][::-1]    
        
        for node_id in top_k:
            human_string = label_lines[node_id]
            score = predictions[x][node_id]
            #print('%s (score = %.3f)' % (human_string, score))
        #return best label and score
        results_frame.append([label_lines[top_k[0]],predictions[x][top_k[0]]])
            
    return(results_frame)

#Positives
def check_positives(path,output):
    photos_run=glob.glob(path)
    counter=0
    positives=[]
    for x in photos_run:
        image=cv2.imread(x)
        pred=TensorflowPredict(read_from="numpy",sess=sess,image_array=[image],label_lines=["Positive","Negative"])
        label,score=pred[0]
        if label == "Negative":
            font = cv2.FONT_HERSHEY_COMPLEX         
            cv2.putText(image,str(pred),(10,20), font, 0.5,(255,255,255),1)            
            cv2.imshow("Annotation", image)
            cv2.waitKey(1)            
            counter+=1                
        positives.append([x,label,score])
        
    print("False Negative Rate: " + str(float(counter)/len(photos_run)))    
    with open(output,"w") as f:
        writer=csv.writer(f)
        for x in positives:
            writer.writerow(x)
       
#Negatives
def check_negatives(path,output):
    photos_run=glob.glob(path)
    counter=0
    negatives=[]
    for x in photos_run:
        image=cv2.imread(x)
        pred=TensorflowPredict(read_from="numpy",sess=sess,image_array=[image],label_lines=["Positive","Negative"])
        label,score=pred[0]
        negatives.append([x,label,score])        
        if label == "Positive":
            font = cv2.FONT_HERSHEY_COMPLEX         
            cv2.putText(image,str(pred[0]),(10,20), font, 0.5,(255,255,255),1)            
            cv2.imshow("Annotation", image)
            cv2.waitKey(1)            
            counter+=1                     
            
    print("False Positive Rate: " + str(float(counter)/len(photos_run)))
    with open(output,"w") as f:
        writer=csv.writer(f)
        for x in negatives:
            writer.writerow(x)    

def interactive(path):
    photos_run=glob.glob(path)
    for x in photos_run:
        image=cv2.imread(x)
        pred=TensorflowPredict(read_from="numpy",sess=sess,image_array=[image],label_lines=["Positive","Negative"])
        cv2.putText(image,str(pred),(10,20),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,0,255),2)
        cv2.imshow("Annotation", image)
        cv2.waitKey(0)

if __name__ == "__main__":
    sess=tf.Session()
    print("Loading tensorflow model. May take several minutes.")
    tf.saved_model.loader.load(sess,[tf.saved_model.tag_constants.SERVING], "/Users/ben/Dropbox/GoogleCloud/DeepMeerkat_20180109_090611/model/")    
    print("Model loaded")
    
    #Interactive
    #interactive("/Users/ben/Dropbox/GoogleCloud/TestCrops/*.jpg")
    
    print("Testing")
    #Testing
    check_negatives(path="/Users/Ben/Dropbox/GoogleCloud/Testing/Negatives/*.jpg", output="/Users/Ben/Dropbox/GoogleCloud/Testing/Testing_Negatives.csv")
    check_positives(path="/Users/Ben/Dropbox/GoogleCloud/Testing/Positives/*.jpg", output="/Users/Ben/Dropbox/GoogleCloud/Testing/Testing_Positives.csv")
    
    print("Training")
    #Training
    #check_negatives(path="/Users/Ben/Dropbox/GoogleCloud/Training/Negatives/*.jpg", output="/Users/Ben/Dropbox/GoogleCloud/Training/Training_Negatives.csv")
    #check_positives(path="/Users/Ben/Dropbox/GoogleCloud/Training/Positives/*.jpg", output="/Users/Ben/Dropbox/GoogleCloud/Training/Training_Positives.csv")    