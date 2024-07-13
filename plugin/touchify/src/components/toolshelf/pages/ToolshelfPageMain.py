
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ....resources import ResourceManager
from ..buttons.ToolshelfButtonBar import ToolshelfButtonBar
from ....settings.TouchifyConfig import TouchifyConfig
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
            self.rootCfg = TouchifyConfig.instance().getJSON().toolshelf_main
        else: 
            self.rootCfg = TouchifyConfig.instance().getJSON().toolshelf_alt


        pageCfg = CfgToolshelfPanel()
        pageCfg.actionHeight = self.rootCfg.actionHeight
        pageCfg.actions = self.rootCfg.actions
        pageCfg.sections = self.rootCfg.sections

        super(ToolshelfPageMain, self).__init__(parent, 'MAIN', pageCfg)
        
        self.splitter.setAutoFillBackground(False)

        self.dockerBtns = ToolshelfButtonBar(self)
        self.dockerBtns.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.shelfLayout.insertWidget(0, self.dockerBtns)    
    
    def addDockerButton(self, properties: CfgToolshelfPanel, onClick, title):
        btn = self.dockerBtns.addButton(properties.id, properties.row, onClick, title, False)
        btn.setIcon(ResourceManager.iconLoader(properties.icon))
        btn.setFixedHeight(self.rootCfg.dockerButtonHeight)
        btn.setMinimumWidth(self.rootCfg.dockerButtonHeight)
        btn.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
           

    def loadPage(self):
        for host_id in self.dockerWidgets:
            self.dockerWidgets[host_id].loadWidget(True)

    def updateStyleSheet(self):
        self.dockerBtns.setStyleSheet(stylesheet.touchify_toolshelf_header_button)
        super().updateStyleSheet()
    

    