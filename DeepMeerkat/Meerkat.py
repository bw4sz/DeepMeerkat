import os
import Video
import CommandArgs
from functools import partial

def start_tensorflow(args):
    import tensorflow as tf
    print("Loading Tensorflow model")
    sess=tf.Session()
    tf.saved_model.loader.load(sess,[tf.saved_model.tag_constants.SERVING], args.path_to_model)
    print("Complete")
    return(sess)

def process_args(argv=None):
    args=CommandArgs.CommandArgs(argv)
    return(args)
    
def create_queue(args,video=None):
    #get all videos in queue
    queue= []

    #if run as a function a video can be passed as a function
    if video:
        queue.append(video)

    #Create Pool of Videos
    if not os.path.isfile(args.input):
        for (root, dirs, files) in os.walk(args.input):
            for files in files:
                fileupper=files.upper()
                if fileupper.endswith((".TLV",".AVI",".MPG",".MP4",".MOD",".MTS",".WMV",".MOV",".MP2",".MPEG-4",".DTS",".VOB",".MJPEG","MPEG",".M4V",".XBA")):
                    queue.append(os.path.join(root, files))
                    print("Added " + str(files) + " to queue")
    else:
        queue=[args.input]

    if len(queue)==0:
        raise ValueError("No videos in the supplied folder. If videos exist, ensure that they can be read by standard video CODEC libraries.")
    return(queue)
            
class DeepMeerkat:
    def __init__(self,vid,args,sess=None):
        print("Welcome to DeepMeerkat")
        
        #Get command line arguments
        self.sess=sess
        self.args=args
        
        #Run Video
        self.run(vid=vid)
    
    def run(self,vid):
        
        print("Processing: " + str(vid))
        if not os.path.exists(vid):
            raise "Video does not exist at specified path"        
        
        if self.args.threaded:

            #load tensorflow session and model if in threaded mode to keep thread safe
            if self.args.tensorflow:
                import tensorflow as tf
                print("Loading Tensorflow model")
                self.sess=tf.Session()
                tf.saved_model.loader.load(self.sess,[tf.saved_model.tag_constants.SERVING], self.args.path_to_model)
                print("Complete")
    
            else:
                sess=None
            
        else:
            pass
        
        #Create Video Class
        self.video_instance=Video.Video(vid,args=self.args,tensorflow_session=self.sess)
        
        #close tensorflow session to keep thread safe
        if self.args.threaded:
            if self.args.tensorflow:
                self.sess.close()
             
if __name__ == "__main__":
    
    #Peek at the args to see if threaded, if not, we can make a new tensorflow session
    args=CommandArgs.CommandArgs(argv=None) 
    
    if not args.threaded:
        if args.tensorflow:   
            #add tensorflow flag for kivy
            tensorflow_status="Loading"                  
            sess=start_tensorflow(args)
    
    #Create queue of videos to run
    queue=create_queue(args=args)
    
    if args.threaded:
        from multiprocessing.dummy import Pool
        pool = Pool(3)         
        mapfunc = partial(DeepMeerkat, args=args)        
        results = pool.map(mapfunc, queue)
        pool.close()
        pool.join()
        
    else:
        for vid in queue:
            results=DeepMeerkat(vid=vid,args=args,sess=sess)