from turtle import width
import cv2 
import numpy as np

class Shifts:
    
    def __init__(self, video_path, ratio):
        '''
        Parameter: 
        - video_path: là một tuple gồm (đường dẫn, bool)
        '''
        path, self.isWebcam = video_path   
        if self.isWebcam:
            self.cap = cv2.VideoCapture(path, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(path)
        self.mask=None
        self.ratio = ratio
            
    def resize_video(self, frame):
        '''
        Thay đổi kích thước ảnh về chiều rông: 800 và chiều cao: 600
        Trả về: một ndarray đã được resize kích thước theo thuật toán INTER_AREA
        '''
        width = int(880 / self.ratio[0])
        height = int(600 / self.ratio[1])
        try:
            return cv2.resize(frame, (width, height), cv2.INTER_AREA)
        except:
            return np.zeros((width, height))
    
    def select_roi(self):
        '''
        Lựa chọn đối tượng theo rõi
        Trả về: 4 giá trị là tọa độ x, y, chiều rộng, chiều cao
        '''
        _, self.frame = self.cap.read()
        self.frame = self.flip_webcam(self.frame, self.isWebcam)
        self.frame = self.resize_video(self.frame)
        self.roi = cv2.selectROI(self.frame, False)
        x, y, w, h = self.roi
        return x, y, w, h
    
    def take_roi(self):
        '''lấy đối tượng cần theo dõi'''
        x, y, w, h = self.select_roi()
        self.tracking = (x, y, w, h)
        self.roi = self.frame[y:y+h, x:x+w]

    def select_color_detection(self, lower, higher):
        '''
        Tìm mask cho đối tượng đã được chọn
        Tham số:
        - lower: kiểu dữ liệu là list lưu giá trị của [Hmin, Smin, Vmin]
        - higher: kiểu dữ liệu là list lưu giá trị của [Hmax, Smax, Vmax]
        
        Trả về:
        - self.mask_roi: Một mảng chứa các giá trị 0 và 255 là mask của roi
        - imgResult: Một mảng lưu giá trị kết hợp giữa ảnh gốc với mask
        '''
        imgHSV = cv2.cvtColor(self.roi, cv2.COLOR_BGR2HSV)
        lowerb = np.array(lower, dtype=np.int16)
        higherb = np.array(higher, dtype=np.int16)
        self.mask_roi = cv2.inRange(imgHSV, lowerb, higherb)
        imgResult = cv2.bitwise_and(self.roi, self.roi, mask=self.mask_roi)
        return self.mask_roi, imgResult
    
    def flip_webcam(self, frame, webcam=False):
        '''Nếu sử dụng webcam thì phương thức sẽ thực hiện để giống
        như một tấm gương'''
        if webcam:
            return cv2.flip(frame, 1)
        else:
            return frame

    def threshold_mask(self, mask):
        """Cắt ngưỡng cho mask"""
        values = np.unique(mask)
        _, new_mask = cv2.threshold(mask, values[-3], values[-1], cv2.THRESH_BINARY)
        return new_mask

    def image_process(self):
        '''Tính toán đồ thị của đối tượng được chọn'''
        self.roi_hsv = cv2.cvtColor(self.roi, cv2.COLOR_BGR2HSV)
        
        #Tính toán đồ thị chu roi_hsv
        self.roi_hist = cv2.calcHist(
            [self.roi_hsv], [0], self.mask_roi, [255], [0, 255])
        
        #Chuẩn hóa các pixel về 0, 255
        self.roi_hist = cv2.normalize(
            self.roi_hist, self.roi_hist, 0, 255, cv2.NORM_MINMAX)
        """
        Xác định tiêu chí kết thức cho thuật toán
        - TERM_CRITERIA_EPS: độ chính xác mong muốn hoặc sự thay đổi trong các tham số mà tại đó thuật toán lặp lại dừng lại
        - TERM_CRITERIA_COUNT: số lần lặp lại hoặc phần tử tối đa để tính toán
        """
        self.term_crit = (cv2.TERM_CRITERIA_EPS |
                          cv2.TERM_CRITERIA_COUNT, 10, 1)