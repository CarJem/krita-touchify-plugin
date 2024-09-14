from ast import main
import copy
from enum import Enum
from krita import *
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import *

from .settings.TouchifySettings import TouchifySettings

from .ext.KritaSettings import KritaSettings

from .ext.extensions import *
from .settings.TouchifyConfig import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .touchify import Touchify

class DockerManager(QObject):
    class BorrowData:
        def __init__(self, dockMode: bool, previousVisibility: bool, mainWindow: QMainWindow, dockWidgetArea: Qt.DockWidgetArea) -> None:
            self.dockerParent = None
            self.dockerWidget = None
            self.dockerScrollArea: QScrollArea | None = None

            self.dockMode = dockMode
            self.previousVisibility = previousVisibility
            self.dockWidgetArea = dockWidgetArea
            self.detachedScrollArea = False
            self.previousTitlebar = None


            self.mainWindow = mainWindow

            self.isDead = False
        
        def setWidgetData(self, docker: QDockWidget):
            if self.dockMode:
                self.dockerWidget: QDockWidget = docker
                self.previousTitlebar = self.dockerWidget.titleBarWidget()
                self.titleBarHider = QWidget()
                self.titleBarHider.setFixedHeight(0)
                self.dockerWidget.setTitleBarWidget(self.titleBarHider)
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
            
            if self.detachedScrollArea:
                self.dockerScrollArea.setWidget(self.dockerWidget)
                self.dockerWidget = self.dockerScrollArea


            if self.dockMode == True:
                self.mainWindow.addDockWidget(self.dockWidgetArea, self.dockerWidget)
                self.dockerWidget.setTitleBarWidget(self.previousTitlebar)
                if self.previousVisibility == False:
                    self.dockerWidget.hide()
            else:
                self.dockerParent.setWidget(self.dockerWidget)
                if self.previousVisibility == True:
                    self.dockerParent.show()
            
            self.isDead = True

    class SignalType(Enum):
        OnReleaseDocker = 1,
        OnStealDocker = 2,
        OnLoadDocker = 3

    class LoadArguments:
        def __init__(self, dockMode: bool = False) -> None:
            self.dockMode = dockMode

    onReleaseDockerSignal = pyqtSignal(str)
    onStealDockerSignal = pyqtSignal(str)
    onLoadDockerSignal = pyqtSignal(str)

    def __init__(self, touchify: "Touchify.TouchifyWindow"):
        
        super().__init__(touchify)

        self.touchify = touchify

        self._shareData: dict[any, DockerManager.BorrowData] = {}
        self._listeners: dict[DockerManager.SignalType, list] = {}
        self._hiddenDockers: dict[Qt.DockWidgetArea, list[str]] = {}

        self._hiddenDockers[1] = TouchifySettings.instance().DockerUtils_HiddenDockersLeft.split(",")
        self._hiddenDockers[2] = TouchifySettings.instance().DockerUtils_HiddenDockersRight.split(",")
        self._hiddenDockers[4] = TouchifySettings.instance().DockerUtils_HiddenDockersUp.split(",")
        self._hiddenDockers[8] = TouchifySettings.instance().DockerUtils_HiddenDockersDown.split(",")
        self.mainWindow = self.touchify.windowSource
        self.qWin = self.touchify.windowSource.qwindow()

    def registerListener(self, type: SignalType, source: Callable):
        if type not in self._listeners:
            self._listeners[type] = list()
    
        self._listeners[type].append(source)
        
        if type == DockerManager.SignalType.OnStealDocker:
            self.onStealDockerSignal.connect(source)
        elif type == DockerManager.SignalType.OnReleaseDocker:
            self.onReleaseDockerSignal.connect(source)
        elif type == DockerManager.SignalType.OnLoadDocker:
            self.onLoadDockerSignal.connect(source)

    def removeListener(self, type: SignalType, source: Callable):
        if type in self._listeners:
            self._listeners[type].remove(source)
            if type == DockerManager.SignalType.OnStealDocker:
                self.onStealDockerSignal.disconnect(source)
            elif type == DockerManager.SignalType.OnReleaseDocker:
                self.onReleaseDockerSignal.disconnect(source)
            elif type == DockerManager.SignalType.OnLoadDocker:
                self.onLoadDockerSignal.disconnect(source)

    def invokeListeners(self, docker_id: str, type: SignalType):
        if type in self._listeners:
            if type == DockerManager.SignalType.OnStealDocker:
                self.onStealDockerSignal.emit(docker_id)
            elif type == DockerManager.SignalType.OnReleaseDocker:
                self.onReleaseDockerSignal.emit(docker_id)
            elif type == DockerManager.SignalType.OnLoadDocker:
                self.onLoadDockerSignal.emit(docker_id)

    def findDocker(self, docker_id: str):
        return self.qWin.findChild(QDockWidget, docker_id)

    def loadDocker(self, docker_id: str, args: LoadArguments):
        # Already in Use, don't borrow twice
        if docker_id in self._shareData:
            if self._shareData[docker_id].isDead == False:
                return None

        docker = self.findDocker(docker_id)
        # Does requested widget exist?
        if isinstance(docker, QDockWidget) and docker.widget():
            self._shareData[docker_id] = DockerManager.BorrowData(args.dockMode, docker.isVisible(), self.qWin, self.qWin.dockWidgetArea(docker))
            self._shareData[docker_id].setWidgetData(docker)
            self.invokeListeners(docker_id, DockerManager.SignalType.OnLoadDocker)
            return self._shareData[docker_id].dockerWidget
        return None
         
    def unloadDocker(self, docker_id: str, invokeRelease: bool = True):
        # Ensure there's a widget to return
        if docker_id in self._shareData:
            self._shareData[docker_id].clearWidgetData()
            del self._shareData[docker_id]
            if invokeRelease: self.invokeListeners(docker_id, DockerManager.SignalType.OnReleaseDocker)
            else: self.invokeListeners(docker_id, DockerManager.SignalType.OnStealDocker)

    def toggleDockersPerArea(self, area: int):
        dockers = self.mainWindow.dockers()
        mainWindow = self.qWin

        if len(self._hiddenDockers[area]) > 0: # show
            for dockerId in self._hiddenDockers[area]:
                docker = next((w for w in self.mainWindow.dockers() if w.objectName() == dockerId), None)
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
                TouchifySettings.instance().DockerUtils_HiddenDockersLeft = ",".join(self._hiddenDockers[area])
            case 2:
                TouchifySettings.instance().DockerUtils_HiddenDockersRight = ",".join(self._hiddenDockers[area])
            case 4:
                TouchifySettings.instance().DockerUtils_HiddenDockersUp = ",".join(self._hiddenDockers[area])
            case 8:
                TouchifySettings.instance().DockerUtils_HiddenDockersDown = ",".join(self._hiddenDockers[area])
        TouchifySettings.instance().saveSettings()

    def dockerWindowTitle(self, docker_id: str):
        docker = self.findDocker(docker_id)
        if docker:
            title = docker.windowTitle()
            return title.replace('&', '')
        else:
            return docker_id
        


