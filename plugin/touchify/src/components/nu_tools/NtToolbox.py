from PyQt5.QtWidgets import QMdiArea, QDockWidget
from .Nt_AdjustToSubwindowFilter import Nt_AdjustToSubwindowFilter
from ... import stylesheet
from ...variables import KRITA_ID_DOCKER_SHAREDTOOLDOCKER, KRITA_ID_MENU_SETTINGS, TOUCHIFY_ID_OPTIONS_NU_OPTIONS_ALTERNATIVE_TOOLBOX_POSITION, TOUCHIFY_ID_OPTIONSROOT_MAIN
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
        self.adjustFilter = Nt_AdjustToSubwindowFilter(self.mdiArea)
        self.adjustFilter.setTargetWidget(self.pad)
        self.mdiArea.subWindowActivated.connect(self.onSubWindowActivated)
        self.qWin.installEventFilter(self.adjustFilter)

        # Create visibility toggle action
        action = window.createAction(KRITA_ID_DOCKER_SHAREDTOOLDOCKER, "Show Toolbox", KRITA_ID_MENU_SETTINGS)
        action.toggled.connect(self.pad.toggleWidgetVisible)
        action.setCheckable(True)
        action.setChecked(True)

        # Disable the related QDockWidget
        self.dockerAction = window.qwindow().findChild(QDockWidget, "ToolBox").toggleViewAction()
        self.dockerAction.setEnabled(False)

    def onSubWindowActivated(self, subWin):
        if subWin:
            self.pad.adjustToView()
            self.updateStyleSheet()

    def findDockerAction(self, window, text):
        dockerMenu = None

        for m in window.qwindow().actions():
            if m.objectName() == "settings_dockers_menu":
                dockerMenu = m

                for a in dockerMenu.menu().actions():
                    if a.text().replace('&', '') == text:
                        return a

        return False

    def updateStyleSheet(self):
        self.pad.setStyleSheet(stylesheet.nu_toolbox_style)

    def close(self):
        self.mdiArea.subWindowActivated.disconnect(self.onSubWindowActivated)
        self.qWin.removeEventFilter(self.adjustFilter)
        self.dockerAction.setEnabled(True)
        return self.pad.close()