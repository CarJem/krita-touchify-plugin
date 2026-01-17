from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.components.toolshelf.ToolshelfNestedDock import ToolshelfNestedDock
from touchify.src.components.toolshelf.ShelfDock import ShelfDock
from touchify.src.components.widgets.triggers.TriggerPanel import TriggerPanel
from touchify.src.components.widgets.canvas.CanvasDualColorButton import CanvasDualColorButton
from touchify.src.config.toolshelf.ToolshelfDock import ToolshelfDock
from touchify.src.components.widgets.brush.BrushBlendingSelector import BrushBlendingSelector
from touchify.src.components.widgets.brush.BrushFlowSlider import BrushFlowSlider
from touchify.src.components.widgets.brush.BrushOpacitySlider import BrushOpacitySlider
from touchify.src.components.widgets.brush.BrushAngleSelector import BrushAngleSelector
from touchify.src.components.widgets.brush.BrushSizeSlider import BrushSizeSlider
from touchify.src.components.widgets.brush.BrushPresetPicker import BrushPresetPicker
from touchify.src.components.widgets.canvas.CanvasColorPicker import CanvasColorPicker
from touchify.src.components.widgets.canvas.CanvasGradientPicker import CanvasGradientPicker
from touchify.src.components.widgets.canvas.CanvasPatternPicker import CanvasPatternPicker
from touchify.src.components.widgets.other.DockerContainer import DockerContainer

from touchify.src.components.widgets.layers.LayerBlendingSelector import LayerBlendingSelector
from touchify.src.components.widgets.layers.LayerLabelBox import LayerLabelBox


from krita import *

from typing import TYPE_CHECKING

from touchify.src.config.triggers.TriggerList import TriggerList

if TYPE_CHECKING:
    from touchify.src.components.toolshelf.ShelfWidget import ShelfWidget

