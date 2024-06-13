from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
import json
from functools import partial
import sys
import importlib.util
from ...classes.config import *
from ...classes.resources import *
from .PopupDialog import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...ext.PyKrita import *
else:
    from krita import *


class PopupDialog_Docker(PopupDialog):

    dockerWidget: QDockWidget = None
    dockerWindow: QMainWindow = None
    dockerLocation: Qt.DockWidgetArea = None
    dockerVisibility: bool = False

    def __init__(self, parent: QMainWindow, args: Popup):     
        super().__init__(parent, args)
        self.grid = self.generateDockerLayout()
        self.getDockerDetails(True)
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
            if self.dockerWindow:
                self.grid.removeWidget(self.dockerWidget)
                self.dockerWindow.addDockWidget(self.dockerLocation, self.dockerWidget)

                titlebarSetting = Krita.instance().readSetting("", "showDockerTitleBars", "false")
                showTitlebar = True if titlebarSetting == "true" else False
                self.dockerWidget.titleBarWidget().setVisible(showTitlebar)

                self.dockerWidget.setVisible(self.dockerVisibility)
        else:
            self.getDockerDetails()
            self.dockerWidget.titleBarWidget().setVisible(False)
            self.grid.addWidget(self.dockerWidget)
            self.dockerWidget.setVisible(True)

    def generateDockerLayout(self):
        grid = QHBoxLayout()
        return grid
    
    def getDockerDetails(self, firstLoad = False):
        if firstLoad:
            dockersList = Krita.instance().dockers()
            for docker in dockersList:
                if (docker.objectName() == self.metadata.docker_id):
                    self.dockerWidget = docker
                    self.dockerWindow = Krita.instance().activeWindow().qwindow()
                    return
            
        self.dockerVisibility = self.dockerWidget.isVisible()
        self.dockerLocation = self.dockerWindow.dockWidgetArea(self.dockerWidget)