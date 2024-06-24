from typing import Dict
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from .ToolshelfQuickActions import ToolshelfQuickActions

from .ToolshelfPageHost import ToolshelfPageHost

from ...cfg.CfgToolshelf import CfgToolboxPanel
from ...cfg.CfgToolshelf import CfgToolboxPanelDocker

from ...docker_manager import DockerManager
from .ToolshelfDockerHost import ToolshelfDockerHost
from ... import stylesheet

class ToolshelfPagePanel(ToolshelfPageHost):

    dockerWidgets: dict = {}

    def __init__(self, parent: QWidget, ID: any, data: CfgToolboxPanel):
        super(ToolshelfPagePanel, self).__init__(parent, ID)

        self.ID = ID
        self.dockerWidgets = {}
        self.size = None
        self.panelProperties = data

        self.quickActions = ToolshelfQuickActions(self.panelProperties.quick_actions, self.panelProperties.actionHeight, self)
        self.shelfLayout.addWidget(self.quickActions)
        
        #region Generation
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setAutoFillBackground(True)
        self.shelfLayout.addWidget(self.splitter)

        data = self.panelProperties
        
        if data.size_x != 0 and data.size_y != 0:
            size = [data.size_x, data.size_y]
            self.setSizeHint(size)


        widget_groups: Dict[int, list[ToolshelfDockerHost]] = {}

        for dockerData in self.panelProperties.additional_dockers:     
            dockerInfo: CfgToolboxPanelDocker = dockerData
            dockerWidget = ToolshelfDockerHost(self, dockerInfo.id)

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
        #endregion

    def unloadDockers(self):
        for host_id in self.dockerWidgets:
            self.dockerWidgets[host_id].unloadDocker()

    def loadDockers(self):
        for host_id in self.dockerWidgets:
            self.dockerWidgets[host_id].loadDocker()

    def setSizeHint(self, size):
        self.size = QSize(size[0], size[1])

    def getDefaultSizeHint(self):
        width_padding = 20
        height_padding = 20

        sizeHint = super().sizeHint()

        container_width = sizeHint.width() + width_padding
        container_height = sizeHint.height() + height_padding

        return QSize(container_width, container_height)
    
    def updateStyleSheet(self):
        self.quickActions.setStyleSheet(stylesheet.nu_tool_options_style)

    def sizeHint(self):
        if self.size:
            return self.size
        else:
            return self.getDefaultSizeHint()
    

    