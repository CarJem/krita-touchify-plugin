
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ..buttons.ToolshelfButtonBar import ToolshelfButtonBar
from ....config import ConfigManager
from .ToolshelfPagePanel import ToolshelfPagePanel
from ....cfg.CfgToolshelf import CfgToolboxPanel
from .... import stylesheet

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..ToolshelfContainer import ToolshelfContainer

class ToolshelfPageMain(ToolshelfPagePanel):



    def __init__(self, parent: "ToolshelfContainer", isPrimaryPanel: bool):

        self.dockerWidgets: dict = {}
        
        self.isPrimaryPanel = isPrimaryPanel

        if self.isPrimaryPanel: 
            self.rootCfg = ConfigManager.instance().getJSON().toolshelf_main
        else: 
            self.rootCfg = ConfigManager.instance().getJSON().toolshelf_alt


        pageCfg = CfgToolboxPanel()
        pageCfg.actionHeight = self.rootCfg.actionHeight
        pageCfg.quick_actions = self.rootCfg.actions
        pageCfg.additional_dockers = self.rootCfg.dockers

        super(ToolshelfPageMain, self).__init__(parent, 'MAIN', pageCfg)
        
        self.splitter.setAutoFillBackground(False)

        self.dockerBtns = ToolshelfButtonBar(self.rootCfg.dockerButtonHeight, self)
        self.shelfLayout.insertWidget(0, self.dockerBtns)    
    
    def addDockerButton(self, properties, onClick, title):
        self.dockerBtns.addButton(properties, onClick, title)

    def loadPage(self):
        for host_id in self.dockerWidgets:
            self.dockerWidgets[host_id].loadWidget(True)

    def updateStyleSheet(self):
        self.dockerBtns.setStyleSheet(stylesheet.nu_toolshelf_button_style)
        super().updateStyleSheet()
    

    