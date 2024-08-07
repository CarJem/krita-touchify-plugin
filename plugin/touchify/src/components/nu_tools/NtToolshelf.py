from PyQt5.QtWidgets import QMdiArea, QDockWidget
from PyQt5.QtCore import QObject, QEvent, QPoint

from ...ext.KritaSettings import KritaSettings

from ...docker_manager import DockerManager
from ...action_manager import ActionManager

from .NtAdjustToSubwindowFilter import NtAdjustToSubwindowFilter
from ...ext.extensions_krita import KritaExtensions
from ...settings.TouchifySettings import TouchifySettings
from ... import stylesheet
from .NtWidgetPad import NtWidgetPad
from krita import *
from ...variables import *
from ..touchify.toolshelf.ToolshelfWidget import ToolshelfWidget

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .NtCanvas import NtCanvas

class NtToolshelf(object):

    def __init__(self, canvas: "NtCanvas", window: Window, alignment: str, isPrimaryPanel: bool, docker_manager: DockerManager, actions_manager: ActionManager):
        self.qWin = window.qwindow()
        self.mdiArea = self.qWin.findChild(QMdiArea)
        self.canvas = canvas
        
        panel_index = 0 if isPrimaryPanel else 1
        self.toolshelf = ToolshelfWidget(panel_index, docker_manager, actions_manager)

        # Create "pad"
        self.pad = NtWidgetPad(self.mdiArea)
        self.pad.setObjectName("toolshelfPad")
        self.pad.setViewAlignment(alignment)
        self.pad.borrowDocker(self.toolshelf)

        # Create and install event filter
        self.adjustFilter = NtAdjustToSubwindowFilter(self.mdiArea)
        self.adjustFilter.setTargetWidget(self)
        self.mdiArea.subWindowActivated.connect(self.onSubWindowActivated)
        self.qWin.installEventFilter(self.adjustFilter)
        self.toolshelf.installEventFilter(self.adjustFilter)
        self.toolshelf.sizeChanged.connect(self.onSizeChanged)

    def onSizeChanged(self):
        self.canvas.updateCanvas()

    def onSubWindowActivated(self, subWin):
        if subWin:
            subWin.installEventFilter(self.adjustFilter)
            self.canvas.updateCanvas()
            self.updateStyleSheet()
    
    def onConfigUpdate(self):
        pass

    def onKritaConfigUpdate(self):
        pass

    def updateStyleSheet(self):
        self.toolshelf.updateStyleSheet()
        return
    
    def close(self):
        self.toolshelf.sizeChanged.disconnect(self.onSizeChanged)
        self.mdiArea.subWindowActivated.disconnect(self.onSubWindowActivated)
        self.toolshelf.removeEventFilter(self.adjustFilter)
        self.qWin.removeEventFilter(self.adjustFilter)
        self.toolshelf.onUnload()
        self.pad.widget = None
        self.pad.widgetDocker = None
        return self.pad.close()

