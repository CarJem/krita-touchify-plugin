from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QSize
from touchify.src.managers.DockerManager import *
from krita import *

    


class DockerContainer(QWidget):
  
    dockerChanged=pyqtSignal()
    dockerSizeChanged=pyqtSignal()

    def __init__(self, parent: QWidget | None, docker_id: str, docker_manager: DockerManager):
        super(DockerContainer, self).__init__(parent)

        self.docker_manager = docker_manager

        self.emptySpaceState: bool = None

        self.isLoaded = False
        self.docker_id = docker_id
        self.borrowedDocker = None
        self.setAutoFillBackground(False)
        self.size = None

        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)

        self.container = QWidget(self)
        self.container.setContentsMargins(0,0,0,0)
        self.layout().addWidget(self.container)

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(2, 2, 2, 2)
        self.container_layout.setSpacing(0)
        self.container_layout.removeWidget
        self.container.setLayout(self.container_layout)
        
        self.hiddenMode = False
        self.nested_mode = False
        self.passiveMode = False
        
        self.unloaded_label = QLabel(self.container)
        self.unloaded_label.linkActivated.connect(self._stealDocker)
        self.unloaded_label.setContentsMargins(0,0,0,0)
        self.unloaded_label.setText("Docker is open elsewhere. Close it to show here or <a href=\"clickable\">click here</a> to move it here.")
        self.unloaded_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unloaded_label.setWordWrap(True)
        self.unloaded_label.setVisible(False)

        self.docker_manager.registerListener(DockerManager.SignalType.OnReleaseDocker, self.onDockerReleased)
        self.docker_manager.registerListener(DockerManager.SignalType.OnLoadDocker, self.onDockerLoaded)

        self.dockerShouldBeActive = False
        self.isLoaded = True

    def showEvent(self, event: QShowEvent):
        Logger.logDebug("Touchify", "DockerContainer", "showEvent", f"activating super function")
        super().showEvent(event)
        Logger.logDebug("Touchify", "DockerContainer", "showEvent", f"super function complete")
        self.loadWidget()
        Logger.logDebug("Touchify", "DockerContainer", "showEvent", f"function complete")
        

    def hideEvent(self, event: QHideEvent):
        Logger.logDebug("Touchify", "DockerContainer", "hideEvent", f"activating super function")
        super().hideEvent(event)
        Logger.logDebug("Touchify", "DockerContainer", "hideEvent", f"super function complete")
        self.unloadWidget()
        Logger.logDebug("Touchify", "DockerContainer", "hideEvent", f"function complete")

    def eventFilter(self, a0: QObject, a1: QEvent):
        if a0 == self.borrowedDocker:
            if a1.type() == QEvent.Type.Resize:
                self.dockerSizeChanged.emit()
        return super().eventFilter(a0, a1)

    def unloadWidget(self):
        Logger.logDebug("Touchify", "DockerContainer", "unloadWidget", f"started: {self.docker_id}")
        self.dockerShouldBeActive = False
        self._unloadDocker()
        Logger.logDebug("Touchify", "DockerContainer", "unloadWidget", f"finished: {self.docker_id}")

    def loadWidget(self, force: bool = False):
        Logger.logDebug("Touchify", "DockerContainer", "loadWidget", f"started: {self.docker_id}")
        self.dockerShouldBeActive = True
        if force:
            if not self.passiveMode: self.docker_manager.unloadDocker(self.docker_id)
            self._loadDocker()
        else: self._loadDocker()
        Logger.logDebug("Touchify", "DockerContainer", "loadWidget", f"finished: {self.docker_id}")

    def shutdownWidget(self):
        self.docker_manager.removeListener(DockerManager.SignalType.OnReleaseDocker, self.onDockerReleased)
        self.docker_manager.unloadDocker(self.docker_id)

    def updateVisibility(self):
        if self.borrowedDocker != None and self.borrowedDocker.parentWidget() == self.container:
            Logger.logDebug("Touchify", "DockerContainer", "updateVisibility", f"hiding: {self.docker_id}")
            self.unloaded_label.setVisible(False)
            self.container_layout.removeWidget(self.unloaded_label)
        else:
            Logger.logDebug("Touchify", "DockerContainer", "updateVisibility", f"showing: {self.docker_id}")
            self.container_layout.addWidget(self.unloaded_label)
            self.unloaded_label.setVisible(True)

    #region Private Functions
    def _stealDocker(self):
        Logger.logDebug("Touchify", "DockerContainer", "_stealDocker", f"started: {self.docker_id}")
        if self.dockerShouldBeActive:
            Logger.logDebug("Touchify", "DockerContainer", "_stealDocker", f"unloading: {self.docker_id}")
            self.docker_manager.unloadDocker(self.docker_id)
            Logger.logDebug("Touchify", "DockerContainer", "_stealDocker", f"loading: {self.docker_id}")
            self._loadDocker()
            Logger.logDebug("Touchify", "DockerContainer", "_stealDocker", f"loaded: {self.docker_id}")
        self.updateVisibility()
        Logger.logDebug("Touchify", "DockerContainer", "_stealDocker", f"finished: {self.docker_id}")

    def _loadDocker(self):
        Logger.logDebug("Touchify", "DockerContainer", "_loadDocker", f"started: {self.docker_id}")
        shareArgs = DockerManager.LoadArguments(self.nested_mode)
        dockerLoaded: QWidget | None = self.docker_manager.loadDocker(self.docker_id, shareArgs)
        Logger.logDebug("Touchify", "DockerContainer", "_loadDocker", f"loaded: {self.docker_id}")
        if not dockerLoaded: return
        self.borrowedDocker = dockerLoaded
        self.borrowedDocker.installEventFilter(self)
        Logger.logDebug("Touchify", "DockerContainer", "_loadDocker", f"installed: {self.docker_id}")
        self.dockerChanged.emit()
        self.container_layout.addWidget(self.borrowedDocker, 1)
        if self.nested_mode: self.borrowedDocker.show()
        self.updateVisibility()
        Logger.logDebug("Touchify", "DockerContainer", "_loadDocker", f"finished: {self.docker_id}")

    def _unloadDocker(self):
        Logger.logDebug("Touchify", "DockerContainer", "_unloadDocker", f"unloading: {self.docker_id}")
        if self.borrowedDocker != None:
            Logger.logDebug("Touchify", "DockerContainer", "_unloadDocker", f"uninstalling: {self.docker_id}")
            try:
                self.borrowedDocker.removeEventFilter(self)
            except (RuntimeError, AttributeError):
                pass
            Logger.logDebug("Touchify", "DockerContainer", "_unloadDocker", f"uninstall finished: {self.docker_id}")
            
        self.docker_manager.unloadDocker(self.docker_id)
        self.dockerChanged.emit()
        self.updateVisibility()
        Logger.logDebug("Touchify", "DockerContainer", "_unloadDocker", f"unloading finished: {self.docker_id}")

    #endregion

    #region Event Functions
    def onDockerReleased(self, ID: any):
        Logger.logDebug("Touchify", "DockerContainer", "onDockerReleased", f"{self.docker_id}")
        if self.dockerShouldBeActive and self.docker_id == ID:
            Logger.logDebug("Touchify", "DockerContainer", "onDockerReleased", f"loading: {self.docker_id}")
            self._loadDocker()
            Logger.logDebug("Touchify", "DockerContainer", "onDockerReleased", f"loaded: {self.docker_id}")
            self.updateVisibility()
        Logger.logDebug("Touchify", "DockerContainer", "onDockerReleased", f"completed: {self.docker_id}")
            

    def onDockerLoaded(self, ID: any):
        Logger.logDebug("Touchify", "DockerContainer", "onDockerLoaded", f"started: {self.docker_id}")
        self.updateVisibility()
        Logger.logDebug("Touchify", "DockerContainer", "onDockerLoaded", f"completed: {self.docker_id}")

    #endregion

    #region Setters
    def setHiddenMode(self, value: bool):
        self.hiddenMode = value

    def setPassiveMode(self, value: bool):
        self.passiveMode = value

    def setDockMode(self, value):
        self.nested_mode = value

    def setSizeHint(self, size):
        self.size = QSize(size[0], size[1])
    #endregion

    #region Overrides

    def hintPadding(self, size: QSize):
        if not self.borrowedDocker: return size
        if not self.nested_mode: return size
        if not isinstance(self.borrowedDocker, QDockWidget): return size

        dock_widget: QDockWidget = self.borrowedDocker
        if not isinstance(dock_widget.widget(), QScrollArea): return size
        scroll_area: QScrollArea = dock_widget.widget()
        
        leftover_width = -(scroll_area.viewport().width() - scroll_area.widget().width())
        leftover_height = -(scroll_area.viewport().height() - scroll_area.widget().height())
        
        #new_size = QSize(size.width() + leftover_width, size.height() + leftover_height)

        return size
    

    def size(self):
        baseSize: QSize = QSize()
        if self.borrowedDocker:
            baseSize = self.borrowedDocker.size()
        else:
            baseSize = super().size()
            
        return baseSize
    
    def minimumSize(self):
        baseSize: QSize = QSize()
        if self.borrowedDocker:
            baseSize = self.borrowedDocker.minimumSize()
        else:
            baseSize = super().minimumSize()
            
        return baseSize
        

    def minimumSizeHint(self):
        baseSize: QSize = QSize()
        if self.borrowedDocker:
            baseSize = self.borrowedDocker.minimumSizeHint()
        else:
            baseSize = super().minimumSizeHint()
            
        return baseSize
    
    def sizeHint(self):
        baseSize: QSize = QSize()
        if self.size != None:
            baseSize = self.size
        elif self.borrowedDocker:
            baseSize = self.borrowedDocker.sizeHint()
        else:
            baseSize = super().sizeHint()
            
        return baseSize

    def widget(self):
        return self.borrowedDocker
    #endregion

