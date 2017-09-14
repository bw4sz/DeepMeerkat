import cv2
import numpy as np
import os
import Video
import CommandArgs
import glob

class DeepMeerkat:
    def __init__(self):
        print("Welcome to DeepMeerkat")
    
    def process_args(self,argv=None):
        self.args=CommandArgs.CommandArgs(argv) 
        
        #add tensorflow flag for kivy
        self.tensorflow_status="Loading"        
    
    def create_queue(self,video=None):
        #get all videos in queue
        self.queue= []

        #if run as a function a video can be passed as a function
        if video:
            self.queue.append(video)

        #Create Pool of Videos
        if not os.path.isfile(self.args.input):
            for (root, dirs, files) in os.walk(self.args.input):
                for files in files:
                    fileupper=files.upper()
                    if fileupper.endswith((".TLV",".AVI",".MPG",".MP4",".MOD",".MTS",".WMV",".MOV",".MP2",".MPEG-4",".DTS",".VOB",".MJPEG","MPEG",".M4V",".XBA")):
                        self.queue.append(os.path.join(root, files))
                        print("Added " + str(files) + " to queue")
        else:
            self.queue=[self.args.input]

        if len(self.queue)==0:
            raise ValueError("No videos in the supplied folder. If videos exist, ensure that they can be read by standard video CODEC libraries.")
        
    def run(self,vid):

        #hold on to original mog variance
        mogvariance=self.args.mogvariance

        #load tensorflow model
        if self.args.tensorflow:
            import tensorflow as tf
            print("Loading Tensorflow model")
            sess=tf.Session()
            tf.saved_model.loader.load(sess,[tf.saved_model.tag_constants.SERVING], self.args.path_to_model)
            print("Complete")

        else:
            sess=None

        #run each video, use created tensorflow instance.
        print("Processing: " + str(vid))
        if not os.path.exists(vid):
            raise "Video does not exist at specified path"
        
        self.video_instance=Video.Video(vid,self.args,tensorflow_session=sess)
        self.video_instance.analyze()
        self.video_instance.write()

        #reset mog variance if adapting during run.
        self.args.mogvariance=mogvariance
        
        #close tensorflow session
        sess.close()

if __name__ == "__main__":
    DM=DeepMeerkat()
    DM.process_args()
    DM.create_queue()
    if DM.args.threaded:
        from multiprocessing import Pool
        from multiprocessing.dummy import Pool as ThreadPool 
        pool = ThreadPool(2)         
        results = pool.map(DM.run,DM.queue)
        pool.close()
        pool.join()

    else:
        for vid in DM.queue:
            DM.run(vid=vid)