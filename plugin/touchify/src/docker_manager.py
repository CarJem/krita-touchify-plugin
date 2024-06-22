from krita import *
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import *

from .variables import KRITA_ID_OPTIONSROOT_MAIN
from .ext.extensions import *
from .config import *

IS_DEV_MODE = False

class DockerManager():

    _dockerParents = {}
    _dockerWidgets = {}
    _previousDockerStates = {}
    _borrowState = {}

    floatingLock_previousState = {}
    floatingLock_isEnabled = False

    def instance():
        try:
            return DockerManager.__instance
        except AttributeError:
            DockerManager.__instance = DockerManager()
            return DockerManager.__instance

    def __init__(self):
        self._qWin = Krita.instance().activeWindow().qwindow()

    def msg(self, text):
        if IS_DEV_MODE:
            msg = QMessageBox(self._qWin)
            msg.setText(text)
            msg.exec_()

    def widget(self, ID):
        return self._dockerWidgets[ID]
    
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

    def borrowDockerWidget(self, ID, dockMode=False):
        # Already in Use, don't borrow twice
        if ID in self._borrowState:
            if self._borrowState[ID] == True:
                self.msg("{0} is already in use".format(ID))
                return None

        docker = KritaExtensions.getDocker(ID)
        # Does requested widget exist?
        if isinstance(docker, QDockWidget) and docker.widget():

            self._previousDockerStates[ID] = {
                "dockMode": dockMode,
                "previousVisibility": docker.isVisible(),
                "dockWidgetArea": self._qWin.dockWidgetArea(docker)
            }

            if dockMode:
                self._borrowState[ID] = True
                self._dockerWidgets[ID] = docker
                self._dockerWidgets[ID].titleBarWidget().setVisible(False)
                self.msg("{0} has been borrowed!".format(ID))
                return self._dockerWidgets[ID]
            else:
                self._borrowState[ID] = True
                self._dockerParents[ID] = docker
                self._dockerWidgets[ID] = docker.widget()
                self._dockerParents[ID].hide()
                self.msg("{0} has been borrowed!".format(ID))
                return self._dockerWidgets[ID]
        self.msg("{0} can't be found!".format(ID))
        return None
    
    def returnWidget(self, ID):
        """
        Return the borrowed docker to it's original QDockWidget"""
        # Ensure there's a widget to return
        if ID in self._borrowState:
            if self._borrowState[ID] == True:

                dockMode = self._previousDockerStates[ID]["dockMode"]
                widgetArea = self._previousDockerStates[ID]["dockWidgetArea"]
                previousVisibility = self._previousDockerStates[ID]["previousVisibility"]

                if dockMode == True:
                    self._qWin.addDockWidget(widgetArea, self._dockerWidgets[ID])
                    titlebarSetting = KritaSettings.readSetting(KRITA_ID_OPTIONSROOT_MAIN, "showDockerTitleBars", "false")
                    showTitlebar = True if titlebarSetting == "true" else False
                    self._dockerWidgets[ID].titleBarWidget().setVisible(showTitlebar)
                    if previousVisibility == False:
                        self._dockerWidgets[ID].hide()
                else:
                    self._dockerParents[ID].setWidget(self._dockerWidgets[ID])
                    if previousVisibility == True:
                        self._dockerParents[ID].show()

                self._borrowState[ID] = False
                self.msg("{0} has been returned!".format(ID))
            else:
                self.msg("{0} is not being borrowed at the moment!".format(ID))
        else:
            self.msg("{0} does not exist!".format(ID))

    def returnAll(self):
        for ID in self._dockerWidgets:
            self.returnWidget(ID)

    def dockerWindowTitle(self, ID):
        docker = KritaExtensions.getDocker(ID)
        if docker:
            title = docker.windowTitle()
            return title.replace('&', '')
        else:
            return ID