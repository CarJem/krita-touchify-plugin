from PyQt5.QtWidgets import QMdiArea, QDockWidget

from touchify.src.components.touchify.canvas.NtToolboxInteractFilter import NtToolboxInteractFilter

from ....settings.TouchifySettings import TouchifySettings
from .NtSubWinFilter import NtSubWinFilter
from ....stylesheet import Stylesheet
from .NtWidgetPad import NtWidgetPad
from .NtWidgetPadAlignment import NtWidgetPadAlignment
from krita import *
from PyQt5.QtWidgets import QMdiArea, QDockWidget
from ....variables import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .NtCanvas import NtCanvas

#Other Toolbox: pyKrita_CoolBox

class NtToolbox(QObject):

    def __init__(self, canvas: "NtCanvas", alignment: NtWidgetPadAlignment, window: Window):
        super().__init__(canvas)
        self.qWin = window.qwindow()
        self.mdiArea = self.qWin.findChild(QMdiArea)
        self.canvas = canvas
        self.toolbox = self.qWin.findChild(QDockWidget, TOUCHIFY_ID_DOCKER_TOOLBOX)
        # Create "pad"
        self.pad = NtWidgetPad(self.mdiArea)
        self.pad.setObjectName("toolBoxPad")
        self.pad.borrowDocker(self.toolbox)
        self.pad.setViewAlignment(alignment)

        #self.interactFilter = NtToolboxInteractFilter(self.mdiArea)
        #self.interactFilter.setTargetWidget(self.toolbox)
        #self.pad.installEventFilter(self.interactFilter)

        # Create and install event filter
        self.adjustFilter = NtSubWinFilter(self.mdiArea)
        self.adjustFilter.setTargetWidget(self)
        self.mdiArea.subWindowActivated.connect(self.onSubWindowActivated)
        self.pad.installEventFilter(self.adjustFilter)
        self.qWin.installEventFilter(self.adjustFilter)
        self.toolbox.installEventFilter(self.adjustFilter)

        # Disable the related QDockWidget
        #self.dockerAction = window.qwindow().findChild(QDockWidget, "ToolBox").toggleViewAction()
        self.dockerAction = window.qwindow().findChild(QDockWidget, TOUCHIFY_ID_DOCKER_TOOLBOX).toggleViewAction()
        self.dockerAction.setEnabled(False)

        qApp.paletteChanged.connect(self.updateStyleSheet)
        self.updateStyleSheet()

    def updatePalette(self):
        self.pad.returnDocker()
        self.pad.borrowDocker(self.toolbox)

    def onSubWindowActivated(self, subWin):
        if subWin:
            subWin.installEventFilter(self.adjustFilter)
            self.canvas.updateCanvas()

    def updateStyleSheet(self):
        self.pad.setStyleSheet(Stylesheet.instance().touchify_nt_toolbox)    


    def close(self):
        self.mdiArea.subWindowActivated.disconnect(self.onSubWindowActivated)
        #self.pad.removeEventFilter(self.interactFilter)
        self.pad.removeEventFilter(self.adjustFilter)
        self.toolbox.removeEventFilter(self.adjustFilter)
        self.qWin.removeEventFilter(self.adjustFilter)
        self.dockerAction.setEnabled(True)
        return self.pad.close()