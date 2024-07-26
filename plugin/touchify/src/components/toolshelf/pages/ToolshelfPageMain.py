
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
        pageCfg.section_show_tabs = True

        super(ToolshelfPageMain, self).__init__(parent, 'MAIN', pageCfg)
        
        self.splitter.setAutoFillBackground(False)
           

    def loadPage(self):
        for host_id in self.dockerWidgets:
            self.dockerWidgets[host_id].loadWidget(True)

    def updateStyleSheet(self):
        super().updateStyleSheet()
    

    