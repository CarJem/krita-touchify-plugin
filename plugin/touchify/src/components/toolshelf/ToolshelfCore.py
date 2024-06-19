from krita import *
from PyQt5.QtWidgets import *
from .ToolshelfRoot import *
from ...variables import *



HAS_KRITA_FULLY_LOADED = False

def ON_KRITA_WINDOW_CREATED():
    global HAS_KRITA_FULLY_LOADED
    HAS_KRITA_FULLY_LOADED = True

class ToolshelfCore(QDockWidget):

    def __init__(self, enableToolOptions: bool = False):
        super().__init__()
        self.setWindowTitle("Touchify Toolshelf")

        self.enableToolOptions = enableToolOptions

        self.mainWidget = QWidget(self)
        self.setWidget(self.mainWidget)

        self.layout = QVBoxLayout()
        self.mainWidget.setLayout(self.layout)

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        if HAS_KRITA_FULLY_LOADED:
            self.onLoaded()
        else:
            Krita.instance().notifier().windowCreated.connect(self.onLoaded)
        

    def onKritaConfigUpdate(self):
        if self.panelStack:
            self.panelStack._mainWidget.onKritaConfigUpdate()
    
    def onLoaded(self):              
        self.panelStack = ToolshelfRoot(self, self.enableToolOptions)
        self.layout.addWidget(self.panelStack)

    def onUnload(self):
        self.panelStack.dismantle()
        self.layout.removeWidget(self.panelStack)
        self.panelStack.deleteLater()
        self.panelStack = None

    def onConfigUpdated(self):
        self.onUnload()
        self.onLoaded()


Krita.instance().notifier().windowCreated.connect(ON_KRITA_WINDOW_CREATED)