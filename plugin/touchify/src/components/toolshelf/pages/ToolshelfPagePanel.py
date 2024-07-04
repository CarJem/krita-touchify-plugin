from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ....docker_manager import DockerManager
from ..buttons.ToolshelfQuickActions import ToolshelfQuickActions
from .ToolshelfPage import ToolshelfPage
from ....cfg.CfgToolshelf import CfgToolboxPanel
from ....cfg.CfgToolshelf import CfgToolboxPanelDocker
from ...DockerContainer import DockerContainer
from .... import stylesheet

from krita import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..ToolshelfContainer import ToolshelfContainer

class ToolshelfPagePanel(ToolshelfPage):

    dockerWidgets: dict = {}

    def __init__(self, parent: "ToolshelfContainer", ID: any, data: CfgToolboxPanel):
        super(ToolshelfPagePanel, self).__init__(parent, ID)

        self.docker_manager = self.toolshelf.dockWidget.docker_manager

        self.ID = ID
        self.dockerWidgets: dict[any, DockerContainer] = {}
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


        widget_groups: dict[int, list[DockerContainer]] = {}

        for dockerData in self.panelProperties.additional_dockers:     
            dockerInfo: CfgToolboxPanelDocker = dockerData
            dockerWidget = DockerContainer(self, dockerInfo.id, self.docker_manager)

            if dockerInfo.size_x != 0 and dockerInfo.size_y != 0:
                size = [dockerInfo.size_x, dockerInfo.size_y]
                dockerWidget.setSizeHint(size)

            if dockerInfo.nesting_mode == "docking":
                dockerWidget.setDockMode(True)

            if dockerInfo.unloaded_visibility == "hidden":
                dockerWidget.setHiddenMode(True)
            
            if dockerInfo.loading_priority == "passive":
                dockerWidget.setPassiveMode(True)
                

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
                    title = self.docker_manager.dockerWindowTitle(item.docker_id)
                    tabBar.addTab(item, title)

                self.splitter.addWidget(tabBar)
        #endregion


    def resizeEvent(self, event: QResizeEvent):
        self.toolshelf.dockWidget.onSizeChanged()
        super().resizeEvent(event)

    def unloadPage(self):
        for host_id in self.dockerWidgets:
            self.dockerWidgets[host_id].unloadWidget()

    def loadPage(self):
        for host_id in self.dockerWidgets:
            self.dockerWidgets[host_id].loadWidget()

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
        self.quickActions.setStyleSheet(stylesheet.nu_toolshelf_button_style)

    def sizeHint(self):
        if self.size:
            return self.size
        else:
            return self.getDefaultSizeHint()
    

    