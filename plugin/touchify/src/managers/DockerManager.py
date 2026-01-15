from enum import Enum
from jemlib.api_krita.wrappers.window import WindowAPI
from krita import *
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import *

from jemlib.alib_vaporjem import Logger
from touchify.src.settings.TouchifySettings import *

from typing import Callable

class DockerManager(QObject):
    class BorrowData:
        def __init__(self, dockMode: bool, docker: QDockWidget, mainWindow: QMainWindow) -> None:
            self.__is_nested_mode = dockMode
            self.__main_window = mainWindow
            self.__was_visible = docker.isVisible()
            self.__docker = docker

            self.isDead = False
            
            self.nestedWidget = None
            self.nestedWidgetArea = self.__main_window.dockWidgetArea(docker)
            self.nestedWidgetTitle = None

            self.childWidget = None
            self.childParent = None
            self.childHasScrollArea = False
            self.childScrollArea: QScrollArea | None = None


        def setup(self):
            if self.__is_nested_mode:
                self.nestedWidget: QDockWidget = self.__docker
                self.nestedWidgetTitle = self.nestedWidget.titleBarWidget()
                self.titleBarHider = QWidget()
                self.titleBarHider.setFixedHeight(0)
                self.nestedWidget.setTitleBarWidget(self.titleBarHider)
            else:
                self.childParent: QDockWidget = self.__docker
                self.childWidget: QWidget = self.__docker.widget()
                self.childParent.hide()
                
                if isinstance(self.childWidget, QScrollArea):
                    self.childHasScrollArea = True
                    self.childScrollArea: QScrollArea = self.childWidget
                    self.childWidget = self.childScrollArea.takeWidget()
                    
                self.childWidgetOldName = self.childWidget.objectName()
                self.childWidget.setObjectName(self.childParent.objectName() + "_touchify_borrowed")



        def widget(self):
            if self.__is_nested_mode:
                return self.nestedWidget
            else:
                return self.childWidget
        
        def clearWidgetData(self):
            if self.__is_nested_mode:
                self.__main_window.addDockWidget(self.nestedWidgetArea, self.nestedWidget)
                self.nestedWidget.setTitleBarWidget(self.nestedWidgetTitle)
                if self.__was_visible == False: self.nestedWidget.hide()
            else:
                self.childWidget.setObjectName(self.childWidgetOldName)

                if self.childHasScrollArea:
                    self.childScrollArea.setWidget(self.childWidget)
                    self.childWidget = self.childScrollArea

                self.childParent.setWidget(self.childWidget)
                if self.__was_visible == True: self.childParent.show()
            
            self.isDead = True

    class SignalType(Enum):
        OnReleaseDocker = 1,
        OnLoadDocker = 3

    class LoadArguments:
        def __init__(self, dockMode: bool = False) -> None:
            self.dockMode = dockMode

    onReleaseDockerSignal = pyqtSignal(str)
    onStealDockerSignal = pyqtSignal(str)
    onLoadDockerSignal = pyqtSignal(str)

    def __init__(self, api: WindowAPI):
        super().__init__(api.qwindow)

        self._shareData: dict[any, DockerManager.BorrowData] = {}
        self._listeners: dict[DockerManager.SignalType, list] = {}

        self.qWin = api.qwindow

    def isNotForbidden(self, obj):
        from touchify.src.components.toolshelf.ToolshelfDockerWidget import ToolshelfDockerWidget
        from touchify.src.components.toolshelf.ToolshelfDockerWidgetPad import ToolshelfDockerWidgetPad
        return not isinstance(obj, ToolshelfDockerWidget) and not isinstance(obj, ToolshelfDockerWidgetPad)

    def registerListener(self, type: SignalType, source: Callable):
        if type not in self._listeners:
            self._listeners[type] = list()
    
        self._listeners[type].append(source)
    
        if type == DockerManager.SignalType.OnReleaseDocker:
            self.onReleaseDockerSignal.connect(source)
        elif type == DockerManager.SignalType.OnLoadDocker:
            self.onLoadDockerSignal.connect(source)

    def removeListener(self, type: SignalType, source: Callable):
        if type in self._listeners:
            self._listeners[type].remove(source)
            if type == DockerManager.SignalType.OnReleaseDocker:
                self.onReleaseDockerSignal.disconnect(source)
            elif type == DockerManager.SignalType.OnLoadDocker:
                self.onLoadDockerSignal.disconnect(source)

    def invokeListeners(self, docker_id: str, type: SignalType):
        if type in self._listeners:
            if type == DockerManager.SignalType.OnReleaseDocker:
                self.onReleaseDockerSignal.emit(docker_id)
            elif type == DockerManager.SignalType.OnLoadDocker:
                self.onLoadDockerSignal.emit(docker_id)

    def findDocker(self, docker_id: str):
        return self.qWin.findChild(QDockWidget, docker_id)

    def loadDocker(self, docker_id: str, args: LoadArguments):
        Logger.logDebug('Touchify',"DockerManager", "loadDocker", f"{docker_id}")
        # Already in Use, don't borrow twice; unload previous docker
        if docker_id in self._shareData:
            if self._shareData[docker_id].isDead == False:
                self._shareData[docker_id].clearWidgetData()
                del self._shareData[docker_id]

        docker = self.findDocker(docker_id)
        # Does requested widget exist?
        if isinstance(docker, QDockWidget) and QDockWidget.widget(docker) and self.isNotForbidden(docker):
            self._shareData[docker_id] = DockerManager.BorrowData(args.dockMode, docker, self.qWin)
            self._shareData[docker_id].setup()
            self.invokeListeners(docker_id, DockerManager.SignalType.OnLoadDocker)
            Logger.logDebug('Touchify', "DockerManager", "loadDocker", f"{docker_id}: success")
            return self._shareData[docker_id].widget()
        Logger.logDebug('Touchify', "DockerManager", "loadDocker", f"{docker_id}: failed")
        return None
         
    def unloadDocker(self, docker_id: str):
        # Ensure there's a widget to return
        if docker_id in self._shareData:
            Logger.logDebug('Touchify', "DockerManager", "unloadDocker", f"{docker_id}: start")
            self._shareData[docker_id].clearWidgetData()
            del self._shareData[docker_id]
            self.invokeListeners(docker_id, DockerManager.SignalType.OnReleaseDocker)
            Logger.logDebug('Touchify', "DockerManager", "unloadDocker", f"{docker_id}: success")

    def dockerWindowTitle(self, docker_id: str):
        docker = self.findDocker(docker_id)
        if docker:
            title = docker.windowTitle()
            return title.replace('&', '')
        else:
            return docker_id
        


