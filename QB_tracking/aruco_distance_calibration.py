import numpy as np
import cv2
import time
import cv2.aruco as aruco
from numpy import mean

id_to_look_for = 0
target_distance_ft = 12
target_distance = 12*target_distance_ft#inches
actual_size = 7.5

cap = cv2.VideoCapture(0)
x,y = (2100,2100)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,y)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,x)
print("The resolution is %s by %s.\nThe fps is %s"%(
           cap.get(cv2.CAP_PROP_FRAME_WIDTH),
           cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
           cap.get(cv2.CAP_PROP_FPS)))

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

time_start = time.perf_counter()
processing_number = 0
height_list = []
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    #print(frame.shape) #480x640
    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
    parameters =  aruco.DetectorParameters_create()
 
    #print(parameters)
 
    '''    detectMarkers(...)
        detectMarkers(image, dictionary[, corners[, ids[, parameters[, rejectedI
        mgPoints]]]]) -> corners, ids, rejectedImgPoints
        '''
        #lists of ids and the corners beloning to each id
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    for a in range(len(corners)):
        target = corners[a]
        if ids[a] == id_to_look_for:
            center, height, distance = get_robot_positions(target)
            height_list.append(height)
            print("found")
 
    #It's working.
    # my problem was that the cellphone put black all around it. The alrogithm
    # depends very much upon finding rectangular black blobs
 
    gray = aruco.drawDetectedMarkers(gray, corners)
 
    #print(rejectedImgPoints)
    # Display the resulting frame
    cv2.imshow('frame',gray)
    processing_number+=1
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
 
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

processing_rate = processing_number/(time.perf_counter() - time_start)
print("The processing rate is %s"%(processing_rate))

mean_height = mean(height_list)
focal_length = (mean_height*target_distance)/actual_size
print(focal_length)
