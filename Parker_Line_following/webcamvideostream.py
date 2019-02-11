# import the necessary packages
from threading import Thread
import cv2
from time import sleep
from time import time
from queue import Queue
from datetime import datetime

class WebcamVideoStream:
    def __init__(self, src=0, name="WebcamVideoStream",output_name = None, res = None,fps =None,output_width=None,output_height = None):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        if fps is not None:
            self.stream.set(cv2.CAP_PROP_FPS,fps)
        if res is not None:
            x,y = res
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH,y)
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT,x)
        print("The resolution is %s by %s.\nThe fps is %s"%(
               self.stream.get(cv2.CAP_PROP_FRAME_WIDTH),
               self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT),
               self.stream.get(cv2.CAP_PROP_FPS)))
        (self.grabbed, self.frame) = self.stream.read()

        # initialize the thread name
        self.name = name

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

        self.on_frame = 0
        self.last_frame_read = 0

        self.time = 0
        self.output_name = output_name
        if self.output_name is not None:
            frame_width  = int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if output_width is not None:
                frame_width = output_width
            if output_height is not None:
                frame_height = output_height
            self.queue_to_save = Queue(maxsize=20)
            self.out = cv2.VideoWriter(self.output_name,cv2.VideoWriter_fourcc('M','J','P','G'), 10, (frame_width,frame_height))
    def specs(self):
        return self.stream.get(cv2.CAP_PROP_FRAME_WIDTH),self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT), self.stream.get(cv2.CAP_PROP_FPS)

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        if self.output_name is not None:
            t_save = Thread(target=self.save_video_thread, name=self.name+"_save", args=())
            t_save.daemon = True
            t_save.start()
        return self
    def write(self,frame,add_time = None):
        if self.output_name is None:
            return 1
        else:
            if add_time is not None:
                frame2 = frame.copy()
                fromat_time = datetime.fromtimestamp(add_time).strftime('%Y-%m-%d %H:%M:%S.%f') 
                cv2.putText(frame2, fromat_time, (1,15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,255), 1)
                self.queue_to_save.put(frame2)
                return
                
            self.queue_to_save.put(frame)
    def save_video_thread(self):
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                self.out.release()
                return
            frame = self.queue_to_save.get()
            self.out.write(frame)
    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                self.stream.release()
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()
            self.time = time()
            self.on_frame +=1

    def read(self,time = False):
        while self.on_frame <= self.last_frame_read:
            sleep(0.001)
        self.last_frame_read = self.on_frame
        # return the frame most recently read
        if time: return self.grabbed,self.frame,self.time
        return self.grabbed,self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
