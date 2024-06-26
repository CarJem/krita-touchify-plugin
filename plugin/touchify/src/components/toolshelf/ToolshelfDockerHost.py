from typing import Callable
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QFrame
from PyQt5.QtCore import QSize, QEvent
from ...docker_manager import *
from krita import *

class ToolshelfDockerHost(QWidget):
  
    def __init__(self, parent: QWidget | None, ID):
        super(ToolshelfDockerHost, self).__init__(parent)
        self.ID = ID
        self.borrowedDocker = None
        self.setAutoFillBackground(True)
        self.size = None
        self.outLayout = QVBoxLayout()
        self.setLayout(self.outLayout)
        self.outLayout.setContentsMargins(0, 0, 0, 0)
        self.outLayout.setSpacing(0)

        self.hide_when_unloaded = False
        self.unloadedLabel = None
        self.unloadedButton = None
        self._updateEmptySpace(True)

        DockerManager.instance().registerListener(DM_ListenerType.OnReleaseDocker, self.onDockerReleased)
        DockerManager.instance().registerListener(DM_ListenerType.OnStealDocker, self.onDockerStolen)

        self.autoFitScrollArea = False
        self.tookScrollArea = False
        self.originalScrollArea: QScrollArea | None = None
        self.dockMode = False
        self.dockerShouldBeActive = False
        self.wasJustStolen = False

    def unloadWidget(self):
        self.dockerShouldBeActive = False
        self._unloadDocker()

    def loadWidget(self):
        self.dockerShouldBeActive = True
        self._loadDocker()

    #region Private Functions
    def _stealDocker(self):
        if self.dockerShouldBeActive:
            DockerManager.instance().stealDocker(self.ID)
            self._loadDocker()

    def _loadDocker(self):
        shareArgs = DockerShareLoadArgs(self.dockMode)
        dockerLoaded: QWidget | None = DockerManager.instance().loadDocker(self.ID, self, shareArgs)
        if not dockerLoaded:
            return
        
        
        if isinstance(dockerLoaded, QScrollArea):
            self.tookScrollArea = True
            scrollArea: QScrollArea = dockerLoaded
            if scrollArea:
                self.originalScrollArea = scrollArea
                self.borrowedDocker = scrollArea.takeWidget()
        else:
            self.borrowedDocker = dockerLoaded
        
        self.outLayout.addWidget(self.borrowedDocker)
        self._updateEmptySpace(False)
        if self.dockMode:
            self.borrowedDocker.show()

    def _unloadDocker(self, invokeRelease: bool = True):
        if self.borrowedDocker:
            if self.tookScrollArea:
                self.originalScrollArea.setWidget(self.borrowedDocker)
                self.tookScrollArea = False
            else:
                self.outLayout.removeWidget(self.borrowedDocker)
        
            DockerManager.instance().unloadDocker(self.ID, invokeRelease)
            self._updateEmptySpace(True)

    def _updateEmptySpace(self, state: bool):

        if self.unloadedLabel == None and self.unloadedButton == None:
            self.unloadedLabel = QLabel()
            self.unloadedLabel.setText("Docker is currently in use elsewhere, click here to move it here")

            self.unloadedButton = QPushButton()
            self.unloadedButton.setText("Load Docker")
            self.unloadedButton.clicked.connect(self._stealDocker)

        if state:
            self.outLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.outLayout.addWidget(self.unloadedLabel)
            self.outLayout.addWidget(self.unloadedButton)
            if self.hide_when_unloaded:
                self.setVisible(False)
        else:
            self.outLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.outLayout.removeWidget(self.unloadedLabel)
            self.outLayout.removeWidget(self.unloadedButton)
            if self.hide_when_unloaded:
                self.setVisible(True)

        self.docker_busy = state
        self.unloadedButton.setVisible(state)
        self.unloadedButton.setEnabled(state)
        self.unloadedLabel.setVisible(state)
        self.unloadedLabel.setEnabled(state)
    #endregion

    #region Event Functions
    def onDockerReleased(self, ID: any):
        if self.dockerShouldBeActive and self.ID == ID:
            self._loadDocker()

    def onDockerStolen(self, ID: any):
        if self.ID == ID and self.dockerShouldBeActive:
            self._unloadDocker(False)

    def onDispose(self):
        DockerManager.instance().removeListener(DM_ListenerType.OnReleaseDocker, self.onDockerReleased)
        DockerManager.instance().removeListener(DM_ListenerType.OnStealDocker, self.onDockerStolen)
        self._unloadDocker()
    #endregion

    #region Setters
    def setHideWhenUnloaded(self, value: bool):
        self.hide_when_unloaded = value

    def setDockMode(self, value):
        self.dockMode = value

    def setSizeHint(self, size):
        self.size = QSize(size[0] + 20, size[1] + 20)
    #endregion

    #region Overrides
    def sizeHint(self):
        if self.size:
            return self.size
        elif self.borrowedDocker:
            return self.borrowedDocker.sizeHint()
        else:
            return super().sizeHint()

    def widget(self):
        return self.borrowedDocker
    #endregion

