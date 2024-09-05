
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ....resources import ResourceManager
from .ToolshelfPageButtons import ToolshelfPageButtons
from ....settings.TouchifyConfig import TouchifyConfig
from .ToolshelfPage import ToolshelfPage
from ....cfg.toolshelf.CfgToolshelf import CfgToolshelfPanel
from ....stylesheet import Stylesheet

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfContainer import ToolshelfContainer

class ToolshelfPageMain(ToolshelfPage):
    def __init__(self, parent: "ToolshelfContainer", panel_index : int):

        self.dockerWidgets: dict = {}
        
        self.PanelIndex = panel_index

        if self.PanelIndex == 0: 
            self.rootCfg = TouchifyConfig.instance().getConfig().toolshelf_main.getActive()
        elif self.PanelIndex == 1: 
            self.rootCfg = TouchifyConfig.instance().getConfig().toolshelf_alt.getActive()
        elif self.PanelIndex == 2: 
            self.rootCfg = TouchifyConfig.instance().getConfig().toolshelf_docker.getActive()
        else:
            self.rootCfg = None


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
    

    