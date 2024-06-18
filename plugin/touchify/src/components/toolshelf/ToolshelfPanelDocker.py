from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QFrame
from PyQt5.QtCore import QSize, QEvent

from ..nu_tools.nt_logic.Nt_ScrollAreaContainer import Nt_ScrollAreaContainer

from ...docker_manager import DockerManager

from krita import *

class ToolshelfPanelDocker(QWidget):

    
    def __init__(self, parent: QWidget | None, ID):
        super(ToolshelfPanelDocker, self).__init__(parent)
        self.ID = ID
        self.borrowedDocker = None
        self.size = None
        self.outLayout = QVBoxLayout()
        self.setLayout(self.outLayout)
        self.outLayout.setContentsMargins(0, 0, 0, 0)
        self.outLayout.setSpacing(0)

        self.autoFitScrollArea = False
        self.tookScrollArea = False
        self.originalScrollArea: QScrollArea | None = None
        self.dockMode = False

    def loadDocker(self):
        dockerLoaded: QWidget | None = DockerManager.instance().borrowDockerWidget(self.ID, self.dockMode)

        if isinstance(dockerLoaded, QScrollArea):
            self.tookScrollArea = True
            scrollArea: QScrollArea = dockerLoaded
            if scrollArea:
                self.originalScrollArea = scrollArea
                self.borrowedDocker = scrollArea.takeWidget()
        else:
            self.borrowedDocker = dockerLoaded
        
        self.outLayout.addWidget(self.borrowedDocker)
        if self.dockMode:
            self.borrowedDocker.show()
        
    def updateSize(self):
        if self.dockMode:
            docker: QDockWidget = self.borrowedDocker
            docker.resize(self.baseSize())
            docker.show()

    def unloadDocker(self):
        if self.borrowedDocker:
            if self.tookScrollArea:
                self.originalScrollArea.setWidget(self.borrowedDocker)
                self.tookScrollArea = False
            else:
                self.outLayout.removeWidget(self.borrowedDocker)
                
            DockerManager.instance().returnWidget(self.ID)

    def setDockMode(self, value):
        self.dockMode = value

    def setSizeHint(self, size):
        self.size = QSize(size[0], size[1])

    def sizeHint(self):
        if self.size:
            return self.size
        else:
            return super().sizeHint()

    def widget(self):
        return self.borrowedDocker

