from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.cfg.toolshelf.ToolshelfData import ToolshelfDataPage
from touchify.src.components.touchify.dockers.toolshelf.Panel import Panel

from krita import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .PageStack import PageStack


class Page(QWidget):
    
    def __init__(self, parent: "PageStack", data: ToolshelfDataPage):
        super(Page, self).__init__(parent)
        self.setAutoFillBackground(True)
        self.setLayout(QVBoxLayout(self))
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0,0,0,0)

        self.ID = data.id

        self.toolshelf: "PageStack" = parent
        self.docker_manager = self.toolshelf.rootWidget.parent_docker.docker_manager
        self.actions_manager = self.toolshelf.rootWidget.parent_docker.actions_manager

        self.panel: Panel = Panel(self, parent, data)        
        self.layout().addWidget(self.panel)

        self.updateStyleSheet()

    def setEditMode(self, value: bool):
        self.panel.setEditMode(value)
    
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