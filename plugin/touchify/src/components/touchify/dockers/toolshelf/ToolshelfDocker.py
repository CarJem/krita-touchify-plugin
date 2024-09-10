
from krita import *
from PyQt5.QtCore import *

from typing import TYPE_CHECKING

from .....docker_manager import DockerManager
from .....action_manager import ActionManager
if TYPE_CHECKING:
    from .....touchify import Touchify

from .ToolshelfWidget import ToolshelfWidget

from .....resources import ResourceManager

DOCKER_TITLE = 'Touchify Toolshelf'

class ToolshelfDocker(DockWidget):

    def __init__(self): 
        super().__init__()
        self.toolshelfHost: ToolshelfWidget = None
        self.docker_manager: DockerManager = None
        self.actions_manager: ActionManager = None
        self.PanelIndex = 2
        self._last_panel_id: str | None = None
        self._last_pinned: bool = False
        self.setWindowTitle(DOCKER_TITLE)
      
    def setup(self, instance: "Touchify.TouchifyWindow"):
        self.docker_manager = instance.docker_management
        self.actions_manager = instance.action_management
        self.onLoaded()
        
    def onKritaConfigUpdate(self):
        pass
    
    def onLoaded(self):              
        self.mainWidget = ToolshelfWidget(self, self.PanelIndex)
        self.setWidget(self.mainWidget)
        self.mainWidget.restorePreviousState(self._last_pinned, self._last_panel_id)

    def onUnload(self):
        self._last_pinned, self._last_panel_id = self.mainWidget.backupPreviousState()
        self.mainWidget.shutdownWidget()
        self.mainWidget.deleteLater()
        self.mainWidget = None

    def onConfigUpdated(self):
        self.onUnload()
        self.onLoaded()
        
    def showEvent(self, event):
        super().showEvent(event)

    def closeEvent(self, event):
        super().closeEvent(event)
        
    def onSizeChanged(self):
        pass

    # notifies when views are added or removed
    # 'pass' means do not do anything
    def canvasChanged(self, canvas):
        pass