
from krita import *
from PyQt5.QtWidgets import QDockWidget
from ....variables import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .NtCanvas import NtCanvas


class NtToolboxInteractFilter(QObject):
    def __init__(self, parent: QWidget):
        super(NtToolboxInteractFilter, self).__init__(parent)
        self.target = None

    def eventFilter(self, obj: QObject, e: QEvent):
        if (self.target and e.type() == QEvent.Type.MouseButtonPress):
            mouseEvent: QMouseEvent = e
            match mouseEvent.button():
                case Qt.MouseButton.RightButton:
                    self.target.contextMenuEvent(QContextMenuEvent(QContextMenuEvent.Reason.Keyboard, QPoint(0,0)))

        return False

    def setTargetWidget(self, wdgt: QDockWidget):
        self.target = wdgt