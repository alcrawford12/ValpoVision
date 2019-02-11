
area_min = 10
res = (640,480)

# import the necessary packages
from time import perf_counter
from numpy import array

#import opencv
import cv2
import cv2.aruco as aruco

#Local files
from get_line import *
from webcamvideostream import *

def crop(image,x,y,width,height):
    return image[y:y+height,x:x+width]

video_camera = True
video_file = "tests/video_red_blue.mp4"


#the boundaries for the HSV values
(lower,upper) = ([74,71,146],[91,186,243])
lower = array(lower)
upper = array(upper)
vs = WebcamVideoStream(src=0,res=res).start()
width,height,_ = vs.specs()

# Where the line is pulled from
box = (0,400,int(width),50)
x_box,y_box,width_box,height_box = box


aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
parameters =  aruco.DetectorParameters_create()

# keep looping
while True:
    # grab the current frame and initialize the status text
    grabbed,frame = vs.read()
    frame = frame if video_camera else frame[1]
    image = frame.copy()
    if not grabbed:
        print("Could not grab frame. :(")

    image_croped = crop(frame,x_box,y_box,width_box,height_box)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_croped =cv2.cvtColor(image_croped, cv2.COLOR_BGR2HSV) #Use for HSV

    mask = cv2.inRange(image_croped, lower, upper)
    

    edged = cv2.erode(mask, None, iterations=1)
    edged = cv2.dilate(mask, None, iterations=2)
    edged = cv2.erode(mask, None, iterations=1)
    edged = cv2.dilate(mask, None, iterations=1)
    
    (_,contours,_) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)

    _, ids, _ = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    id_found = 255
    if ids is not None:
        id_found = ids[0][0]
    pos = get_line(image,contours,box)
    pos = int(pos*255/width)

    if(args.verbose):
        if (pos==0):turn_str = "Not Found."
        elif(pos<128):turn_str = "Turning left."
        else:turn_str = "Turning right."
        print("Position:" , pos,"Id found:",id_found,turn_str)
    
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
