from PyQt5.QtWidgets import QMdiArea, QDockWidget

from ...config import InternalConfig, KritaSettings

from ... import stylesheet
from ...variables import KRITA_ID_DOCKER_SHAREDTOOLDOCKER, KRITA_ID_MENU_SETTINGS, TOUCHIFY_ID_OPTIONS_NU_OPTIONS_ALTERNATIVE_TOOLBOX_POSITION, TOUCHIFY_ID_OPTIONSROOT_MAIN
from .nt_logic.NtWidgetPad import NtWidgetPad
from .nt_logic.Nt_AdjustToSubwindowFilter import Nt_AdjustToSubwindowFilter

from .nt_logic.NtDockers import NtDockers
from krita import *
from PyQt5.QtCore import QObject, QEvent, QPoint



class NtToolOptions(QObject):
    def __init__(self, window):
        super(NtToolOptions, self).__init__(window.qwindow())
        self.qWin: QWindow = window.qwindow()

        if InternalConfig.instance().nuOptions_ToolboxOnRight: 
            self.alignment = 'left'
        else: 
            self.alignment= 'right'

        self.tooloptions = NtDockers(window, self.alignment, True)
        self.setViewAlignment(self.alignment)


    def onConfigUpdate(self):
        if self.tooloptions:
            self.tooloptions.toolshelf.onConfigUpdated()

    def setViewAlignment(self, alignment):
        self.alignment = alignment
        self.tooloptions.pad.setViewAlignment(self.alignment)

    def onKritaConfigUpdate(self):
        if self.tooloptions:
            self.tooloptions.toolshelf.onKritaConfigUpdate()

        if self.alignment == 'right' and InternalConfig.instance().nuOptions_ToolboxOnRight:
            self.setViewAlignment('left')
        elif self.alignment == 'left' and not InternalConfig.instance().nuOptions_ToolboxOnRight:
            self.setViewAlignment('right')

    def updateStyleSheet(self):
        self.tooloptions.updateStyleSheet()

    def show(self):
        self.tooloptions.pad.show()

    def close(self):
        self.tooloptions.close()