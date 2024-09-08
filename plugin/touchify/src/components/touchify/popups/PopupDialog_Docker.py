from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
import json
from functools import partial
import sys
import importlib.util

from ..core.DockerContainer import DockerContainer

from ....cfg.action.CfgTouchifyActionPopup import CfgTouchifyActionPopup
from ....settings.TouchifyConfig import *
from ....resources import *
from .PopupDialog import *
from ....docker_manager import *

from krita import *


class PopupDialog_Docker(PopupDialog):



    def __init__(self, parent: QWidget, args: CfgTouchifyActionPopup, docker_manager: DockerManager):     
        super().__init__(parent, args)

        self.dockerWidget: QDockWidget = None
        self.dockerLocation: Qt.DockWidgetArea = None
        self.dockerVisibility: bool = False

        self.grid = self.generateDockerLayout()
        self.docker_id = args.docker_id
        self.initLayout()

        self.docker_panel = DockerContainer(self, self.docker_id, docker_manager)
        self.docker_panel.setDockMode(True)
        self.docker_panel.setHiddenMode(True)
        self.grid.addWidget(self.docker_panel)

        dialog_width = self.metadata.actions_item_width - 20
        dialog_height = self.metadata.actions_item_height - 20
        self.docker_panel.setSizeHint([dialog_width, dialog_height])


    def shutdownWidget(self):
        self.docker_panel.shutdownWidget()
        super().shutdownWidget()

    
    def closeEvent(self, event):
        super().closeEvent(event)
        self.updateDocker(True)
   
    def generateSize(self):
        dialog_width = self.metadata.actions_item_width
        dialog_height = self.metadata.actions_item_height
        return [int(dialog_width), int(dialog_height)]

    def triggerPopup(self, parent: QWidget | None):
        if not self.isVisible():
            self.updateDocker()
        super().triggerPopup(parent)

    def updateDocker(self, closing = False):
        if closing:
            self.docker_panel.unloadWidget()
        else:
            self.docker_panel.loadWidget(True)

    def generateDockerLayout(self):
        grid = QHBoxLayout(self)
        return grid
