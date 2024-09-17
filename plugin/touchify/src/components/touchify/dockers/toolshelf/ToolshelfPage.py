from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from .ToolshelfSectionGroup import ToolshelfSectionGroup
from ...actions.TouchifyActionPanel import TouchifyActionPanel
from .....cfg.toolshelf.CfgToolshelf import CfgToolshelfPanel
from .....cfg.toolshelf.CfgToolshelf import CfgToolshelfSection
from ...special.DockerContainer import DockerContainer
from .ToolshelfSpecialWidget import ToolshelfSpecialWidget
from .....stylesheet import Stylesheet
from .ToolshelfPageSplitter import ToolshelfSplitter

from krita import *

from typing import TYPE_CHECKING, Mapping
if TYPE_CHECKING:
    from .ToolshelfPageStack import ToolshelfPageStack

class ToolshelfPage(QWidget):
    
    dockerWidgets: dict = {}
    
    pageLoadedSignal = pyqtSignal()
    pageUnloadSignal = pyqtSignal()

    def __init__(self, parent: "ToolshelfPageStack", ID: any, data: CfgToolshelfPanel):
        super(ToolshelfPage, self).__init__(parent)
        self.toolshelf: "ToolshelfPageStack" = parent
        self.ID = ID

        self.setAutoFillBackground(True)

        self.shelfLayout = QVBoxLayout(self)
        self.shelfLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.shelfLayout.setContentsMargins(0, 0, 0, 0)
        self.shelfLayout.setSpacing(0)
        self.setLayout(self.shelfLayout)


        self.tabType = data.tab_type

        self.docker_manager = self.toolshelf.rootWidget.parent_docker.docker_manager
        self.actions_manager = self.toolshelf.rootWidget.parent_docker.actions_manager

        self.ID = ID
        self.dockerWidgets: dict[any, DockerContainer] = {}
        self.size = None
        self.panelProperties = data
        self._initPageActions()
        self._initSections()


        qApp.paletteChanged.connect(self.updateStyleSheet)
        self.updateStyleSheet()
    

    def _initPageActions(self):
        actionsList = self.panelProperties.actions
        actionHeight = self.panelProperties.action_height

        self.quickActions = TouchifyActionPanel(actionsList, self, self.actions_manager)
        self.quickActions.setAutoFillBackground(True)
        self.quickActions.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        
        for btnKey in self.quickActions._buttons:
            self.quickActions._buttons[btnKey].setFixedHeight(actionHeight)
            self.quickActions._buttons[btnKey].setMinimumWidth(actionHeight)
            self.quickActions._buttons[btnKey].setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        self.shelfLayout.addWidget(self.quickActions)
      
    def _initSections(self):    


        self.bgWidget = QWidget(self)
        self.bgWidget.setLayout(QVBoxLayout(self))
        self.bgWidget.layout().setSpacing(0)
        self.bgWidget.layout().setContentsMargins(0,0,0,0)
        self.bgWidget.setAutoFillBackground(True)
        self.shelfLayout.addWidget(self.bgWidget)

        self.splitter = ToolshelfSplitter(Qt.Orientation.Vertical)
        self.bgWidget.layout().addWidget(self.splitter)


        data = self.panelProperties
        
        if data.size_x != 0 and data.size_y != 0:
            size = [data.size_x, data.size_y]
            self.setSizeHint(size)

        widget_groups = self._createSections()
        self._insertSections(widget_groups)

    def _createSections(self):
        widget_groups: Mapping[int, Mapping[int, list[DockerContainer | TouchifyActionPanel]]] = {}
        
        for dockerData in self.panelProperties.sections:     
            actionInfo: CfgToolshelfSection = dockerData
            actionWidget = self._createSection(actionInfo)
            if actionWidget == None: continue

            if actionInfo.panel_y not in widget_groups:
                widget_groups[actionInfo.panel_y] = {}
            if actionInfo.panel_x not in widget_groups[actionInfo.panel_y]:
                widget_groups[actionInfo.panel_y][actionInfo.panel_x] = []

            widget_groups[actionInfo.panel_y][actionInfo.panel_x].append(actionWidget)
        return widget_groups
    
    def _createActionSection(self, actionInfo: CfgToolshelfSection):
        
        display_type = "toolbar"
        if actionInfo.action_section_display_mode == "flat":
            display_type = "toolbar_flat"
        
        icon_size = actionInfo.action_section_icon_size
        fixed_width = actionInfo.action_section_btn_width
        fixed_height = actionInfo.action_section_btn_height
               
        actionWidget = TouchifyActionPanel(cfg=actionInfo.action_section_contents, parent=self, actions_manager=self.actions_manager, type=display_type, icon_width=icon_size, icon_height=icon_size, item_height=fixed_height, item_width=fixed_width)
        actionWidget.setTitle(actionInfo.action_section_name)
        actionWidget.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        #region ActionContainer Setup    

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
                actionWidget.setSizePolicy(expand_x, expand_y)

        if actionInfo.size_x != 0 or actionInfo.size_y != 0:
            if actionInfo.size_x != 0:
                actionWidget.setFixedWidth(actionInfo.size_x)
            if actionInfo.size_y != 0:
                actionWidget.setFixedHeight(actionInfo.size_y)
        else:
            if actionInfo.min_size_x != 0:
                actionWidget.setMinimumWidth(actionInfo.min_size_x)
            if actionInfo.min_size_y != 0:
                actionWidget.setMinimumHeight(actionInfo.min_size_y)
            if actionInfo.max_size_x != 0:
                actionWidget.setMaximumWidth(actionInfo.max_size_x)
            if actionInfo.max_size_y != 0:
                actionWidget.setMaximumHeight(actionInfo.max_size_y)
        #endregion
        return actionWidget
    
    def _createDockerSection(self, actionInfo: CfgToolshelfSection):
        actionWidget = DockerContainer(self, actionInfo.id, self.docker_manager)
        if actionInfo.docker_nesting_mode == "docking":
            actionWidget.setDockMode(True)

        if actionInfo.docker_unloaded_visibility == "hidden":
            actionWidget.setHiddenMode(True)
        
        if actionInfo.docker_loading_priority == "passive":
            actionWidget.setPassiveMode(True)
            
        if actionInfo.size_x != 0 and actionInfo.size_y != 0:
            size = [actionInfo.size_x, actionInfo.size_y]
            actionWidget.setSizeHint(size)
        if actionInfo.min_size_x != 0:
            actionWidget.setMinimumWidth(actionInfo.min_size_x)
        if actionInfo.min_size_y != 0:
            actionWidget.setMinimumHeight(actionInfo.min_size_y)
        if actionInfo.max_size_x != 0:
            actionWidget.setMaximumWidth(actionInfo.max_size_x)
        if actionInfo.max_size_y != 0:
            actionWidget.setMaximumHeight(actionInfo.max_size_y)


        self.dockerWidgets[actionInfo.id] = actionWidget
        self.pageLoadedSignal.connect(actionWidget.loadWidget)
        self.pageUnloadSignal.connect(actionWidget.unloadWidget)
        return actionWidget
    
    def _createSpecialSection(self, actionInfo: CfgToolshelfSection):
        actionWidget = ToolshelfSpecialWidget(self, actionInfo)
            
        if actionInfo.size_x != 0 and actionInfo.size_y != 0:
            size = [actionInfo.size_x, actionInfo.size_y]
            actionWidget.setSizeHint(size)
        if actionInfo.min_size_x != 0:
            actionWidget.setMinimumWidth(actionInfo.min_size_x)
        if actionInfo.min_size_y != 0:
            actionWidget.setMinimumHeight(actionInfo.min_size_y)
        if actionInfo.max_size_x != 0:
            actionWidget.setMaximumWidth(actionInfo.max_size_x)
        if actionInfo.max_size_y != 0:
            actionWidget.setMaximumHeight(actionInfo.max_size_y)
        return actionWidget

    def _createSection(self, actionInfo: CfgToolshelfSection):
        if actionInfo.section_type == CfgToolshelfSection.SectionType.Docker:
            return self._createDockerSection(actionInfo)
        elif actionInfo.section_type == CfgToolshelfSection.SectionType.Actions:
            return self._createActionSection(actionInfo)
        elif actionInfo.section_type == CfgToolshelfSection.SectionType.Special:
            return self._createSpecialSection(actionInfo)
        else:
            return None
              
    def _insertSections(self, widget_groups: Mapping[int, Mapping[int, list[DockerContainer | TouchifyActionPanel]]]):
        def initCell(x, y, splitter: QSplitter):
            if len(widget_groups[y][x]) == 1:
                splitter.addWidget(widget_groups[y][x][0])
            else:
                tabBar = ToolshelfSectionGroup(self)
                for item in widget_groups[y][x]:
                    if isinstance(item, DockerContainer):
                        title = self.docker_manager.dockerWindowTitle(item.docker_id)
                        tabBar.addTab(item, title)
                    elif isinstance(item, TouchifyActionPanel):
                        tabBar.addTab(item, item.title)
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
                subSplitter = ToolshelfSplitter(Qt.Orientation.Horizontal)
                subSplitter.setAutoFillBackground(True)
                for panel_x in sorted(columns):
                    initCell(panel_x, panel_y, subSplitter)
                self.splitter.addWidget(subSplitter)

    def activate(self):
        self.toolshelf.changePanel(self.ID)

    def resizeEvent(self, event: QResizeEvent):
        self.toolshelf.rootWidget.onSizeChanged()
        super().resizeEvent(event)

    def unloadPage(self):
        self.pageUnloadSignal.emit()

    def loadPage(self):
        self.pageLoadedSignal.emit()

    def setSizeHint(self, size):
        self.size = QSize(size[0] + 20, size[1] + 20)

    def getDefaultSizeHint(self):
        width_padding = 20
        height_padding = 20

        sizeHint = super().sizeHint()

        container_width = sizeHint.width() + width_padding
        container_height = sizeHint.height() + height_padding

        return QSize(container_width, container_height)
    
    def updateStyleSheet(self):
        self.quickActions.setStyleSheet(Stylesheet.instance().touchify_toolshelf_header)

    def sizeHint(self):
        if self.size:
            return self.size
        else:
            return self.getDefaultSizeHint()
    

    