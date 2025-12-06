from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.components.toolshelf.ShelfItem import ShelfItem
from touchify.src.components.trigger_buttons.TouchifyActionPanel import TouchifyActionPanel
from touchify.src.components.widgets.CanvasDualColorButton import CanvasDualColorButton
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


from krita import *

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from touchify.src.components.toolshelf.ShelfWidget import ShelfWidget

class ShelfLoader(QObject):
    def __init__(self, parent: "ShelfWidget"):
        super().__init__(parent)
        self.rootPanel = parent


    def Section_Actions(self, actionInfo: ToolshelfDataSection):
        dock = ShelfItem(actionInfo)
        actionWidget = TouchifyActionPanel(cfg=actionInfo, parent=dock, actions_manager=self.rootPanel.managers.mgr_actions)
        actionWidget.Data_Load()
        dock.setTitle(actionWidget.title)
        dock.addWidget(actionWidget)
        return dock
    
    def Section_Docker(self, actionInfo: ToolshelfDataSection):
        dock = ShelfItem(actionInfo)
        actionWidget = DockerContainer(dock, actionInfo.docker_id, self.rootPanel.managers.mgr_dockers)
        if actionInfo.docker_nesting_mode == ToolshelfDataSection.DockerNestingMode.Docking:
            actionWidget.setDockMode(True)

        if actionInfo.docker_unloaded_visibility == ToolshelfDataSection.DockerUnloadedVisibility.Hidden:
            actionWidget.setHiddenMode(True)
        
        if actionInfo.docker_loading_priority == ToolshelfDataSection.DockerLoadingPriority.Passive:
            actionWidget.setPassiveMode(True)
            
        if actionInfo.size_x != 0 and actionInfo.size_y != 0:
            actionWidget.setSizeHint([actionInfo.size_x, actionInfo.size_y])

        dock.addWidget(actionWidget)
        dock.setTitle(self.rootPanel.managers.mgr_dockers.dockerWindowTitle(actionInfo.docker_id))
        return dock
    
    def Section_Special(self, actionInfo: ToolshelfDataSection):
        dock = ShelfItem(actionInfo)
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
    
    def Init_Section(self, section_info: ToolshelfDataSection):
        sectionWidget: ShelfItem | None = None

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

        return sectionWidget