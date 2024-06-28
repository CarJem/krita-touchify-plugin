from PyQt5.QtWidgets import QMdiArea, QDockWidget
from .NtAdjustToSubwindowFilter import NtAdjustToSubwindowFilter
from ... import stylesheet
from .NtWidgetPad import NtWidgetPad
from krita import *
from PyQt5.QtWidgets import QMdiArea, QDockWidget
from ...variables import *

class NtToolbox():

    def __init__(self, window: Window):
        self.qWin = window.qwindow()
        self.mdiArea = self.qWin.findChild(QMdiArea)
        toolbox = self.qWin.findChild(QDockWidget, 'ToolBox')

        # Create "pad"
        self.pad = NtWidgetPad(self.mdiArea)
        self.pad.setObjectName("toolBoxPad")
        self.pad.borrowDocker(toolbox)
        self.pad.setViewAlignment('left')

        # Create and install event filter
        self.adjustFilter = NtAdjustToSubwindowFilter(self.mdiArea)
        self.adjustFilter.setTargetWidget(self.pad)
        self.mdiArea.subWindowActivated.connect(self.onSubWindowActivated)
        self.qWin.installEventFilter(self.adjustFilter)

        # Disable the related QDockWidget
        self.dockerAction = window.qwindow().findChild(QDockWidget, "ToolBox").toggleViewAction()
        self.dockerAction.setEnabled(False)

    def onSubWindowActivated(self, subWin):
        if subWin:
            self.pad.adjustToView()
            self.updateStyleSheet()

    def updateStyleSheet(self):
        self.pad.setStyleSheet(stylesheet.nu_toolbox_style)

    def close(self):
        self.mdiArea.subWindowActivated.disconnect(self.onSubWindowActivated)
        self.qWin.removeEventFilter(self.adjustFilter)
        self.dockerAction.setEnabled(True)
        return self.pad.close()