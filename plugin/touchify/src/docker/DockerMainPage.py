from typing import TYPE_CHECKING

from ..cfg.KB_Actions import KB_Actions
if TYPE_CHECKING:
    from ..ext.PyKrita import *
else:
    from krita import *

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import QMargins
from ..config import *
from .DockerButtonBar import DockerButtonBar
from ..borrow_manager import KBBorrowManager
from .DockerPanelHost import DockerPanelHost
from ..components.nu_tools.nt_logic.Nt_ScrollAreaContainer import Nt_ScrollAreaContainer

class DockerMainPage(QWidget):
    _margins = QMargins(4, 4, 4, 4)

    def __init__(self, parent=None):
        super(DockerMainPage, self).__init__(parent)
        configManager: ConfigManager = ConfigManager.instance()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(self._margins)

        self.dockerBtns = DockerButtonBar(configManager.getJSON().kb_dockerButtonHeight)
        self.layout().addWidget(self.dockerBtns)    

        self.quickActions = DockerButtonBar(configManager.getJSON().kb_actionHeight)
        self.initQuickActions()
        self.layout().addWidget(self.quickActions)

        self.toolSettingsDocker = DockerPanelHost('sharedtooldocker')
        self.toolSettingsDocker.toolsHack = True
        self.toolSettingsDocker.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.layout().addWidget(self.toolSettingsDocker)

        self.loadDockers()

    def addDockerButton(self, properties, onClick, title):
        self.dockerBtns.addButton(properties, onClick, title)

    def initQuickActions(self):
        configManager: ConfigManager = ConfigManager.instance()
        for entry in configManager.getJSON().kb_actions:
            act: KB_Actions = entry
            if act.isEnabled:
                action = Krita.instance().action(act.id)
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
        self.toolSettingsDocker.loadDocker()
        
    def unloadDockers(self):
        self.toolSettingsDocker.unloadDocker()