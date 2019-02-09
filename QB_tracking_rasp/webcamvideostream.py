# import the necessary packages
from threading import Thread
import cv2
from time import sleep

class WebcamVideoStream:
    def __init__(self, src=0, name="WebcamVideoStream", res = None,fps =None):
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
    def specs(self):
        return self.stream.get(cv2.CAP_PROP_FRAME_WIDTH),self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT), self.stream.get(cv2.CAP_PROP_FPS)

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                self.stream.release()
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()
            self.on_frame +=1

    def read(self):
        while self.on_frame <= self.last_frame_read:
            #sleep(0.001)
            pass
        self.last_frame_read = self.on_frame
        # return the frame most recently read
        return self.grabbed,self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
