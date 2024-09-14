from PyQt5.QtWidgets import QSizePolicy, QStackedWidget
import uuid
from krita import *
from PyQt5.QtWidgets import *

from krita import *

from .....settings.TouchifyConfig import *
from .....variables import *
from .....docker_manager import *
from .ToolshelfWidget import *

from .....cfg.toolshelf.CfgToolshelfPanel import CfgToolshelfPanel
from .....cfg.toolshelf.CfgToolshelf import CfgToolshelf

from .ToolshelfPageMain import ToolshelfPageMain
from .....action_manager import ActionManager

 
class ToolshelfDockWidget(QDockWidget):

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
            if self.mainWidget:
                return True
        return False

    def onKritaConfigUpdate(self):
        pass

    def onSizeChanged(self):
        self.sizeChanged.emit()
    
    def onLoaded(self):              
        self.mainWidget = ToolshelfWidget(self, self.PanelIndex)
        self.scrollArea.setWidget(self.mainWidget)
        self.mainWidget.restorePreviousState(self._last_pinned, self._last_panel_id)

    def onUnload(self):
        self._last_pinned, self._last_panel_id = self.mainWidget.backupPreviousState()
        self.mainWidget.shutdownWidget()
        self.scrollArea.takeWidget()
        self.mainWidget.deleteLater()
        self.mainWidget = None

    def onConfigUpdated(self):
        self.onUnload()
        self.onLoaded()