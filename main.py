import cv2
import time
import snow
from album import *
from ScreenShot import *
import threading
import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic


form_class = uic.loadUiType("main.ui")[0]

class MainUI(QMainWindow, form_class) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.camera = MySnowCam(0)
        
        self.btn_faceswap.clicked.connect(self.Select_Face_swap)
        self.btn_mask.clicked.connect(self.Select_Mask)
        self.btn_rabbit.clicked.connect(self.Select_Rabbit)
        self.btn_nomal.clicked.connect(self.Select_Noaml)
        
        self.btn_save.clicked.connect(self.screenShot)
        self.btn_album.clicked.connect(self.Click_Album)
    
        
        th = threading.Thread(target=self.update)
        th.start()
        
    def screenShot(self):
        # Get a frame from the video source
        ret, frame = self.camera.get_frame()
 
        if ret:
            title_name = "Snow" + time.strftime("%Y-%m-%d-%H-%M-%S")
            h,w,b = frame.shape
            qimg = QtGui.QImage(frame.data,w,h,w*b, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qimg)
            
            ScreenShot(self, pixmap, title_name)
            
    
    def update(self):
        while True:
            ret, frame = self.camera.get_frame()
            if ret:
                 h,w,b = frame.shape
                 qimg = QtGui.QImage(frame.data,w,h,w*b, QtGui.QImage.Format_RGB888)
                 pixmap = QtGui.QPixmap.fromImage(qimg)
                 self.lb_camera.setPixmap(pixmap)
                 #카메라에서 사진을 찍어서 캠버스에 업데이트
                 self.lb_camera.resize(pixmap.width(), pixmap.height())
                
                 self.lb_camera.show()
        
        
    def Select_Face_swap(self):
        self.camera.snowType = 1
    def Select_Rabbit(self):
        self.camera.snowType = 2
    def Select_Mask(self):
        self.camera.snowType = 3
    def Select_Noaml(self):
        self.camera.snowType = 0
    def Click_Album(self):
        Album(self)
        
class MySnowCam(snow.Snow):
    def __init__(self, video_source=0):
        self.cam = cv2.VideoCapture(video_source)
        self.success = True
        if not self.cam.isOpened():
            messagebox.showerror("경고", "카메라가 연결되었는지 확인하고 다시 시도해주세요")
            self.success = False
        self.width = self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
        #카메라의 크기를 받음, Snow를 상속했음으로 Snow의 메소드 사용가능
        self.snowType = 0
        
    def get_frame(self):
        #클릭한 버튼에 따라 스노우캠을 바꿈
        if self.cam.isOpened():
            ret, frame = self.cam.read()
            if ret:
                frame = cv2.flip(frame, 1)
                
                if self.snowType == 1:
                    img = self.Face_Swap(frame)
                elif self.snowType == 2:
                    img = self.Rabbit_Ears(frame)
                elif self.snowType == 3:
                    img = self.SunGlass(frame)
                else:
                    img = frame
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                return (ret, img)
            else:
                return (ret, None)
        else:
            return (ret, None)
 
    def __del__(self):
        if self.cam.isOpened():
            self.cam.release()        
        
if __name__ == "__main__":
    app =  QApplication(sys.argv)
    
    myWindow = MainUI()
    myWindow.show()
    app.exec_()
