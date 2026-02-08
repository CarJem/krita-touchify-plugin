from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
    

class PopupGeometryInfo:
    def __init__(self, position: QPoint, size: QSize):
        self.position: QPoint = position
        self.size: QSize = size