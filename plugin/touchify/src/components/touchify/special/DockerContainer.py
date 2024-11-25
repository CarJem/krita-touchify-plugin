from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QSize
from touchify.src.docker_manager import *
from krita import *

    


class DockerContainer(QWidget):
  
    dockerChanged=pyqtSignal()

    def __init__(self, parent: QWidget | None, docker_id: str, docker_manager: DockerManager):
        super(DockerContainer, self).__init__(parent)

        self.docker_manager = docker_manager

        self.emptySpaceState: bool = None

        self.isLoaded = False
        self.docker_id = docker_id
        self.borrowedDocker = None
        self.setAutoFillBackground(False)
        self.size = None

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)

        self.container = QWidget(self)
        self.container.setContentsMargins(0,0,0,0)
        self.layout().addWidget(self.container)

        self.container_layout = QVBoxLayout(self)
        self.container_layout.setContentsMargins(2, 2, 2, 2)
        self.container_layout.setSpacing(0)
        self.container_layout.removeWidget
        self.container.setLayout(self.container_layout)
        
        self.hiddenMode = False
        self.dockMode = False
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

    def unloadWidget(self):
        self.dockerShouldBeActive = False
        self._unloadDocker()

    def loadWidget(self, force: bool = False):
        self.dockerShouldBeActive = True
        if force:
            if not self.passiveMode: self.docker_manager.unloadDocker(self.docker_id)
            self._loadDocker()
        else: self._loadDocker()

    def shutdownWidget(self):
        self.docker_manager.removeListener(DockerManager.SignalType.OnReleaseDocker, self.onDockerReleased)
        self.docker_manager.unloadDocker(self.docker_id)

    def updateVisibility(self):
        if self.borrowedDocker != None and self.borrowedDocker.parentWidget() == self.container:
            self.unloaded_label.setVisible(False)
            self.container_layout.removeWidget(self.unloaded_label)
            self.adjustSize()
        else:
            self.container_layout.addWidget(self.unloaded_label)
            self.unloaded_label.setVisible(True)
            self.adjustSize()

    #region Private Functions
    def _stealDocker(self):
        if self.dockerShouldBeActive:
            self.docker_manager.unloadDocker(self.docker_id)
            self._loadDocker()
        self.updateVisibility()

    def _loadDocker(self):
        shareArgs = DockerManager.LoadArguments(self.dockMode)
        dockerLoaded: QWidget | None = self.docker_manager.loadDocker(self.docker_id, shareArgs)
        if not dockerLoaded: return
        self.borrowedDocker = dockerLoaded
        self.dockerChanged.emit()
        self.container_layout.addWidget(self.borrowedDocker)
        if self.dockMode: self.borrowedDocker.show()
        self.updateVisibility()

    def _unloadDocker(self):
        self.docker_manager.unloadDocker(self.docker_id)
        self.dockerChanged.emit()
        self.updateVisibility()

    #endregion

    #region Event Functions
    def onDockerReleased(self, ID: any):
        if self.dockerShouldBeActive and self.docker_id == ID:
            self._loadDocker()
            self.updateVisibility()

    def onDockerLoaded(self, ID: any):
        self.updateVisibility()

    #endregion

    #region Setters
    def setHiddenMode(self, value: bool):
        self.hiddenMode = value

    def setPassiveMode(self, value: bool):
        self.passiveMode = value

    def setDockMode(self, value):
        self.dockMode = value

    def setSizeHint(self, size):
        self.size = QSize(size[0], size[1])
    #endregion

    #region Overrides
    
    def sizeHint(self):
        baseSize: QSize = QSize()
        if self.size:
            baseSize = self.size
        else:
            baseSize = super().sizeHint()
            
        return baseSize

    def widget(self):
        return self.borrowedDocker
    #endregion

