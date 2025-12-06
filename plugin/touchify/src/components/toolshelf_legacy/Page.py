from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.config.toolshelf_legacy.ToolshelfData import ToolshelfDataPage
from touchify.src.components.toolshelf_legacy.Panel import Panel

from krita import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .PageStack import PageStack


class Page(QWidget):

    dataLoaded=pyqtSignal()

    panelItemUpdated=pyqtSignal()
    panelItemResized=pyqtSignal()
    
    def __init__(self, parent: "PageStack", data: ToolshelfDataPage):
        super(Page, self).__init__(parent)
        self.setAutoFillBackground(True)
        self.setLayout(QVBoxLayout(self))
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0,0,0,0)

        self.ID = data.id

        self.toolshelf: "PageStack" = parent

        self.panel: Panel = Panel(self, parent, data)     
        self.panel.dataLoaded.connect(self.Data_Recieved)
        self.panel.panelItemUpdated.connect(self.onPanelItemUpdated) 
        self.panel.panelItemResized.connect(self.onPanelItemResized)
        self.layout().addWidget(self.panel)

        self.updateStyleSheet()

    def Data_Load(self):
        self.panel.Data_Load()

    def Data_Recieved(self):
        self.dataLoaded.emit()

    def onPanelItemUpdated(self):
        self.panelItemUpdated.emit()

    def onPanelItemResized(self):
        self.panelItemResized.emit()

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
        pass