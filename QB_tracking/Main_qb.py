id_to_look_for = 0
secondary_id_to_look_for = 2
src = 0
show_feed = True
max_queue_size = 5
res = (2100,2100)
trim_height = 500

import cv2
from numpy import mean
from time import perf_counter
import cv2.aruco as aruco
from webcamvideostream import *
from MovingAverage import *

#set_up_queue
moving_average_main_distance = MovingAverageClass(max_queue_size)
moving_average_main_center = MovingAverageClass(max_queue_size)
moving_average_side_center = MovingAverageClass(max_queue_size)

## 5.5 in 64.5 pixels at 7ft
## 4 inch 45.5 pixels at 7ft


##items to send
turn_left = False
turn_right = False

#2 bits for distance
#0 is none
#1 is short
#2 is medium
#3 is long
distance1 = False
distance2 = False

#3 bytes of tag_number, for tag number
target_found = 0#1 for target found
turn_percent = 0
target_distance = 0

cap = WebcamVideoStream(src= src,res = res)
cap.start()
target_width = 7.5
focal_length = 880 #(Pixels_size*distance)/actual_width
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


width,height,fps = cap.specs()

goal_position = width/2


trim_heightTOP = int((height-trim_height)/2)
trim_heightBOTTOM = int((height+trim_height)/2)
if (height <= trim_height):
    trim_heightTOP = int(0)
    trim_heightBOTTOM = int(height)

##Set up queue
last_center_found = None
queue_of_distance = []


first_time = True
last_robot_position = None
on_target = True
while(True):
    # Capture frame-by-frame
    grabbed, frame= cap.read()
    if not grabbed:
        print("Camera could not be connected :(")
        break
    #print(frame.shape) #480x640
    # Our operations on the frame come here
    frame_trim = frame[trim_heightTOP:trim_heightBOTTOM,:]
    gray = cv2.cvtColor(frame_trim, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
    parameters =  aruco.DetectorParameters_create()
 
    #print(parameters)
 
    '''    detectMarkers(...)
        detectMarkers(image, dictionary[, corners[, ids[, parameters[, rejectedI
        mgPoints]]]]) -> corners, ids, rejectedImgPoints
        '''
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
    #print(robot_distance)
    print(turn_percent, target_distance)

    """if (turn_percent <128):  
        print("turn left")
    elif (turn_percent>128):
        print("turn right")
    else:
        print("On target")"""
    #else: print("Not found")
    
    
    # Display the resulting frame
    if show_feed:
        gray = aruco.drawDetectedMarkers(gray, corners)
        if (cv2.getWindowProperty('frame', 0) < 0) and not first_time:   break
        if first_time:first_frame = False
        
        cv2.imshow('frame',gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    processing_number+=1

# When everything done, release the capture
cap.stop()
cv2.destroyAllWindows()

processing_rate = processing_number/(perf_counter() - time_start)
print("The processing rate is %s"%(processing_rate))
