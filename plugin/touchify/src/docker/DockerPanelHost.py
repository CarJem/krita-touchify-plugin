from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QFrame
from PyQt5.QtCore import QSize

from ..borrow_manager import KBBorrowManager

class DockerPanelHost(QWidget):

    
    def __init__(self, ID):
        super(DockerPanelHost, self).__init__()
        self.ID = ID
        self.borrowedDocker = None
        self.size = None
        self.outLayout = QVBoxLayout()
        self.outLayout.addStretch()
        self.setLayout(self.outLayout)
        self.outLayout.setContentsMargins(0, 0, 0, 0)
        self.outLayout.setSpacing(0)

        self.toolsHack = False
        self.toolsHackDocker = None

    def loadDocker(self):
        dockerLoaded: QScrollArea = KBBorrowManager.instance().borrowDockerWidget(self.ID)


        if self.toolsHack:
            self.toolsHackDocker = dockerLoaded
            self.borrowedDocker = dockerLoaded.takeWidget()
        else:
            self.borrowedDocker = dockerLoaded


        self.outLayout.addWidget(self.borrowedDocker)
        
    def unloadDocker(self):
        if self.borrowedDocker:
            self.outLayout.removeWidget(self.borrowedDocker)
            KBBorrowManager.instance().returnWidget(self.ID)

    def sizeHint(self):
        if self.toolsHack:
            return self.borrowedDocker.minimumSize()
        else: 
            return super().sizeHint()

    def widget(self):
        return self.borrowedDocker

