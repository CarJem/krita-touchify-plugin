from PyQt5.QtWidgets import QDockWidget

from touchify.src.components.touchify.dockers.toolbox.ToolboxDocker import ToolboxDocker

from touchify.src.components.touchify.canvas.NtWidgetPad import NtWidgetPad
from krita import *
from PyQt5.QtWidgets import QDockWidget
from touchify.__env__ import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .NtCanvas import NtCanvas

class NtToolbox(NtWidgetPad):

    def __init__(self, canvas: "NtCanvas", window: Window):
        super().__init__(window, canvas)
        self.reopenDockerOnReturn = False
        self.toolbox: ToolboxDocker = self.source_window.findChild(ToolboxDocker, TOUCHIFY_DOCKERID_DOCKER_TOOLBOX)
        
        self.setObjectName("toolBoxPad")
        self.borrowDocker(self.toolbox)

        # Disable the related QDockWidget
        self.dockerAction = window.qwindow().findChild(QDockWidget, TOUCHIFY_DOCKERID_DOCKER_TOOLBOX).toggleViewAction()
        self.dockerAction.setEnabled(False)

        self.toolbox.toolboxWidget.horizontalModeAction.setEnabled(False)

    def close(self):
        self.toolbox.toolboxWidget.horizontalModeAction.setEnabled(True)
        self.dockerAction.setEnabled(True)
        return super().close()