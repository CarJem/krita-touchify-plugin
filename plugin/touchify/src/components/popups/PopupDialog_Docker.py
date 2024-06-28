from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
import json
from functools import partial
import sys
import importlib.util

from ..DockerContainer import DockerContainer

from ...cfg.CfgPopup import CfgPopup
from ...config import *
from ...resources import *
from .PopupDialog import *
from ...docker_manager import *

from krita import *


class PopupDialog_Docker(PopupDialog):

    dockerWidget: QDockWidget = None
    dockerLocation: Qt.DockWidgetArea = None
    dockerVisibility: bool = False

    def __init__(self, parent: QMainWindow, args: CfgPopup):     
        super().__init__(parent, args)
        self.grid = self.generateDockerLayout()
        self.docker_id = args.docker_id
        self.initLayout()

        self.docker_panel = DockerContainer(self, self.docker_id)
        self.docker_panel.setDockMode(True)
        self.docker_panel.setHiddenMode(True)
        self.grid.addWidget(self.docker_panel)

    
    def closeEvent(self, event):
        super().closeEvent(event)
        self.updateDocker(True)
   
    def generateSize(self):
        dialog_width = self.metadata.item_width
        dialog_height = self.metadata.item_height
        return [int(dialog_width), int(dialog_height)]

    def triggerPopup(self, mode: str, parent: QWidget | None):
        if not self.isVisible():
            self.updateDocker()
        super().triggerPopup(mode, parent)

    def updateDocker(self, closing = False):
        if closing:
            self.docker_panel.unloadWidget()
        else:
            self.docker_panel.loadWidget(True)

    def generateDockerLayout(self):
        grid = QHBoxLayout()
        return grid
