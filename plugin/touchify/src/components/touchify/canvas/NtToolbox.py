from PyQt5.QtWidgets import QDockWidget

from ..dockers.toolbox.ToolboxDocker import ToolboxDocker

from .NtWidgetPad import NtWidgetPad
from krita import *
from PyQt5.QtWidgets import QDockWidget
from ....variables import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .NtCanvas import NtCanvas

class NtToolbox(NtWidgetPad):

    def __init__(self, canvas: "NtCanvas", window: Window):
        super().__init__(window, canvas)

        self.toolbox: ToolboxDocker = self.qWin.findChild(ToolboxDocker, TOUCHIFY_ID_DOCKER_TOOLBOX)
        self.toolbox.installEventFilter(self.adjustFilter)
        
        self.setObjectName("toolBoxPad")
        self.borrowDocker(self.toolbox)

        # Disable the related QDockWidget
        self.dockerAction = window.qwindow().findChild(QDockWidget, TOUCHIFY_ID_DOCKER_TOOLBOX).toggleViewAction()
        self.dockerAction.setEnabled(False)

        self.toolbox.toolboxWidget.horizontalModeAction.setEnabled(False)

    def close(self):
        self.toolbox.toolboxWidget.horizontalModeAction.setEnabled(True)
        self.dockerAction.setEnabled(True)
        self.toolbox.removeEventFilter(self.adjustFilter)
        return super().close()