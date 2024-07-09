from uuid import uuid4
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ..buttons.ToolshelfButtonBar import ToolshelfButtonBar

from ..buttons.ToolshelfPageTabWidget import ToolshelfPageTabWidget
from ....docker_manager import DockerManager
from ..buttons.ToolshelfQuickActions import ToolshelfQuickActions
from ....cfg.CfgToolshelf import CfgToolshelfPanel
from ....cfg.CfgToolshelf import CfgToolshelfDocker
from ...DockerContainer import DockerContainer
from .... import stylesheet

from krita import *

from typing import TYPE_CHECKING, Mapping
if TYPE_CHECKING:
    from ..ToolshelfContainer import ToolshelfContainer



class ToolshelfPage(QWidget):

    dockerWidgets: dict = {}

    def __init__(self, parent: "ToolshelfContainer", ID: any, data: CfgToolshelfPanel):
        super(ToolshelfPage, self).__init__(parent)
        self.toolshelf: "ToolshelfContainer" = parent
        self.ID = ID

        self.shelfLayout = QVBoxLayout()
        self.shelfLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.shelfLayout.setContentsMargins(0, 0, 0, 0)
        self.shelfLayout.setSpacing(1)
        self.setLayout(self.shelfLayout)

        self.docker_manager = self.toolshelf.dockWidget.docker_manager

        self.ID = ID
        self.dockerWidgets: dict[any, DockerContainer] = {}
        self.size = None
        self.panelProperties = data

        self.quickActions = ToolshelfQuickActions(self.panelProperties.quick_actions, self)
        self.quickActions.bar.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        for btnKey in self.quickActions.bar._buttons:
            self.quickActions.bar._buttons[btnKey].setFixedHeight(self.panelProperties.actionHeight)
            self.quickActions.bar._buttons[btnKey].setMinimumWidth(self.panelProperties.actionHeight)
            self.quickActions.bar._buttons[btnKey].setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        self.shelfLayout.addWidget(self.quickActions)
        
        #region Generation

        self.bgWidget = QWidget(self)
        self.bgWidget.setLayout(QVBoxLayout())
        self.bgWidget.layout().setSpacing(0)
        self.bgWidget.layout().setContentsMargins(0,0,0,0)
        self.bgWidget.setAutoFillBackground(True)
        self.shelfLayout.addWidget(self.bgWidget)

        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setAutoFillBackground(True)
        self.bgWidget.layout().addWidget(self.splitter)

        data = self.panelProperties
        
        if data.size_x != 0 and data.size_y != 0:
            size = [data.size_x, data.size_y]
            self.setSizeHint(size)


        widget_groups: Mapping[int, Mapping[int, list[DockerContainer | ToolshelfQuickActions]]] = {}

        for dockerData in self.panelProperties.additional_dockers:     
            actionInfo: CfgToolshelfDocker = dockerData
            if actionInfo.section_type == "docker":
                actionWidget = DockerContainer(self, actionInfo.id, self.docker_manager)

                if actionInfo.size_x != 0 and actionInfo.size_y != 0:
                    size = [actionInfo.size_x, actionInfo.size_y]
                    actionWidget.setSizeHint(size)

                if actionInfo.nesting_mode == "docking":
                    actionWidget.setDockMode(True)

                if actionInfo.unloaded_visibility == "hidden":
                    actionWidget.setHiddenMode(True)
                
                if actionInfo.loading_priority == "passive":
                    actionWidget.setPassiveMode(True)

                self.dockerWidgets[actionInfo.id] = actionWidget
            elif actionInfo.section_type == "actions":
                actionWidget = ToolshelfQuickActions(actionInfo.action_section_contents, self)
                actionWidget.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
                for btn in actionWidget.bar._buttons:
                    actionBtn = actionWidget.bar._buttons[btn]

                    if actionInfo.action_section_btn_height != 0:
                        actionBtn.setFixedHeight(actionInfo.action_section_btn_height)
                    if actionInfo.action_section_btn_width != 0:
                        actionBtn.setFixedWidth(actionInfo.action_section_btn_width)

                    actionBtn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)                    

                if actionInfo.action_section_alignment_x != "none" or actionInfo.action_section_alignment_y != "none":
                    align_x = actionInfo.action_section_alignment_x
                    align_y = actionInfo.action_section_alignment_y

                    alignment_x = Qt.AlignmentFlag.AlignLeft
                    alignment_y = Qt.AlignmentFlag.AlignTop

                    expand_x = QSizePolicy.Policy.Preferred
                    expand_y = QSizePolicy.Policy.Preferred

                    if align_y == "top": alignment_y = Qt.AlignmentFlag.AlignTop
                    elif align_y == "center": alignment_y = Qt.AlignmentFlag.AlignVCenter
                    elif align_y == "center": alignment_y = Qt.AlignmentFlag.AlignVCenter
                    elif align_y == "bottom": alignment_y = Qt.AlignmentFlag.AlignBottom
                    elif align_y == "expanding": expand_y = QSizePolicy.Policy.Expanding

                    if align_x == "left": alignment_x = Qt.AlignmentFlag.AlignLeft
                    elif align_x == "center": alignment_x = Qt.AlignmentFlag.AlignHCenter
                    elif align_x == "right": alignment_x = Qt.AlignmentFlag.AlignRight
                    elif align_x == "expanding": expand_x = QSizePolicy.Policy.Expanding

                    actionWidget.layout().setAlignment(alignment_x | alignment_y)
                    if expand_x:
                        actionWidget.bar.setSizePolicy(expand_x, expand_y)

                if actionInfo.size_x != 0:
                    actionWidget.bar.setMinimumWidth(actionInfo.size_x)
                if actionInfo.size_y != 0:
                    actionWidget.bar.setMinimumHeight(actionInfo.size_y)
            else:
                continue


            
            if actionInfo.panel_y not in widget_groups:
                widget_groups[actionInfo.panel_y] = {}
            if actionInfo.panel_x not in widget_groups[actionInfo.panel_y]:
                widget_groups[actionInfo.panel_y][actionInfo.panel_x] = []

            widget_groups[actionInfo.panel_y][actionInfo.panel_x].append(actionWidget)
            
        def initCell(x, y, splitter: QSplitter):
            if len(widget_groups[y][x]) == 1:
                splitter.addWidget(widget_groups[y][x][0])
            else:
                tabBar = ToolshelfPageTabWidget(self)
                for item in widget_groups[y][x]:
                    if isinstance(item, DockerContainer):
                        title = self.docker_manager.dockerWindowTitle(item.docker_id)
                        tabBar.addTab(item, title)
                    else:
                        tabBar.addTab(item, "Unknown")
                tabBar.setCurrentIndex(0)
                splitter.addWidget(tabBar)

        for panel_y in sorted(widget_groups.keys()):
            columns = widget_groups[panel_y].keys()
            if len(columns) == 1:
                panel_x = list(columns)[0]
                initCell(panel_x, panel_y, self.splitter)
            else:
                subSplitter = QSplitter(Qt.Orientation.Horizontal)
                subSplitter.setAutoFillBackground(True)
                for panel_x in sorted(columns):
                    initCell(panel_x, panel_y, subSplitter)
                self.splitter.addWidget(subSplitter)
                
                

        #endregion

    def activate(self):
        self.toolshelf.changePanel(self.ID)

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
    

    