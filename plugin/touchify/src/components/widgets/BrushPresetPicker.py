
from krita import *
from PyQt5.QtCore import *
from touchify.__env__ import *

from touchify.src.api_krita.wrappers.window import WindowAPI
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.PluginManagers import TouchifyManagers

class BrushPresetPicker(QPushButton):

    def __init__(self, parent: QWidget | None = None):
        super(BrushPresetPicker, self).__init__(parent)
        self.clicked.connect(self.openBrushPicker)

    def setInstance(self, window: WindowAPI, managers: "TouchifyManagers"):
        self.managers = managers
        self.notifier = window.notifier
        self.notifier.brushChanged.connect(self.onBrushChanged)
        self.onBrushChanged(self.notifier.getCurrentBrush())

    def openBrushPicker(self):
        self.managers.mgr_actions.Create_Popup("touchify_internal_brush_picker", self)
    
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