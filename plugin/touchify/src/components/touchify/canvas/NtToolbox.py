
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
        self.reopenDockerOnReturn = False
        self.toolbox = ToolboxDocker(self)
        self.toolbox.setContentsMargins(0,0,0,0)
        self.toolbox.setup(canvas.app_engine)
        self.toolbox.toolboxWidget.horizontalModeAction.setEnabled(False)
        self.setObjectName("toolBoxPad")
        self.borrowDocker(self.toolbox)

    def close(self):
        return super().close()