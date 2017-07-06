import argparse

def CommandArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="path of single video",type=str,default='C:/Program Files (x86)/MotionMeerkat/PlotwatcherTest.tlv')
    parser.add_argument("--output", help="output directory",default="C:/MotionMeerkat")
    parser.add_argument("--threshold", help="Threshold of movement",default=30,type=int)
    parser.add_argument("--draw", help="'Draw' or 'enter' object size",type=str,default='enter')
    parser.add_argument("--size", help="Minimum size of contour",default=0.001,type=float)
    parser.add_argument("--burnin", help="Delay time",default=0,type=int)
    parser.add_argument("--scan", help="Scan one of every X frames for motion",default=0,type=int)
    parser.add_argument("--moglearning", help="Speed of MOG background detector, lowering values are more sensitive to movement",default=0.09,type=float)                                
    parser.add_argument("--mogvariance", help="Variance in MOG to select background",default=25,type=int)                                
    parser.add_argument("--crop", help="Set region of interest?",action='store_true')
    parser.add_argument("--todraw", help="Draw boxes to highlight motion'?",action="store_true")
    parser.add_argument("--show", help="Show frames as you process",default='frames',action='store_true')
    parser.add_argument("--tensorflow", help="Process model with a tensorflow image trained on google cloud machine learning engine",action='store_false')	
    parser.add_argument("--path_to_model", help="Path to model/ directory",default="C:/Users/Ben/Dropbox/GoogleCloud/DeepMeerkat_20170623_155904/model/")								    
    parser.add_argument("--review_type", help="Output images as 'frames','video','both', 'none' ?",default='frames',type=str)
    args=parser.parse_args()
    return(args)
    