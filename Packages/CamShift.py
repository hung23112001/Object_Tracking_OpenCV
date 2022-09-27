from math import sqrt
import numpy as np
import cv2
from Packages.Shift import Shifts

class CamShift(Shifts):
    '''Lớp CamShift kế thừa lại các phương thức từ lớp Shifts'''
    
    old_x, old_y = 0, 0
    status = True
    
    def __init__(self, video_path, ratio):
        super().__init__(video_path, ratio)
    
    def __call__(self):
        ret, frame = self.cap.read()
        if ret == True:
            frame = self.resize_video(self.flip_webcam(frame, self.isWebcam))
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            #Ghi lại mức độ phù hợp của các pixel của một hình ảnh nhất định với sự phân bố của các pixel trong mô hình biểu đồ.
            dst = cv2.calcBackProject([hsv],[0],self.roi_hist,[0,255],1)
            dst = self.threshold_mask(dst)
            
            #Sử dụng thuật toán Camshift
            ret, self.tracking = cv2.CamShift(dst, self.tracking, self.term_crit)
            if ret[0] == (0, 0):
                if CamShift.old_x == 0 and CamShift.old_y == 0:
                    CamShift.status = False
            
            CamShift.old_x = ret[0][0]
            CamShift.old_y = ret[0][1]
            pts = cv2.boxPoints(ret)
            pts = np.int0(pts)
            
            if CamShift.status:
                #Vẽ một số đường cong đa giác.
                img2 = cv2.polylines(frame,[pts],True, (0, 255, 255),2)
                img = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
                cv2.putText(img,'Object',pts[0],
                        cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2)
            else:
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                cv2.putText(img, 'Fail to track the object', (int(250 / self.ratio[0]), int(290 / self.ratio[1])),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (225, 0, 25), 2)
            return dst, img
        else:
            return 'Error'