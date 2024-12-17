



from touchify.src.components.touchify.canvas.NtWidgetPad import NtWidgetPad
from krita import *
from touchify.src.variables import *
from touchify.src.components.touchify.dockers.toolshelf.ToolshelfCanvasWidget import ToolshelfCanvasWidget

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .NtCanvas import NtCanvas
    from touchify.src.window import TouchifyWindow

class NtToolshelf(NtWidgetPad):

    def __init__(self, canvas: "NtCanvas", window: Window, isPrimaryPanel: bool, app_engine: "TouchifyWindow"):
        super().__init__(window, canvas, True)   
        panel_index = 0 if isPrimaryPanel else 1

        self.toolshelf = ToolshelfCanvasWidget(panel_index, app_engine)
        self.toolshelf.updateViewRequested.connect(self.onUpdateViewRequested)
        self.toolshelf.installEventFilter(self.adjustFilter)

        self.setObjectName("toolshelfPad")
        self.borrowDocker(self.toolshelf)
        

    def onUpdateViewRequested(self):
        self.canvas.updateView()
    
    def close(self):
        self.toolshelf.updateViewRequested.disconnect(self.onUpdateViewRequested)
        self.toolshelf.removeEventFilter(self.adjustFilter)
        self.toolshelf.onUnload()
        result = super().close()
        self.toolshelf.close()
        return result

