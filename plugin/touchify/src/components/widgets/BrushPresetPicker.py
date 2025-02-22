
from krita import *
from PyQt5.QtCore import *

from touchify.__env__ import *


from typing import TYPE_CHECKING

from touchify.src.api_krita import KritaAPI
if TYPE_CHECKING:
    from touchify.src.PluginWindow import TouchifyWindow

class BrushPresetPicker(QPushButton):

    def __init__(self, parent: QWidget | None = None):
        super(BrushPresetPicker, self).__init__(parent)
        self.clicked.connect(self.openBrushPicker)

    def setInstance(self, window: "TouchifyWindow"):
        self.appEngine = window
        self.notifier = window.api_window.notifier()
        self.notifier.brushChanged.connect(self.onBrushChanged)
        self.onBrushChanged(self.notifier.getCurrentBrush())

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