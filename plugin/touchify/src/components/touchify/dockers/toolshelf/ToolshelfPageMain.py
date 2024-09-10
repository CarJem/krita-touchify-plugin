
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from .....resources import ResourceManager
from .....settings.TouchifyConfig import TouchifyConfig
from .ToolshelfPage import ToolshelfPage
from .....cfg.toolshelf.CfgToolshelfPanel import CfgToolshelfPanel
from .....cfg.toolshelf.CfgToolshelf import CfgToolshelf
from .....stylesheet import Stylesheet

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfPageStack import ToolshelfPageStack

class ToolshelfPageMain(ToolshelfPage):
    def __init__(self, parent: "ToolshelfPageStack", cfg: CfgToolshelf):

        self.dockerWidgets: dict = {}
        

        self.rootCfg = cfg
        pageCfg = CfgToolshelfPanel()
        pageCfg.tab_type = self.rootCfg.tab_type
        pageCfg.actionHeight = self.rootCfg.actionHeight
        pageCfg.actions = self.rootCfg.actions
        pageCfg.sections = self.rootCfg.sections

        super(ToolshelfPageMain, self).__init__(parent, 'ROOT', pageCfg)
        
        self.splitter.setAutoFillBackground(False)
           

    def loadPage(self):
        for host_id in self.dockerWidgets:
            self.dockerWidgets[host_id].loadWidget(True)
    

    