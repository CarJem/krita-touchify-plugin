from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class MouseReleaseListener(QObject):
    mouseReleased = pyqtSignal()

    def __init__(self):
        super().__init__()

    def eventFilter(self, obj, event):
        if (event.type() == QEvent.MouseButtonRelease) or \
        (event.type() == QEvent.TabletRelease):
            self.mouseReleased.emit()
        return super().eventFilter(obj, event)