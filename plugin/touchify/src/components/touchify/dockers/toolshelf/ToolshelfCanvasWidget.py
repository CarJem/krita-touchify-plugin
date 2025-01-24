from krita import *
from PyQt5.QtWidgets import *

from krita import *

from touchify.src.global_events import TouchifyEvents
from touchify.src.settings import *
from touchify.src.variables import *
from touchify.src.features.docker_manager import *
from touchify.src.components.touchify.dockers.toolshelf.ToolshelfWidget import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.window import TouchifyWindow



 
class ToolshelfCanvasWidget(QDockWidget):

    resizeByDefaultRequested=pyqtSignal()

    def __init__(self, parent: QWidget, panel_index: int, app_engine: "TouchifyWindow"):
        super().__init__(parent)
        self.setWindowTitle("Touchify Toolshelf")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.PanelIndex = panel_index
        self.docker_manager = app_engine.docker_management
        self.actions_manager = app_engine.action_management
        self.canvas_manager = app_engine.canvas_management

        stylesheet = f"""QScrollArea {{ background: transparent; }}
        QScrollArea > QWidget > ToolshelfContainer {{ background: transparent; }}
        """
        self.previous_state: ToolshelfWidget.PreviousState = ToolshelfWidget.PreviousState()
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setMouseTracking(True)
        self.scrollArea.setContentsMargins(0,0,0,0)
        self.scrollArea.setViewportMargins(0,0,0,0)
        self.scrollArea.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setStyleSheet(stylesheet)
        self.setWidget(self.scrollArea)
        self.onLoaded()

        TouchifyEvents.instance().SIGNAL_TOUCHIFY_CONFIG_UPDATED.connect(self.onConfigUpdated)
        TouchifyEvents.instance().SIGNAL_TOOLSHELF_PRESET_CHANGED.connect(self.onPresetChanged)

    def closeEvent(self, event):
        TouchifyEvents.instance().SIGNAL_TOUCHIFY_CONFIG_UPDATED.disconnect(self.onConfigUpdated)
        TouchifyEvents.instance().SIGNAL_TOOLSHELF_PRESET_CHANGED.disconnect(self.onPresetChanged)
        super().closeEvent(event)

    def onToolshelfPageChanged(self):
        pass

    def onToolshelfResize(self):
        pass

    def onToolshelfChanged(self):
        pass

    def onResizeByDefaultRequested(self):
        self.resizeByDefaultRequested.emit()
    
    def onLoaded(self):              
        self.mainWidget = ToolshelfWidget(self, TouchifySettings.instance().getActiveToolshelf(self.PanelIndex), self.PanelIndex)
        self.mainWidget.resizeByDefaultRequested.connect(self.onResizeByDefaultRequested)
        self.mainWidget.toolshelfPageChanged.connect(self.onToolshelfPageChanged)
        self.mainWidget.toolshelfResized.connect(self.onToolshelfResize)
        self.mainWidget.toolshelfChanged.connect(self.onToolshelfChanged)
        self.scrollArea.setWidget(self.mainWidget)
        self.mainWidget.restorePreviousState(self.previous_state)

    def onUnload(self):
        if self.mainWidget:
            self.previous_state = self.mainWidget.backupPreviousState()
            self.mainWidget.toolshelfPageChanged.disconnect(self.onToolshelfPageChanged)
            self.mainWidget.toolshelfResized.disconnect(self.onToolshelfResize)
            self.mainWidget.toolshelfChanged.disconnect(self.onToolshelfChanged)
            self.mainWidget.shutdownWidget()
            self.scrollArea.takeWidget()
            self.mainWidget.deleteLater()
            self.mainWidget = None

    def onPresetChanged(self, index: int):
        if self.PanelIndex == index:
            self.onConfigUpdated()

    def onConfigUpdated(self):
        self.onUnload()
        self.onLoaded()