import cv2
import numpy as np
from Packages.Shift import Shifts


class Dense_OpticalFlow(Shifts):

    def __init__(self, video_path):
        super().__init__(video_path)
        _, frame = self.cap.read()
        frame = self.resize_video(self.flip_webcam(frame, self.isWebcam))
        self.prvs = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.hsv = np.zeros_like(frame)
        self.hsv[..., 1] = 255

    def __call__(self):
        _, frame = self.cap.read()
        frame = self.resize_video(self.flip_webcam(frame, self.isWebcam))
        next = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(self.prvs, next, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        self.hsv[..., 0] = ang*180/np.pi/2
        self.hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        bgr = cv2.cvtColor(self.hsv, cv2.COLOR_HSV2BGR)
        return next, bgr