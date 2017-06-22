import glob
import cv2
import random


cv2.namedWindow("image")
images=glob.glob("G:/Crops/**/*.jpg",recursive=True)
position=0

pfilename=list(random.randint(0,1000000))

nfilename=list(random.randint(0,1000000))

while(True):
    #show images
    print("=="*40)
    print(position)
    try: 
        print(images[position])
    except:
        print("Images complete")
        break
    img=cv2.imread(images[position])
    cv2.imshow("image", img)    
    k=cv2.waitKey(0)
    if not k==255:
        print(k)
    #1key positive
    if k==49:
        fname="C:/Users/Ben/Dropbox/GoogleCloud/Positives/" + str(pfilename.pop())+".jpg"
        cv2.imwrite(filename=fname,img=img)
        position+=1
        
    #2key negative
    if k==50:
        fname="C:/Users/Ben/Dropbox/GoogleCloud/Negatives/" +str(nfilename.pop())+".jpg"
        cv2.imwrite(filename=fname,img=img)
        position+=1
        
    #9, go back
    if k==57:
        position+=-1
        
    #0 go forward    
    if k==48:
        position+=1
        
