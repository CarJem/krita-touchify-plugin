
from enum import Enum
from krita import *
from PyQt5.QtCore import *

from touchify.__env__ import *

from touchify.src.api_krita import KritaAPI
from touchify.src.components.common.buttons.ColorFramedButton import ColorFramedButton

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.PluginWindow import TouchifyWindow

class CanvasColorPicker(ColorFramedButton):

    class Mode(Enum):
        Foreground=0
        Background=1

    def __init__(self, parent: QWidget | None = None, mode: Mode = 0):
        super(CanvasColorPicker, self).__init__(parent)
        self.mode = mode

        if self.mode == CanvasColorPicker.Mode.Foreground:
            self.clicked.connect(self.setForegroundColor)
        if self.mode == CanvasColorPicker.Mode.Background:
            self.clicked.connect(self.setBackgroundColor)

    def setInstance(self, window: "TouchifyWindow"):
        self.appEngine = window
        self.appEngine.mgr_actions.canvasChanged.connect(self.onCanvasChanged)
        self.onCanvasChanged(self.appEngine.mgr_actions.getCurrentCanvas())
        if self.mode == CanvasColorPicker.Mode.Foreground:
            self.appEngine.mgr_actions.foregroundColorChanged.connect(self.onColorChanged)
            self.onColorChanged(self.appEngine.mgr_actions.getCanvasColor())
        if self.mode == CanvasColorPicker.Mode.Background:
            self.appEngine.mgr_actions.backgroundColorChanged.connect(self.onColorChanged)
            self.onColorChanged(self.appEngine.mgr_actions.getCanvasColor(True))

    def setForegroundColor(self):
        KritaAPI.get_action("chooseForegroundColor").trigger()

    def setBackgroundColor(self):
        KritaAPI.get_action("chooseBackgroundColor").trigger()
    
    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)

    def krita_to_qcolor(self, source: ManagedColor):
        if self.canvas == None or source == None: return QColor()
        return source.colorForCanvas(self.canvas)
    
    def onCanvasChanged(self, canvas: Canvas):
        self.canvas = canvas

    def onColorChanged(self, managed_color: ManagedColor):
        color = self.krita_to_qcolor(managed_color)
        self.setColor(color)