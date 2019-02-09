# USAGE
# python video.py --video FlightDemo.mp4
area_min = 10
res = (640,480)
# import the necessary packages

from webcamvideostream import *
import cv2
from time import sleep
from numpy import array
from get_line import *
from time import perf_counter
from i2c_messages import *
import cv2.aruco as aruco

def crop(image,x,y,width,height):
    return image[y:y+height,x:x+width]

#handle exit()
from signal import signal
from signal import SIGINT
def sigint_handler(signum, frame):
    # When everything done, release the capture
    vs.stop()
    cv2.destroyAllWindows()

    print("\nThe processing rate is %s"%((processing_rate/(perf_counter() - time_start))))
    raise SystemExit(0)

signal(SIGINT, sigint_handler)#run commands on control c


#the boundaries for the HSV values
(lower,upper) = ([74,71,146],[91,186,243])
lower = array(lower)
upper = array(upper)
vs = WebcamVideoStream(src=0,res=res).start()
width,height,_ = vs.specs()

# Where the line is pulled from
box = (0,400,int(width),50)
x_box,y_box,width_box,height_box = box

message = i2c_messages(addr = 0x8, # bus address,
                       bus_number = 1,# indicates /dev/ic2-1,
                       suppress_errors = False #optional
                       )

time_start = perf_counter()#keep time
processing_rate = 0 #keep time

aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
parameters =  aruco.DetectorParameters_create()

# keep looping
while True:
    # grab the current frame and initialize the status text
    grabbed,frame = vs.read()
    frame = frame
    image = frame.copy()

    image_croped = crop(frame,x_box,y_box,width_box,height_box)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_croped = cv2.cvtColor(image_croped, cv2.COLOR_BGR2HSV) #Use for HSV

    mask = cv2.inRange(image_croped, lower, upper)
    

    edged = cv2.erode(mask, None, iterations=1)
    edged = cv2.dilate(mask, None, iterations=2)
    edged = cv2.erode(mask, None, iterations=1)
    edged = cv2.dilate(mask, None, iterations=1)
    
    (contours,_) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    _, ids, _ = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    id_found = 255
    if ids is not None:
        id_found = ids[0][0]
    
    pos = get_line(image,contours,box)
    pos = int(pos*255/width)
    print(pos,id_found)
    message.write_array([pos,id_found])
    
    processing_rate+=1

vs.stop()
cv2.destroyAllWindows()


processing_rate = (processing_rate/(perf_counter() - time_start))
print("\nThe processing rate is %s"%(processing_rate))
