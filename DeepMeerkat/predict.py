import sys
import tensorflow as tf
import os
import glob
import numpy as np
import argparse
import cv2
from collections import defaultdict

def TensorflowPredict(read_from,sess,image_array=None,imagedir=None,numpy_name="image",wait_time=10,label_lines=None):
    
    #frames to be analyzed
    tfimages=[]     
    
    #names for those frames
    image_name=[]
    
    # Read in the image_data
    if read_from=="file":
        if os.path.isdir(imagedir):
            find_photos=glob.glob(imagedir+"*.jpg")            
            for x in find_photos:
                image_data = tf.gfile.FastGFile(x, 'rb').read()    
                tfimages.append(image_data)
                image_name.append(x)
        else:
            image_data = tf.gfile.FastGFile(imagedir, 'rb').read()                    
            tfimages.append(image_data)
            image_name.append(imagedir)
            
    if read_from=="numpy":
        for x in image_array:
            bimage=cv2.imencode(".jpg", x)[1].tostring()
            tfimages.append(bimage)
            
            #set imagedir for dict recall
            image_name.append(numpy_name)
    
    # Feed the image_data as input to the graph and get first prediction
    softmax_tensor = sess.graph.get_tensor_by_name('final_ops/softmax:0')
    predictions = sess.run(softmax_tensor, {'Placeholder:0': tfimages})
    
    #output results
    results_frame=defaultdict(list)
    
    for x in range(0,len(predictions)):
        # Sort to show labels of first prediction in order of confidence
        top_k = predictions[x].argsort()[-len(predictions[x]):][::-1]    
        
        for node_id in top_k:
            human_string = label_lines[node_id]
            score = predictions[x][node_id]
            print('%s (score = %.3f)' % (human_string, score))
        results_frame[image_name[x]].append(label_lines[top_k[0]])
            
    return(results_frame)
            
if __name__ == "__main__":
    sess=tf.Session()
    print("Loading tensorflow model. May take several minutes.")
    tf.saved_model.loader.load(sess,[tf.saved_model.tag_constants.SERVING], "C:/Users/Ben/Dropbox/GoogleCloud/DeepMeerkat_20170801_172956/model/")    
    print("Model loaded")
    photos_run=glob.glob("C:/Users/Ben/Dropbox/Thesis/Maquipucuna_SantaLucia/FlowerPhotos/*.jpg")
    #photos_run=glob.glob("G:/Crops/*.jpg")
    for x in photos_run:
        image=cv2.imread(x)
        pred=TensorflowPredict(read_from="numpy",sess=sess,image_array=[image],label_lines=["Positive","Negative"])
        font = cv2.FONT_HERSHEY_COMPLEX         
        cv2.putText(image,str(pred["image"]),(10,20), font, 1,(255,255,255),1)            
        cv2.imshow("Annotation", image)
        cv2.waitKey(0)
