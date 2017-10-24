import glob
import cv2
import random
import os
2
cv2.namedWindow("image")
images=glob.glob("/Users/ben/Dropbox/GoogleCloud/TestCrops/Positives/*.jpg")
position=0

pfilename=[random.randint(0,1000000) for r in range(len(images))] 


nfilename=[random.randint(0,1000000) for r in range(len(images))] 

for path in images:
    
    #read and show image
    img=cv2.imread(path)
    cv2.imshow("image", img)    
    k=cv2.waitKey(0)
    
    #label image
    if not k==255:
        print(k)
        
    #1key positive
    if k==49:
        fname="/Users/ben/Dropbox/GoogleCloud/Training/Positives/" + str(pfilename.pop())+".jpg"
        cv2.imwrite(filename=fname,img=img)            
        
    #2key negative
    if k==50:
        fname="/Users/ben/Dropbox/GoogleCloud/Training/Negatives/" +str(nfilename.pop())+".jpg"
        cv2.imwrite(filename=fname,img=img)    
              
    #9, go back
    if k==57:
        pass
        
    #0 go forward    
    if k==48:
        pass
    
    cv2.destroyAllWindows()        
    os.remove(path)
      
