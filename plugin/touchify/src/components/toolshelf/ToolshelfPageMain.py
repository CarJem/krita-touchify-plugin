


from .ToolshelfQuickActions import ToolshelfQuickActions
from .ToolshelfPageHost import ToolshelfPageHost
from ...cfg.CfgToolshelf import CfgToolboxAction
from ...variables import *
from ...cfg.CfgToolshelf import CfgToolboxAction
from krita import *

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import QMargins
from ...config import *
from .ToolshelfButtonBar import ToolshelfButtonBar
from .ToolshelfDockerHost import ToolshelfDockerHost
from ... import stylesheet

class ToolshelfPageMain(ToolshelfPageHost):
    _lastSharedToolOptionsState = False

    def __init__(self, parent: QStackedWidget=None, enableToolOptions: bool = False):
        super(ToolshelfPageMain, self).__init__(parent, 'MAIN')
        
        self.isUnloading = False
        self.enableToolOptions = enableToolOptions
        self._lastSharedToolOptionsState = self.getSharedToolOptionState()

        if self.enableToolOptions: 
            self.cfg = ConfigManager.instance().getJSON().toolshelf_main
        else: 
            self.cfg = ConfigManager.instance().getJSON().toolshelf_alt


        self.dockerBtns = ToolshelfButtonBar(self.cfg.dockerButtonHeight, self)
        self.shelfLayout.addWidget(self.dockerBtns)    

        self.quickActions = ToolshelfQuickActions(self.cfg.actions, self.cfg.actionHeight, self)
        self.shelfLayout.addWidget(self.quickActions)

        self.toolSettingsDocker = ToolshelfDockerHost(self, KRITA_ID_DOCKER_SHAREDTOOLDOCKER)
        self.toolSettingsDocker.dockMode = False
        self.shelfLayout.addWidget(self.toolSettingsDocker)

    def sizeHint(self):
        size_qa = super().sizeHint()

        width_padding = 20
        height_padding = 20

        container_width = size_qa.width() + width_padding
        container_height = size_qa.height() + height_padding

        return QSize(container_width, container_height)

    def getSharedToolOptionState(self):
        if InternalConfig.instance().nuOptions_SharedToolDocker and self.enableToolOptions:
            return True
        else: return False

    def onKritaConfigUpdate(self):       
        _sharedToolOptionsState = self.getSharedToolOptionState()
        if self._lastSharedToolOptionsState != _sharedToolOptionsState:
            self._lastSharedToolOptionsState = _sharedToolOptionsState
            if self.toolshelfRoot.currentIndex() == 0:
                if _sharedToolOptionsState:
                    self.loadDocker()
                else:
                    self.unloadDocker()

    def updateStyleSheet(self):
        self.dockerBtns.setStyleSheet(stylesheet.nu_tool_options_style)
        self.quickActions.setStyleSheet(stylesheet.nu_tool_options_style)

    def addDockerButton(self, properties, onClick, title):
        self.dockerBtns.addButton(properties, onClick, title)

    def initQuickActions(self):
        actions = self.cfg.actions
        for entry in actions:
            act: CfgToolboxAction = entry
            if act.isEnabled:
                action = Krita.instance().action(act.id)
                if action:
                    self.quickActions.addButton(
                        act,
                        action.trigger,
                        action.toolTip(),
                        action.isCheckable()
                        )

                    if action.isCheckable():
                        btn = self.quickActions.button(act.id)
                        btn.setChecked(action.isChecked())

    def loadDockers(self):
        if self._lastSharedToolOptionsState:
            self.toolSettingsDocker.loadDocker()
            self.toolSettingsDocker.setHidden(False)
        
    def unloadDockers(self):
        self.toolSettingsDocker.unloadDocker()
        self.toolSettingsDocker.setHidden(True)