class ShelfLoader(QObject):

    class PlaceholderWidget(QLabel):
        def __init__(self, parent: QWidget = None):
            super().__init__(parent)
            self.setText("< placeholder >")
            

    def __init__(self, parent: "ShelfWidget"):
        super().__init__(parent)
        self.rootPanel = parent


    def Section_Actions(self, actionInfo: ToolshelfDock):
        dock = ShelfDock(actionInfo)
        
        cfg = TriggerList()
        cfg.convertFrom(type(ToolshelfDock), actionInfo)

        actionWidget = TriggerPanel(cfg=cfg, parent=dock, actions_manager=self.rootPanel.managers.mgr_actions)
        actionWidget.Data_Load()
        dock.setTitle(actionWidget.title)
        dock.addWidget(actionWidget)
        return dock
    
    def Section_Docker(self, actionInfo: ToolshelfDock):
        dock = ShelfDock(actionInfo)
        actionWidget = DockerContainer(dock, actionInfo.docker_id, self.rootPanel.managers.mgr_dockers)
        if actionInfo.docker_nesting_mode == ToolshelfDock.DockerNestingMode.Docking:
            actionWidget.setDockMode(True)
            actionWidget.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

        if actionInfo.docker_unloaded_visibility == ToolshelfDock.DockerUnloadedVisibility.Hidden:
            actionWidget.setHiddenMode(True)
        
        if actionInfo.docker_loading_priority == ToolshelfDock.DockerLoadingPriority.Passive:
            actionWidget.setPassiveMode(True)
            
        if actionInfo.docker_size_hint_x != 0 and actionInfo.docker_size_hint_y != 0:
            actionWidget.setSizeHint([actionInfo.docker_size_hint_x, actionInfo.docker_size_hint_y])

        dock.addWidget(actionWidget)
        dock.setTitle(self.rootPanel.managers.mgr_dockers.dockerWindowTitle(actionInfo.docker_id))
        return dock
    
    def Section_Special(self, actionInfo: ToolshelfDock):
        if actionInfo.special_item_type == ToolshelfDock.SpecialItemType.NestedShelf:
            return ToolshelfNestedDock(self.rootPanel, actionInfo, self.rootPanel.managers)
        
        dock = ShelfDock(actionInfo)
        match actionInfo.special_item_type:
            case ToolshelfDock.SpecialItemType.BrushBlendingMode:
                actionWidget = BrushBlendingSelector(self.rootPanel)
                actionWidget.setInstance(self.rootPanel.api_window)
            case ToolshelfDock.SpecialItemType.LayerBlendingMode:
                actionWidget = LayerBlendingSelector(self.rootPanel)
                actionWidget.setInstance(self.rootPanel.api_window)
            case ToolshelfDock.SpecialItemType.LayerLabelBox:
                actionWidget = LayerLabelBox(self.rootPanel)
                actionWidget.setInstance(self.rootPanel.api_window)
            case ToolshelfDock.SpecialItemType.BrushSizeSlider:
                actionWidget = BrushSizeSlider(self.rootPanel)
                actionWidget.setOrientation(actionInfo.special_slider_orientation)
                actionWidget.setInstance(self.rootPanel.api_window)
            case ToolshelfDock.SpecialItemType.BrushOpacitySlider:
                actionWidget = BrushOpacitySlider(self.rootPanel)
                actionWidget.setOrientation(actionInfo.special_slider_orientation)
                actionWidget.setInstance(self.rootPanel.api_window)
            case ToolshelfDock.SpecialItemType.BrushFlowSlider:
                actionWidget = BrushFlowSlider(self.rootPanel)
                actionWidget.setOrientation(actionInfo.special_slider_orientation)
                actionWidget.setInstance(self.rootPanel.api_window)
            case ToolshelfDock.SpecialItemType.BrushAngleSelector:
                actionWidget = BrushAngleSelector(self.rootPanel)
                actionWidget.setInstance(self.rootPanel.api_window)
            case ToolshelfDock.SpecialItemType.BackgroundColorBox:
                actionWidget = CanvasColorPicker(self.rootPanel, CanvasColorPicker.Mode.Background)
                actionWidget.setInstance(self.rootPanel.api_window)
            case ToolshelfDock.SpecialItemType.ForegroundColorBox:
                actionWidget = CanvasColorPicker(self.rootPanel, CanvasColorPicker.Mode.Foreground)
                actionWidget.setInstance(self.rootPanel.api_window)
            case ToolshelfDock.SpecialItemType.ForegroundBackgroundColorPicker:
                actionWidget = CanvasDualColorButton(self.rootPanel)
                actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                actionWidget.setInstance(self.rootPanel.api_window)
            case ToolshelfDock.SpecialItemType.BrushPicker:
                actionWidget = BrushPresetPicker(self.rootPanel)
                actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                actionWidget.setInstance(self.rootPanel.api_window, self.rootPanel.managers)
            case ToolshelfDock.SpecialItemType.PatternPicker:
                actionWidget = CanvasPatternPicker(self.rootPanel)
                actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                actionWidget.setInstance(self.rootPanel.api_window, self.rootPanel.managers)
            case ToolshelfDock.SpecialItemType.GradientPicker:
                actionWidget = CanvasGradientPicker(self.rootPanel)
                actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                actionWidget.setInstance(self.rootPanel.api_window, self.rootPanel.managers)
            case _:
                actionWidget = QWidget(self)
        dock.addWidget(actionWidget)
        return dock
    
    def Section_Placeholder(self, actionInfo: ToolshelfDock):
        dock = ShelfDock(actionInfo)
        actionWidget = self.PlaceholderWidget(self.rootPanel)
        dock.addWidget(actionWidget)
        return dock
    
    def Init_BlankSection(self):
        actionInfo = ToolshelfDock()
        actionInfo.section_type = ToolshelfDock.SectionType.Placeholder
        return self.Init_Section(actionInfo)
    
    def Init_Section(self, section_info: ToolshelfDock):
        sectionWidget: ShelfDock | None = None

        match section_info.section_type:
            case ToolshelfDock.SectionType.Docker:
                sectionWidget = self.Section_Docker(section_info)
            case ToolshelfDock.SectionType.Actions:
                sectionWidget = self.Section_Actions(section_info)
            case ToolshelfDock.SectionType.Special:
                sectionWidget = self.Section_Special(section_info)
            case ToolshelfDock.SectionType.Placeholder:
                sectionWidget = self.Section_Placeholder(section_info)
            case _:
                sectionWidget = self.Section_Placeholder(section_info)

        if sectionWidget != None:
            if section_info.min_size_x != 0: sectionWidget.setMinimumWidth(section_info.min_size_x)
            if section_info.min_size_y != 0: sectionWidget.setMinimumHeight(section_info.min_size_y)
            if section_info.max_size_x != 0: sectionWidget.setMaximumWidth(section_info.max_size_x)
            if section_info.max_size_y != 0: sectionWidget.setMaximumHeight(section_info.max_size_y)

        return sectionWidget