from typing import Dict
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ...cfg.CfgToolshelf import CfgToolboxPanel
from ...cfg.CfgToolshelf import CfgToolboxPanelDocker

from ...docker_manager import DockerManager
from .ToolshelfPanelDocker import ToolshelfPanelDocker

class ToolshelfPanelHost(QWidget):

    dockerWidgets: dict = {}

    def __init__(self, parent: QWidget, ID: any, isPanelMode: bool, data: QWidget | CfgToolboxPanel):
        super(ToolshelfPanelHost, self).__init__(parent)

        self.ID = ID
        self.dockerWidgets = {}
        self.dockerMode = False

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

                self.generateDockerPanelLayout()

    def generateDockerPanelLayout(self):
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.layout().addWidget(self.splitter)

        data = self.panelProperties
        
        if data.size_x != 0 and data.size_y != 0:
            size = [data.size_x, data.size_y]
            self.setSizeHint(size)


        widget_groups: Dict[int, list[ToolshelfPanelDocker]] = {}

        for dockerData in self.panelProperties.additional_dockers:     
            dockerInfo: CfgToolboxPanelDocker = dockerData
            dockerWidget = ToolshelfPanelDocker(self, dockerInfo.id)

            if dockerInfo.size_x != 0 and dockerInfo.size_y != 0:
                size = [dockerInfo.size_x, dockerInfo.size_y]
                dockerWidget.setSizeHint(size)

            if dockerInfo.nesting_mode == "docking":
                dockerWidget.setDockMode(True)

            self.dockerWidgets[dockerInfo.id] = dockerWidget
            
            if dockerInfo.panel_y not in widget_groups:
                widget_groups[dockerInfo.panel_y] = []
            widget_groups[dockerInfo.panel_y].append(dockerWidget)
            

        for panel_y in sorted(widget_groups.keys()):

            if len(widget_groups[panel_y]) == 1:
                self.splitter.addWidget(widget_groups[panel_y][0])
            else:

                tabBar = QTabWidget()

                for item in widget_groups[panel_y]:
                    title = DockerManager.instance().dockerWindowTitle(item.ID)
                    tabBar.addTab(item, title)

                self.splitter.addWidget(tabBar)
            

            


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
    

    