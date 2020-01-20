#path hack
import os
import sys

#DeepMeerkat
from DeepMeerkat import Video

import glob
#Load data
positives = glob.glob("/Users/Ben/Dropbox/Crops_BW/Positives/*.jpg")
negatives = glob.glob("/Users/Ben/Dropbox/Crops_BW/Negatives/*.jpg")

#Load model

#positives

true_positive = 0
false_positive = 0
for image in positives:
    
    #predict image
    #prediction = predict()
    
    if prediction =="positive":
        true_positive+=1
    else:
        false_positive+=1
    
#negatives:
true_negative = 0
false_negative = 0
for image in negatives:
    
    #predict image
    #prediction = predict()
    
    if prediction =="negative":
        true_negative+=1
    else:
        false_negative+=1
        

