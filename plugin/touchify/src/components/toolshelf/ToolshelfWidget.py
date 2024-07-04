from ast import Call
from PyQt5.QtWidgets import QSizePolicy, QStackedWidget
import uuid
from krita import *
from PyQt5.QtWidgets import *

from krita import *
from touchify.src.components.toolshelf.buttons.ToolboxPanelHeader import ToolboxPanelHeader
from .buttons.ToolshelfQuickActions import ToolshelfQuickActions
from .pages.ToolshelfPagePanel import ToolshelfPagePanel

from ...config import *
from ...variables import *
from ...docker_manager import *
from .ToolshelfContainer import *

from ...cfg.CfgToolshelf import CfgToolboxPanel
from .pages.ToolshelfPageMain import ToolshelfPageMain
from .pages.ToolshelfPage import ToolshelfPage

 
class ToolshelfWidget(QDockWidget):

    sizeChanged = pyqtSignal()

    def __init__(self, isPrimaryPanel: bool, docker_manager: DockerManager):
        super().__init__()
        self.setWindowTitle("Touchify Toolshelf")
        self.isPrimaryPanel = isPrimaryPanel
        self.docker_manager = docker_manager

        stylesheet = f"""QScrollArea {{ background: transparent; }}
        QScrollArea > QWidget > ToolshelfContainer {{ background: transparent; }}
        """

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setStyleSheet(stylesheet)
        self.setWidget(self.scrollArea)
        self.onLoaded()


    def hasPanelStack(self):
        if hasattr(self, "panelStack"):
            if self.panelStack:
                return True
        return False

    def updateStyleSheet(self):
        if self.hasPanelStack():
            self.panelStack.updateStyleSheet()

    def onKritaConfigUpdate(self):
        if self.hasPanelStack():
            self.panelStack.onKritaConfigUpdate()

    def onSizeChanged(self):
        self.sizeChanged.emit()
    
    def onLoaded(self):              
        self.panelStack = ToolshelfContainer(self, self.isPrimaryPanel)
        self.panelStack.updateStyleSheet()
        self.scrollArea.setWidget(self.panelStack)

    def onUnload(self):
        self.panelStack.shutdownWidget()
        self.scrollArea.takeWidget()
        self.panelStack.deleteLater()
        self.panelStack = None

    def onConfigUpdated(self):
        self.onUnload()
        self.onLoaded()