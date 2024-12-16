
from krita import *
from PyQt5.QtCore import *

from typing import TYPE_CHECKING

from touchify.src.settings import TouchifySettings

from touchify.src.docker_manager import DockerManager
from touchify.src.action_manager import ActionManager
if TYPE_CHECKING:
    from .....window import TouchifyWindow

from touchify.src.components.touchify.dockers.toolshelf.ToolshelfWidget import ToolshelfWidget


DOCKER_TITLE = 'Touchify Toolshelf'

class ToolshelfDockWidgetKrita(DockWidget):

    def __init__(self): 
        super().__init__()
        self.toolshelfHost: ToolshelfWidget = None
        self.docker_manager: DockerManager = None
        self.actions_manager: ActionManager = None
        self.PanelIndex = 2
        self.previous_state: ToolshelfWidget.PreviousState = ToolshelfWidget.PreviousState()
        self.setWindowTitle(DOCKER_TITLE)
      
    def setup(self, instance: "TouchifyWindow"):
        self.docker_manager = instance.docker_management
        self.actions_manager = instance.action_management
        self.onLoaded()
        
    def onKritaConfigUpdate(self):
        pass
    
    def onLoaded(self):              
        self.mainWidget = ToolshelfWidget(self, TouchifySettings.instance().getActiveToolshelf(self.PanelIndex), self.PanelIndex)
        self.setWidget(self.mainWidget)
        self.mainWidget.restorePreviousState(self.previous_state)

    def onUnload(self):
        if hasattr(self, 'mainWidget'):
            self.previous_state = self.mainWidget.backupPreviousState()
            self.mainWidget.shutdownWidget()
            self.mainWidget.deleteLater()
            self.mainWidget = None

    def onConfigUpdated(self):
        self.onUnload()
        self.onLoaded()

    def requestViewUpdate(self):
        if self.isFloating():
            self.adjustSize()

    def sizeHint(self):
        if hasattr(self, "mainWidget"):
            if self.mainWidget:
                return self.mainWidget.sizeHint()
        
        return super().sizeHint()

    def minimumSizeHint(self):
        if hasattr(self, "mainWidget"):
            if self.mainWidget:
                return self.mainWidget.minimumSizeHint()

        return super().minimumSizeHint()

    def minimumSize(self):
        if hasattr(self, "mainWidget"):
            if self.mainWidget:
                return self.mainWidget.minimumSize()

        return super().minimumSize()
        
    def maximumSize(self):
        if hasattr(self, "mainWidget"):
            if self.mainWidget:
                return self.mainWidget.maximumSize()
        return super().maximumSize()
        
    def showEvent(self, event):
        super().showEvent(event)

    def closeEvent(self, event):
        super().closeEvent(event)

    # notifies when views are added or removed
    # 'pass' means do not do anything
    def canvasChanged(self, canvas):
        pass