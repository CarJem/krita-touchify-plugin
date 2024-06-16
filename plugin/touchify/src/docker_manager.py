from krita import *
from PyQt5.QtWidgets import QWidget
from .ext.extensions import *
from .config import *

class DockerManager():

    _widgetDocker = {}
    _actualDocker = {}
    _previousDockerState = {}

    def __init__(self):
        self._qWin = Krita.instance().activeWindow().qwindow()

    def widget(self, ID):
        return self._actualDocker[ID]
    
    def borrowDockerWidget(self, ID):
        return self.borrowDockerWidget(self, ID, False)

    def borrowDockerWidget(self, ID, dockMode=False):
        """
        Borrow a docker widget from Krita's existing list of dockers and 
        returns True. Returns False if invalid widget was passed."""
        docker = self._qWin.findChild(QDockWidget, ID)
        # Does requested widget exist?
        if isinstance(docker, QDockWidget) and docker.widget():

            self._previousDockerState[ID] = {
                "dockMode": dockMode,
                "previousVisibility": docker.isVisible(),
                "dockWidgetArea": self._qWin.dockWidgetArea(docker)
            }

            if dockMode:
                self._actualDocker[ID] = docker
                self._actualDocker[ID].titleBarWidget().setVisible(False)
                return self._actualDocker[ID]
            else:
                self._widgetDocker[ID] = docker
                self._actualDocker[ID] = docker.widget()
                self._widgetDocker[ID].hide()
                return self._actualDocker[ID]
        return None
    
    def returnWidget(self, ID):
        """
        Return the borrowed docker to it's original QDockWidget"""
        # Ensure there's a widget to return
        if ID in self._actualDocker:
            if self._actualDocker[ID]:
                if self._previousDockerState[ID]["dockMode"]:
                    self._qWin.addDockWidget(self._previousDockerState[ID]["dockWidgetArea"], self._actualDocker[ID])
                    titlebarSetting = KritaSettings.readSetting("", "showDockerTitleBars", "false")
                    showTitlebar = True if titlebarSetting == "true" else False
                    self._actualDocker[ID].titleBarWidget().setVisible(showTitlebar)
                    if self._previousDockerState[ID]["previousVisibility"] == False:
                        self._actualDocker[ID].hide()
                else:
                    self._widgetDocker[ID].setWidget(self._actualDocker[ID])
                    if self._previousDockerState[ID]["previousVisibility"] == True:
                        self._widgetDocker[ID].show()
                self._previousDockerState[ID] = None
                self._actualDocker[ID] = None
                self._widgetDocker[ID] = None

    def returnAll(self):
        for ID in self._widgetDocker:
            self.returnWidget(ID)

    def dockerWindowTitle(self, ID):
        title = self._qWin.findChild(QWidget, ID).windowTitle()
        return title.replace('&', '')
    
    def instance():
        if DockerManager.root == None:
            DockerManager.root = DockerManager()
        return DockerManager.root
    
DockerManager.root = None