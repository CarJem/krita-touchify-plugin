from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class GlobalEventFilter(QObject):
    mouseReleased = pyqtSignal()
    mouseMoved = pyqtSignal()
    windowActivated = pyqtSignal()


    def __init__(self):
        super().__init__()

    def eventFilter(self, obj, event):
        if (event.type() == QEvent.MouseButtonRelease) or \
        (event.type() == QEvent.TabletRelease):
            self.mouseReleased.emit()
        return super().eventFilter(obj, event)