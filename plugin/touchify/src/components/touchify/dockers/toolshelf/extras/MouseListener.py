from PyQt5.QtWidgets import QSizePolicy, QStackedWidget
import uuid
from krita import *
from PyQt5.QtWidgets import *

class MouseListener(QObject):
    mouseReleased = pyqtSignal()

    def __init__(self):
        super().__init__()

    def eventFilter(self, obj, event):
        if (event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton) or \
        (event.type() == QEvent.TabletRelease and event.button() == Qt.LeftButton):
            self.mouseReleased.emit()
        return super().eventFilter(obj, event)