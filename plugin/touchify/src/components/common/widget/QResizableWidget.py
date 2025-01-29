from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QSize

class QResizableWidget(QWidget):
    def resize(self, w: int, h: int):
        if w < 0: w = 0
        if h < 0: h = 0
        super().resize(w, h)

    def setFixedSize(self, w: int, h: int):
        if w < 0: w = 0
        if h < 0: h = 0
        return super().setFixedSize(w, h)

    def setFixedSize(self, size: QSize):
        w = size.width()
        h = size.height()
        if w < 0: w = 0
        if h < 0: h = 0
        return super().setFixedSize(w, h)
    
    def resize(self, size: QSize):
        w = size.width()
        h = size.height()
        if w < 0: w = 0
        if h < 0: h = 0
        super().resize(w, h)

    def setMinimumHeight(self, minh: int) -> None:
        if minh < 0: minh = 0
        return super().setMinimumHeight(minh)
    
    def setMinimumWidth(self, minw: int) -> None:
        if minw < 0: minw = 0
        return super().setMinimumWidth(minw)

    def setMinimumSize(self, minw: int, minh: int) -> None:
        if minw < 0: minw = 0
        if minh < 0: minh = 0
        return super().setMinimumSize(minw, minh)
    
    def setMinimumSize(self, size: QSize) -> None:
        minw = size.width()
        minh = size.height()
        if minw < 0: minw = 0
        if minh < 0: minh = 0
        return super().setMinimumSize(minw, minh)