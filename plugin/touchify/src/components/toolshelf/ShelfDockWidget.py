
from krita import *
from PyQt5.QtCore import *

from typing import TYPE_CHECKING


from touchify.src.managers.normal.canvas import CanvasManager
from touchify.src.managers.shared.events import GlobalEvents

from touchify.src.managers.normal.dockers import DockerManager
from touchify.src.managers.normal.action_manager import ActionManager
if TYPE_CHECKING:
    from ...PluginWindow import TouchifyWindow
    from touchify.src.PluginManagers import TouchifyManagers

from touchify.src.components.toolshelf.ShelfWidget import ShelfWidget

DOCKER_TITLE="Touchify Core: Toolshelf"

class ShelfDockWidget(DockWidget):

    resizeByDefaultRequested=pyqtSignal()

    def __init__(self): 
        super().__init__()
        self.app_window: "TouchifyWindow" = None
        self.managers: "TouchifyManagers" = None
        self.toolshelfHost: ShelfWidget = None
        self.docker_manager: DockerManager = None
        self.actions_manager: ActionManager = None
        self.canvas_manager: CanvasManager = None
        self.PanelIndex = 1
        self.setWindowTitle(DOCKER_TITLE)
        GlobalEvents.instance().SIGNAL_TOUCHIFY_CONFIG_UPDATED.connect(self.onConfigUpdated)
        GlobalEvents.instance().SIGNAL_TOOLSHELF_PRESET_CHANGED.connect(self.onPresetChanged)


      
    def setup(self, app_window: "TouchifyWindow"):
        self.app_window = app_window
        self.managers = app_window.managers
        self.onLoaded()
    
    def onLoaded(self):              
        self.mainWidget = ShelfWidget(self, self.managers, self.PanelIndex)
        self.setWidget(self.mainWidget)

    def onUnload(self):
        if not hasattr(self, 'mainWidget'): return
        if not self.mainWidget: return
    
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

class ShelfDockWidgetAlt(ShelfDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(DOCKER_TITLE + " (Alt)")
        self.PanelIndex = 2