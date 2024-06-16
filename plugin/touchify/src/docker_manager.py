from krita import *
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import *
from .ext.extensions import *
from .config import *

class DockerManager():

    borrowing_widgetDocker = {}
    borrowing_actualDocker = {}
    borrowing_previousDockerState = {}

    floatingLock_previousState = {}
    floatingLock_isEnabled = False

    def __init__(self):
        self._qWin = Krita.instance().activeWindow().qwindow()

    def widget(self, ID):
        return self.borrowing_actualDocker[ID]
    
    def toggleLockFloatingDockers(self, value=None):
        if value:
            self.floatingLock_isEnabled = True
            for docker in Krita.instance().dockers():
                docker_id = docker.objectName()
                if docker.isFloating():
                    self.floatingLock_previousState[docker_id] = docker.allowedAreas()
                    docker.setAllowedAreas(Qt.DockWidgetArea.NoDockWidgetArea)
                else:
                    self.floatingLock_previousState[docker_id] = None
        else:
            self.floatingLock_isEnabled = False
            for docker in Krita.instance().dockers():
                docker_id = docker.objectName()
                if docker_id in self.floatingLock_previousState:
                    if self.floatingLock_previousState[docker_id] != None:
                        docker.setAllowedAreas(self.floatingLock_previousState[docker_id])
                        self.floatingLock_previousState[docker_id] = None

    def borrowDockerWidget(self, ID):
        return self.borrowDockerWidget(self, ID, False)

    def borrowDockerWidget(self, ID, dockMode=False):

        # Already in Use, don't borrow twice
        if ID in self.borrowing_actualDocker:
            if self.borrowing_actualDocker[ID] != None:
                return None

        docker = self._qWin.findChild(QDockWidget, ID)
        # Does requested widget exist?
        if isinstance(docker, QDockWidget) and docker.widget():

            self.borrowing_previousDockerState[ID] = {
                "dockMode": dockMode,
                "previousVisibility": docker.isVisible(),
                "dockWidgetArea": self._qWin.dockWidgetArea(docker)
            }

            if dockMode:
                self.borrowing_actualDocker[ID] = docker
                self.borrowing_actualDocker[ID].titleBarWidget().setVisible(False)
                return self.borrowing_actualDocker[ID]
            else:
                self.borrowing_widgetDocker[ID] = docker
                self.borrowing_actualDocker[ID] = docker.widget()
                self.borrowing_widgetDocker[ID].hide()
                return self.borrowing_actualDocker[ID]
        return None
    
    def returnWidget(self, ID):
        """
        Return the borrowed docker to it's original QDockWidget"""
        # Ensure there's a widget to return
        if ID in self.borrowing_actualDocker:
            if self.borrowing_actualDocker[ID]:
                if self.borrowing_previousDockerState[ID]["dockMode"]:
                    self._qWin.addDockWidget(self.borrowing_previousDockerState[ID]["dockWidgetArea"], self.borrowing_actualDocker[ID])
                    titlebarSetting = KritaSettings.readSetting("", "showDockerTitleBars", "false")
                    showTitlebar = True if titlebarSetting == "true" else False
                    self.borrowing_actualDocker[ID].titleBarWidget().setVisible(showTitlebar)
                    if self.borrowing_previousDockerState[ID]["previousVisibility"] == False:
                        self.borrowing_actualDocker[ID].hide()
                else:
                    self.borrowing_widgetDocker[ID].setWidget(self.borrowing_actualDocker[ID])
                    if self.borrowing_previousDockerState[ID]["previousVisibility"] == True:
                        self.borrowing_widgetDocker[ID].show()
                self.borrowing_previousDockerState[ID] = None
                self.borrowing_actualDocker[ID] = None
                self.borrowing_widgetDocker[ID] = None

    def returnAll(self):
        for ID in self.borrowing_widgetDocker:
            self.returnWidget(ID)

    def dockerWindowTitle(self, ID):
        title = self._qWin.findChild(QWidget, ID).windowTitle()
        return title.replace('&', '')
    
    def instance():
        if DockerManager.root == None:
            DockerManager.root = DockerManager()
        return DockerManager.root
    
DockerManager.root = None