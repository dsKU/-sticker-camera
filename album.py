from tkinter import *
import PIL.Image, PIL.ImageTk
import glob
import os
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtCore import QCoreApplication

from PyQt5 import QtGui
from PyQt5.QtCore import *

albumDialog = uic.loadUiType("album.ui")[0]

class Album(QDialog,albumDialog):
    def __init__(self, parent):
        super(Album, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Album")
        self.btn_delete.clicked.connect(self.Delete_img)
        
        self.del_arr = []

        self.Insert_img()
        self.show()
        
    def Sel_Picture(self):
        #이미지만 넣었을 때 파일이름 알아내
        idx = self.img_arr.index(self.sender())
        mag = self.images[idx]
        
        if mag in self.del_arr:
            self.sender().setStyleSheet("border: 2px solid None")
            self.del_arr.remove(mag)

        else:
            self.sender().setStyleSheet("border: 2px solid red")
            self.del_arr.append(mag)

        #사진을 클릭하면 빨간색 테두리가 됨
        
    def Delete_img(self):
        if len(self.del_arr) == 0:
            return

        for i in self.del_arr:
            if os.path.isfile(i):
                os.remove(i)
                
        self.del_arr = []
        self.Insert_img()

    
    def Insert_img(self):        
        gridLayout = QGridLayout()
        scroll = QScrollArea()
        groupBox = QGroupBox()
        
        self.img_arr = []
    
        self.images = glob.glob('./album/*.jpg')
        i = 1
        j = 0
       
        for img_name in self.images:
            btn = QPushButton(self)
            btn.resize(400,300)
            btn.setIcon(QtGui.QIcon(img_name))

            btn.setIconSize(QSize(400,300))
            btn.setStyleSheet("border: 2px solid None")
            btn.clicked.connect(lambda:self.Sel_Picture())
            
            self.img_arr.append(btn)
            
            gridLayout.addWidget(btn,i,j)
            j = j + 1
            if j >= 2:
                i = i + 1
                j = 0
        groupBox.setLayout(gridLayout)
        scroll.setFixedWidth(900)
        scroll.setFixedHeight(600)
        self.scrollArea.setWidget(groupBox)

        

