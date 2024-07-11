from PyQt5.QtWidgets import QMdiArea, QDockWidget
from .NtAdjustToSubwindowFilter import NtAdjustToSubwindowFilter
from ... import stylesheet
from .NtWidgetPad import NtWidgetPad
from krita import *
from PyQt5.QtWidgets import QMdiArea, QDockWidget
from ...variables import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .NtCanvas import NtCanvas

#Other Toolbox: pyKrita_CoolBox

class NtToolboxInteractFilter(QObject):
    def __init__(self, parent=None):
        super(NtToolboxInteractFilter, self).__init__(parent)
        self.target = None

    def eventFilter(self, obj: QObject, e: QEvent):
        if (self.target and e.type() == QEvent.Type.MouseButtonPress):
            mouseEvent: QMouseEvent = e
            if mouseEvent.button() == Qt.MouseButton.RightButton:
                self.target.contextMenuEvent(QContextMenuEvent(QContextMenuEvent.Reason.Keyboard, QPoint(0,0)))

        return False

    def setTargetWidget(self, wdgt: QDockWidget):
        self.target = wdgt

class NtToolbox(object):

    def __init__(self, canvas: "NtCanvas", alignment: str, window: Window):
        self.qWin = window.qwindow()
        self.mdiArea = self.qWin.findChild(QMdiArea)
        self.canvas = canvas
        self.toolbox = self.qWin.findChild(QDockWidget, 'ToolBox')

        # Create "pad"
        self.pad = NtWidgetPad(self.mdiArea)
        self.pad.setObjectName("toolBoxPad")
        self.pad.borrowDocker(self.toolbox)
        self.pad.setViewAlignment(alignment)

        self.interactFilter = NtToolboxInteractFilter(self.mdiArea)
        self.interactFilter.setTargetWidget(self.toolbox)
        self.pad.installEventFilter(self.interactFilter)

        # Create and install event filter
        self.adjustFilter = NtAdjustToSubwindowFilter(self.mdiArea)
        self.adjustFilter.setTargetWidget(self)
        self.mdiArea.subWindowActivated.connect(self.onSubWindowActivated)
        self.pad.installEventFilter(self.adjustFilter)
        self.qWin.installEventFilter(self.adjustFilter)
        self.toolbox.installEventFilter(self.adjustFilter)

        # Disable the related QDockWidget
        self.dockerAction = window.qwindow().findChild(QDockWidget, "ToolBox").toggleViewAction()
        self.dockerAction.setEnabled(False)

    def onSubWindowActivated(self, subWin):
        if subWin:
            subWin.installEventFilter(self.adjustFilter)
            self.canvas.updateCanvas()
            self.updateStyleSheet()

    def updateStyleSheet(self):
        self.pad.setStyleSheet(stylesheet.touchify_nt_toolbox)

    def close(self):
        self.mdiArea.subWindowActivated.disconnect(self.onSubWindowActivated)
        self.pad.removeEventFilter(self.interactFilter)
        self.pad.removeEventFilter(self.adjustFilter)
        self.toolbox.removeEventFilter(self.adjustFilter)
        self.qWin.removeEventFilter(self.adjustFilter)
        self.dockerAction.setEnabled(True)
        return self.pad.close()