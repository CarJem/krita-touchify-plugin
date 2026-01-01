
from jemlib.alib_vaporjem import Logger
from krita import DockWidget
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from typing import TYPE_CHECKING


from jemlib.api_touchify.env import *
from touchify.src.config.toolshelf.ToolshelfArea import ToolshelfArea
from touchify.src.config.toolshelf.ToolshelfAreaSettings import ToolshelfAreaSettings
from jemlib.managers.GlobalEvents import GlobalEvents

if TYPE_CHECKING:
    from ...PluginWindow import TouchifyWindow
    from touchify.src.PluginManagers import TouchifyManagers

from touchify.src.components.toolshelf.ShelfWidget import ShelfWidget



TIMER_INTERVAL = 10

class ToolshelfDockerWidget(DockWidget):

    DOCKER_TITLE=f"{TouchifyEnv.Title.CORE_DOCKERS_PREFIX} Toolshelf"
    CLONE_DOCKER_TITLE=f"{TouchifyEnv.Title.CLONE_DOCKERS_PREFIX}  Toolshelf"

    resizeByDefaultRequested=pyqtSignal()

    def __init__(self, index: int = 0): 
        super().__init__()
        self.app_window: "TouchifyWindow" = None
        self.managers: "TouchifyManagers" = None
        self.mainWidget: ShelfWidget = None
        
        self._originalSizePolicy = self.sizePolicy()
        self.sizeManagementType = ToolshelfAreaSettings.ResizeStyle.Default


        
        if index == 0:
            self.setWindowTitle(ToolshelfDockerWidget.DOCKER_TITLE)
            self.PanelIndex = 0
        elif index != -1:
            self.PanelIndex = index
            self.setWindowTitle(f"{ToolshelfDockerWidget.CLONE_DOCKER_TITLE} (Ext. {index})")
        
        GlobalEvents().SIGNAL_TOOLSHELF_PRESET_UPDATED.connect(self.onPresetUpdated)
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
            if self.sizeManagementType == ToolshelfAreaSettings.ResizeStyle.Minimum:
                self.resize(self.mainWidget.minimumSize().grownBy(margins))
            elif self.sizeManagementType == ToolshelfAreaSettings.ResizeStyle.AdjustSize:
                self.adjustSize()
            elif self.sizeManagementType == ToolshelfAreaSettings.ResizeStyle.SizeHint:
                self.resize(self.mainWidget.sizeHint().grownBy(margins))
            elif self.sizeManagementType == ToolshelfAreaSettings.ResizeStyle.SizeHintMinimum:
                self.resize(self.mainWidget.minimumSizeHint().grownBy(margins))
        else:
            pass


    def onShelfIndexChanged(self):
        pass

    def shelfReloadEvent(self, state: ToolshelfArea):
        Logger.debug('Touchify', 'ToolshelfDockerWidget', f'shelfReloadEvent: start')
        if state.options.resize_style == ToolshelfAreaSettings.ResizeStyle.Minimum:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.sizeManagementType = ToolshelfAreaSettings.ResizeStyle.Minimum
        elif state.options.resize_style == ToolshelfAreaSettings.ResizeStyle.AdjustSize:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.sizeManagementType = ToolshelfAreaSettings.ResizeStyle.AdjustSize
        elif state.options.resize_style == ToolshelfAreaSettings.ResizeStyle.SizeHintMinimum:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.sizeManagementType = ToolshelfAreaSettings.ResizeStyle.SizeHintMinimum
        elif state.options.resize_style == ToolshelfAreaSettings.ResizeStyle.SizeHint:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.sizeManagementType = ToolshelfAreaSettings.ResizeStyle.SizeHint
        else:
            self.setSizePolicy(self._originalSizePolicy)
            self.sizeManagementType = ToolshelfAreaSettings.ResizeStyle.Default
        Logger.debug('Touchify', 'ToolshelfDockerWidget', f'shelfReloadEvent: end')

    def onTouchifyReload(self):
        Logger.debug('Touchify', 'ToolshelfDockerWidget', f'onTouchifyReload')
        if self.mainWidget: 
            QTimer.singleShot(100, self.mainWidget.onConfigUpdated)

    def onPresetUpdated(self, registry_index: int = 0):
        Logger.debug('Touchify', 'ToolshelfDockerWidget', f'onPresetUpdated')
        if registry_index == 0 or registry_index == self.PanelIndex:
            self.onTouchifyReload() 

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

    def onThemeChanged(self):
        if self.mainWidget: 
            QTimer.singleShot(100, self.mainWidget.onThemeChanged)


def DynamicToolshelfDockerWidget(value: int):
    class DynamicToolshelfDockerWidget(ToolshelfDockerWidget):
        def __init__(self):
            super().__init__(value)
    
    return DynamicToolshelfDockerWidget