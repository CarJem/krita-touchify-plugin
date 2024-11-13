from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from touchify.src.cfg.toolshelf.CfgToolshelf import CfgToolshelfPanel
from touchify.src.components.touchify.dockers.toolshelf.ToolshelfPanel import ToolshelfPanel


from krita import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfPageStack import ToolshelfPageStack


class ToolshelfPage(QWidget):
    
    def __init__(self, parent: "ToolshelfPageStack", ID: any, data: CfgToolshelfPanel):
        super(ToolshelfPage, self).__init__(parent)
        self.setAutoFillBackground(True)
        self.setLayout(QVBoxLayout(self))
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0,0,0,0)

        self.toolshelf: "ToolshelfPageStack" = parent
        self.docker_manager = self.toolshelf.rootWidget.parent_docker.docker_manager
        self.actions_manager = self.toolshelf.rootWidget.parent_docker.actions_manager

        self.panel: ToolshelfPanel = ToolshelfPanel(self, parent, data)        
        self.layout().addWidget(self.panel)

        self.updateStyleSheet()

    def sizeHint(self):
        return self.panel.sizeHint()
    
    def activate(self):
        self.toolshelf.changePanel(self.ID)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)

    def unloadPage(self):
        self.panel.pageUnloadSignal.emit()

    def loadPage(self):
        self.panel.pageLoadedSignal.emit()
    
    def updateStyleSheet(self):
        self.panel.updateStyleSheet()