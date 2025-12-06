



from touchify.src.api_krita.wrappers.window import WindowAPI
from touchify.src.components.canvas.NtWidgetPad import NtWidgetPad
from krita import *
from touchify.__env__ import *
from touchify.src.components.toolshelf_legacy.ToolshelfCanvasWidget import ToolshelfCanvasWidget

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .NtCanvas import NtCanvas
    from touchify.src.PluginManagers import TouchifyManagers

class NtToolshelf(NtWidgetPad):

    def __init__(self, canvas: "NtCanvas", window: WindowAPI, panel_index: int, managers: "TouchifyManagers"):
        super().__init__(window, canvas, True)   

        self.toolshelf = ToolshelfCanvasWidget(self, panel_index, managers)
        self.toolshelf.resizeByDefaultRequested.connect(self.onResizeByDefaultRequested)
        self.setObjectName("toolshelfPad")
        self.borrowDocker(self.toolshelf)

    def onResizeByDefaultRequested(self):
        self.setResizable(True)
    
    def close(self):
        self.toolshelf.onUnload()
        result = super().close()
        self.toolshelf.close()
        return result

