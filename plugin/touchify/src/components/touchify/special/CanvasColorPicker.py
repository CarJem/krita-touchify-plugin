
from enum import Enum
from krita import *
from PyQt5.QtCore import *

from touchify.src.variables import *

from touchify.src.components.pyqt.widgets.ColorFramedButton import ColorFramedButton
from touchify.src.helpers import TouchifyHelpers

DOCKER_TITLE = 'Touchify Addon: Color Options'
DOCKER_ID="Touchify/ColorOptionsDocker"

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.window import TouchifyWindow

class CanvasColorPicker(ColorFramedButton):

    class Mode(Enum):
        Foreground=0
        Background=1

    def __init__(self, parent: QWidget | None = None, mode: Mode = 0):
        super(CanvasColorPicker, self).__init__(parent)
        self.mode = mode
        self.canvas: Canvas = None

        if self.mode == CanvasColorPicker.Mode.Foreground:
            self.clicked.connect(self.setForegroundColor)
        if self.mode == CanvasColorPicker.Mode.Background:
            self.clicked.connect(self.setBackgroundColor)
        
        self.setupTimer()

    def setupTimer(self):
        parentExtension = TouchifyHelpers.getExtension()
        if parentExtension:
            parentExtension.intervalTimerTicked.connect(self.updateColors)

    def setForegroundColor(self):
        Krita.instance().action("chooseForegroundColor").trigger()

    def setBackgroundColor(self):
        Krita.instance().action("chooseBackgroundColor").trigger()

    def krita_to_qcolor(self, source: ManagedColor):
        if self.canvas == None or source == None: return QColor()
        return source.colorForCanvas(self.canvas)
    
    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)

    def updateColors(self):
        activeWin = Krita.instance().activeWindow()
        if activeWin == None: return
        activeView = activeWin.activeView()
        if activeView == None: return

        canvas = activeView.canvas()
        if canvas == None: return
        
        self.canvas = canvas
        
        if self.mode == CanvasColorPicker.Mode.Foreground:
            fg_color = self.krita_to_qcolor(activeView.foregroundColor())
            self.setColor(fg_color)
        
        if self.mode == CanvasColorPicker.Mode.Background:
            bg_color = self.krita_to_qcolor(activeView.backgroundColor())
            self.setColor(bg_color)