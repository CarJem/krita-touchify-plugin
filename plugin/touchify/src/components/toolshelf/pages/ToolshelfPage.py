
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ....cfg.CfgToolshelf import CfgToolboxPanel
from ....cfg.CfgToolshelf import CfgToolboxPanelDocker
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..ToolshelfContainer import ToolshelfContainer

class ToolshelfPage(QWidget):


    def __init__(self, parent: "ToolshelfContainer", ID: any):
        super(ToolshelfPage, self).__init__(parent)

        self.toolshelf: "ToolshelfContainer" = parent
        self.ID = ID

        self.shelfLayout = QVBoxLayout()
        self.shelfLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.shelfLayout.setContentsMargins(0, 0, 0, 0)
        self.shelfLayout.setSpacing(1)
        self.setLayout(self.shelfLayout)

    def unloadPage(self):
        pass

    def loadPage(self):
        pass

    def activate(self):
        self.parentWidget().changePanel(self.ID)

    def setSizeHint(self, size):
        pass

    def sizeHint(self):
        return super().sizeHint()

    

    