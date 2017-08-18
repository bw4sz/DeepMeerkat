import argparse
import logging

def CommandArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--training", help="generate test clips",action="store_true")
    parser.add_argument("--input", help="path of single video",type=str,default='Hummingbird.avi')
    parser.add_argument("--output", help="output directory",default="/Users/Ben/DeepMeerkat")
    parser.add_argument("--draw_size", help="'Draw' or 'enter' object size",type=str,default='enter')
    parser.add_argument("--size", help="Minimum size of contour",default=0.02,type=float)
    parser.add_argument("--resize", help="Reduce frame size for processing, 1 is no resizing, 2 is reduce by half",default=1,type=float)
    parser.add_argument("--burnin", help="Delay time",default=0,type=int)
    parser.add_argument("--buffer", help="Frames to auto write on either side of tensorflow event",default=3,type=int)
    parser.add_argument("--scan", help="Scan one of every X frames for motion",default=0,type=int)
    parser.add_argument("--moglearning", help="Speed of MOG background detector, lowering values are more sensitive to movement",default=0.10,type=float)
    parser.add_argument("--mogvariance", help="Variance in MOG to select background",default=20,type=int)
    parser.add_argument("--crop", help="Set region of interest?",action='store_true')
    parser.add_argument("--draw_box", help="Draw boxes to highlight motion'?",action="store_true")
    parser.add_argument("--show", help="Show frames as you process",action='store_true')
    parser.add_argument("--tensorflow", help="Process model with a tensorflow image trained on google cloud machine learning engine",action='store_false')
    parser.add_argument("--path_to_model", help="Path to model/ directory",default="/Users/Ben/Dropbox/GoogleCloud/DeepMeerkat_20170801_172956/model/")
    args,_=parser.parse_known_args()
    
    print("DeepMeerkat args: " + str(args))
    logging.info("DeepMeerkat args: " + str(args))
    return(args)
