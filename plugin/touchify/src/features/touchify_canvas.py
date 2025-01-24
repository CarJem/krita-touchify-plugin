from PyQt5.QtWidgets import *

from touchify.src.components.touchify.canvas.NtCanvas import NtCanvas

from touchify.src.variables import *
from touchify.src.settings import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.window import TouchifyWindow


from krita import *
    
class TouchifyCanvas(QObject):

    def __init__(self, instance: "TouchifyWindow"):
        super().__init__(instance)
        self.appEngine = instance
        self.ntCanvas: NtCanvas | None = None

    def onWindowCreated(self):
        self.qWin = self.appEngine.windowSource.qwindow()
        self.ntCanvas.windowCreated(self.appEngine)

    def finalizeActions(self):
        self.ntCanvas.finishMenuActions()

    def createActions(self, window: Window, mainMenuBar: QMenuBar):
        self.ntCanvas = NtCanvas(window.qwindow().window(), window)
        self.ntCanvas.createMenuActions(window, mainMenuBar)
