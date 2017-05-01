import tensorflow as tf
import os
import glob
import numpy as np
import argparse

class tensorflow:    
    
    def __init__(self):
        print("Tensorflow object")
                    
    def predict(self,read_from,sess,image_array=None,imagedir=None):
        
        #frames to be analyzed
        tfimages=[]    
        
        find_photos=glob.glob(imagedir+"*.jpg")
        
        # Read in the image_data
        if read_from=="file":
            for x in find_photos:
                image_data = tf.gfile.FastGFile(x, 'rb').read()    
                tfimages.append(image_data)
        if read_from=="numpy":
            for x in image_array:
                bimage=cv2.imencode(".jpg", x)[1].tostring()
                tfimages.append(bimage)

        # Loads label file, strips off carriage return
        self.label_lines = [line.rstrip() for line in tf.gfile.GFile("dict.txt")]
        
        # Feed the image_data as input to the graph and get first prediction
        softmax_tensor = sess.graph.get_tensor_by_name('final_ops/softmax:0')
        predictions = sess.run(softmax_tensor, {'Placeholder:0': tfimages})
        
        for prediction in predictions:
            # Sort to show labels of first prediction in order of confidence
            top_k = prediction.argsort()[-len(prediction):][::-1]
        
            for node_id in top_k:
                human_string = self.label_lines[node_id]
                score = prediction[node_id]
                print('%s (score = %.5f)' % (human_string, score))
            return(human_string)

if __name__ == "__main__":
    sess=tf.Session()
    tf.saved_model.loader.load(sess,[tf.saved_model.tag_constants.SERVING], "model")    
    tensorflow_instance=tensorflow()
#   tensorflow_instance.predict(read_from="file",sess=sess,imagedir="C:/Users/Ben/Dropbox/GoogleCloud/Negatives/120")
