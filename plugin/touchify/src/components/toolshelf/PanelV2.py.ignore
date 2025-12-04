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

from touchify_prototype.third_deps.pyqtgraph_docking.dockarea.Dock import Dock
from touchify_prototype.third_deps.pyqtgraph_docking.dockarea.DockArea import DockArea

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

        def LoadData(self, panelConfig: ToolshelfDataPage) -> WIDGET_GROUP:
            widget_groups: dict = {}

            for sectionInfo in panelConfig:     
                sectionInfo: ToolshelfDataSection

                if sectionInfo.panel_y not in widget_groups:
                    widget_groups[sectionInfo.panel_y] = {}
                if sectionInfo.panel_x not in widget_groups[sectionInfo.panel_y]:
                    widget_groups[sectionInfo.panel_y][sectionInfo.panel_x] = []

                widget_groups[sectionInfo.panel_y][sectionInfo.panel_x].append(sectionInfo)
            return widget_groups
        
        def LoadData_Async(self):
            widget_groups = self.LoadData(self.panel_config)
            self.dataRecieved.emit(widget_groups)
            self.seperate_thread.quit()


    class PanelLoader(QObject):
        def __init__(self, parent: "Panel"):
            super().__init__(parent)
            self.rootPanel = parent

        def CreateDock(self):
            dock = Dock("", size=(1,1), autoOrientation=False)
            dock.setContentsMargins(0,0,0,0)
            dock.layout.setContentsMargins(0,0,0,0)
            dock.layout.setSpacing(0)
            dock.hideTitleBar()
            return dock

        def Section_Actions(self, actionInfo: ToolshelfDataSection):
            dock = self.CreateDock()
            actionWidget = TouchifyActionPanel(cfg=actionInfo, parent=dock, actions_manager=self.rootPanel.managers.mgr_actions)
            self.rootPanel.Data_AppendWorker(actionWidget.dataLoaded)
            actionWidget.Data_Load()
            dock.setTitle(actionWidget.title)
            dock.addWidget(actionWidget)
            return dock
        
        def Section_Docker(self, actionInfo: ToolshelfDataSection):
            dock = self.CreateDock()
            actionWidget = DockerContainer(dock, actionInfo.docker_id, self.rootPanel.managers.mgr_dockers)
            if actionInfo.docker_nesting_mode == ToolshelfDataSection.DockerNestingMode.Docking:
                actionWidget.setDockMode(True)

            if actionInfo.docker_unloaded_visibility == ToolshelfDataSection.DockerUnloadedVisibility.Hidden:
                actionWidget.setHiddenMode(True)
            
            if actionInfo.docker_loading_priority == ToolshelfDataSection.DockerLoadingPriority.Passive:
                actionWidget.setPassiveMode(True)
                
            if actionInfo.size_x != 0 and actionInfo.size_y != 0:
                actionWidget.setSizeHint([actionInfo.size_x, actionInfo.size_y])

            self.rootPanel.dockerWidgets[actionInfo.docker_id] = actionWidget
            actionWidget.dockerChanged.connect(self.rootPanel.onDockerUpdate)
            actionWidget.dockerSizeChanged.connect(self.rootPanel.onDockerSizeChanged)
            dock.addWidget(actionWidget)
            dock.setTitle(self.rootPanel.managers.mgr_dockers.dockerWindowTitle(actionInfo.docker_id))
            return dock
        
        def Section_Special(self, actionInfo: ToolshelfDataSection):
            dock = self.CreateDock()
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BrushBlendingMode:
                actionWidget = BrushBlendingSelector(self.rootPanel)
                actionWidget.setInstance(self.rootPanel.api_window)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.LayerBlendingMode:
                actionWidget = LayerBlendingSelector(self.rootPanel)
                actionWidget.setInstance(self.rootPanel.api_window)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.LayerLabelBox:
                actionWidget = LayerLabelBox(self.rootPanel)
                actionWidget.setInstance(self.rootPanel.api_window)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BrushSizeSlider:
                actionWidget = BrushSizeSlider(self.rootPanel)
                actionWidget.setInstance(self.rootPanel.api_window)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BrushOpacitySlider:
                actionWidget = BrushOpacitySlider(self.rootPanel)
                actionWidget.setInstance(self.rootPanel.api_window)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BrushFlowSlider:
                actionWidget = BrushFlowSlider(self.rootPanel)
                actionWidget.setInstance(self.rootPanel.api_window)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BrushRotationSlider:
                actionWidget = BrushRotationSlider(self.rootPanel)
                actionWidget.setInstance(self.rootPanel.api_window)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BackgroundColorBox:
                actionWidget = CanvasColorPicker(self.rootPanel, CanvasColorPicker.Mode.Background)
                actionWidget.setInstance(self.rootPanel.api_window)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.ForegroundColorBox:
                actionWidget = CanvasColorPicker(self.rootPanel, CanvasColorPicker.Mode.Foreground)
                actionWidget.setInstance(self.rootPanel.api_window)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.ForegroundBackgroundColorPicker:
                actionWidget = CanvasDualColorButton(self.rootPanel)
                actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                actionWidget.setInstance(self.rootPanel.api_window)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.BrushPicker:
                actionWidget = BrushPresetPicker(self.rootPanel)
                actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                actionWidget.setInstance(self.rootPanel.api_window, self.rootPanel.managers)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.PatternPicker:
                actionWidget = CanvasPatternPicker(self.rootPanel)
                actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                actionWidget.setInstance(self.rootPanel.api_window, self.rootPanel.managers)
            if actionInfo.special_item_type == ToolshelfDataSection.SpecialItemType.GradientPicker:
                actionWidget = CanvasGradientPicker(self.rootPanel)
                actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                actionWidget.setInstance(self.rootPanel.api_window, self.rootPanel.managers)

            dock.addWidget(actionWidget)
            return dock

        def Section_Subpanel(self, actionInfo: ToolshelfDataSection):
            dock = CreateDock()
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

            actionWidget.panelItemResized.connect(self.onSubpanelItemResized)
            actionWidget.panelItemUpdated.connect(self.onSubpanelItemUpdated)
            
            self.pageLoadedSignal.connect(actionWidget.onLoadPage)
            self.pageUnloadSignal.connect(actionWidget.onUnloadPage)

            dock.addWidget(actionWidget)
            dock.setTitle(actionWidget.title())
            return dock
        
        def GetSubpanelData(self, actionInfo: ToolshelfDataSection):
            if actionInfo.subpanel_mode == ToolshelfDataSection.SubpanelMode.Data:
                subpanel_data = actionInfo.subpanel_data
            elif actionInfo.subpanel_mode == ToolshelfDataSection.SubpanelMode.Reference:
                toolshelf_data: ToolshelfData = TouchifySettings.instance().getRegistryItem(actionInfo.subpanel_id, ToolshelfData)
                if not toolshelf_data: return None
                subpanel_data = deepcopy(toolshelf_data.homepage)
                subpanel_data.display_name = actionInfo.display_name
            else:
                return None
            
            return subpanel_data
        
        def Init_Section(self, dock_area: DockArea, section_info: ToolshelfDataSection, dockRelativeTo: QWidget, dockPosition: str):
            sectionWidget: Dock | None = None

            match section_info.section_type:
                case ToolshelfDataSection.SectionType.Docker:
                    sectionWidget = self.Section_Docker(section_info)
                case ToolshelfDataSection.SectionType.Actions:
                    sectionWidget = self.Section_Actions(section_info)
                case ToolshelfDataSection.SectionType.Special:
                    sectionWidget = self.Section_Special(section_info)
                case _:
                    sectionWidget = None

            if sectionWidget != None:
                if section_info.min_size_x != 0: sectionWidget.setMinimumWidth(section_info.min_size_x)
                if section_info.min_size_y != 0: sectionWidget.setMinimumHeight(section_info.min_size_y)
                if section_info.max_size_x != 0: sectionWidget.setMaximumWidth(section_info.max_size_x)
                if section_info.max_size_y != 0: sectionWidget.setMaximumHeight(section_info.max_size_y)
        
            dock_area.addDock(sectionWidget, dockPosition, dockRelativeTo)
            return sectionWidget

        def Init_Panel(self, dock_area: DockArea, widget_groups: WIDGET_GROUP, last_row_item: QWidget = None, last_cell_item: QWidget = None):
            for iy, cell_rows in sorted(widget_groups.items()):
                last_row_item = None
                for ix, cell_item in sorted(cell_rows.items()):    
                    last_cell_item = None

                    for section_info in cell_item:
                        if section_info.section_type == ToolshelfDataSection.SectionType.Subpanel:
                            #TODO: Subsection Logic
                            subpanel_info = self.GetSubpanelData(section_info)
                            if subpanel_info != None:
                                sub_widget_groups = self.rootPanel.data_loader.LoadData(subpanel_info)
                                last_sub_dock = self.Init_Panel(dock_area, sub_widget_groups)
                                if dock != None: last_cell_item = dock
                        else:
                            dockRelativeTo = last_cell_item if last_cell_item != None else last_row_item if last_row_item != None  else None
                            dockPosition = 'above' if last_cell_item != None else 'right' if last_row_item != None  else 'bottom'
                            dock = self.Init_Section(dock_area, section_info, dockRelativeTo, dockPosition)
                            if dock != None: last_cell_item = dock

                    last_row_item = last_cell_item
             
        

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

        self.managers = self.page_stack.container.display.managers
        self.api_window = self.page_stack.container.display.managers.mgr_actions.api_window
        
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

        self.actions_panel = TouchifyActionPanel.Titlebar(self.panel_config.actions, self, self.managers.mgr_actions)
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

        self.panel_loader = Panel.PanelLoader(self)

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
        self.sections_stack = DockArea(self)
        self.sections_container.layout().addWidget(self.sections_stack)

        self.panel_loader.Init_Panel(self.sections_stack, widget_groups)

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
        