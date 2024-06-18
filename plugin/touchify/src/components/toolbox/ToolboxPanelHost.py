from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QStackedWidget
from PyQt5.QtCore import QSize

from ...cfg.CfgToolboxPanel import CfgToolboxPanel
from ...cfg.CfgToolboxPanelDocker import CfgToolboxPanelDocker

from ...docker_manager import DockerManager
from .ToolboxPanelDocker import ToolboxPanelDocker

class ToolboxPanelHost(QWidget):

    dockerWidgets: {}

    def __init__(self, parent: QWidget, ID: any, isPanelMode: bool, data: QWidget | CfgToolboxPanel):
        super(ToolboxPanelHost, self).__init__(parent)

        self.ID = ID
        self.dockerWidgets = {}
        self.dockerMode = False

        self.setAutoFillBackground(True)
        self.size = None
        
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        if isPanelMode:
            self.dockerMode = False
            self.mainPage = data
            self.layout().addWidget(self.mainPage)
        else:
            if isinstance(data, CfgToolboxPanel):
                self.dockerMode = True
                self.panelProperties = data

                if data.size_x != 0 and data.size_y != 0:
                    size = [data.size_x, data.size_y]
                    self.setSizeHint(size)

                for dockerData in self.panelProperties.additional_dockers:
                    dockerInfo: CfgToolboxPanelDocker = dockerData
                    dockerWidget = ToolboxPanelDocker(self, dockerInfo.id)

                    if dockerInfo.size_x != 0 and dockerInfo.size_y != 0:
                        size = [dockerInfo.size_x, dockerInfo.size_y]
                        dockerWidget.setSizeHint(size)

                    if dockerInfo.nesting_mode == "docking":
                        dockerWidget.setDockMode(True)

                    self.dockerWidgets[dockerInfo.id] = dockerWidget
                    self.layout().addWidget(dockerWidget)


    def unloadDockers(self):
        if self.dockerMode == True:
            for host_id in self.dockerWidgets:
                self.dockerWidgets[host_id].unloadDocker()
        else:
            self.mainPage.unloadDocker()

    def loadDockers(self):
        if self.dockerMode == True:
            for host_id in self.dockerWidgets:
                self.dockerWidgets[host_id].loadDocker()
        else:
            self.mainPage.loadDocker()

    def activate(self):
        self.parentWidget().changePanel(self.ID)

    def setSizeHint(self, size):
        self.size = QSize(size[0], size[1])

    def sizeHint(self):
        if not self.dockerMode:
            return self.mainPage.sizeHint()
        else:
            if self.size:
                return self.size
            else:
                return super().sizeHint()
    

    