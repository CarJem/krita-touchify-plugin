from copy import deepcopy
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.components.trigger_buttons.TouchifyActionPanel import TouchifyActionPanel
from touchify.src.components.widgets.CanvasDualColorButton import CanvasDualColorButton
from touchify.src.config.toolshelf.ToolshelfData import ToolshelfData, ToolshelfDataPage
from touchify.src.config.toolshelf.ToolshelfDataSection import ToolshelfDataSection
from touchify.src.components.widgets.BrushBlendingSelector import BrushBlendingSelector
from touchify.src.components.widgets.BrushFlowSlider import BrushFlowSlider
from touchify.src.components.widgets.BrushOpacitySlider import BrushOpacitySlider
from touchify.src.components.widgets.BrushRotationSlider import BrushRotationSlider
from touchify.src.components.widgets.BrushSizeSlider import BrushSizeSlider
from touchify.src.components.widgets.BrushPresetPicker import BrushPresetPicker
from touchify.src.components.widgets.CanvasColorPicker import CanvasColorPicker
from touchify.src.components.widgets.CanvasGradientPicker import CanvasGradientPicker
from touchify.src.components.widgets.CanvasPatternPicker import CanvasPatternPicker
from touchify.src.components.special.DockerContainer import DockerContainer

from touchify.src.components.widgets.LayerBlendingSelector import LayerBlendingSelector
from touchify.src.components.widgets.LayerLabelBox import LayerLabelBox
from touchify.src.managers.shared.settings import TouchifySettings


from krita import *

from typing import TYPE_CHECKING, Mapping
if TYPE_CHECKING:
    from .PageStack import PageStack

WIDGET_GROUP = Mapping[int, Mapping[int, list[ToolshelfDataSection]]]

