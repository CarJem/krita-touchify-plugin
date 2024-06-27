from PyQt5.QtWidgets import QMdiArea, QDockWidget
from PyQt5.QtCore import QObject, QEvent, QPoint

from .Nt_AdjustToSubwindowFilter import Nt_AdjustToSubwindowFilter
from ...ext.extensions import KritaExtensions
from ...config import InternalConfig, KritaSettings
from ... import stylesheet
from .NtWidgetPad import NtWidgetPad
from krita import *
from ...variables import *
from ..toolshelf.ToolshelfWidget import ToolshelfWidget

class NtToolOptions():

    def __init__(self, window: Window, alignment: str, isPrimaryPanel: bool = False):
        self.qWin = window.qwindow()
        self.mdiArea = self.qWin.findChild(QMdiArea)

        self.toolshelf = ToolshelfWidget(isPrimaryPanel)

        # Create "pad"
        self.pad = NtWidgetPad(self.mdiArea)
        self.pad.setObjectName("toolOptionsPad")
        self.pad.setViewAlignment(alignment)
        self.pad.borrowDocker(self.toolshelf)

        # Create and install event filter
        self.adjustFilter = Nt_AdjustToSubwindowFilter(self.mdiArea)
        self.adjustFilter.setTargetWidget(self.pad)
        self.mdiArea.subWindowActivated.connect(self.onSubWindowActivated)
        self.qWin.installEventFilter(self.adjustFilter)

        # Create visibility toggle action 
        action_id = TOUCHIFY_ID_ACTION_SHOW_TOOL_OPTIONS if isPrimaryPanel else TOUCHIFY_ID_ACTION_SHOW_TOOL_OPTIONS_ALT
        action_name = "Show Tool Options Shelf" if isPrimaryPanel else "Show Toolbox Shelf"
        action = window.createAction(action_id, action_name, KRITA_ID_MENU_SETTINGS)
        action.toggled.connect(self.pad.toggleWidgetVisible)
        action.setCheckable(True)
        action.setChecked(True)

    def onSubWindowActivated(self, subWin):
        if subWin:
            self.pad.adjustToView()
            self.updateStyleSheet()
    
    def onConfigUpdate(self):
        pass

    def onKritaConfigUpdate(self):
        pass

    def updateStyleSheet(self):
        self.toolshelf.updateStyleSheet()
        return
    
    def close(self):
        self.mdiArea.subWindowActivated.disconnect(self.onSubWindowActivated)
        self.qWin.removeEventFilter(self.adjustFilter)
        self.toolshelf.onUnload()
        self.pad.widget = None
        self.pad.widgetDocker = None
        return self.pad.close()

