
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ..buttons.ToolshelfButtonBar import ToolshelfButtonBar
from ....config import ConfigManager
from .ToolshelfPage import ToolshelfPage
from ....cfg.CfgToolshelf import CfgToolshelfPanel
from .... import stylesheet

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..ToolshelfContainer import ToolshelfContainer

class ToolshelfPageMain(ToolshelfPage):
    def __init__(self, parent: "ToolshelfContainer", isPrimaryPanel: bool):

        self.dockerWidgets: dict = {}
        
        self.isPrimaryPanel = isPrimaryPanel

        if self.isPrimaryPanel: 
            self.rootCfg = ConfigManager.instance().getJSON().toolshelf_main
        else: 
            self.rootCfg = ConfigManager.instance().getJSON().toolshelf_alt


        pageCfg = CfgToolshelfPanel()
        pageCfg.actionHeight = self.rootCfg.actionHeight
        pageCfg.quick_actions = self.rootCfg.actions
        pageCfg.additional_dockers = self.rootCfg.dockers

        super(ToolshelfPageMain, self).__init__(parent, 'MAIN', pageCfg)
        
        self.splitter.setAutoFillBackground(False)

        self.dockerBtns = ToolshelfButtonBar(self)
        self.dockerBtns.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.shelfLayout.insertWidget(0, self.dockerBtns)    
    
    def addDockerButton(self, properties: CfgToolshelfPanel, onClick, title):
        self.dockerBtns.addCfgButton(properties, onClick, title)
        self.dockerBtns.button(properties.id).setFixedHeight(self.rootCfg.dockerButtonHeight)
        self.dockerBtns.button(properties.id).setMinimumWidth(self.rootCfg.dockerButtonHeight)
        self.dockerBtns.button(properties.id).setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
           

    def loadPage(self):
        for host_id in self.dockerWidgets:
            self.dockerWidgets[host_id].loadWidget(True)

    def updateStyleSheet(self):
        self.dockerBtns.setStyleSheet(stylesheet.nu_toolshelf_button_style)
        super().updateStyleSheet()
    

    