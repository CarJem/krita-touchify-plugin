

from ...variables import *
from ...cfg.CfgToolboxAction import CfgToolboxAction
from krita import *

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import QMargins
from ...config import *
from .ToolboxButtonBar import ToolboxButtonBar
from .ToolboxPanelDocker import ToolboxPanelDocker

class ToolboxMainPage(QWidget):
    _margins = QMargins(4, 4, 4, 4)


    _lastSharedToolOptionsState = False

    def __init__(self, parent=None):
        super(ToolboxMainPage, self).__init__(parent)
        self._lastSharedToolOptionsState = self.getSharedToolOptionState()
        configManager: ConfigManager = ConfigManager.instance()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(self._margins)

        self.dockerBtns = ToolboxButtonBar(configManager.getJSON().kb_dockerButtonHeight)
        self.layout().addWidget(self.dockerBtns)    

        self.quickActions = ToolboxButtonBar(configManager.getJSON().kb_actionHeight)
        self.initQuickActions()
        self.layout().addWidget(self.quickActions)

        self.toolSettingsDocker = ToolboxPanelDocker(self, KRITA_ID_DOCKER_SHAREDTOOLDOCKER)
        self.autoFitScrollArea = True
        self.layout().addWidget(self.toolSettingsDocker)


        if self._lastSharedToolOptionsState:
            self.loadDocker()


    def getSharedToolOptionState(self):
        if KritaSettings.readSetting(TOUCHIFY_ID_OPTIONSROOT_MAIN, TOUCHIFY_ID_OPTIONS_TOOLBOX_USE_SHAREDTOOLDOCKER, "true") == "true":
            return True
        else: return False


    def onKritaConfigUpdate(self):
        _sharedToolOptionsState = self.getSharedToolOptionState()
        if self._lastSharedToolOptionsState != _sharedToolOptionsState:
            if _sharedToolOptionsState:
                self.loadDocker()
            else:
                self.unloadDocker()
            self._lastSharedToolOptionsState = _sharedToolOptionsState
        

    def addDockerButton(self, properties, onClick, title):
        self.dockerBtns.addButton(properties, onClick, title)

    def initQuickActions(self):
        configManager: ConfigManager = ConfigManager.instance()
        for entry in configManager.getJSON().kb_actions:
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
        self.toolSettingsDocker.loadDocker()
        
    def unloadDocker(self):
        self.toolSettingsDocker.unloadDocker()