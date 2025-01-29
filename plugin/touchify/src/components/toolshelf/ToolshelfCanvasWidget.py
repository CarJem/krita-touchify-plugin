from krita import *
from PyQt5.QtWidgets import *

from krita import *

from touchify.src.managers.shared.events import GlobalEvents
from touchify.src.managers.shared.settings import *
from touchify.__env__ import *
from touchify.src.managers.normal.dockers import *
from touchify.src.components.toolshelf.ToolshelfWidget import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.PluginWindow import TouchifyWindow

 
class ToolshelfCanvasWidget(QDockWidget):

    resizeByDefaultRequested=pyqtSignal()

    def __init__(self, parent: QWidget, panel_index: int, app_engine: "TouchifyWindow"):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.PanelIndex = panel_index
        self.docker_manager = app_engine.mgr_dockers
        self.actions_manager = app_engine.mgr_actions
        self.canvas_manager = app_engine.mgr_canvas

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

        GlobalEvents.instance().SIGNAL_TOUCHIFY_CONFIG_UPDATED.connect(self.onConfigUpdated)
        GlobalEvents.instance().SIGNAL_TOOLSHELF_PRESET_CHANGED.connect(self.onPresetChanged)

    def closeEvent(self, event):
        GlobalEvents.instance().SIGNAL_TOUCHIFY_CONFIG_UPDATED.disconnect(self.onConfigUpdated)
        GlobalEvents.instance().SIGNAL_TOOLSHELF_PRESET_CHANGED.disconnect(self.onPresetChanged)
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
        if not hasattr(self, 'mainWidget'): return
        if not self.mainWidget: return
        
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