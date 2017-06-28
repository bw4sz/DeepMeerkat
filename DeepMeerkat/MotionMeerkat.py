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
            self.args.batch=True
            for (root, dirs, files) in os.walk(self.args.input):
                for files in files:
                    fileupper=files.upper()
                    if fileupper.endswith((".TLV",".AVI",".MPG",".MP4",".MOD",".MTS",".WMV",".MOV",".MP2",".MPEG-4",".DTS",".VOB",".MJPEG",".M4V",".XBA")):
                        self.queue.append(os.path.join(root, files))                                                
                        print("Added " + str(files) + " to queue")
        else:
            self.queue=[self.args.input]
            self.args.batch=False
            
        if len(self.queue)==0:
            raise ValueError("No videos in the supplied folder. If videos exist, ensure that they can be read by standard video CODEC libraries.")
        
    def run(self):
        for vid in self.queue:
            video_instance=Video.Video(vid,self.args)
            video_instance.analyze()
            video_instance.write()
        
if __name__ == "__main__":
    MM=MotionMeerkat()  
    MM.process_args() 
    MM.run()
    
    