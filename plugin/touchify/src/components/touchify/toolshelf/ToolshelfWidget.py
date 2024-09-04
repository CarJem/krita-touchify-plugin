from PyQt5.QtWidgets import QSizePolicy, QStackedWidget
import uuid
from krita import *
from PyQt5.QtWidgets import *

from krita import *

from ....settings.TouchifyConfig import *
from ....variables import *
from ....docker_manager import *
from .ToolshelfContainer import *

from ....cfg.toolshelf.CfgToolshelf import CfgToolshelfPanel
from .ToolshelfPageMain import ToolshelfPageMain
from ....action_manager import ActionManager

 
class ToolshelfWidget(QDockWidget):

    sizeChanged = pyqtSignal()

    def __init__(self, panel_index: int, docker_manager: DockerManager, actions_manager: ActionManager):
        super().__init__()
        self.setWindowTitle("Touchify Toolshelf")
        self.PanelIndex = panel_index
        self.docker_manager = docker_manager
        self.actions_manager = actions_manager

        stylesheet = f"""QScrollArea {{ background: transparent; }}
        QScrollArea > QWidget > ToolshelfContainer {{ background: transparent; }}
        """
        self._last_panel_id: str | None = None
        self._last_pinned: bool = False
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
        self.panelStack = ToolshelfContainer(self, self.PanelIndex)
        self.panelStack.updateStyleSheet()
        self.scrollArea.setWidget(self.panelStack)

        if self._last_pinned:
            self.panelStack.setPinned(self._last_pinned)

        if self.panelStack.panel(self._last_panel_id) != None:
            self.panelStack.changePanel(self._last_panel_id)

    def onUnload(self):
        self._last_panel_id = self.panelStack._current_panel_id
        self._last_pinned = self.panelStack._pinned
        self.panelStack.shutdownWidget()
        self.scrollArea.takeWidget()
        self.panelStack.deleteLater()
        self.panelStack = None

    def onConfigUpdated(self):
        self.onUnload()
        self.onLoaded()