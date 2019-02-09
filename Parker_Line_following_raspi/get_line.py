import cv2
from numpy import array
from numpy import int0
from numpy import argsort


def get_line(image,contours,box,side="center"):
    x_box,y_box,width_box,height_box = box
    if len(contours) == 0:
        cv2.rectangle(image,(x_box,y_box),(x_box+width_box,y_box+height_box),(0,255,0),2)
        return 0
    cnt = max(contours, key = cv2.contourArea)
    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.05 * peri, True)
    area = cv2.contourArea(cnt)
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
    return top_x_center
    
