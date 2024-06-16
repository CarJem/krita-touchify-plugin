from krita import *
from PyQt5.QtWidgets import *
from .components.toolbox.ToolboxRoot import *
from .variables import *

class TouchifyToolbox(DockWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Touchify Toolbox")

        self.mainWidget = QWidget(self)
        self.setWidget(self.mainWidget)

        self.layout = QVBoxLayout()
        self.mainWidget.setLayout(self.layout)

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        Krita.instance().notifier().windowCreated.connect(self.onLoaded)

        cfg: ConfigManager = ConfigManager.instance()
        cfg.notifyConnect(self.onConfigUpdated)
    
    def onLoaded(self):              
        self.panelStack = ToolboxRoot(self)
        self.layout.addWidget(self.panelStack)

    def onConfigUpdated(self):
        self.panelStack.dismantle()
        self.layout.removeWidget(self.panelStack)
        self.panelStack.deleteLater()
        self.panelStack = None

        self.panelStack = ToolboxRoot(self)
        self.layout.addWidget(self.panelStack)

    def canvasChanged(self, canvas):
        pass

# And add the extension to Krita's list of extensions:
Krita.instance().addDockWidgetFactory(DockWidgetFactory(TOUCHIFY_ID_DOCKER_TOOLBOX, DockWidgetFactoryBase.DockRight, TouchifyToolbox)) # type: ignore

