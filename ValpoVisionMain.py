# USAGE
area_min = 10
res = (640,480)
# import the necessary packages

from webcamvideostream import *
import cv2
from time import sleep
from numpy import array
from numpy import int0
from numpy import argsort
from get_line import *

def crop(image,x,y,width,height):
    return image[y:y+height,x:x+width]

video_camera = True
video_file = "tests/video_red_blue.mp4"


#the boundaries for the HSV values
(lower,upper) = ([56,65,135],[89,151,183])
lower = array(lower)
upper = array(upper)
vs = WebcamVideoStream(src=0,res=res).start()

# Where the line is pulled from
box = (50,400,500,50)
x_box,y_box,width_box,height_box = box

# keep looping
while True:
    # grab the current frame and initialize the status text
    grabbed,frame = vs.read()
    frame = frame if video_camera else frame[1]
    image = frame.copy()

    image_croped = crop(frame,x_box,y_box,width_box,height_box)
    image_croped =cv2.cvtColor(image_croped, cv2.COLOR_BGR2HSV) #Use for HSV

    mask = cv2.inRange(image_croped, lower, upper)
    

    edged = cv2.erode(mask, None, iterations=1)
    edged = cv2.dilate(mask, None, iterations=2)
    edged = cv2.erode(mask, None, iterations=1)
    edged = cv2.dilate(mask, None, iterations=1)
    
    (_,contours,_) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)

    pos = get_line(image,contours,box)

    
    cv2.imshow("Frame",image)
    cv2.imshow("image_croped",image_croped)
    cv2.imshow("mask",mask)
    
    key = cv2.waitKey(1) & 0xFF
    
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
#camera.release()
cv2.destroyAllWindows()
vs.stop()
