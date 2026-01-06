from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class PropertyTabs(QTabBar):

    #currentChanged=pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.setExpanding(False)
        self.setMovable(False)
        self.setUsesScrollButtons(True)
        self.setTabsClosable(False)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        try:
            if obj is self and event.type() == QEvent.Type.Wheel:
                return True
        except:
            pass

        return super().eventFilter(obj, event)
    
    def currentIndex(self):
        return super().currentIndex()
    
    def count(self):
        return super().count()
    
    def addTab(self, text: str):
        return super().addTab(text)
    
    def removeTab(self, index):
        return super().removeTab(index)
    
    def setCurrentIndex(self, index: int):
        return super().setCurrentIndex(index)
    
    def scroll(self, dx: int, dy: int):
        return super().scroll(dx, dy)