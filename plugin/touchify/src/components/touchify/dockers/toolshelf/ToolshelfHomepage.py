
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.components.touchify.dockers.toolshelf.ToolshelfPage import ToolshelfPage
from touchify.src.cfg.toolshelf.CfgToolshelfPanel import CfgToolshelfPanel
from touchify.src.cfg.toolshelf.CfgToolshelf import CfgToolshelf

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfPageStack import ToolshelfPageStack

class ToolshelfHomepage(ToolshelfPage):
    def __init__(self, parent: "ToolshelfPageStack", cfg: CfgToolshelf):

        self.dockerWidgets: dict = {}
        

        self.rootCfg = cfg
        pageCfg = CfgToolshelfPanel()
        pageCfg.tab_type = self.rootCfg.tab_type
        pageCfg.action_height = self.rootCfg.action_height
        pageCfg.actions = self.rootCfg.actions
        pageCfg.sections = self.rootCfg.sections

        super(ToolshelfHomepage, self).__init__(parent, 'ROOT', pageCfg)
        
        self.panel.splitter.setAutoFillBackground(False)
           

    def loadPage(self):
        self.panel.loadPage()
    

    