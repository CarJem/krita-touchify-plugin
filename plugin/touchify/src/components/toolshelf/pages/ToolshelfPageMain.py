from typing import Dict
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ..buttons.ToolshelfButtonBar import ToolshelfButtonBar

from ....config import ConfigManager

from .ToolshelfPagePanel import ToolshelfPagePanel

from ..buttons.ToolshelfQuickActions import ToolshelfQuickActions

from .ToolshelfPage import ToolshelfPage

from ....cfg.CfgToolshelf import CfgToolboxPanel
from ....cfg.CfgToolshelf import CfgToolboxPanelDocker

from ....docker_manager import DockerManager
from ..ToolshelfDockerHost import ToolshelfDockerHost
from .... import stylesheet
from ....variables import KRITA_ID_DOCKER_SHAREDTOOLDOCKER

class ToolshelfPageMain(ToolshelfPagePanel):

    dockerWidgets: dict = {}

    def __init__(self, parent: QStackedWidget=None, isPrimaryPanel: bool = False):
        
        self.isPrimaryPanel = isPrimaryPanel

        if self.isPrimaryPanel: 
            self.rootCfg = ConfigManager.instance().getJSON().toolshelf_main
        else: 
            self.rootCfg = ConfigManager.instance().getJSON().toolshelf_alt


        self.cfg = CfgToolboxPanel()
        self.cfg.actionHeight = self.rootCfg.actionHeight
        self.cfg.quick_actions = self.rootCfg.actions
        
        if self.isPrimaryPanel:
            toolOptionsDocker = CfgToolboxPanelDocker()
            toolOptionsDocker.id = KRITA_ID_DOCKER_SHAREDTOOLDOCKER
            toolOptionsDocker.unloaded_visibility = "hidden"
            self.cfg.additional_dockers.append(toolOptionsDocker)

        super(ToolshelfPageMain, self).__init__(parent, 'MAIN', self.cfg)

        self.dockerBtns = ToolshelfButtonBar(self.rootCfg.dockerButtonHeight, self)
        self.shelfLayout.insertWidget(0, self.dockerBtns)    
    
    def addDockerButton(self, properties, onClick, title):
        self.dockerBtns.addButton(properties, onClick, title)

    def updateStyleSheet(self):
        self.dockerBtns.setStyleSheet(stylesheet.nu_tool_options_style)
        super().updateStyleSheet()
    

    