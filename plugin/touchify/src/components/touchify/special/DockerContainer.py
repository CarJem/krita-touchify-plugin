from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QSize
from touchify.src.docker_manager import *
from krita import *

    


class DockerContainer(QWidget):
  
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
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)
        self.container.setLayout(self.container_layout)
        
        self.hiddenMode = False
        self.dockMode = False
        self.passiveMode = False
        
        self.unloaded_label = QLabel(self.container)
        self.unloaded_label.setText("Docker is currently in use elsewhere, click here to move it here")
        self.unloaded_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unloaded_label.setWordWrap(True)
        self.unloaded_label.setVisible(False)

        self.unloaded_button = QPushButton(self.container)
        self.unloaded_button.setText("Load Docker")
        self.unloaded_button.clicked.connect(self._stealDocker)
        self.unloaded_button.setVisible(False)

        self._updateEmptySpace(True)

        self.docker_manager.registerListener(DockerManager.SignalType.OnReleaseDocker, self.onDockerReleased)
        self.docker_manager.registerListener(DockerManager.SignalType.OnStealDocker, self.onDockerStolen)

        self.dockerShouldBeActive = False
        self.isLoaded = True

    def unloadWidget(self):
        self.dockerShouldBeActive = False
        self._unloadDocker()

    def loadWidget(self, force: bool = False):
        self.dockerShouldBeActive = True
        if force:
            if not self.passiveMode: self.docker_manager.unloadDocker(self.docker_id, False)
            self._loadDocker()
        else:
            self._loadDocker()

    def shutdownWidget(self):
        self.docker_manager.removeListener(DockerManager.SignalType.OnReleaseDocker, self.onDockerReleased)
        self.docker_manager.removeListener(DockerManager.SignalType.OnStealDocker, self.onDockerStolen)
        self.docker_manager.unloadDocker(self.docker_id, False)

    #region Private Functions
    def _stealDocker(self):
        if self.dockerShouldBeActive:
            self.docker_manager.unloadDocker(self.docker_id, False)
            self._loadDocker()

    def _loadDocker(self):
        shareArgs = DockerManager.LoadArguments(self.dockMode)
        dockerLoaded: QWidget | None = self.docker_manager.loadDocker(self.docker_id, shareArgs)
        if not dockerLoaded: 
            if not self.borrowedDocker:
                self._updateEmptySpace(True)
            return
        self.borrowedDocker = dockerLoaded
        self.container_layout.addWidget(self.borrowedDocker)
        self._updateEmptySpace(False)
        if self.dockMode: self.borrowedDocker.show()

    def _unloadDocker(self, invokeRelease: bool = True):
        if self.borrowedDocker: self._updateEmptySpace(True)
        self.docker_manager.unloadDocker(self.docker_id, invokeRelease)

    def _updateEmptySpace(self, state: bool):
        if self.emptySpaceState != state:
            if state:
                self.container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.container_layout.addWidget(self.unloaded_label)
                self.container_layout.addWidget(self.unloaded_button)
                if self.hiddenMode:
                    self.container.setVisible(False)
                    self.container.setAutoFillBackground(False)
            else:
                self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                self.container_layout.removeWidget(self.unloaded_label)
                self.container_layout.removeWidget(self.unloaded_button)
                if self.hiddenMode:
                    self.container.setVisible(True)
                    self.container.setAutoFillBackground(True)

            self.docker_busy = state
            self.emptySpaceState = state
            self.unloaded_button.setVisible(state)
            self.unloaded_button.setEnabled(state)
            self.unloaded_label.setVisible(state)
            self.unloaded_label.setEnabled(state)

    #endregion

    #region Event Functions
    def onDockerStolen(self, ID: any):
        if self.docker_id == ID:
            self._updateEmptySpace(True)

    def onDockerReleased(self, ID: any):
        if self.dockerShouldBeActive and self.docker_id == ID:
            self._loadDocker()
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
    
    
    def minimumSize(self) -> QSize:
        baseSize: QSize = QSize()
        if self.borrowedDocker:
            baseSize = self.borrowedDocker.minimumSize()
        else:
            baseSize = super().minimumSize()
        return baseSize
    
    def sizeHint(self):
        baseSize: QSize = QSize()
        if self.size:
            baseSize = self.size
        elif self.borrowedDocker:
            baseSize = self.borrowedDocker.sizeHint()
        else:
            baseSize = super().sizeHint()
            
        return baseSize

    def widget(self):
        return self.borrowedDocker
    #endregion

