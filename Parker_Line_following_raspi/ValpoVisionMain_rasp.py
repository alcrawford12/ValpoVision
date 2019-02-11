# USAGE
# python ValpoVisionMain_rasp.py [-verbose] [-o <outputFileName.avi>] [-fps <fps>]
#                                [-resX <resolution in the x> -resY <resolution in the y>]
res = (640,480)
fps = 30
#the boundaries for the HSV values
(lower,upper) = ([74,71,146],[91,186,243])
ARDUINO_ADDRESS = 0x8

# import the necessary packages
from time import perf_counter
from numpy import array

#import opencv
import cv2
import cv2.aruco as aruco

#Local files
from get_line import *
from webcamvideostream import *
from i2c_messages import *


#handle exit()
from signal import signal
from signal import SIGINT
def sigint_handler(signum, frame):
    # When everything done, release the capture
    vs.stop()

    print("\nThe processing rate is %s"%((processing_rate/(perf_counter() - time_start))))
    raise SystemExit(0)

signal(SIGINT, sigint_handler)#run commands on ^C


#handle inputs
import argparse
parser = argparse.ArgumentParser(description='Line following tracking')
parser.add_argument('-verbose', action="store_true", dest="verbose", default=False)
parser.add_argument('-o', action="store", dest="output_name")
parser.add_argument('-fps', action="store", dest="fps", type=int)
parser.add_argument('-resX', action="store", dest="resX", type=int)
parser.add_argument('-resY', action="store", dest="resY", type=int)
args = parser.parse_args()
if (args.fps is not None):camera_fps = args.fps
if ((args.resX is not None)and(args.resY is not None)):res = (args.resX,args.resY)


def crop(image,x,y,width,height):
    return image[y:y+height,x:x+width]

#make sure boundaries are in the right range
lower = array(lower)
upper = array(upper)

vs = WebcamVideoStream(src=0,res=res,fps = fps,output_name = args.output_name).start()
width,height,_ = vs.specs()

# Where the line is pulled from
box = (0,400,int(width),50)
x_box,y_box,width_box,height_box = box

message = i2c_messages(addr = ARDUINO_ADDRESS, # bus address,
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
    grabbed,frame,time_ = vs.read(time = True)
    if not grabbed:
        print("Could not grab frame. :(")
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
    if(args.verbose):
        if (pos==0):turn_str = "Not Found."
        elif(pos<128):turn_str = "Turning left."
        else:turn_str = "Turning right."
        print("Position:" , pos,"Id found:",id_found,turn_str)

    if(args.output_name is not None):
        vs.write(image,add_time = time_)
    
    message.write_array([pos,id_found])
    
    processing_rate+=1
