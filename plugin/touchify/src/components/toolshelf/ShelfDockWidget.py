
from krita import *
from PyQt5.QtCore import *

from typing import TYPE_CHECKING


from touchify.src.config.toolshelf.ToolshelfContainer import ToolshelfContainer
from touchify.src.config.toolshelf.ToolshelfSettings import ToolshelfSettings
from touchify.src.managers.shared.events import GlobalEvents

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
        self.mainWidget: ShelfWidget = None
        
        self._originalSizePolicy = self.sizePolicy()
        self.shrinkToFit = False

        self.PanelIndex = 1
        self.setWindowTitle(DOCKER_TITLE)
        GlobalEvents.instance().SIGNAL_TOUCHIFY_CONFIG_UPDATED.connect(self.onConfigUpdated)

    def setup(self, app_window: "TouchifyWindow"):
        self.app_window = app_window
        self.managers = app_window.managers
        self.mainWidget = ShelfWidget(self, self.managers, self.PanelIndex)
        self.setWidget(self.mainWidget)    

    def shelfReload(self, state: ToolshelfContainer):
        if state.options.resize_style == ToolshelfSettings.ResizeStyle.Minimum:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.shrinkToFit = True
        else:
            self.setSizePolicy(self._originalSizePolicy)
            self.shrinkToFit = False

        if self.shrinkToFit:
            self.adjustSize()


    def onConfigUpdated(self):
        if self.mainWidget: self.mainWidget.onConfigUpdated()

    def resizeEvent(self, a0):
        if self.shrinkToFit and a0.oldSize != a0.size:
            return self.adjustSize()
        return super().resizeEvent(a0)
        
    def showEvent(self, event):
        super().showEvent(event)

    def closeEvent(self, event):
        GlobalEvents.instance().SIGNAL_TOUCHIFY_CONFIG_UPDATED.disconnect(self.onConfigUpdated)
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