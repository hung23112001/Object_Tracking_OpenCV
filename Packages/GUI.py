import tkinter
import cv2
import numpy as np
from tkinter import StringVar, Tk, ttk
from tkinter import filedialog
from PIL import Image, ImageTk
from Packages.MeanShift import MeanShift
from Packages.CamShift import CamShift
from Packages.LucasKanadeOpticalFlow import LucasKanade_OpticalFlow
from Packages.MIL import MIL


# Lớp Window: Tạo ra cửa sổ tên là Single Tracking
class Window:

    def __init__(self, master, size_master):
        '''
        Hàm tạo:
        - Tham số master: là một cửa sổ
        '''
        self.master = master
        self.size_master = size_master
        width, height = size_master.split('x')
        self.ratio = (1920 / int(width), 1080 / int(height))
        self.frame = ttk.Frame(self.master, padding=(3, 3, 12, 12))
        self.frame.grid()  # Hiển thị các thành phần theo dạng lưới
        self.isRun = True
        modesVar = tkinter.StringVar()
        self.video_path = tkinter.StringVar()
        self.video_path.set(0)
        self.init_HSVvalue()
        self.canvas()
        self.label()
        self.button()
        self.scale()
        self.modes = self.Combobox(modesVar)
        self.grid()
    
    def __call__(self):
        '''
        Thiết lập các thông số cơ bản cho cửa sổ:
        Tên cửa sổ, kích thước cửa sổ.
        '''
        self.master.title('Single Tracking')
        self.master.geometry(self.size_master)
        self.master.resizable(True, True)
        # self.master.minsize(950, 610)

    def canvas(self):
        width = int(880 / self.ratio[0] - 26)
        height = int(600 / self.ratio[1] - 26)
        self.canvas_window = tkinter.Canvas(
            self.master, width=width, height=height, background='black')
        self.canvas_window_mask = tkinter.Canvas(
            self.master, width=width, height=height, background='black')
        self.color_detection = tkinter.Canvas(
            self.master, width=int(200/self.ratio[0]), height=int(200/self.ratio[0]), background='black')
        self.result_detection = tkinter.Canvas(
            self.master, width=int(200/self.ratio[0]), height=int(200/self.ratio[0]), background='black')
        self.scale_cavas = tkinter.Canvas(self.master, width=550 if self.ratio[0] == 1 else 400, height=int(300))

    def button(self):
        '''
        Tạo các nút 'Select file', 'Clear', 'Quit'
        '''
        button_size = 22
        self.button_select_file = ttk.Button(
            text='Select video', width=button_size, command=self.open_file_select_video)
        self.quit_button = ttk.Button(
            text='Quit', width=button_size, command=self.master.destroy)
        self.clear_button = ttk.Button(
            self.master, text='Clear', width=button_size, command=self.clear_window)
        self.pause_button = ttk.Button(
            self.master, text='Pause', width=button_size, command=self.pause_video)
        self.continue_button = ttk.Button(
            self.master, text='Continue', width=button_size, command=self.continue_video)
        self.Run = ttk.Button(self.scale_cavas, text='Run',
                              width=button_size, command=self.setIsRun)

    def open_file_select_video(self):
        '''
        Phương thức có tác dụng mở file để chọn file có đuôi là '*.mp4' hoặc tất cả các đuôi
        giá trị filename trả về một đường dẫn
        Sau đó gán đường dẫn đó cho video_path 
        '''
        fileTypes = (
            ('Video file', '*.mp4'),
            ('All file', '*.*')
        )
        filename = filedialog.askopenfilename(filetypes=fileTypes)
        self.video_path.set(filename)

    def label(self):
        self.color_detection_label = ttk.Label(
            self.scale_cavas, text='Color Detection')
        # Hmin
        self.Hmin_label = ttk.Label(self.scale_cavas, text='Hmin')
        self.Hmin_value_label = ttk.Label(
            self.scale_cavas, textvariable=self.Hmin_value)
        # Hmax
        self.Hmax_label = ttk.Label(self.scale_cavas, text='Hmax')
        self.Hmax_value_label = ttk.Label(
            self.scale_cavas, textvariable=self.Hmax_value)
        # Smin
        self.Smin_label = ttk.Label(self.scale_cavas, text='Smin')
        self.Smin_value_label = ttk.Label(
            self.scale_cavas, textvariable=self.Smin_value)
        # Smax
        self.Smax_label = ttk.Label(self.scale_cavas, text='Smax')
        self.Smax_value_label = ttk.Label(
            self.scale_cavas, textvariable=self.Smax_value)
        # Vmin
        self.Vmin_label = ttk.Label(self.scale_cavas, text='Vmin')
        self.Vmin_value_label = ttk.Label(
            self.scale_cavas, textvariable=self.Vmin_value)
        # Vmax
        self.Vmax_label = ttk.Label(self.scale_cavas, text='Vmax')
        self.Vmax_value_label = ttk.Label(
            self.scale_cavas, textvariable=self.Vmax_value)

        # self.roi_mask_detection = ttk.Label(self.scale_cavas, text='Mask roi')
        # self.roi_result_detection = ttk.Label(self.scale_cavas, text='Result roi')

    def init_HSVvalue(self):
        """Khởi tạo biến lưu trữ giá trị HSV"""
        self.Hmin_value = StringVar()
        self.Hmax_value = StringVar()
        self.Smin_value = StringVar()
        self.Smax_value = StringVar()
        self.Vmin_value = StringVar()
        self.Vmax_value = StringVar()
        self.setStringVar()

    def setStringVar(self):
        """Thiết lập các giá trin mặc định giá trị HSV"""
        # Hmin
        self.Hmin_value.set('0')
        # Hmax
        self.Hmax_value.set('179')
        # Smin
        self.Smin_value.set('0')
        # Smax
        self.Smax_value.set('255')
        # Vmin
        self.Vmin_value.set('0')
        # Vmax
        self.Vmax_value.set('255')

    def grid(self):
        '''
        Thiết lập vị trí của các phần tử trên cửa sổ
        '''
        self.button_select_file.grid(row=0, column=11, columnspan=2)
        self.clear_button.grid(row=2, column=11)
        self.pause_button.grid(row=1, column=11)
        self.quit_button.grid(row=3, column=11)
        self.continue_button.grid(row=4, column=11)
        self.modes.grid(row=5, column=11)
        self.canvas_window.grid(row=0, column=1, rowspan=22, columnspan=10)
        self.canvas_window_mask.grid(
            row=0, column=13, rowspan=22, columnspan=10)
        self.scale_cavas.grid(row=23, column=1, columnspan=10, rowspan=9)
        self.color_detection_label.place(x=185, y=10)
        # #Hmin
        self.Hmin_label.place(x=10, y=50)
        self.Hmin.place(x=60, y=47)
        self.Hmin_value_label.place(x=420, y=50)
        # #Hmax
        self.Hmax_label.place(x=10, y=80)
        self.Hmax.place(x=60, y=77)
        self.Hmax_value_label.place(x=420, y=80)
        # #Smin
        self.Smin_label.place(x=10, y=110)
        self.Smin.place(x=60, y=107)
        self.Smin_value_label.place(x=420, y=110)
        # #Smax
        self.Smax_label.place(x=10, y=140)
        self.Smax.place(x=60, y=137)
        self.Smax_value_label.place(x=420, y=140)
        # #Vmin
        self.Vmin_label.place(x=10, y=170)
        self.Vmin.place(x=60, y=167)
        self.Vmin_value_label.place(x=420, y=170)
        # #Vmax
        self.Vmax_label.place(x=10, y=200)
        self.Vmax.place(x=60, y=197)
        self.Vmax_value_label.place(x=420, y=200)
        #Run
        self.Run.place(x=150, y=230)

        # Color Detection grid
        # self.roi_mask_detection.place(x=int(1103/self.ratio[0]), y=int(815/self.ratio[1]))
        self.color_detection.place(x=int(1028/self.ratio[0]), y=int(610/self.ratio[1]))
        # self.roi_result_detection.place(x=int(1313/self.ratio[0]), y=int(815/self.ratio[1]))
        self.result_detection.place(x=int(1238/self.ratio[0]), y=int(610/self.ratio[1]))

    def Combobox(self, modesVar):
        # Tạo một Combobox
        modes = ttk.Combobox(self.master, textvariable=modesVar)
        # Tạo một danh sách lựa chọn
        modes['values'] = ('MeanShift', 'CamShift',
                           'Lucas-Kanade Opitcal Flow',
                           'Multiple instance learning')
        # Dùng để gọi hàm selectMode khi lựa chọn một phần tử trong list
        modes.bind('<<ComboboxSelected>>', self.selectMode)
        # Chỉ cho phép đọc không cho chỉnh sửa
        modes.state(['readonly'])
        return modes

    def setValue(self, value=0, status=False):
        """
        Tham số:
        - value: nhận giá trị truyền vào từ thanh trượt scale
        - status: nhận trạng thái truyền vào là loại nào mặc định là False
        
        Trả về:
        - Nếu 'status' là False thì sẽ trả về giá trị lower và higher là một tuple(list)
        - Còn không sẽ gán các giá trị HSV bằng value
        """
        if status == 'hmin':
            self.Hmin_value.set(round(float(value)))
        elif status == 'hmax':
            self.Hmax_value.set(round(float(value)))
        elif status == 'vmin':
            self.Vmin_value.set(round(float(value)))
        elif status == 'vmax':
            self.Vmax_value.set(round(float(value)))
        elif status == 'smin':
            self.Smin_value.set(round(float(value)))
        elif status == 'smax':
            self.Smax_value.set(round(float(value)))
        if status == False:
            lower = [self.Hmin_value.get(), self.Smin_value.get(),
                     self.Vmin_value.get()]
            higher = [self.Hmax_value.get(), self.Smax_value.get(),
                      self.Vmax_value.get()]
            return lower, higher

    def scale(self):
        """Tạo thanh trượt"""
        self.Hmin = ttk.Scale(self.scale_cavas, length=350, from_=0, to=179,
                              variable=self.Hmin_value, command=lambda s: self.setValue(s, 'hmin'))
        
        self.Hmax = ttk.Scale(self.scale_cavas, length=350, from_=0, to=179,
                              variable=self.Hmax_value, command=lambda s: self.setValue(s, 'hmax'))
        
        self.Smin = ttk.Scale(self.scale_cavas, length=350, from_=0, to=255,
                              variable=self.Smin_value, command=lambda s: self.setValue(s, 'smin'))
        
        self.Smax = ttk.Scale(self.scale_cavas, length=350, from_=0, to=255,
                              variable=self.Smax_value, command=lambda s: self.setValue(s, 'smax'))
        
        self.Vmin = ttk.Scale(self.scale_cavas, length=350, from_=0, to=255,
                              variable=self.Vmin_value, command=lambda s: self.setValue(s, 'vmin'))
        
        self.Vmax = ttk.Scale(self.scale_cavas, length=350, from_=0, to=255,
                              variable=self.Vmax_value, command=lambda s: self.setValue(s, 'vmax'))

    def selectMode(self, event):
        mode = event.widget.get()
        path = ((0, True) if self.video_path.get() == '0' else (self.video_path.get(), False))
        self.status = True

        if mode == 'MeanShift':
            self.tracker_status = 'ms'
            self.cap = MeanShift(path, self.ratio)
            self.cap.count = 0
            self.cap.take_roi()
            self.updateRoi()
            self.delay = 1

        if mode == 'CamShift':
            self.tracker_status = 'cs'
            self.cap = CamShift(path, self.ratio)
            self.cap.take_roi()
            self.updateRoi()
            self.delay = 1
        
        if mode == 'Multiple instance learning':
            self.tracker_status = 'mil'
            self.cap = MIL(path, self.ratio)
            self.cap.process()
            self.delay = 1
            self.update_Lucas()
            
        if mode == 'Lucas-Kanade Opitcal Flow':
            self.tracker_status = 'lk'
            self.cap = LucasKanade_OpticalFlow(path, self.ratio)
            self.delay = 1
            self.update_Lucas()

    def clear_window(self):
        # 'Set lại các trạng thái mặc định '
        # self.modes.set('')
        # try:
        #     self.canvas_window.delete(self.myImg)
        #     self.canvas_window_mask.delete(self.myMask)
        #     self.result_detection.delete(self.myImg_roi)
        #     self.color_detection.delete(self.myMask_roitk)
        # except:
        #     pass
        # self.video_path.set(0)
        # self.isRun = True
        # self.setStringVar()
        self.master.destroy()
        self.master = Window(Tk(), self.size_master)

    def pause_video(self):
        '''Dừng video lại'''
        self.status = False
        
    def continue_video(self):
        '''Tiếp tục chạy video'''
        self.status = True
        self.update()
        
    def setIsRun(self):
        self.isRun = False
        self.update()

    def updateRoi(self):
        '''Cập nhật lại frame của roi khi thay đổi các giá trị HSV'''
        if self.isRun:
            lower, higher = self.setValue()
            self.mask_roi, frame = self.cap.select_color_detection(
                lower, higher)
            if self.mask_roi.shape[0] <= 200//self.ratio[0] and self.mask_roi.shape[1] <= 200//self.ratio[1]:
                size_cavas = int(200 / self.ratio[0])
                self.mask_roi = cv2.resize(self.mask_roi, (size_cavas, size_cavas))
                frame = cv2.resize(frame, (size_cavas, size_cavas))
                
            self.frame_roi = ImageTk.PhotoImage(
                image=Image.fromarray(frame))
            self.mask_roitk = ImageTk.PhotoImage(
                image=Image.fromarray(self.mask_roi))
            self.myImg_roi = self.result_detection.create_image(
                0, 0, image=self.frame_roi, anchor=tkinter.NW)
            self.myMask_roitk = self.color_detection.create_image(
                0, 0, image=self.mask_roitk, anchor=tkinter.NW)
            self.master.after(1, self.updateRoi)
        self.cap.image_process()

    def update_Lucas(self):
        if self.tracker_status == 'lk':
            self.canvas_window.bind('<Button-1>', self.cap.select_point)
        mask, frame = self.cap()
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
        self.mask = ImageTk.PhotoImage(image=Image.fromarray(mask))
        self.myImg = self.canvas_window.create_image(
            0, 0, image=self.photo, anchor=tkinter.NW)
        self.myMask = self.canvas_window_mask.create_image(
            0, 0, image=self.mask, anchor=tkinter.NW)
        self.master.after(self.delay, self.update)
                
    def update(self):
        '''
        Thay các khung hình để
        Cập nhật lại self.canvas
        '''            
        if not self.isRun:
            try:
                mask, frame = self.cap()
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.mask = ImageTk.PhotoImage(image=Image.fromarray(mask))
                self.myImg = self.canvas_window.create_image(
                    0, 0, image=self.photo, anchor=tkinter.NW)
                self.myMask = self.canvas_window_mask.create_image(
                    0, 0, image=self.mask, anchor=tkinter.NW)
                if self.status:
                    self.master.after(self.delay, self.update)
            except:
                pass