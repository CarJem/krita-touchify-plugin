
from krita import *
from PyQt5.QtCore import *

from touchify.src.variables import *


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.window import TouchifyWindow

class CanvasBrushPicker(QPushButton):

    def __init__(self, parent: QWidget | None = None):
        super(CanvasBrushPicker, self).__init__(parent)
        self.clicked.connect(self.openBrushPicker)

    def setInstance(self, window: "TouchifyWindow"):
        self.appEngine = window
        self.appEngine.mgr_actions.brushChanged.connect(self.onBrushChanged)
        self.onBrushChanged(self.appEngine.mgr_actions.getCurrentBrush())

    def openBrushPicker(self):
        self.appEngine.mgr_actions.Create_Popup("touchify_internal_brush_picker", self)
    
    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)

    def resizeEvent(self, a0: QResizeEvent):
        self.setIconSize(a0.size().shrunkBy(QMargins(4,4,4,4)))
        return super().resizeEvent(a0)

    def onBrushChanged(self, current_brush: Resource):
        self.brush = current_brush

        if not self.brush: return
        
        image = self.brush.image()
        if image: self.setIcon(QIcon(QPixmap.fromImage(image)))