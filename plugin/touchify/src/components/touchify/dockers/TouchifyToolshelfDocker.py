
from krita import *
from PyQt5.QtCore import *

from typing import TYPE_CHECKING

from ....docker_manager import DockerManager
from ....action_manager import ActionManager
if TYPE_CHECKING:
    from ....touchify_instance import TouchifyInstance

from ..toolshelf.ToolshelfContainer import ToolshelfContainer

from ....resources import ResourceManager

DOCKER_TITLE = 'Touchify Toolshelf'

class TouchifyToolshelfDocker(DockWidget):

    def __init__(self): 
        super().__init__()
        self.toolshelfHost: ToolshelfContainer = None
        self.docker_manager: DockerManager = None
        self.actions_manager: ActionManager = None
        self.PanelIndex = 2
        self._last_panel_id: str | None = None
        self._last_pinned: bool = False
        self.setWindowTitle(DOCKER_TITLE)
      
    def setup(self, instance: "TouchifyInstance"):
        self.docker_manager = instance.docker_management
        self.actions_manager = instance.action_management
        self.onLoaded()
        
    def onKritaConfigUpdate(self):
        if self.panelStack:
            self.panelStack.onKritaConfigUpdate()
    
    def onLoaded(self):              
        self.panelStack = ToolshelfContainer(self, self.PanelIndex)
        self.panelStack.updateStyleSheet()
        self.setWidget(self.panelStack)

        if self._last_pinned:
            self.panelStack.setPinned(self._last_pinned)

        if self.panelStack.panel(self._last_panel_id) != None:
            self.panelStack.changePanel(self._last_panel_id)

    def onUnload(self):
        self._last_panel_id = self.panelStack._current_panel_id
        self._last_pinned = self.panelStack._pinned
        self.panelStack.shutdownWidget()
        self.panelStack.deleteLater()
        self.panelStack = None

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