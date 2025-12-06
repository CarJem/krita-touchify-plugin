
from krita import *
from PyQt5.QtCore import *

from typing import TYPE_CHECKING


from touchify.src.managers.normal.canvas import CanvasManager
from touchify.src.managers.shared.events import GlobalEvents
from touchify.src.managers.shared.settings import TouchifySettings

from touchify.src.managers.normal.dockers import DockerManager
from touchify.src.managers.normal.action_manager import ActionManager
if TYPE_CHECKING:
    from ...PluginWindow import TouchifyWindow
    from touchify.src.PluginManagers import TouchifyManagers

from touchify.src.components.toolshelf_old.ToolshelfWidget import ToolshelfWidget

DOCKER_TITLE="Touchify Core: Toolshelf"

class ToolshelfDockWidget(DockWidget):

    resizeByDefaultRequested=pyqtSignal()

    def __init__(self): 
        super().__init__()
        self.app_window: "TouchifyWindow" = None
        self.managers: "TouchifyManagers" = None
        self.toolshelfHost: ToolshelfWidget = None
        self.docker_manager: DockerManager = None
        self.actions_manager: ActionManager = None
        self.canvas_manager: CanvasManager = None
        self.PanelIndex = -1
        self.previous_state: ToolshelfWidget.PreviousState = ToolshelfWidget.PreviousState()
        self.setWindowTitle(DOCKER_TITLE)
        GlobalEvents.instance().SIGNAL_TOUCHIFY_CONFIG_UPDATED.connect(self.onConfigUpdated)
        GlobalEvents.instance().SIGNAL_TOOLSHELF_PRESET_CHANGED.connect(self.onPresetChanged)


      
    def setup(self, app_window: "TouchifyWindow"):
        self.app_window = app_window
        self.managers = app_window.managers
        self.onLoaded()

    def onResizeByDefaultRequested(self):
        self.resizeByDefaultRequested.emit()
    
    def onLoaded(self):              
        self.mainWidget = ToolshelfWidget(self, self.managers, TouchifySettings.instance().getActiveToolshelf(self.PanelIndex), self.PanelIndex)
        self.mainWidget.resizeByDefaultRequested.connect(self.onResizeByDefaultRequested)
        self.mainWidget.toolshelfPageChanged.connect(self.onToolshelfPageChanged)
        self.mainWidget.toolshelfResized.connect(self.onToolshelfResize)
        self.mainWidget.toolshelfChanged.connect(self.onToolshelfChanged)
        self.setWidget(self.mainWidget)
        self.mainWidget.restorePreviousState(self.previous_state)

    def onUnload(self):
        if not hasattr(self, 'mainWidget'): return
        if not self.mainWidget: return
        
        self.previous_state = self.mainWidget.backupPreviousState()
        self.mainWidget.toolshelfPageChanged.disconnect(self.onToolshelfPageChanged)
        self.mainWidget.toolshelfResized.disconnect(self.onToolshelfResize)
        self.mainWidget.toolshelfChanged.disconnect(self.onToolshelfChanged)
        self.mainWidget.shutdownWidget()
        self.mainWidget.deleteLater()
        self.mainWidget = None

    def onPresetChanged(self, index: int):
        if self.PanelIndex == index:
            self.onConfigUpdated()

    def onConfigUpdated(self):
        self.onUnload()
        self.onLoaded()

    def onToolshelfResize(self):
        pass

    def onToolshelfChanged(self):
        pass

    def onToolshelfPageChanged(self):
        if self.isFloating(): self.adjustSize()

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
        GlobalEvents.instance().SIGNAL_TOUCHIFY_CONFIG_UPDATED.disconnect(self.onConfigUpdated)
        GlobalEvents.instance().SIGNAL_TOOLSHELF_PRESET_CHANGED.disconnect(self.onPresetChanged)
        return super().closeEvent(event)

    # notifies when views are added or removed
    # 'pass' means do not do anything
    def canvasChanged(self, canvas):
        pass

class ToolshelfDockWidgetAlt(ToolshelfDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(DOCKER_TITLE + " (Alt)")
        self.PanelIndex = -2