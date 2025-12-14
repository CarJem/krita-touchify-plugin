
from krita import DockWidget
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from typing import TYPE_CHECKING


from touchify.__env__ import *
from touchify.src.config.toolshelf.ToolshelfContainer import ToolshelfContainer
from touchify.src.config.toolshelf.ToolshelfSettings import ToolshelfSettings
from touchify.src.managers.GlobalEvents import GlobalEvents

if TYPE_CHECKING:
    from ...PluginWindow import TouchifyWindow
    from touchify.src.PluginManagers import TouchifyManagers

from touchify.src.components.toolshelf.ShelfWidget import ShelfWidget



TIMER_INTERVAL = 10

class ToolshelfDockerWidget(DockWidget):

    DOCKER_TITLE=f"{Env.Title.CORE_DOCKERS_PREFIX} Toolshelf"
    CLONE_DOCKER_TITLE=f"{Env.Title.CLONE_DOCKERS_PREFIX}  Toolshelf"

    resizeByDefaultRequested=pyqtSignal()

    def __init__(self, index: int = 0): 
        super().__init__()
        self.app_window: "TouchifyWindow" = None
        self.managers: "TouchifyManagers" = None
        self.mainWidget: ShelfWidget = None
        
        self._originalSizePolicy = self.sizePolicy()
        self.sizeManagementType = ToolshelfSettings.ResizeStyle.Default


        
        if index == 0:
            self.setWindowTitle(ToolshelfDockerWidget.DOCKER_TITLE)
            self.PanelIndex = 0
        elif index != -1:
            self.PanelIndex = index
            self.setWindowTitle(f"{ToolshelfDockerWidget.CLONE_DOCKER_TITLE} (Ext. {index})")

        
        GlobalEvents().SIGNAL_TOUCHIFY_CONFIG_UPDATED.connect(self.onConfigUpdated)
        GlobalEvents().SIGNAL_TOOLSHELF_UPDATED.connect(self.onConfigUpdated)
        self.startTimer(TIMER_INTERVAL)

    def timerEvent(self, a0: QTimerEvent):
        if self.isVisible():
            self.shrinkToFit()
        return super().timerEvent(a0)

    def setup(self, app_window: "TouchifyWindow"):
        self.app_window = app_window
        self.managers = app_window.managers
        self.mainWidget = ShelfWidget(self, self.managers, self.PanelIndex)
        self.mainWidget.sigShelfIndexChanged.connect(self.onShelfIndexChanged)
        self.mainWidget.setTitlebarVisibility(True)
        self.setWidget(self.mainWidget)    

    def getWindowMargins(self):
        border_thickness = 5
        return QMargins(border_thickness, border_thickness + self.titleBarWidget().height(), border_thickness, border_thickness)

    def shrinkToFit(self):
        margins = self.getWindowMargins()
        if self.isFloating():
            if self.sizeManagementType == ToolshelfSettings.ResizeStyle.Minimum:
                self.resize(self.mainWidget.minimumSize().grownBy(margins))
            elif self.sizeManagementType == ToolshelfSettings.ResizeStyle.AdjustSize:
                self.adjustSize()
            elif self.sizeManagementType == ToolshelfSettings.ResizeStyle.SizeHint:
                self.resize(self.mainWidget.sizeHint().grownBy(margins))
            elif self.sizeManagementType == ToolshelfSettings.ResizeStyle.SizeHintMinimum:
                self.resize(self.mainWidget.minimumSizeHint().grownBy(margins))
        else:
            pass


    def onShelfIndexChanged(self):
        pass

    def shelfReloadEvent(self, state: ToolshelfContainer):
        if state.options.resize_style == ToolshelfSettings.ResizeStyle.Minimum:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.sizeManagementType = ToolshelfSettings.ResizeStyle.Minimum
        elif state.options.resize_style == ToolshelfSettings.ResizeStyle.AdjustSize:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.sizeManagementType = ToolshelfSettings.ResizeStyle.AdjustSize
        elif state.options.resize_style == ToolshelfSettings.ResizeStyle.SizeHintMinimum:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.sizeManagementType = ToolshelfSettings.ResizeStyle.SizeHintMinimum
        elif state.options.resize_style == ToolshelfSettings.ResizeStyle.SizeHint:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.sizeManagementType = ToolshelfSettings.ResizeStyle.SizeHint
        else:
            self.setSizePolicy(self._originalSizePolicy)
            self.sizeManagementType = ToolshelfSettings.ResizeStyle.Default

    def onConfigUpdated(self, registry_index: int = -1):
        if registry_index == -1 or registry_index == self.PanelIndex:
            if self.mainWidget: 
                self.mainWidget.onConfigUpdated()

    def resizeEvent(self, a0):
        return super().resizeEvent(a0)
        
    def showEvent(self, event):
        super().showEvent(event)

    def closeEvent(self, event):
        return super().closeEvent(event)

    # notifies when views are added or removed
    # 'pass' means do not do anything
    def canvasChanged(self, canvas):
        pass


def DynamicToolshelfDockerWidget(value: int):
    class DynamicToolshelfDockerWidget(ToolshelfDockerWidget):
        def __init__(self):
            super().__init__(value)
    
    return DynamicToolshelfDockerWidget