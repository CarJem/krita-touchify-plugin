from krita import *
from PyQt5.QtWidgets import *

from krita import *

from touchify.src.settings import *
from touchify.src.variables import *
from touchify.src.docker_manager import *
from touchify.src.components.touchify.dockers.toolshelf.ToolshelfWidget import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.window import TouchifyWindow



 
class ToolshelfCanvasWidget(QDockWidget):

    updateViewRequested = pyqtSignal()

    def __init__(self, panel_index: int, app_engine: "TouchifyWindow"):
        super().__init__()
        self.setWindowTitle("Touchify Toolshelf")
        self.PanelIndex = panel_index
        self.docker_manager = app_engine.docker_management
        self.actions_manager = app_engine.action_management
        self.canvas_manager = app_engine.canvas_management

        stylesheet = f"""QScrollArea {{ background: transparent; }}
        QScrollArea > QWidget > ToolshelfContainer {{ background: transparent; }}
        """
        self.previous_state: ToolshelfWidget.PreviousState = ToolshelfWidget.PreviousState()
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setContentsMargins(0,0,0,0)
        self.scrollArea.setViewportMargins(0,0,0,0)
        self.scrollArea.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setStyleSheet(stylesheet)
        self.setWidget(self.scrollArea)
        self.onLoaded()

    def onKritaConfigUpdate(self):
        pass

    def requestViewUpdate(self):
        self.updateViewRequested.emit()
    
    def onLoaded(self):              
        self.mainWidget = ToolshelfWidget(self, TouchifySettings.instance().getActiveToolshelf(self.PanelIndex), self.PanelIndex)
        self.scrollArea.setWidget(self.mainWidget)
        self.mainWidget.restorePreviousState(self.previous_state)

    def onUnload(self):
        self.previous_state = self.mainWidget.backupPreviousState()
        self.mainWidget.shutdownWidget()
        self.scrollArea.takeWidget()
        self.mainWidget.deleteLater()
        self.mainWidget = None

    def onConfigUpdated(self):
        self.onUnload()
        self.onLoaded()