


from ...cfg.CfgToolshelf import CfgToolboxAction
from ...variables import *
from ...cfg.CfgToolshelf import CfgToolboxAction
from krita import *

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import QMargins
from ...config import *
from .ToolshelfButtonBar import ToolshelfButtonBar
from .ToolshelfPanelDocker import ToolshelfPanelDocker
from ... import stylesheet

class ToolshelfMainPage(QWidget):
    _margins = QMargins(1, 1, 1, 1)


    _lastSharedToolOptionsState = False

    def __init__(self, parent: QStackedWidget=None, enableToolOptions: bool = False):
        self.isUnloading = False
        self.enableToolOptions = enableToolOptions
        self.toolshelfRoot: QStackedWidget = parent
        self.cfg = self.getCfg(enableToolOptions)


        super(ToolshelfMainPage, self).__init__(parent)
        self.setContentsMargins(0,0,0,0)
        self._lastSharedToolOptionsState = self.getSharedToolOptionState()

        self.ourLayout = QVBoxLayout()

        self.ourLayout.setContentsMargins(self._margins)
        self.ourLayout.setSpacing(1)

        self.dockerBtns = ToolshelfButtonBar(self.cfg.dockerButtonHeight)
        self.ourLayout.addWidget(self.dockerBtns)    

        self.quickActions = ToolshelfButtonBar(self.cfg.actionHeight)
        self.initQuickActions()
        self.ourLayout.addWidget(self.quickActions)


        self.emptySpace = QWidget()
        self.emptySpace.setFixedHeight(4)
        self.ourLayout.addWidget(self.emptySpace)

        self.toolSettingsDocker = ToolshelfPanelDocker(self, KRITA_ID_DOCKER_SHAREDTOOLDOCKER)
        self.autoFitScrollArea = True
        self.ourLayout.addWidget(self.toolSettingsDocker)
        self.setLayout(self.ourLayout)

    def getCfg(self, enableToolOptions: bool = False):
        cfg = ConfigManager.instance().getJSON()
        if enableToolOptions: return cfg.toolshelf_main
        else: return cfg.toolshelf_alt

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

    def loadDocker(self):
        if self._lastSharedToolOptionsState:
            self.toolSettingsDocker.loadDocker()
        
    def unloadDocker(self):
        self.toolSettingsDocker.unloadDocker()