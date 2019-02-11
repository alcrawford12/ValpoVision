# USAGE
# python Main_qb_rasp.py [-verbose] [-o <outputFileName.avi>] [-fps <fps>]
#                        [-resX <resolution in the x> -resY <resolution in the y>]
#                        [-trimHeight <trim height>] [-targetWidth <target_width>]
#                        [-focalLength <focal_length>]
id_to_look_for = 0
secondary_id_to_look_for = 2
src = 0
show_feed = True
max_queue_size = 5
res = (2100,2100)
trim_height = 500
camera_fps = 30
target_width = 7.5
focal_length = 880 #(Pixels_size*distance)/actual_width
ARDUINO_ADDRESS = 0x8

#import Libraries
from time import perf_counter
from numpy import mean

#import opencv
import cv2.aruco as aruco
import cv2

#Local files
from webcamvideostream import *
from MovingAverage import *
from i2c_messages import *


#handle exit
from signal import signal
from signal import SIGINT
def sigint_handler(signum, frame):
    # When everything done, release the capture
    cap.stop()

    processing_rate = processing_number/(perf_counter() - time_start)
    print("\nThe processing rate is %s"%(processing_rate))
    raise SystemExit(0)

signal(SIGINT, sigint_handler)#run commands on ^C


#handle inputs from command lime
import argparse
parser = argparse.ArgumentParser(description='QB tracking')
parser.add_argument('-verbose', action="store_true", dest="verbose", default=False)
parser.add_argument('-o', action="store", dest="output_name")
parser.add_argument('-fps', action="store", dest="fps", type=int)
parser.add_argument('-resX', action="store", dest="resX", type=int)
parser.add_argument('-resY', action="store", dest="resY", type=int)
parser.add_argument('-trimHeight', action="store", dest="trim_height", type=int)
parser.add_argument('-targetWidth', action="store", dest="target_width", type=float)
parser.add_argument('-focalLength', action="store", dest="focal_length", type=int)
args = parser.parse_args()
if (args.fps is not None):camera_fps = args.fps
if ((args.resX is not None)and(args.resY is not None)):res = (args.resX,args.resY)
if (args.trim_height is not None):trim_height = args.trim_height
if (args.target_width is not None):target_width = args.target_width
if (args.focal_length is not None):focal_length = args.focal_length


#set_up_queue
moving_average_main_distance = MovingAverageClass(max_queue_size)
moving_average_main_center = MovingAverageClass(max_queue_size)
moving_average_side_center = MovingAverageClass(max_queue_size)

#3 bytes of tag_number, for tag number
target_found = 0#1 for target found
turn_percent = 0
target_distance = 0

cap = WebcamVideoStream(src= src,res = res,fps=camera_fps,output_name = args.output_name,output_height = trim_height )
cap.start()

def get_distance(pixel_height):
    return (target_width*focal_length)/pixel_height
def get_robot_positions(corners_of_target):
    y_cordinates = target[0][:,1].copy()#take all y_cordinates
    x_cordinates = target[0][:,0].copy()#take all x_cordinates
    center = [mean(x_cordinates),mean(y_cordinates)]
    y_cordinates.sort()
    top = (y_cordinates[2]+y_cordinates[3])/2
    bottom = (y_cordinates[0]+y_cordinates[1])/2
    height = top - bottom
    distance = get_distance(top - bottom)
    return center, height, distance
time_start = perf_counter()
processing_number = 0

#set the frame heights
width,height,fps = cap.specs()

goal_position = width/2


trim_heightTOP = int((height-trim_height)/2)
trim_heightBOTTOM = int((height+trim_height)/2)
if (height <= trim_height):
    trim_heightTOP = int(0)
    trim_heightBOTTOM = int(height)
    print("Trim_height is less than height. This might cause errors and it cannot save videos.")
    args.output_name = False

aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
parameters =  aruco.DetectorParameters_create()

message = i2c_messages(addr = ARDUINO_ADDRESS, # bus address,
                       bus_number = 1,# indicates /dev/ic2-1,
                       suppress_errors = False #optional
                       )

while(True):
    # Capture frame-by-frame
    grabbed, frame,time_= cap.read(time = True)
    if not grabbed:
        print("Camera could not be connected :(")
        break
    #print(frame.shape) #480x640
    # Our operations on the frame come here
    frame_trim = frame[trim_heightTOP:trim_heightBOTTOM,:]
    gray = cv2.cvtColor(frame_trim, cv2.COLOR_BGR2GRAY)
 
    #print(parameters)
 
        #lists of ids and the corners beloning to each id
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    #print(corners)
    
    #shift terms now even if term is not found
    moving_average_main_distance.shift_terms()
    moving_average_main_center.shift_terms()
    moving_average_side_center.shift_terms()
    for a in range(len(corners)):
        target = corners[a]
        if ids[a] == id_to_look_for:
            center, height, distance = get_robot_positions(target)
            #print(distance)
            moving_average_main_distance.add_number(distance)
            moving_average_main_center.add_number(center)
        if ids[a] == secondary_id_to_look_for:
            center, height, distance = get_robot_positions(target)
            moving_average_side_center.add_number(center)
            


    #see if moving average exists
    robot_center = moving_average_main_center.get_last_term()
    robot_distance = moving_average_main_distance.get_moving_average()
    if robot_center is None:
        robot_center = moving_average_side_center.get_last_term()
    if robot_center is not None:#robot has been found in the last five_turns
        target_found = 1
        robot_position = robot_center[0]#get x position
        turn_percent = int((robot_position - goal_position)/width*254 + 127)
    else:
        target_found = 0
        turn_percent = 0
        target_distance = 0
    if robot_distance is not None:
        target_distance = int(robot_distance)
    else:
        target_distance = int(0)

    #save to video
    if(args.output_name is not None):
        frame_trim = aruco.drawDetectedMarkers(frame_trim, corners)
        print(frame_trim.shape ,trim_height)
        cap.write(frame_trim,add_time = time_)

    #show print outs
    if(args.verbose):
        if (turn_percent==0):turn_str = "Not Found."
        elif(turn_percent<128):turn_str = "Turning right."
        else:turn_str = "Turning left."
        print("Position:" ,turn_percent, "Target Distance: ", target_distance,turn_str)
    
    message.write_array([turn_percent,target_distance])
    
    processing_number+=1


