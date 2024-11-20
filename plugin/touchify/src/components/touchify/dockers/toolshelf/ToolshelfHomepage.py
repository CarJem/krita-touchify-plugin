
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.components.touchify.dockers.toolshelf.ToolshelfPage import ToolshelfPage
from touchify.src.cfg.toolshelf.CfgToolshelf import CfgToolshelf

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfPageStack import ToolshelfPageStack

class ToolshelfHomepage(ToolshelfPage):
    def __init__(self, parent: "ToolshelfPageStack", cfg: CfgToolshelf):
        self.homepageData = cfg.homepage
        self.homepageData.id = 'ROOT'
        super(ToolshelfHomepage, self).__init__(parent, cfg.homepage)
        self.panel.splitter.setAutoFillBackground(False)
    

    