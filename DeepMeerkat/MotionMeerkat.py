import cv2
import numpy as np
import os 
import Video
import CommandArgs
import glob

class MotionMeerkat:
    def __init__(self):
        print("Welcome to MotionMeerkat")
    
    def process_args(self):
        self.args=CommandArgs.CommandArgs()
        
        #get all videos in queue
        self.queue= []
        
        #Create Pool of Videos
        if not os.path.isfile(self.args.input):
            for (root, dirs, files) in os.walk(self.args.input):
                for files in files:
                    fileupper=files.upper()
                    if fileupper.endswith((".TLV",".AVI",".MPG",".MP4",".MOD",".MTS",".WMV",".MOV",".MP2",".MPEG-4",".DTS",".VOB",".MJPEG",".M4V",".XBA")):
                        self.queue.append(os.path.join(root, files))                                                
                        print("Added " + str(files) + " to queue")
        else:
            self.queue=[self.args.input]
            
        if len(self.queue)==0:
            raise ValueError("No videos in the supplied folder. If videos exist, ensure that they can be read by standard video CODEC libraries.")
        
    def run(self):
        
        #hold on to original mog variance 
        mogvariance=self.args.mogvariance
        
        #init tensorflow
        #load tensorflow model
        if self.args.tensorflow:
            import tensorflow as tf
            print("Loading Tensorflow model")
            sess=tf.Session()
            tf.saved_model.loader.load(sess,[tf.saved_model.tag_constants.SERVING], self.args.path_to_model)                
            print("Complete")
            
            #get dictionary
            # Loads label file, strips off carriage return
            self.args.label_lines = [line.rstrip() for line in tf.gfile.GFile(os.path.abspath("../training/dict.txt"))]
        else:
            sess=None
            
        #run each video, use created tensorflow instance.
        for vid in self.queue:
            video_instance=Video.Video(vid,self.args,tensorflow_session=sess)
            video_instance.analyze()
            video_instance.write()
            
            #reset mog variance if adapting during run.
            self.args.mogvariance=mogvariance
        
if __name__ == "__main__":
    MM=MotionMeerkat()  
    MM.process_args() 
    MM.run()
    
    