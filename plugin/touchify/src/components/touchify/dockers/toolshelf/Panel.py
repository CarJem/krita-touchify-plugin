from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.components.touchify.actions.TouchifyActionPanel import TouchifyActionPanel
from touchify.src.cfg.toolshelf.ToolshelfData import ToolshelfDataPage
from touchify.src.cfg.toolshelf.ToolshelfDataSection import ToolshelfDataSection
from touchify.src.components.touchify.special.BrushBlendingSelector import BrushBlendingSelector
from touchify.src.components.touchify.special.BrushFlowSlider import BrushFlowSlider
from touchify.src.components.touchify.special.BrushOpacitySlider import BrushOpacitySlider
from touchify.src.components.touchify.special.BrushRotationSlider import BrushRotationSlider
from touchify.src.components.touchify.special.BrushSizeSlider import BrushSizeSlider
from touchify.src.components.touchify.special.CanvasColorPicker import CanvasColorPicker
from touchify.src.components.touchify.special.DockerContainer import DockerContainer

from touchify.src.components.touchify.special.LayerBlendingSelector import LayerBlendingSelector
from touchify.src.components.touchify.special.LayerLabelBox import LayerLabelBox
from touchify.src.settings import TouchifySettings
from touchify.src.stylesheet import Stylesheet


from krita import *

from typing import TYPE_CHECKING, Mapping
if TYPE_CHECKING:
    from .PageStack import PageStack


