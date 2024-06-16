from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
import json
from functools import partial
import sys
import importlib.util

from ...cfg.CfgPopup import Popup
from ...config import *
from ...resources import *
from .PopupDialog import *
from ...docker_manager import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...ext.PyKrita import *
else:
    from krita import *


class PopupDialog_Docker(PopupDialog):

    dockerWidget: QDockWidget = None
    dockerLocation: Qt.DockWidgetArea = None
    dockerVisibility: bool = False

    def __init__(self, parent: QMainWindow, args: Popup):     
        super().__init__(parent, args)
        self.grid = self.generateDockerLayout()
        self.dockerID = args.docker_id
        self.initLayout()

    
    def closeEvent(self, event):
        super().closeEvent(event)
        self.updateDocker(True)
   
    def generateSize(self):
        dialog_width = self.metadata.item_width
        dialog_height = self.metadata.item_height
        return [int(dialog_width), int(dialog_height)]

    def triggerPopup(self, mode):
        if not self.isVisible():
            self.updateDocker()
        super().triggerPopup(mode)

    def updateDocker(self, closing = False):
        if closing:
            self.grid.removeWidget(self.dockerWidget)
            KBBorrowManager.instance().returnWidget(self.dockerID)
            self.dockerWidget = None
        else:
            self.dockerWidget = KBBorrowManager.instance().borrowDockerWidget(self.dockerID, True)
            self.grid.addWidget(self.dockerWidget)
            self.dockerWidget.show()

    def generateDockerLayout(self):
        grid = QHBoxLayout()
        return grid
