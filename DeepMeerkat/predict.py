if sys.version_info >= (3, 0):
    import tensorflow as tf
import os
import glob
import numpy as np
import argparse
import cv2

class tensorflow:    
    
    def __init__(self):
        print("Tensorflow object")
                    
    def predict(self,read_from,sess,image_array=None,imagedir=None,numpy_name=None,wait_time=10):
        
        #frames to be analyzed
        tfimages=[]     
        #names for those frames
        self.image_name=[]
        
        # Read in the image_data
        if read_from=="file":
            if os.path.isdir(imagedir):
                find_photos=glob.glob(imagedir+"*.jpg")            
                for x in find_photos:
                    image_data = tf.gfile.FastGFile(x, 'rb').read()    
                    tfimages.append(image_data)
                    self.image_name.append(x)
            else:
                image_data = tf.gfile.FastGFile(imagedir, 'rb').read()                    
                tfimages.append(image_data)
                self.image_name.append(imagedir)
                
        if read_from=="numpy":
            for x in image_array:
                bimage=cv2.imencode(".jpg", x)[1].tostring()
                tfimages.append(bimage)
                
                #set imagedir for dict recall
                self.image_name.append(numpy_name)

        # Loads label file, strips off carriage return
        self.label_lines = [line.rstrip() for line in tf.gfile.GFile("training/dict.txt")]
        
        # Feed the image_data as input to the graph and get first prediction
        softmax_tensor = sess.graph.get_tensor_by_name('final_ops/softmax:0')
        predictions = sess.run(softmax_tensor, {'Placeholder:0': tfimages})
        
        #output results
        self.results_frame={}
        
        for x in range(0,len(predictions)):
            # Sort to show labels of first prediction in order of confidence
            top_k = predictions[x].argsort()[-len(predictions[x]):][::-1]    
            
            for node_id in top_k:
                human_string = self.label_lines[node_id]
                score = predictions[x][node_id]
                print('%s (score = %.4f)' % (human_string, score))
            self.results_frame[self.image_name[x]]=self.label_lines[top_k[0]]
        
        for x in self.results_frame.items():
            print(x)
            
        return(self.results_frame)
    def show(self,wait_time):
        
        font = cv2.FONT_HERSHEY_SIMPLEX        
        for x in self.image_name:
            image=cv2.imread(x)
            annotation=self.results_frame[x]
            cv2.putText(image,annotation,(10,20), font, 0.75,(255,255,255),1,cv2.LINE_AA)            
            cv2.imshow("Annotation", image)
            cv2.waitKey(wait_time)
        
if __name__ == "__main__":
    sess=tf.Session()
    tf.saved_model.loader.load(sess,[tf.saved_model.tag_constants.SERVING], "C:/Users/Ben/Dropbox/GoogleCloud/hummingbird_model/")    
    tensorflow_instance=tensorflow()
    #photos_run=glob.glob("C:/Users/Ben/Dropbox/Thesis/Maquipucuna_SantaLucia/FlowerPhotos/*.jpg")
    photos_run=glob.glob("G:/Crops_06212017/*.jpg")
    for x in photos_run:
        pred=tensorflow_instance.predict(read_from="file",sess=sess,imagedir=x)
        tensorflow_instance.show(wait_time=0)
