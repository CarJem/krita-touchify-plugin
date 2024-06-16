from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QSize

from ...docker_manager import DockerManager
from .ToolboxPanelHost import DockerPanelHost
from .ToolboxMainPage import DockerMainPage

class DockerPanel(QWidget):
    def __init__(self, ID=None, widget=None):
        super(DockerPanel, self).__init__()
        self.ID = ID
        self.setAutoFillBackground(True)
        self.size = None
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        if widget:
            self.dockerMode = False
            self.w = widget
        else:
            self.dockerMode = True
            self.w = DockerPanelHost(self, self.ID)
        self.layout().addWidget(self.w)

    def unloadDockers(self):
        if self.dockerMode or self.w is DockerMainPage: 
            self.w.unloadDocker()

    def loadDockers(self):
        if self.dockerMode or self.w is DockerMainPage: 
            self.w.loadDocker() 

    def activate(self):
        self.parentWidget().setCurrentWidget(self)

    def widget(self):
        return self.w
    
    def setDockMode(self, mode):
        if self.w and isinstance(self.w, DockerPanelHost):
            self.w.setDockMode(mode)


    def setSizeHint(self, size):
        self.size = QSize(size[0], size[1]+12)

    def sizeHint(self):
        if self.size:
            return self.size
        else:
            return self.w.sizeHint()
    

    