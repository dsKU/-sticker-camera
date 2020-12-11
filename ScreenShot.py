import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtCore import QCoreApplication

from PyQt5 import QtGui
from PyQt5.QtCore import *

import PIL.Image, PIL.ImageTk
import glob
import os

saveDialog = uic.loadUiType("save.ui")[0]

class ScreenShot(QDialog,saveDialog):
    def __init__(self, parent, img, title):
        super(ScreenShot, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(title)
        self.title = title
        self.img = img
        self.lb_img.setPixmap(self.img)
        self.lb_img.resize(self.img.width(), self.img.height())        
        self.lb_img.show()
        
        self.btn_save.clicked.connect(self.Click_Save)
        
        self.show()
        
    def Click_Save(self):
        name = self.title
        path = './album/' + name + '.jpg'
        self.img.save(path)
        #self.img.show()
        self.close()
        #클릭시 이미지가 저장이 되고 폼이 꺼짐

