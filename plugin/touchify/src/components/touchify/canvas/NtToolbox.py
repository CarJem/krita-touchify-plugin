
from touchify.src.components.touchify.dockers.toolbox.ToolboxDocker import ToolboxDocker

from touchify.src.components.touchify.canvas.NtWidgetPad import NtWidgetPad
from krita import *
from touchify.src.variables import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .NtCanvas import NtCanvas

class NtToolbox(NtWidgetPad):

    def __init__(self, canvas: "NtCanvas", window: Window):
        super().__init__(window, canvas)

        # General Code
        self.option_returnDockerOnClose = False
        self.toolbox: ToolboxDocker = self.source_window.findChild(ToolboxDocker, TOUCHIFY_ID_DOCKER_TOOLBOX)
        self.dockerAction = window.qwindow().findChild(QDockWidget, TOUCHIFY_ID_DOCKER_TOOLBOX).toggleViewAction()
        self.dockerAction.setEnabled(False)
        self.borrowDocker(self.toolbox)

        # Alternative Code
        #self.toolbox = ToolboxDocker(self)
        #self.toolbox.toolboxWidget.scrollArea.setWidgetResizable(True)
        #self.toolbox.setup(canvas.app_engine)
        #self.borrowDocker(self.toolbox)

        self.toolbox.toolboxWidget.horizontalModeAction.setEnabled(False)
        self.setObjectName("toolBoxPad")

    def close(self):
        # Alternative Code
        self.toolbox.toolboxWidget.horizontalModeAction.setEnabled(True)
        self.dockerAction.setEnabled(True)

        return super().close()