class Panel(QWidget):

    class DataLoader(QObject):

        dataRecieved = pyqtSignal(dict)

        def __init__(self, panel: "ToolshelfDataPage" ):
            super().__init__()
            self.seperate_thread = QThread()
            self.moveToThread(self.seperate_thread)
            self.seperate_thread.setTerminationEnabled(True)
            self.panel_config = panel

            # Thread
            self.seperate_thread.started.connect(self.LoadData_Async)

        def start(self, priority: QThread.Priority = QThread.Priority.NormalPriority):
            self.seperate_thread.start(priority)

        def LoadData_Async(self):
            widget_groups: dict = {}

            for sectionInfo in self.panel_config.sections:     
                sectionInfo: ToolshelfDataSection

                if sectionInfo.panel_y not in widget_groups:
                    widget_groups[sectionInfo.panel_y] = {}
                if sectionInfo.panel_x not in widget_groups[sectionInfo.panel_y]:
                    widget_groups[sectionInfo.panel_y][sectionInfo.panel_x] = []

                widget_groups[sectionInfo.panel_y][sectionInfo.panel_x].append(sectionInfo)
            self.dataRecieved.emit(widget_groups)
            self.seperate_thread.quit()
                
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
            result.setStyleSheet(self.getEditSelectorStylesheet())
            result.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            result.setVisible(False)
            return result
        
        def getEditSelectorStylesheet(self):
            base_color = qApp.palette().highlight().color()
            base_factor = 25

            normal_color = f"rgba({base_color.red()},{base_color.green()},{base_color.blue()},{0})"
            hover_color = f"rgba({base_color.red() + base_factor},{base_color.green() + base_factor},{base_color.blue() + base_factor},{150})"
            press_color = f"rgba({base_color.red() - base_factor},{base_color.green() - base_factor},{base_color.blue() - base_factor},{150})"

            normal_style = f"QPushButton {{ background-color: {normal_color}; border: none; }}"
            hover_style = f"QPushButton:hover {{ background-color: {hover_color}; border: none; }}"
            pressed_style = f"QPushButton:pressed {{ background-color: {press_color}; border: none; }}"
            
            stylesheet = f"{normal_style} {hover_style} {pressed_style}"
            return stylesheet

        def addWidget(self, widget: QWidget, x: int, y: int):
            edit_container = self.createEditSelector()
            self.section_widgets.append((widget, edit_container))

            self.ourLayout.addWidget(edit_container, y, x)
            self.ourLayout.addWidget(widget, y, x)
            
    class SectionGroup(QWidget):
        groupItemChanged = pyqtSignal()

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
                if i == index: widget.setEnabled(True)
                else: widget.setDisabled(True)

            if self.mode == ToolshelfDataPage.TabType.Buttons:
                if index in self.tabTitles:
                    self.tabButton.setText(self.tabTitles[index])
            else:
                pass

            self.groupItemChanged.emit()
        
    dockerWidgets: dict = {}

    workersAssigned = pyqtSignal()
    dataLoaded = pyqtSignal()

    pageLoadedSignal = pyqtSignal()
    pageUnloadSignal = pyqtSignal()

    panelItemUpdated = pyqtSignal()
    panelItemResized = pyqtSignal()

    def __init__(self, parent: QWidget | None, toolshelf: "PageStack", data: ToolshelfDataPage):
        super(Panel, self).__init__(parent)

        self.page_stack: "PageStack" = toolshelf
        self.panel_config = data

        self.docker_manager = self.page_stack.rootWidget.parent_docker.docker_manager
        self.actions_manager = self.page_stack.rootWidget.parent_docker.actions_manager
        self.dockerWidgets: dict[any, DockerContainer] = {}
        self.size = None

        self.total_jobs = 0
        self.completed_jobs = 0

        self.setAutoFillBackground(True)

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)
        self.setLayout(self.root_layout)

        self.actions_panel = TouchifyActionPanel.Titlebar(self.panel_config.actions, self, self.actions_manager)
        self.actions_panel.dataLoaded.connect(self.Data_TitlebarLoaded)
        self.actions_panel.Data_Load()
        self.actions_panel.setAutoFillBackground(True)
        self.actions_panel.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.root_layout.addWidget(self.actions_panel)
        
        self.sections_container = QWidget(self)
        self.sections_container.setLayout(QVBoxLayout(self.sections_container))
        self.sections_container.layout().setSpacing(0)
        self.sections_container.layout().setContentsMargins(0,0,0,0)
        self.sections_container.setAutoFillBackground(True)
        self.root_layout.addWidget(self.sections_container)

        self.data_loader = Panel.DataLoader(data)
        self.data_loader.dataRecieved.connect(self.Data_Recieved)

        self.Data_AppendWorker(self.data_loader.dataRecieved)
        self.Data_AppendWorker(self.actions_panel.dataLoaded)

    def Data_Load(self):
        self.data_loader.start()

    def Data_OnWorkerComplete(self):
        self.completed_jobs += 1
        #print("Panel Section: ", self.completed_jobs, " / ", self.total_jobs)
        if self.total_jobs == self.completed_jobs: 
            self.dataLoaded.emit()

    def Data_AppendWorker(self, signal_handler: pyqtBoundSignal):
        self.total_jobs += 1
        signal_handler.connect(self.Data_OnWorkerComplete)

    def Data_TitlebarLoaded(self):
        for btnKey in self.actions_panel._buttons:
            self.actions_panel._buttons[btnKey].setFixedHeight(int(self.panel_config.action_height * TouchifySettings.instance().preferences().Interface_ToolshelfActionBarScale))
            self.actions_panel._buttons[btnKey].setMinimumWidth(int(self.panel_config.action_height * TouchifySettings.instance().preferences().Interface_ToolshelfActionBarScale))
            self.actions_panel._buttons[btnKey].setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)




    def Data_Recieved(self, widget_groups: WIDGET_GROUP):
        def Init_Section(sectionInfo: ToolshelfDataSection):
            sectionWidget = None
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

            return sectionWidget

        def Init_Cell(x: int, y: int, splitter: Panel.SectionSplit, sections: list[ToolshelfDataSection]):
            if len(sections) == 1:
                widget = Init_Section(sections[0])
                if widget: splitter.addWidget(widget, x, y)
            else:
                tabBar = Panel.SectionGroup(self, self.panel_config.tab_type)
                for section in sections:
                    item = Init_Section(section)
                    if isinstance(item, DockerContainer): tabBar.addTab(item, self.docker_manager.dockerWindowTitle(item.docker_id))
                    elif isinstance(item, TouchifyActionPanel): tabBar.addTab(item, item.title)
                    elif isinstance(item, Panel): tabBar.addTab(item, item.title())
                    else: tabBar.addTab(item, "Unknown")
                tabBar.setCurrentIndex(0)
                tabBar.groupItemChanged.connect(self.onGroupItemChanged)
                splitter.addWidget(tabBar, x, y)

        def Section_Actions(actionInfo: ToolshelfDataSection):
            actionWidget = TouchifyActionPanel(cfg=actionInfo, parent=self, actions_manager=self.actions_manager)
            self.Data_AppendWorker(actionWidget.dataLoaded)
            actionWidget.Data_Load()
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
            actionWidget.dockerSizeChanged.connect(self.onDockerSizeChanged)
            return actionWidget
        
        def Section_Special(actionInfo: ToolshelfDataSection):
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BrushBlendingMode:
                actionWidget = BrushBlendingSelector(self)
                actionWidget.setInstance(self.actions_manager.appEngine)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.LayerBlendingMode:
                actionWidget = LayerBlendingSelector(self)
                actionWidget.setInstance(self.actions_manager.appEngine)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.LayerLabelBox:
                actionWidget = LayerLabelBox(self)
                actionWidget.setInstance(self.actions_manager.appEngine)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BrushSizeSlider:
                actionWidget = BrushSizeSlider(self)
                actionWidget.setInstance(self.actions_manager.appEngine)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BrushOpacitySlider:
                actionWidget = BrushOpacitySlider(self)
                actionWidget.setInstance(self.actions_manager.appEngine)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BrushFlowSlider:
                actionWidget = BrushFlowSlider(self)
                actionWidget.setInstance(self.actions_manager.appEngine)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BrushRotationSlider:
                actionWidget = BrushRotationSlider(self)
                actionWidget.setInstance(self.actions_manager.appEngine)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BackgroundColorBox:
                actionWidget = CanvasColorPicker(self, CanvasColorPicker.Mode.Background)
                actionWidget.setInstance(self.actions_manager.appEngine)
                actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.ForegroundColorBox:
                actionWidget = CanvasColorPicker(self, CanvasColorPicker.Mode.Foreground)
                actionWidget.setInstance(self.actions_manager.appEngine)
                actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.ForegroundBackgroundColorPicker:
                actionWidget = CanvasDualColorButton(self)
                actionWidget.setInstance(self.actions_manager.appEngine)
                actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BrushPicker:
                actionWidget = BrushPresetPicker(self)
                actionWidget.setInstance(self.actions_manager.appEngine)
                actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.PatternPicker:
                actionWidget = CanvasPatternPicker(self)
                actionWidget.setInstance(self.actions_manager.appEngine)
                actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.GradientPicker:
                actionWidget = CanvasGradientPicker(self)
                actionWidget.setInstance(self.actions_manager.appEngine)
                actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            if actionInfo.min_size_x != 0: actionWidget.setMinimumWidth(actionInfo.min_size_x)
            if actionInfo.min_size_y != 0: actionWidget.setMinimumHeight(actionInfo.min_size_y)
            if actionInfo.max_size_x != 0: actionWidget.setMaximumWidth(actionInfo.max_size_x)
            if actionInfo.max_size_y != 0: actionWidget.setMaximumHeight(actionInfo.max_size_y)
            return actionWidget

        def Section_Subpanel(actionInfo: ToolshelfDataSection):
            if actionInfo.subpanel_mode == ToolshelfDataSection.SubpanelMode.Data:
                actionWidget = Panel(self, self.page_stack, actionInfo.subpanel_data)
                self.Data_AppendWorker(actionWidget.dataLoaded)
                actionWidget.Data_Load()
            elif actionInfo.subpanel_mode == ToolshelfDataSection.SubpanelMode.Reference:
                toolshelf_data: ToolshelfData = TouchifySettings.instance().getRegistryItem(actionInfo.subpanel_id, ToolshelfData)
                if not toolshelf_data: return None
                toolshelf_page = deepcopy(toolshelf_data.homepage)
                toolshelf_page.display_name = actionInfo.display_name
                actionWidget = Panel(self, self.page_stack, toolshelf_page)
                self.Data_AppendWorker(actionWidget.dataLoaded)
                actionWidget.Data_Load()
            else:
                return None


            if actionInfo.size_x != 0 and actionInfo.size_y != 0: 
                actionWidget.setSizeHint([actionInfo.size_x, actionInfo.size_y])

            if actionInfo.min_size_x != 0: actionWidget.setMinimumWidth(actionInfo.min_size_x)
            if actionInfo.min_size_y != 0: actionWidget.setMinimumHeight(actionInfo.min_size_y)
            if actionInfo.max_size_x != 0: actionWidget.setMaximumWidth(actionInfo.max_size_x)
            if actionInfo.max_size_y != 0: actionWidget.setMaximumHeight(actionInfo.max_size_y)

            actionWidget.panelItemResized.connect(self.onSubpanelItemResized)
            actionWidget.panelItemUpdated.connect(self.onSubpanelItemUpdated)
            
            self.pageLoadedSignal.connect(actionWidget.onLoadPage)
            self.pageUnloadSignal.connect(actionWidget.onUnloadPage)
            return actionWidget
        

        self.sections_stack = Panel.SectionSplit(Qt.Orientation.Vertical, "root", self)
        self.sections_container.layout().addWidget(self.sections_stack)

        for row_key in sorted(widget_groups.keys()):
            row_length = len(widget_groups[row_key].keys())
            row_items = [widget_groups[row_key][ix] for ix in sorted(widget_groups[row_key].keys())]

            iy = sorted(widget_groups.keys()).index(row_key)

            if row_length == 1:
                Init_Cell(0, iy, self.sections_stack, row_items[0])
            else:
                row_splitter = Panel.SectionSplit(Qt.Orientation.Horizontal, f"sub_root_{iy}")
                row_splitter.setAutoFillBackground(True)
                for ix in range(0, row_length):
                    Init_Cell(ix, 0, row_splitter, row_items[ix])
                self.sections_stack.addWidget(row_splitter, 0, iy)

        qApp.paletteChanged.connect(self.updateStyleSheet)
        self.updateStyleSheet()

        self.workersAssigned.emit()

    def setEditMode(self, value: bool):
        self.sections_stack.setEditMode(value)

    def onDockerUpdate(self):
        self.panelItemUpdated.emit()

    def onDockerSizeChanged(self):
        self.panelItemResized.emit()

    def onGroupItemChanged(self):
        self.panelItemUpdated.emit()

    def onSubpanelItemResized(self):
        self.panelItemResized.emit()

    def onSubpanelItemUpdated(self):
        self.panelItemUpdated.emit()

    def title(self):
        if self.panel_config:
            if self.panel_config.hasDisplayName(): 
                return self.panel_config.display_name
            else:
                return self.panel_config.id
        else:
            return "Unknown Panel"

    def onUnloadPage(self):
        self.pageUnloadSignal.emit()

    def onLoadPage(self):
        self.pageLoadedSignal.emit()

    def setSizeHint(self, size):
        self.size = QSize(size[0], size[1])
    
    def updateStyleSheet(self):
        stylesheet = f"""
            QWidget#toolshelf-header {{
                background-color: palette(alternate-base);
                border: none;
            }}

            QWidget#toolshelf-tablist-row {{
                background-color: palette(alternate-base);
                border: none;
            }}

            QPushButton, QToolButton {{
                background-color: palette(alternate-base);
                border: none;
            }}

            QPushButton:hover, QToolButton:hover {{
                background-color: palette(highlight);
            }}

            QPushButton:checked, QToolButton:checked {{
                background-color: palette(highlight);
            }}
            
            QPushButton:pressed, QToolButton:pressed {{
                background-color: palette(alternate-base);
            }}

            QPushButton#back-widget {{
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border: none;
            }}

            QPushButton#pin-widget {{
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                border: none;
            }}

            QPushButton::menu-indicator, QToolButton::menu-indicator {{ 
                image: none; 
            }}

            QPushButton#menu-widget {{
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                border: none;
            }}

            QWidget#filler-widget {{
                background-color: palette(alternate-base);
                border: none;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
            }}
        """
        self.actions_panel.setStyleSheet(stylesheet)

    def sizeHint(self):
        resultingSize = super().sizeHint()
        if self.size: resultingSize = self.size

        resultingSize.setWidth(resultingSize.width())
        resultingSize.setHeight(resultingSize.height())

        return resultingSize
        