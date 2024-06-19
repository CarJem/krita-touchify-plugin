


from ...variables import *
from ...cfg.CfgToolboxAction import CfgToolboxAction
from krita import *

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import QMargins
from ...config import *
from .ToolshelfButtonBar import ToolshelfButtonBar
from .ToolshelfPanelDocker import ToolshelfPanelDocker

class ToolshelfMainPage(QWidget):
    _margins = QMargins(4, 4, 4, 4)


    _lastSharedToolOptionsState = False

    def __init__(self, parent: QStackedWidget=None, enableToolOptions: bool = False):
        self.isUnloading = False
        self.enableToolOptions = enableToolOptions
        self.toolshelfRoot: QStackedWidget = parent
        super(ToolshelfMainPage, self).__init__(parent)
        self._lastSharedToolOptionsState = self.getSharedToolOptionState()
        configManager: ConfigManager = ConfigManager.instance()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(self._margins)

        self.dockerBtns = ToolshelfButtonBar(configManager.getJSON().kb_dockerButtonHeight)
        self.layout().addWidget(self.dockerBtns)    

        self.quickActions = ToolshelfButtonBar(configManager.getJSON().kb_actionHeight)
        self.initQuickActions()
        self.layout().addWidget(self.quickActions)

        self.toolSettingsDocker = ToolshelfPanelDocker(self, KRITA_ID_DOCKER_SHAREDTOOLDOCKER)
        self.autoFitScrollArea = True
        self.layout().addWidget(self.toolSettingsDocker)


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
        

    def addDockerButton(self, properties, onClick, title):
        self.dockerBtns.addButton(properties, onClick, title)

    def initQuickActions(self):
        cfg = ConfigManager.instance().getJSON()
        actions = cfg.kb_dockers if self.enableToolOptions else cfg.kb_toolbox_dockers
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