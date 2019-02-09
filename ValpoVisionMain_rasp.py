# USAGE
# python video.py --video FlightDemo.mp4
area_min = 10
res = (640,480)
# import the necessary packages

from webcamvideostream import *
import cv2
from time import sleep
from numpy import array
from numpy import int0
from numpy import argsort
from time import perf_counter

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
(lower,upper) = ([56,65,135],[89,151,183])
lower = array(lower)
upper = array(upper)
vs = WebcamVideoStream(src=0,res=res).start()

# Where the line is pulled from
box = (50,400,500,50)
x_box,y_box,width_box,height_box = box

time_start = perf_counter()#keep time
processing_rate = 0 #keep time
# keep looping
while True:
    # grab the current frame and initialize the status text
    grabbed,frame = vs.read()
    frame = frame
    image = frame.copy()

    image_croped = crop(frame,x_box,y_box,width_box,height_box)
    image_croped = cv2.cvtColor(image_croped, cv2.COLOR_BGR2HSV) #Use for HSV

    mask = cv2.inRange(image_croped, lower, upper)
    

    edged = cv2.erode(mask, None, iterations=1)
    edged = cv2.dilate(mask, None, iterations=2)
    edged = cv2.erode(mask, None, iterations=1)
    edged = cv2.dilate(mask, None, iterations=1)
    
    (contours,_) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    top_x_center = 0
    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.05 * peri, True)
        area = cv2.contourArea(cnt)
        if len(approx) >= 4 and len(approx) <= 6 and area>area_min:
            box = int0(cv2.boxPoints(cv2.minAreaRect(cnt) ))
            shifted_box = []
            for a in box:
                shifted_box.append([a[0]+x_box,a[1]+y_box])
            shifted_box = int0(shifted_box)
            sorted_box=shifted_box[argsort(shifted_box[:,1])]
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
    
    print(top_x_center)
    processing_rate+=1

vs.stop()
cv2.destroyAllWindows()


processing_rate = (processing_rate/(perf_counter() - time_start))
print("\nThe processing rate is %s"%(processing_rate))
