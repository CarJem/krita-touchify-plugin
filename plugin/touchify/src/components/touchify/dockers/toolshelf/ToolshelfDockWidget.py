from krita import *
from PyQt5.QtWidgets import *

from krita import *

from touchify.src.settings import *
from touchify.src.variables import *
from touchify.src.docker_manager import *
from touchify.src.components.touchify.dockers.toolshelf.ToolshelfWidget import *


from touchify.src.action_manager import ActionManager

 
class ToolshelfDockWidget(QDockWidget):

    updateViewRequested = pyqtSignal()

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

    def requestViewUpdate(self):
        self.updateViewRequested.emit()
    
    def onLoaded(self):              
        self.mainWidget = ToolshelfWidget(self, TouchifyConfig.instance().getActiveToolshelf(self.PanelIndex), self.PanelIndex)
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