class Panel(QWidget):

    class SectionSplit(QWidget):

        
        def __init__(self, orientation: Qt.Orientation, name: str = "", parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self.edit_mode = False
            self.orientation = orientation
            if name != "": self.setObjectName(name)
            
            self.ourLayout = QGridLayout(self)
            self.ourLayout.setContentsMargins(0,0,0,0)
            self.ourLayout.setSpacing(0)
            self.setLayout(self.ourLayout)

            self.section_widgets: list[tuple[QWidget, QPushButton]] = []


        def setEditMode(self, value):
            self.edit_mode = value
            
            for widget, edit_area in self.section_widgets:
                if isinstance(widget, Panel.SectionSplit):
                    widget: Panel.SectionSplit
                    widget.setEditMode(value)
                elif isinstance(widget, Panel):
                    widget: Panel
                    widget.setEditMode(value)
                else:
                    edit_area.setVisible(self.edit_mode)
                    widget.stackUnder(edit_area)

        def createEditSelector(self):
            result = QPushButton(self)
            result.setFlat(True)
            result.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            result.setContentsMargins(0,0,0,0)
            result.setStyleSheet(Stylesheet.instance().touchify_edit_mode_selector())
            result.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            result.setVisible(False)
            return result

        def addWidget(self, widget: QWidget, x: int, y: int):
            edit_container = self.createEditSelector()
            self.section_widgets.append((widget, edit_container))

            self.ourLayout.addWidget(edit_container, y, x)
            self.ourLayout.addWidget(widget, y, x)
            
    class SectionGroup(QWidget):
        def __init__(self, parent: "Panel", tab_type: str) -> None:
            super().__init__(parent)
            
            self.panel: "Panel" = parent
            self.tabTitles: dict[int, str] = {}

            self.setAutoFillBackground(True)

            self.__layout = QVBoxLayout(self)
            self.__layout.setSpacing(1)
            self.__layout.setContentsMargins(0,0,0,0)
            self.setLayout(self.__layout)
            
            self.mode = tab_type

            if self.mode == ToolshelfDataPage.TabType.Buttons:
                self.tabButton = QPushButton(self)
                self.tabButtonMenu = QMenu(self)
                self.tabButton.setMenu(self.tabButtonMenu)
                self.__layout.addWidget(self.tabButton)   
            else:
                self.tabBar = QTabBar(self)
                self.tabBar.setExpanding(False)
                self.tabBar.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
                self.tabBar.currentChanged.connect(self.onTabBarIndexChanged)
                self.__layout.addWidget(self.tabBar) 

            self.stackPanel = QStackedWidget(self)
            self.stackPanel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            self.stackPanel.currentChanged.connect(self.onCurrentChanged)
            self.__layout.addWidget(self.stackPanel)    
        
        def setCurrentIndex(self, index):
            self.stackPanel.setCurrentIndex(index)
            self.onCurrentChanged(index)

        def addTab(self, item: QWidget, title: str):
            index = self.stackPanel.addWidget(item)
            if self.mode == "buttons":
                self.tabButtonMenu.addAction(title, lambda: self.setCurrentIndex(index))
                self.tabTitles[index] = title
                self.onCurrentChanged(0)
            else:
                self.tabBar.addTab(title)
                self.tabTitles[index] = title

        def onTabBarIndexChanged(self):
            self.setCurrentIndex(self.tabBar.currentIndex())

        def onCurrentChanged(self, index):
            for i in range(0, self.stackPanel.count()):

                widget = self.stackPanel.widget(i)
                if i == index:
                    if isinstance(widget, DockerContainer):  
                        if widget.isEnabled() == False: widget.loadWidget()


                    policy = QSizePolicy.Policy.Preferred
                    widget.setSizePolicy(policy, policy)
                    widget.setEnabled(True)
                    widget.updateGeometry()
                    widget.adjustSize()
                else:
                    if isinstance(widget, DockerContainer): 
                        if widget.isEnabled(): widget.unloadWidget()

                    policy = QSizePolicy.Policy.Ignored
                    widget.setSizePolicy(policy, policy)
                    widget.setDisabled(True)
                    widget.updateGeometry()
                    widget.adjustSize()

            if self.mode == ToolshelfDataPage.TabType.Buttons:
                if index in self.tabTitles:
                    self.tabButton.setText(self.tabTitles[index])
            else:
                pass

            self.adjustSize()
            self.stackPanel.adjustSize()
            self.panel.adjustSize()
            self.panel.page_stack.rootWidget.requestViewUpdate()
        
    dockerWidgets: dict = {}
    
    pageLoadedSignal = pyqtSignal()
    pageUnloadSignal = pyqtSignal()

    def __init__(self, parent: QWidget | None, toolshelf: "PageStack", data: ToolshelfDataPage):
        super(Panel, self).__init__(parent)
        self.page_stack: "PageStack" = toolshelf
        self.panel_config = data

        self.docker_manager = self.page_stack.rootWidget.parent_docker.docker_manager
        self.actions_manager = self.page_stack.rootWidget.parent_docker.actions_manager
        self.dockerWidgets: dict[any, DockerContainer] = {}
        self.size = None

        self.setAutoFillBackground(True)

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)
        self.setLayout(self.root_layout)

        self.actions_panel = TouchifyActionPanel(self.panel_config.actions, self, self.actions_manager)
        self.actions_panel.setAutoFillBackground(True)
        self.actions_panel.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.root_layout.addWidget(self.actions_panel)
        
        for btnKey in self.actions_panel._buttons:
            self.actions_panel._buttons[btnKey].setFixedHeight(int(self.panel_config.action_height * TouchifySettings.instance().preferences().Interface_ToolshelfActionBarScale))
            self.actions_panel._buttons[btnKey].setMinimumWidth(int(self.panel_config.action_height * TouchifySettings.instance().preferences().Interface_ToolshelfActionBarScale))
            self.actions_panel._buttons[btnKey].setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)

        self.sections_container = QWidget(self)
        self.sections_container.setLayout(QVBoxLayout(self))
        self.sections_container.layout().setSpacing(0)
        self.sections_container.layout().setContentsMargins(0,0,0,0)
        self.sections_container.setAutoFillBackground(True)
        self.root_layout.addWidget(self.sections_container)

        self.__initSections__()

        qApp.paletteChanged.connect(self.updateStyleSheet)
        self.updateStyleSheet()

    def __initSections__(self):
        def initCell(x: int, y: int, splitter: Panel.SectionSplit, widgets: list[QWidget]):
            if len(widgets) == 1:
                splitter.addWidget(widgets[0], x, y)
            else:
                tabBar = Panel.SectionGroup(self, self.panel_config.tab_type)
                for item in widgets:
                    if isinstance(item, DockerContainer): tabBar.addTab(item, self.docker_manager.dockerWindowTitle(item.docker_id))
                    elif isinstance(item, TouchifyActionPanel): tabBar.addTab(item, item.title)
                    elif isinstance(item, Panel): tabBar.addTab(item, item.title())
                    else: tabBar.addTab(item, "Unknown")
                tabBar.setCurrentIndex(0)
                splitter.addWidget(tabBar, x, y)

        def Section_Actions(actionInfo: ToolshelfDataSection):
            
            display_type = TouchifyActionPanel.DisplayType.Toolbar
            if actionInfo.action_section_display_mode == ToolshelfDataSection.ActionSectionDisplayMode.Flat:
                display_type = TouchifyActionPanel.DisplayType.ToolbarFlat

            if actionInfo.ignore_scaling:
                scale = 1
            else:
                scale = TouchifySettings.instance().preferences().Interface_ToolshelfActionSectionScale

            
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

            if actionInfo.action_section_alignment_x != ToolshelfDataSection.SectionAlignmentX.Nothing or actionInfo.action_section_alignment_y != ToolshelfDataSection.SectionAlignmentY.Nothing:
                align_x = actionInfo.action_section_alignment_x
                align_y = actionInfo.action_section_alignment_y

                alignment_x = Qt.AlignmentFlag.AlignLeft
                alignment_y = Qt.AlignmentFlag.AlignTop

                expand_x = QSizePolicy.Policy.Preferred
                expand_y = QSizePolicy.Policy.Preferred

                if align_y == ToolshelfDataSection.SectionAlignmentY.Top: alignment_y = Qt.AlignmentFlag.AlignTop
                elif align_y == ToolshelfDataSection.SectionAlignmentY.Center: alignment_y = Qt.AlignmentFlag.AlignVCenter
                elif align_y == ToolshelfDataSection.SectionAlignmentY.Bottom: alignment_y = Qt.AlignmentFlag.AlignBottom
                elif align_y == ToolshelfDataSection.SectionAlignmentY.Expanding: expand_y = QSizePolicy.Policy.Expanding

                if align_x == ToolshelfDataSection.SectionAlignmentX.Left: alignment_x = Qt.AlignmentFlag.AlignLeft
                elif align_x == ToolshelfDataSection.SectionAlignmentX.Center: alignment_x = Qt.AlignmentFlag.AlignHCenter
                elif align_x == ToolshelfDataSection.SectionAlignmentX.Right: alignment_x = Qt.AlignmentFlag.AlignRight
                elif align_x == ToolshelfDataSection.SectionAlignmentX.Expanding: expand_x = QSizePolicy.Policy.Expanding

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
        
        def Section_Docker(actionInfo: ToolshelfDataSection):
            actionWidget = DockerContainer(self, actionInfo.docker_id, self.docker_manager)
            if actionInfo.docker_nesting_mode == ToolshelfDataSection.DockerNestingMode.Docking:
                actionWidget.setDockMode(True)

            if actionInfo.docker_unloaded_visibility == ToolshelfDataSection.DockerUnloadedVisibility.Hidden:
                actionWidget.setHiddenMode(True)
            
            if actionInfo.docker_loading_priority == ToolshelfDataSection.DockerLoadingPriority.Passive:
                actionWidget.setPassiveMode(True)
                
            if actionInfo.size_x != 0 and actionInfo.size_y != 0:
                actionWidget.setSizeHint([actionInfo.size_x, actionInfo.size_y])

            if actionInfo.min_size_x != 0: actionWidget.setMinimumWidth(actionInfo.min_size_x)
            if actionInfo.min_size_y != 0: actionWidget.setMinimumHeight(actionInfo.min_size_y)
            if actionInfo.max_size_x != 0: actionWidget.setMaximumWidth(actionInfo.max_size_x)
            if actionInfo.max_size_y != 0: actionWidget.setMaximumHeight(actionInfo.max_size_y)

            self.dockerWidgets[actionInfo.docker_id] = actionWidget
            actionWidget.dockerChanged.connect(self.onDockerUpdate)
            self.pageLoadedSignal.connect(actionWidget.loadWidget)
            self.pageUnloadSignal.connect(actionWidget.unloadWidget)

            return actionWidget
        
        def Section_Special(actionInfo: ToolshelfDataSection):
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BrushBlendingMode:
                actionWidget = BrushBlendingSelector(self)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.LayerBlendingMode:
                actionWidget = LayerBlendingSelector(self)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.LayerLabelBox:
                actionWidget = LayerLabelBox(self)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BrushSizeSlider:
                actionWidget = BrushSizeSlider(self)
                actionWidget.setSourceWindow(self.actions_manager.appEngine.windowSource)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BrushOpacitySlider:
                actionWidget = BrushOpacitySlider(self)
                actionWidget.setSourceWindow(self.actions_manager.appEngine.windowSource)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BrushFlowSlider:
                actionWidget = BrushFlowSlider(self)
                actionWidget.setSourceWindow(self.actions_manager.appEngine.windowSource)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BrushRotationSlider:
                actionWidget = BrushRotationSlider(self)
                actionWidget.setSourceWindow(self.actions_manager.appEngine.windowSource)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BackgroundColorBox:
                actionWidget = CanvasColorPicker(self, CanvasColorPicker.Mode.Background)
                actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.ForegroundColorBox:
                actionWidget = CanvasColorPicker(self, CanvasColorPicker.Mode.Foreground)
                actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            if actionInfo.min_size_x != 0: actionWidget.setMinimumWidth(actionInfo.min_size_x)
            if actionInfo.min_size_y != 0: actionWidget.setMinimumHeight(actionInfo.min_size_y)
            if actionInfo.max_size_x != 0: actionWidget.setMaximumWidth(actionInfo.max_size_x)
            if actionInfo.max_size_y != 0: actionWidget.setMaximumHeight(actionInfo.max_size_y)
            return actionWidget

        def Section_Subpanel(actionInfo: ToolshelfDataSection):
            actionWidget = Panel(self, self.page_stack, actionInfo.subpanel_data)

            if actionInfo.size_x != 0 and actionInfo.size_y != 0: 
                actionWidget.setSizeHint([actionInfo.size_x, actionInfo.size_y])

            if actionInfo.min_size_x != 0: actionWidget.setMinimumWidth(actionInfo.min_size_x)
            if actionInfo.min_size_y != 0: actionWidget.setMinimumHeight(actionInfo.min_size_y)
            if actionInfo.max_size_x != 0: actionWidget.setMaximumWidth(actionInfo.max_size_x)
            if actionInfo.max_size_y != 0: actionWidget.setMaximumHeight(actionInfo.max_size_y)
            
            self.pageLoadedSignal.connect(actionWidget.loadPage)
            self.pageUnloadSignal.connect(actionWidget.unloadPage)
            return actionWidget
        
        widget_groups: Mapping[int, Mapping[int, list[QWidget]]] = {}

        for sectionInfo in self.panel_config.sections:     
            sectionInfo: ToolshelfDataSection
            match sectionInfo.section_type:
                case ToolshelfDataSection.SectionType.Docker:
                    sectionWidget = Section_Docker(sectionInfo)
                case ToolshelfDataSection.SectionType.Actions:
                    sectionWidget = Section_Actions(sectionInfo)
                case ToolshelfDataSection.SectionType.Subpanel:
                    sectionWidget = Section_Subpanel(sectionInfo)
                case ToolshelfDataSection.SectionType.Special:
                    sectionWidget = Section_Special(sectionInfo)
                case _:
                    sectionWidget = None

            if sectionWidget == None: continue

            if sectionInfo.panel_y not in widget_groups:
                widget_groups[sectionInfo.panel_y] = {}
            if sectionInfo.panel_x not in widget_groups[sectionInfo.panel_y]:
                widget_groups[sectionInfo.panel_y][sectionInfo.panel_x] = []

            widget_groups[sectionInfo.panel_y][sectionInfo.panel_x].append(sectionWidget)

        self.sections_stack = Panel.SectionSplit(Qt.Orientation.Vertical, "root")
        self.sections_container.layout().addWidget(self.sections_stack)

        for row_key in sorted(widget_groups.keys()):
            row_length = len(widget_groups[row_key].keys())
            row_items = [widget_groups[row_key][ix] for ix in sorted(widget_groups[row_key].keys())]

            iy = sorted(widget_groups.keys()).index(row_key)

            if row_length == 1:
                initCell(0, iy, self.sections_stack, row_items[0])
            else:
                row_splitter = Panel.SectionSplit(Qt.Orientation.Horizontal, f"sub_root_{iy}")
                row_splitter.setAutoFillBackground(True)
                for ix in range(0, row_length):
                    initCell(ix, 0, row_splitter, row_items[ix])
                self.sections_stack.addWidget(row_splitter, 0, iy)

    def setEditMode(self, value: bool):
        self.sections_stack.setEditMode(value)

    def onDockerUpdate(self):
        self.page_stack.onDockerUpdate()

    def title(self):
        if self.panel_config:
            if self.panel_config.hasDisplayName(): 
                return self.panel_config.display_name
            else:
                return self.panel_config.id
        else:
            return "Unknown Panel"

    def unloadPage(self):
        self.pageUnloadSignal.emit()

    def loadPage(self):
        self.pageLoadedSignal.emit()

    def setSizeHint(self, size):
        self.size = QSize(size[0], size[1])
    
    def updateStyleSheet(self):
        self.actions_panel.setStyleSheet(Stylesheet.instance().touchify_toolshelf_header)

    def sizeHint(self):
        resultingSize = super().sizeHint()
        if self.size: resultingSize = self.size

        resultingSize.setWidth(resultingSize.width())
        resultingSize.setHeight(resultingSize.height())

        return resultingSize