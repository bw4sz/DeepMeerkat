#Harvest Photos
import os
import fnmatch
from shutil import copyfile
import glob

#get processed photos
processed=glob.glob("/Users/Ben/Dropbox/GoogleCloud/Detection/images/training/*.jpg")
processed = [os.path.basename(x) for x in processed]

photos=[]

sites=glob.glob("/Users/ben/Dropbox/HummingbirdProject/Completed_Frames/*/foundframes/")

for site in sites:
    for root, dirnames, filenames in os.walk(site):
        for filename in fnmatch.filter(filenames, '*.jpg'):
            photos.append(os.path.join(root, filename))
        
for photo in photos:
    
    #get name
    path = os.path.normpath(photo)
    path=path.split(os.sep)[-3:]
    path="_".join(path)
    dest="/Users/Ben/Dropbox/GoogleCloud/Detection/images/evaluation/" + path
    if not path in processed:    
        print(dest)        
        copyfile(photo,dest)
    else:
        print(dest + " exists")
