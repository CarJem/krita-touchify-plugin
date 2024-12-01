

from touchify.src.docker_manager import DockerManager
from touchify.src.action_manager import ActionManager


from touchify.src.settings import TouchifyConfig
from touchify.src.components.touchify.canvas.NtWidgetPad import NtWidgetPad
from krita import *
from touchify.src.variables import *
from touchify.src.components.touchify.dockers.toolshelf.ToolshelfDockWidget import ToolshelfDockWidget

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .NtCanvas import NtCanvas

class NtToolshelf(NtWidgetPad):

    def __init__(self, canvas: "NtCanvas", window: Window, isPrimaryPanel: bool, docker_manager: DockerManager, actions_manager: ActionManager):
        super().__init__(window, canvas, True)   
        panel_index = 0 if isPrimaryPanel else 1

        self.toolshelf = ToolshelfDockWidget(panel_index, docker_manager, actions_manager)
        self.toolshelf.updateViewRequested.connect(self.onUpdateViewRequested)
        self.toolshelf.installEventFilter(self.adjustFilter)

        self.setObjectName("toolshelfPad")
        self.borrowDocker(self.toolshelf)

        toolshelf_cfg = TouchifyConfig.instance().getActiveToolshelf(panel_index)
        if toolshelf_cfg:
            if toolshelf_cfg.header_options:
                if toolshelf_cfg.header_options.default_to_pinned == True:
                    self.toggle()
        

    def onUpdateViewRequested(self):
        self.canvas.updateView()
    
    def close(self):
        self.toolshelf.updateViewRequested.disconnect(self.onUpdateViewRequested)
        self.toolshelf.removeEventFilter(self.adjustFilter)
        self.toolshelf.onUnload()
        result = super().close()
        self.toolshelf.close()
        return result

