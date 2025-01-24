



from touchify.src.components.touchify.canvas.NtWidgetPad import NtWidgetPad
from krita import *
from touchify.src.variables import *
from touchify.src.components.touchify.dockers.toolshelf.ToolshelfCanvasWidget import ToolshelfCanvasWidget

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .NtCanvas import NtCanvas
    from touchify.src.window import TouchifyWindow

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

