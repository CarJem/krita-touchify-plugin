



from touchify.src.components.canvas.NtWidgetPad import NtWidgetPad
from krita import *
from touchify.__env__ import *
from touchify.src.components.toolshelf.ToolshelfCanvasWidget import ToolshelfCanvasWidget

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .NtCanvas import NtCanvas
    from touchify.src.PluginWindow import TouchifyWindow

class NtToolshelf(NtWidgetPad):

    def __init__(self, canvas: "NtCanvas", window: Window, panel_index: int, app_engine: "TouchifyWindow"):
        super().__init__(window, canvas, True)   

        self.toolshelf = ToolshelfCanvasWidget(self, panel_index, app_engine)
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

