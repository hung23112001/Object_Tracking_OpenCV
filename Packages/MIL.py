import cv2
import numpy as np
from Packages.Shift import Shifts

class MIL(Shifts):

    def __init__(self, video_path, ratio):
        super().__init__(video_path, ratio)
        self.tracker = cv2.TrackerMIL_create()
    
    def process(self):
        # _, frame = self.cap.read()
        roi = self.select_roi()
        self.ret = self.tracker.init(self.frame, roi)
    
    def __call__(self):
        ret, frame = self.cap.read()
        frame = self.resize_video(self.flip_webcam(frame, self.isWebcam))
        success, roi = self.tracker.update(frame)
        (x,y,w,h)=tuple(map(int,roi))

        # Draw rects as tracker moves
        if success:
            
            # Sucess on tracking
            pts1=(x,y)
            pts2=(x+w,y+h)
            cv2.rectangle(frame,pts1,pts2,(255,10,55),3)
            cv2.putText(frame,'Object',pts1,
                        cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        # else
        else:
        
            # Failure on tracking
            cv2.putText(frame,'Fail to track the object', (int(250 / self.ratio[0]), int(290 / self.ratio[1])),
                        cv2.FONT_HERSHEY_SIMPLEX,1,(25,125,255),2)
        
        return np.zeros_like(frame[:,:,0]), cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)