import copy
from enum import Enum
from krita import *
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import *

from .ext.extensions import *
from .config import *

IS_DEV_MODE = False
DEV_DISABLE = False


    

class DockerShareLoadArgs:
    dockMode: bool = False

    def __init__(self, dockMode: bool = False) -> None:
        self.dockMode = dockMode

class DockerShareData:

    def __init__(self, dockMode: bool, previousVisibility: bool, dockWidgetArea: Qt.DockWidgetArea) -> None:
        self.dockerParent = None
        self.dockerWidget = None
        self.dockerScrollArea: QScrollArea | None = None

        self.dockMode = dockMode
        self.previousVisibility = previousVisibility
        self.dockWidgetArea = dockWidgetArea
        self.detachedScrollArea = False

        self.isDead = False
    
    def setWidgetData(self, docker: QDockWidget):
        if self.dockMode:
            self.dockerWidget: QDockWidget = docker
            self.dockerWidget.titleBarWidget().setVisible(False)
        else:
            self.dockerParent: QDockWidget = docker
            self.dockerWidget: QWidget = docker.widget()
            self.dockerParent.hide()

        if isinstance(self.dockerWidget, QScrollArea):
            self.detachedScrollArea = True
            self.dockerScrollArea: QScrollArea = self.dockerWidget
            self.dockerWidget = self.dockerScrollArea.takeWidget()
    
    def clearWidgetData(self):
        self.dockerWidget: QDockWidget


        try:
            if self.detachedScrollArea:
                self.dockerScrollArea.setWidget(self.dockerWidget)
                self.dockerWidget = self.dockerScrollArea


            if self.dockMode == True:
                KritaExtensions.getMainWindow().addDockWidget(self.dockWidgetArea, self.dockerWidget)
                showTitlebar = KritaSettings.showDockerTitlebars()
                self.dockerWidget.titleBarWidget().setVisible(showTitlebar)
                if self.previousVisibility == False:
                    self.dockerWidget.hide()
            else:
                self.dockerParent.setWidget(self.dockerWidget)
                if self.previousVisibility == True:
                    self.dockerParent.show()
        except RuntimeError:
            pass
        
        self.isDead = True

class DM_ListenerType(Enum):
    OnReleaseDocker = 1,
    OnStealDocker = 2,
    OnLoadDocker = 3
    
class DockerManager():
    _shareData: dict[any, DockerShareData] = {}
    _listeners: dict[DM_ListenerType, list] = {}
    _hiddenDockers: dict[Qt.DockWidgetArea, list[str]] = {}
    _devDisable: bool = True

    def instance():
        try:
            return DockerManager.__instance
        except AttributeError:
            DockerManager.__instance = DockerManager()
            return DockerManager.__instance

    def __init__(self):
        self._hiddenDockers[1] = InternalConfig.instance().DockerUtils_HiddenDockersLeft.split(",")
        self._hiddenDockers[2] = InternalConfig.instance().DockerUtils_HiddenDockersRight.split(",")
        self._hiddenDockers[4] = InternalConfig.instance().DockerUtils_HiddenDockersUp.split(",")
        self._hiddenDockers[8] = InternalConfig.instance().DockerUtils_HiddenDockersDown.split(",")

    def registerListener(self, type: DM_ListenerType, source: Callable):
        if DEV_DISABLE:
            return
        if type not in self._listeners:
            self._listeners[type] = list()
    
        self._listeners[type].append(source)

    def removeListener(self, type: DM_ListenerType, source: Callable):
        if DEV_DISABLE:
            return
        if type in self._listeners:
            self._listeners[type].remove(source)

    def invokeListeners(self, docker_id: str, type: DM_ListenerType):
        if type in self._listeners:
            for hook in self._listeners[type]:
                hook(docker_id)

    def loadDocker(self, docker_id: str, args: DockerShareLoadArgs):
        if DEV_DISABLE:
            return None
        
        # Already in Use, don't borrow twice
        if docker_id in self._shareData:
            if self._shareData[docker_id].isDead == False:
                return None

        docker = KritaExtensions.getDocker(docker_id)
        # Does requested widget exist?
        if isinstance(docker, QDockWidget) and docker.widget():
            self._shareData[docker_id] = DockerShareData(args.dockMode, docker.isVisible(), KritaExtensions.getMainWindow().dockWidgetArea(docker))
            self._shareData[docker_id].setWidgetData(docker)
            self.invokeListeners(docker_id, DM_ListenerType.OnLoadDocker)
            return self._shareData[docker_id].dockerWidget
        return None
         
    def unloadDocker(self, docker_id: str, invokeRelease: bool = True):
        if DEV_DISABLE:
            return
        # Ensure there's a widget to return
        if docker_id in self._shareData:
            self._shareData[docker_id].clearWidgetData()
            del self._shareData[docker_id]
            if invokeRelease: self.invokeListeners(docker_id, DM_ListenerType.OnReleaseDocker)
            else: self.invokeListeners(docker_id, DM_ListenerType.OnStealDocker)

    def toggleDockersPerArea(self, area: int):
        dockers = Krita.instance().dockers()
        mainWindow = Krita.instance().activeWindow().qwindow()

        if len(self._hiddenDockers[area]) > 0: # show
            for dockerId in self._hiddenDockers[area]:
                docker = next((w for w in Krita.instance().dockers() if w.objectName() == dockerId), None)
                if docker:
                    docker.setVisible(True)
            self._hiddenDockers[area] = []
        else: # hide
            for docker in dockers:
                if docker.isHidden() or docker.isFloating():
                    continue

                if mainWindow.dockWidgetArea(docker) == area:
                    self._hiddenDockers[area].append(docker.objectName())
                    docker.setVisible(False)

        match area:
            case 1:
                InternalConfig.instance().DockerUtils_HiddenDockersLeft = ",".join(self._hiddenDockers[area])
            case 2:
                InternalConfig.instance().DockerUtils_HiddenDockersRight = ",".join(self._hiddenDockers[area])
            case 4:
                InternalConfig.instance().DockerUtils_HiddenDockersUp = ",".join(self._hiddenDockers[area])
            case 8:
                InternalConfig.instance().DockerUtils_HiddenDockersDown = ",".join(self._hiddenDockers[area])
        InternalConfig.instance().saveSettings()

    def dispose(self):
        for docker_id in self._shareData:
            self.unloadDocker(self._shareData[docker_id], False)
            self._shareData[docker_id] = None
        
        for listenerType in self._listeners:
            for listener in self._listeners[listenerType]:
                self._listeners[listenerType].remove(listener)

    def dockerWindowTitle(self, ID):
        docker = KritaExtensions.getDocker(ID)
        if docker:
            title = docker.windowTitle()
            return title.replace('&', '')
        else:
            return ID
        


