import cv2
import numpy as np
from Packages.Shift import Shifts


class MeanShift(Shifts):

    old_ret_prev = 0
    old_ret = 0

    def __init__(self, video_path, ratio):
        super().__init__(video_path, ratio)
        self.count = 0
        self.status = True

    def __call__(self):
        _, frame = self.cap.read()
        frame = self.resize_video(self.flip_webcam(frame, self.isWebcam))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Ghi lại mức độ phù hợp của các pixel của một hình ảnh nhất định với sự phân bố của các pixel trong mô hình biểu đồ.
        mask = cv2.calcBackProject([hsv], [0], self.roi_hist, [0, 255], 1)
        mask = self.threshold_mask(mask)

        # Sử dụng thuật toán Camshift
        suc, self.tracking = cv2.meanShift(mask, self.tracking, self.term_crit)
        if suc == 0 and MeanShift.old_ret == 0 and MeanShift.old_ret_prev == 0:
            self.count += 1
            if self.count == 5:
                self.status = False
        MeanShift.old_ret_prev = MeanShift.old_ret
        MeanShift.old_ret = suc

        if self.status:
            # Cập nhật lại tọa độ
            x, y, w, h = self.tracking
            img2 = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            img = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
            cv2.putText(img, 'Object', (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        else:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.putText(img, 'Fail to track the object', (int(250 / self.ratio[0]), int(290 / self.ratio[1])),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        return mask, img
