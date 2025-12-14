
from krita import *
from PyQt5.QtCore import *
from touchify.__env__ import *

from touchify.src.api_krita.wrappers.window import WindowAPI
from typing import TYPE_CHECKING

from touchify.src.alib_widgets.buttons.IconButton import IconButton
if TYPE_CHECKING:
    from touchify.src.PluginManagers import TouchifyManagers

class BrushPresetPicker(IconButton):

    def __init__(self, parent: QWidget | None = None):
        super(BrushPresetPicker, self).__init__(parent)
        self.clicked.connect(self.openBrushPicker)
        self.setContentsMargins(0,0,0,0)

    def setInstance(self, window: WindowAPI, managers: "TouchifyManagers"):
        self.managers = managers
        self.notifier = window.notifier
        self.notifier.brushChanged.connect(self.onBrushChanged)
        self.onBrushChanged(self.notifier.getCurrentBrush())

    def openBrushPicker(self):
        self.managers.mgr_actions.Create_Popup(Env.InternalPopups.BRUSH_PICKER, self) 

    def onBrushChanged(self, current_brush: Resource):
        self.brush = current_brush

        if not self.brush: return
        
        image = self.brush.image()
        if image: self.setIcon(QIcon(QPixmap.fromImage(image)))

        self.repaint()