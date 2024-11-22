from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from touchify.src.components.touchify.dockers.toolshelf.ToolshelfSectionGroup import ToolshelfSectionGroup
from touchify.src.components.touchify.actions.TouchifyActionPanel import TouchifyActionPanel
from touchify.src.cfg.toolshelf.CfgToolshelf import CfgToolshelfPanel
from touchify.src.cfg.toolshelf.CfgToolshelfSection import CfgToolshelfSection
from touchify.src.components.touchify.special.DockerContainer import DockerContainer
from touchify.src.components.touchify.dockers.toolshelf.ToolshelfSpecialSection import ToolshelfSpecialSection
from touchify.src.settings import TouchifyConfig
from touchify.src.stylesheet import Stylesheet
from touchify.src.components.touchify.dockers.toolshelf.ToolshelfSectionSplit import ToolshelfSectionSplit


from krita import *

from typing import TYPE_CHECKING, Mapping
if TYPE_CHECKING:
    from .ToolshelfPageStack import ToolshelfPageStack
    from . import ToolshelfPanel


class ToolshelfPanel(QWidget):
    
    dockerWidgets: dict = {}
    
    pageLoadedSignal = pyqtSignal()
    pageUnloadSignal = pyqtSignal()

    def __init__(self, parent: QWidget | None, toolshelf: "ToolshelfPageStack", data: CfgToolshelfPanel):
        super(ToolshelfPanel, self).__init__(parent)
        self.page_stack: "ToolshelfPageStack" = toolshelf

        self.setAutoFillBackground(True)

        self.shelfLayout = QVBoxLayout(self)
        self.shelfLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.shelfLayout.setContentsMargins(0, 0, 0, 0)
        self.shelfLayout.setSpacing(0)
        self.setLayout(self.shelfLayout)


        self.tabType = data.tab_type

        self.docker_manager = self.page_stack.rootWidget.parent_docker.docker_manager
        self.actions_manager = self.page_stack.rootWidget.parent_docker.actions_manager

        self.dockerWidgets: dict[any, DockerContainer] = {}
        self.size = None
        self.panelProperties = data
        self._initPageActions()
        self._initSections()


        qApp.paletteChanged.connect(self.updateStyleSheet)
        self.updateStyleSheet()
    

    #region Init

    def _initPageActions(self):
        actionsList = self.panelProperties.actions
        actionHeight = int(self.panelProperties.action_height * TouchifyConfig.instance().preferences().Interface_ToolshelfActionBarScale)

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

        self.splitter = ToolshelfSectionSplit(Qt.Orientation.Vertical)
        self.bgWidget.layout().addWidget(self.splitter)


        data = self.panelProperties
        
        if data.size_x != 0 and data.size_y != 0:
            size = [data.size_x, data.size_y]
            self.setSizeHint(size)

        widget_groups: Mapping[int, Mapping[int, list[QWidget]]] = {}
        
        for actionInfo in self.panelProperties.sections:     
            actionInfo: CfgToolshelfSection

            if actionInfo.section_type == CfgToolshelfSection.SectionType.Docker:
                actionWidget = self._createDockerSection(actionInfo)
            elif actionInfo.section_type == CfgToolshelfSection.SectionType.Actions:
                actionWidget = self._createActionSection(actionInfo)
            elif actionInfo.section_type == CfgToolshelfSection.SectionType.Subpanel:
                actionWidget = self._createSubpageSection(actionInfo)
            elif actionInfo.section_type == CfgToolshelfSection.SectionType.Special:
                actionWidget = self._createSpecialSection(actionInfo)
            else:
                actionWidget = None

            if actionWidget == None: continue

            if actionInfo.panel_y not in widget_groups:
                widget_groups[actionInfo.panel_y] = {}
            if actionInfo.panel_x not in widget_groups[actionInfo.panel_y]:
                widget_groups[actionInfo.panel_y][actionInfo.panel_x] = []

            widget_groups[actionInfo.panel_y][actionInfo.panel_x].append(actionWidget)

        for panel_y in sorted(widget_groups.keys()):
            columns = widget_groups[panel_y].keys()
            if len(columns) == 1:
                panel_x = list(columns)[0]
                self._initSectionCell(panel_x, panel_y, self.splitter, widget_groups)
            else:
                subSplitter = ToolshelfSectionSplit(Qt.Orientation.Horizontal)
                subSplitter.setAutoFillBackground(True)
                for panel_x in sorted(columns):
                    self._initSectionCell(panel_x, panel_y, subSplitter, widget_groups)
                self.splitter.addWidget(subSplitter)

    def _initSectionCell(self, x: int, y: int, splitter: QSplitter, widget_groups: Mapping[int, Mapping[int, list[QWidget]]]):
        if len(widget_groups[y][x]) == 1:
            splitter.addWidget(widget_groups[y][x][0])
        else:
            tabBar = ToolshelfSectionGroup(self)
            for item in widget_groups[y][x]:
                if isinstance(item, DockerContainer): tabBar.addTab(item, self.docker_manager.dockerWindowTitle(item.docker_id))
                elif isinstance(item, TouchifyActionPanel): tabBar.addTab(item, item.title)
                elif isinstance(item, ToolshelfPanel): tabBar.addTab(item, item.title())
                else: tabBar.addTab(item, "Unknown")
            tabBar.setCurrentIndex(0)
            splitter.addWidget(tabBar)
    
    #endregion

    #region Section Construction

    def _createActionSection(self, actionInfo: CfgToolshelfSection):
        
        display_type = TouchifyActionPanel.DisplayType.Toolbar
        if actionInfo.action_section_display_mode == CfgToolshelfSection.ActionSectionDisplayMode.Flat:
            display_type = TouchifyActionPanel.DisplayType.ToolbarFlat

        if actionInfo.ignore_scaling:
            scale = 1
        else:
            scale = TouchifyConfig.instance().preferences().Interface_ToolshelfActionSectionScale

        
        icon_size = int(actionInfo.action_section_icon_size * scale)
        fixed_width = int(actionInfo.action_section_btn_width * scale)
        fixed_height = int(actionInfo.action_section_btn_height * scale)

        min_size_x = int(actionInfo.min_size_x * scale)
        min_size_y = int(actionInfo.min_size_y * scale)
        max_size_x = int(actionInfo.max_size_x * scale)
        max_size_y = int(actionInfo.max_size_y * scale)
        size_x = int(actionInfo.size_x * scale)
        size_y = int(actionInfo.size_y * scale)

        

               
        actionWidget = TouchifyActionPanel(cfg=actionInfo.action_section_contents, parent=self, actions_manager=self.actions_manager, type=display_type, icon_width=icon_size, icon_height=icon_size, item_height=fixed_height, item_width=fixed_width)
        actionWidget.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        if actionInfo.hasDisplayName(): actionWidget.setTitle(actionInfo.display_name)
        else: actionWidget.setTitle(actionInfo.action_section_id)

        if actionInfo.action_section_alignment_x != CfgToolshelfSection.SectionAlignmentX.Nothing or actionInfo.action_section_alignment_y != CfgToolshelfSection.SectionAlignmentY.Nothing:
            align_x = actionInfo.action_section_alignment_x
            align_y = actionInfo.action_section_alignment_y

            alignment_x = Qt.AlignmentFlag.AlignLeft
            alignment_y = Qt.AlignmentFlag.AlignTop

            expand_x = QSizePolicy.Policy.Preferred
            expand_y = QSizePolicy.Policy.Preferred

            if align_y == CfgToolshelfSection.SectionAlignmentY.Top: alignment_y = Qt.AlignmentFlag.AlignTop
            elif align_y == CfgToolshelfSection.SectionAlignmentY.Center: alignment_y = Qt.AlignmentFlag.AlignVCenter
            elif align_y == CfgToolshelfSection.SectionAlignmentY.Bottom: alignment_y = Qt.AlignmentFlag.AlignBottom
            elif align_y == CfgToolshelfSection.SectionAlignmentY.Expanding: expand_y = QSizePolicy.Policy.Expanding

            if align_x == CfgToolshelfSection.SectionAlignmentX.Left: alignment_x = Qt.AlignmentFlag.AlignLeft
            elif align_x == CfgToolshelfSection.SectionAlignmentX.Center: alignment_x = Qt.AlignmentFlag.AlignHCenter
            elif align_x == CfgToolshelfSection.SectionAlignmentX.Right: alignment_x = Qt.AlignmentFlag.AlignRight
            elif align_x == CfgToolshelfSection.SectionAlignmentX.Expanding: expand_x = QSizePolicy.Policy.Expanding

            actionWidget.layout().setAlignment(alignment_x | alignment_y)
            if expand_x: actionWidget.setSizePolicy(expand_x, expand_y)

        if size_x != 0 or size_y != 0:
            if size_x != 0: actionWidget.setFixedWidth(size_x)
            if size_y != 0: actionWidget.setFixedHeight(size_y)
        else:
            if min_size_x != 0: actionWidget.setMinimumWidth(min_size_x)
            if min_size_y != 0: actionWidget.setMinimumHeight(min_size_y)
            if max_size_x != 0: actionWidget.setMaximumWidth(max_size_x)
            if max_size_y != 0: actionWidget.setMaximumHeight(max_size_y)

        return actionWidget
    
    def _createDockerSection(self, actionInfo: CfgToolshelfSection):
        actionWidget = DockerContainer(self, actionInfo.docker_id, self.docker_manager)
        if actionInfo.docker_nesting_mode == CfgToolshelfSection.DockerNestingMode.Docking:
            actionWidget.setDockMode(True)

        if actionInfo.docker_unloaded_visibility == CfgToolshelfSection.DockerUnloadedVisibility.Hidden:
            actionWidget.setHiddenMode(True)
        
        if actionInfo.docker_loading_priority == CfgToolshelfSection.DockerLoadingPriority.Passive:
            actionWidget.setPassiveMode(True)
            
        if actionInfo.size_x != 0 and actionInfo.size_y != 0:
            actionWidget.setSizeHint([actionInfo.size_x, actionInfo.size_y])

        if actionInfo.min_size_x != 0: actionWidget.setMinimumWidth(actionInfo.min_size_x)
        if actionInfo.min_size_y != 0: actionWidget.setMinimumHeight(actionInfo.min_size_y)
        if actionInfo.max_size_x != 0: actionWidget.setMaximumWidth(actionInfo.max_size_x)
        if actionInfo.max_size_y != 0: actionWidget.setMaximumHeight(actionInfo.max_size_y)

        self.dockerWidgets[actionInfo.docker_id] = actionWidget
        self.pageLoadedSignal.connect(actionWidget.loadWidget)
        self.pageUnloadSignal.connect(actionWidget.unloadWidget)

        return actionWidget
    
    def _createSpecialSection(self, actionInfo: CfgToolshelfSection):
        actionWidget = ToolshelfSpecialSection(self, actionInfo, self.actions_manager)
            
        if actionInfo.size_x != 0 and actionInfo.size_y != 0: 
            actionWidget.setSizeHint([actionInfo.size_x, actionInfo.size_y])

        if actionInfo.min_size_x != 0: actionWidget.setMinimumWidth(actionInfo.min_size_x)
        if actionInfo.min_size_y != 0: actionWidget.setMinimumHeight(actionInfo.min_size_y)
        if actionInfo.max_size_x != 0: actionWidget.setMaximumWidth(actionInfo.max_size_x)
        if actionInfo.max_size_y != 0: actionWidget.setMaximumHeight(actionInfo.max_size_y)
        return actionWidget

    def _createSubpageSection(self, actionInfo: CfgToolshelfSection):
        actionWidget = ToolshelfPanel(self, self.page_stack, actionInfo.subpanel_data)

        if actionInfo.size_x != 0 and actionInfo.size_y != 0: 
            actionWidget.setSizeHint([actionInfo.size_x, actionInfo.size_y])

        if actionInfo.min_size_x != 0: actionWidget.setMinimumWidth(actionInfo.min_size_x)
        if actionInfo.min_size_y != 0: actionWidget.setMinimumHeight(actionInfo.min_size_y)
        if actionInfo.max_size_x != 0: actionWidget.setMaximumWidth(actionInfo.max_size_x)
        if actionInfo.max_size_y != 0: actionWidget.setMaximumHeight(actionInfo.max_size_y)
        
        self.pageLoadedSignal.connect(actionWidget.loadPage)
        self.pageUnloadSignal.connect(actionWidget.unloadPage)
        return actionWidget
    
    #endregion

    def title(self):
        if self.panelProperties:
            if self.panelProperties.hasDisplayName(): 
                return self.panelProperties.display_name
            else:
                return self.panelProperties.id
        else:
            return "Unknown Panel"

    def unloadPage(self):
        self.pageUnloadSignal.emit()

    def loadPage(self):
        self.pageLoadedSignal.emit()

    def setSizeHint(self, size):
        self.size = QSize(size[0], size[1])
    
    def updateStyleSheet(self):
        self.quickActions.setStyleSheet(Stylesheet.instance().touchify_toolshelf_header)

    def sizeHint(self):
        resultingSize = super().sizeHint()
        if self.size: resultingSize = self.size

        resultingSize.setWidth(resultingSize.width())
        resultingSize.setHeight(resultingSize.height())

        return resultingSize