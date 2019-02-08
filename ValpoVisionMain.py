# USAGE
# python video.py --video FlightDemo.mp4
area_min = 10
# import the necessary packages
import argparse
from imutils.video import VideoStream
import cv2
import time
import numpy as np


def crop(image,x,y,width,height):
    return image[y:y+height,x:x+width]


video_camera = True
video_file = "tests/video_red_blue.mp4"



(lower,upper) = ([56,65,135],[89,151,183])
lower = np.array(lower)
upper = np.array(upper)
vs = VideoStream(src=0).start()
time.sleep(2.0)

box = (50,400,500,50)
x_box,y_box,width_box,height_box = box
def crop(image,x,y,width,height):
    return image[y:y+height,x:x+width]

# keep looping
while True:
    # grab the current frame and initialize the status text
    frame = vs.read()
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

    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.05 * peri, True)
        area = cv2.contourArea(cnt)
        if len(approx) >= 4 and len(approx) <= 6 and area>area_min:
            box = np.int0(cv2.boxPoints(cv2.minAreaRect(cnt) ))
            print(box)
            shifted_box = []
            for a in box:
                shifted_box.append([a[0]+x_box,a[1]+y_box])
            shifted_box = np.int0(shifted_box)
            sorted_box=shifted_box[np.argsort(shifted_box[:,1])]
            top = sorted_box[0:2]
            top_x = [n[0] for n in top]
            top_x_left  = top_x[0] if top_x[0] < top_x[1] else top_x[1] 
            top_x_right = top_x[0] if top_x[0] > top_x[1] else top_x[1]
            bottom = sorted_box[2:4]
            bottom_x = [n[0] for n in bottom]
            bottom_x_left  = bottom_x[0] if bottom_x[0] < bottom_x[1] else bottom_x[1] 
            bottom_x_right = bottom_x[0] if bottom_x[0] > bottom_x[1] else bottom_x[1]

            top_x_center = (top_x_left + top_x_right)/2
            bottom_x_center = (bottom_x_left + bottom_x_right)/2

            cv2.line(image, (int(top_x_right), y_box), (int(bottom_x_right), y_box+height_box), (255,0,0), 2)
            cv2.line(image, (int(top_x_center), y_box), (int(bottom_x_center), y_box+height_box), (0,255,0), 2)
            cv2.line(image, (int(top_x_left), y_box), (int(bottom_x_left), y_box+height_box), (255,0,0), 2)
    cv2.rectangle(image,(x_box,y_box),(x_box+width_box,y_box+height_box),(0,255,0),2)

    
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
