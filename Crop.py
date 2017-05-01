def Crop(img,title):
    def onmouse(event,x,y,flags,param):
        global ix,iy,roi,drawing        
        
        # Draw Rectangle
        if event == cv2.EVENT_RBUTTONDOWN:
            drawing = True
            ix,iy = x,y

        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing == True:
                cv2.rectangle(img,(ix,iy),(x,y),BLUE,-1)
                rect = (ix,iy,abs(ix-x),abs(iy-y))

        elif event == cv2.EVENT_RBUTTONUP:
            drawing = False
            cv2.rectangle(img,(ix,iy),(x,y),BLUE,-1)
            rect = (ix,iy,x,y)
            roi.extend(rect)

    cv2.namedWindow(title,cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(title,onmouse)

    print ("Right click and hold to draw a single rectangle ROI, beginning at the top left corner of the desired area. A blue box should appear. Hit esc to exit screen. Window can be resized by selecting borders.")
    while(1):
            cv2.namedWindow(title,cv2.WINDOW_NORMAL)                 
            cv2.imshow(title,img)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                    break
    
    cv2.destroyAllWindows()
    
    return(roi)    
