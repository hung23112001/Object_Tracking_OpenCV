import cv2
import numpy as np
from Packages.Shift import Shifts


class LucasKanade_OpticalFlow(Shifts):
    point_selected = False
    point = ()
    old_points = np.array([[]])
    x, y = 0, 0

    def __init__(self, video_path, ratio):
        super().__init__(video_path, ratio)
        self.lucas_params = dict(winSize=(10, 10),
                                 maxLevel=2,
                                 criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        _, frame = self.cap.read()
        frame = self.resize_video(self.flip_webcam(frame, self.isWebcam))
        self.old_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def select_point(self, event):
        '''Lấy tọa độ khi click chuột trái'''
        LucasKanade_OpticalFlow.x, LucasKanade_OpticalFlow.y = event.x, event.y
        LucasKanade_OpticalFlow.point = (event.x, event.y)
        LucasKanade_OpticalFlow.point_selected = True
        LucasKanade_OpticalFlow.old_points = np.array(
            [[event.x, event.y]], dtype=np.float32)

    def __call__(self):
        try:
            _, frame = self.cap.read()
            frame = self.resize_video(self.flip_webcam(frame, self.isWebcam))
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if LucasKanade_OpticalFlow.point_selected: #Nếu point_selected là True 
                    
                #Vẽ vòng tròn có tâm là 'point' bán kính là '4', màu đỏ và độ dày của đường tròn là 2 
                cv2.circle(frame, LucasKanade_OpticalFlow.point, 4, (0, 0, 255), 2)
                #Tính toán luồng quang học cho một tập hợp đối tượng bằng phương pháp LucasKanade với phương pháp kim tự tháp
                new_points, status, error = cv2.calcOpticalFlowPyrLK(self.old_gray, gray_frame, LucasKanade_OpticalFlow.old_points, None, **self.lucas_params)
                
                #Cập nhật lại các giá trị mới
                self.old_gray = gray_frame.copy()
                LucasKanade_OpticalFlow.old_points = new_points
                
                x, y = new_points.ravel()
                x = 0 if x < 0 else x
                y = 0 if y < 0 else y
                cv2.circle(frame, (int(x), int(y)), 5, (0, 255, 0), -1)
                
            return gray_frame, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except:
            pass
    