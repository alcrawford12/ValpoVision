# USAGE
# python Main_qb_rasp.py [-fps <fps>] [-targetDistance <targetDistance>]
#                        [-resX <resolution in the x> -resY <resolution in the y>]
#                        [-actualSize <size in inches>] [-id <id number>]

from numpy import mean
import cv2
import cv2.aruco as aruco
from webcamvideostream import *

id_to_look_for = 2
target_distance_ft = 12
target_distance = 12*target_distance_ft#inches
actual_size = 7.5
res = (2100,2100)
camera_fps = 30
show_video = False

#handle exit
from signal import signal
from signal import SIGINT
def sigint_handler(signum, frame):
    # When everything done, release the capture
    cap.stop()
    cv2.destroyAllWindows()

    if (len(height_list) == 0):
        print("No targets Found")
        raise SystemExit(0)
    mean_height = mean(height_list)
    focal_length = (mean_height*target_distance)/actual_size
    print("Focal Length: ",focal_length)
    raise SystemExit(0)

signal(SIGINT, sigint_handler)#run commands on ^C

#handle inputs from command lime
import argparse
parser = argparse.ArgumentParser(description='QB tracking Calibration')
parser.add_argument('-fps', action="store", dest="fps", type=int)
parser.add_argument('-resX', action="store", dest="resX", type=int)
parser.add_argument('-resY', action="store", dest="resY", type=int)
parser.add_argument('-targetDistance', action="store", dest="targetDistance", type=int)
parser.add_argument('-id', action="store", dest="id", type=int)
parser.add_argument('-actualSize', action="store", dest="actualSize", type=float)
args = parser.parse_args()
if (args.fps is not None):camera_fps = args.fps
if ((args.resX is not None)and(args.resY is not None)):res = (args.resX,args.resY)
if (args.targetDistance is not None):target_distance = args.targetDistance
if (args.actualSize is not None):actual_size = args.actualSize
if (args.id is not None):id_to_look_for = args.id

cap = WebcamVideoStream(0,res = res,fps=camera_fps).start()

def get_robot_positions(corners_of_target):
    y_cordinates = target[0][:,1].copy()#take all y_cordinates
    x_cordinates = target[0][:,0].copy()#take all x_cordinates
    center = [mean(x_cordinates),mean(y_cordinates)]
    y_cordinates.sort()
    top = (y_cordinates[2]+y_cordinates[3])/2
    bottom = (y_cordinates[0]+y_cordinates[1])/2
    height = top - bottom
    distance = None
    return center, height, distance


height_list = []
aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
parameters =  aruco.DetectorParameters_create()
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    #print(frame.shape) #480x640
    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
 
    #print(parameters)

    #lists of ids and the corners beloning to each id
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    for a in range(len(corners)):
        target = corners[a]
        if ids[a] == id_to_look_for:
            center, height, distance = get_robot_positions(target)
            height_list.append(height)
            print("ID found")
 
    #It's working.
    # my problem was that the cellphone put black all around it. The alrogithm
    # depends very much upon finding rectangular black blobs
 
    gray = aruco.drawDetectedMarkers(gray, corners)

    if show_video:
        # Display the resulting frame
        frame = aruco.drawDetectedMarkers(frame, corners)
        cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
 
# When everything done, release the capture
cap.stop()
cv2.destroyAllWindows()

if (len(height_list) == 0):
    print("No targets Found")
    raise SystemExit(0)
mean_height = mean(height_list)
focal_length = (mean_height*target_distance)/actual_size
print("Focal Length: ",focal_length)
