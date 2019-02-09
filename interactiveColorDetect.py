import cv2
import cv2 as cv
import numpy as np
 
kernel = np.ones((5,5),np.uint8)
 
# Take input from webcam
cap = cv2.VideoCapture(0)
 
# Reduce the size of video to 320x240 so rpi can process faster
cap.set(3,860)
cap.set(4,860)
 
def nothing(x):
    pass
# Creating a windows for later use
cv2.namedWindow('HueComp')
cv2.namedWindow('SatComp')
cv2.namedWindow('ValComp')
cv2.namedWindow('closing')
cv2.namedWindow('tracking')
 
 
# Creating track bar for min and max for hue, saturation and value
# You can adjust the defaults as you like
cv2.createTrackbar('hmin', 'HueComp',106,179,nothing)
cv2.createTrackbar('hmax', 'HueComp',116,179,nothing)
 
cv2.createTrackbar('smin', 'SatComp',73,255,nothing)
cv2.createTrackbar('smax', 'SatComp',125,255,nothing)
 
cv2.createTrackbar('vmin', 'ValComp',186,255,nothing)
cv2.createTrackbar('vmax', 'ValComp',255,255,nothing)
 
# My experimental values
# hmn = 12
# hmx = 37
# smn = 145
# smx = 255
# vmn = 186
# vmx = 255
 
 
while(1):
 
    buzz = 0
    _, frame = cap.read()
 
    #converting to HSV
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    hue,sat,val = cv2.split(hsv)
 
    # get info from track bar and appy to result
    hmn = cv2.getTrackbarPos('hmin','HueComp')
    hmx = cv2.getTrackbarPos('hmax','HueComp')
   
 
    smn = cv2.getTrackbarPos('smin','SatComp')
    smx = cv2.getTrackbarPos('smax','SatComp')
 
 
    vmn = cv2.getTrackbarPos('vmin','ValComp')
    vmx = cv2.getTrackbarPos('vmax','ValComp')
 
    # Apply thresholding
    hthresh = cv2.inRange(np.array(hue),np.array(hmn),np.array(hmx))
    sthresh = cv2.inRange(np.array(sat),np.array(smn),np.array(smx))
    vthresh = cv2.inRange(np.array(val),np.array(vmn),np.array(vmx))
 
    # AND h s and v
    tracking = cv2.bitwise_and(hthresh,cv2.bitwise_and(sthresh,vthresh))
 
    # Some morpholigical filtering
    dilation = cv2.dilate(tracking,kernel,iterations = 1)
    closing = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE, kernel)
    closing = cv2.GaussianBlur(closing,(5,5),0)
 
   
                
 
    #you can use the 'buzz' variable as a trigger to switch some GPIO lines on Rpi :)
    # print buzz                    
    # if buzz:
        # put your GPIO line here
 
   
    #Show the result in frames
    cv2.imshow('HueComp',hthresh)
    cv2.imshow('SatComp',sthresh)
    cv2.imshow('ValComp',vthresh)
    cv2.imshow('closing',closing)
    cv2.imshow('tracking',frame)
 
    k = cv2.waitKey(5) & 0xFF
    if k == ord('q'):
        break
print("Hue min  = ", hmn,"Hue max  = ",hmx,"\nSat min  = ",smn,"Sat max  = ",smx,"\nValue min =",vmn,"Value max =",vmx)

cap.release()
 
cv2.destroyAllWindows()
