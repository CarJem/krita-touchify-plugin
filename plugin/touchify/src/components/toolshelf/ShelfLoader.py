from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.components.toolshelf.ShelfItem import ShelfItem
from touchify.src.components.trigger_buttons.TouchifyActionPanel import TouchifyActionPanel
from touchify.src.components.widgets.CanvasDualColorButton import CanvasDualColorButton
from touchify.src.config.toolshelf.ToolshelfDock import ToolshelfDock
from touchify.src.components.widgets.BrushBlendingSelector import BrushBlendingSelector
from touchify.src.components.widgets.sliders.BrushFlowSlider import BrushFlowSlider
from touchify.src.components.widgets.sliders.BrushOpacitySlider import BrushOpacitySlider
from touchify.src.components.widgets.sliders.BrushRotationSlider import BrushRotationSlider
from touchify.src.components.widgets.sliders.BrushSizeSlider import BrushSizeSlider
from touchify.src.components.widgets.BrushPresetPicker import BrushPresetPicker
from touchify.src.components.widgets.CanvasColorPicker import CanvasColorPicker
from touchify.src.components.widgets.CanvasGradientPicker import CanvasGradientPicker
from touchify.src.components.widgets.CanvasPatternPicker import CanvasPatternPicker
from touchify.src.components.special.DockerContainer import DockerContainer

from touchify.src.components.widgets.LayerBlendingSelector import LayerBlendingSelector
from touchify.src.components.widgets.LayerLabelBox import LayerLabelBox


from krita import *

from typing import TYPE_CHECKING

from touchify.src.config.triggers.TriggerPanel import TriggerPanel

if TYPE_CHECKING:
    from touchify.src.components.toolshelf.ShelfWidget import ShelfWidget

class ShelfLoader(QObject):
    def __init__(self, parent: "ShelfWidget"):
        super().__init__(parent)
        self.rootPanel = parent


    def Section_Actions(self, actionInfo: ToolshelfDock):
        dock = ShelfItem(actionInfo)
        
        cfg = TriggerPanel()
        cfg.convertFrom(type(ToolshelfDock), actionInfo)

        actionWidget = TouchifyActionPanel(cfg=cfg, parent=dock, actions_manager=self.rootPanel.managers.mgr_actions)
        actionWidget.Data_Load()
        dock.setTitle(actionWidget.title)
        dock.addWidget(actionWidget)
        return dock
    
    def Section_Docker(self, actionInfo: ToolshelfDock):
        dock = ShelfItem(actionInfo)
        actionWidget = DockerContainer(dock, actionInfo.docker_id, self.rootPanel.managers.mgr_dockers)
        if actionInfo.docker_nesting_mode == ToolshelfDock.DockerNestingMode.Docking:
            actionWidget.setDockMode(True)

        if actionInfo.docker_unloaded_visibility == ToolshelfDock.DockerUnloadedVisibility.Hidden:
            actionWidget.setHiddenMode(True)
        
        if actionInfo.docker_loading_priority == ToolshelfDock.DockerLoadingPriority.Passive:
            actionWidget.setPassiveMode(True)
            
        if actionInfo.size_x != 0 and actionInfo.size_y != 0:
            actionWidget.setSizeHint([actionInfo.size_x, actionInfo.size_y])

        dock.addWidget(actionWidget)
        dock.setTitle(self.rootPanel.managers.mgr_dockers.dockerWindowTitle(actionInfo.docker_id))
        return dock
    
    def Section_Special(self, actionInfo: ToolshelfDock):
        dock = ShelfItem(actionInfo)
        if actionInfo.special_item_type == ToolshelfDock.SpecialItemType.BrushBlendingMode:
            actionWidget = BrushBlendingSelector(self.rootPanel)
            actionWidget.setInstance(self.rootPanel.api_window)
        if actionInfo.special_item_type == ToolshelfDock.SpecialItemType.LayerBlendingMode:
            actionWidget = LayerBlendingSelector(self.rootPanel)
            actionWidget.setInstance(self.rootPanel.api_window)
        if actionInfo.special_item_type == ToolshelfDock.SpecialItemType.LayerLabelBox:
            actionWidget = LayerLabelBox(self.rootPanel)
            actionWidget.setInstance(self.rootPanel.api_window)
        if actionInfo.special_item_type == ToolshelfDock.SpecialItemType.BrushSizeSlider:
            actionWidget = BrushSizeSlider(self.rootPanel)
            actionWidget.setOrientation(actionInfo.special_slider_orientation)
            actionWidget.setInstance(self.rootPanel.api_window)
        if actionInfo.special_item_type == ToolshelfDock.SpecialItemType.BrushOpacitySlider:
            actionWidget = BrushOpacitySlider(self.rootPanel)
            actionWidget.setOrientation(actionInfo.special_slider_orientation)
            actionWidget.setInstance(self.rootPanel.api_window)
        if actionInfo.special_item_type == ToolshelfDock.SpecialItemType.BrushFlowSlider:
            actionWidget = BrushFlowSlider(self.rootPanel)
            actionWidget.setOrientation(actionInfo.special_slider_orientation)
            actionWidget.setInstance(self.rootPanel.api_window)
        if actionInfo.special_item_type == ToolshelfDock.SpecialItemType.BrushRotationSlider:
            actionWidget = BrushRotationSlider(self.rootPanel)
            actionWidget.setOrientation(actionInfo.special_slider_orientation)
            actionWidget.setInstance(self.rootPanel.api_window)
        if actionInfo.special_item_type == ToolshelfDock.SpecialItemType.BackgroundColorBox:
            actionWidget = CanvasColorPicker(self.rootPanel, CanvasColorPicker.Mode.Background)
            actionWidget.setInstance(self.rootPanel.api_window)
        if actionInfo.special_item_type == ToolshelfDock.SpecialItemType.ForegroundColorBox:
            actionWidget = CanvasColorPicker(self.rootPanel, CanvasColorPicker.Mode.Foreground)
            actionWidget.setInstance(self.rootPanel.api_window)
        if actionInfo.special_item_type == ToolshelfDock.SpecialItemType.ForegroundBackgroundColorPicker:
            actionWidget = CanvasDualColorButton(self.rootPanel)
            actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            actionWidget.setInstance(self.rootPanel.api_window)
        if actionInfo.special_item_type == ToolshelfDock.SpecialItemType.BrushPicker:
            actionWidget = BrushPresetPicker(self.rootPanel)
            actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            actionWidget.setInstance(self.rootPanel.api_window, self.rootPanel.managers)
        if actionInfo.special_item_type == ToolshelfDock.SpecialItemType.PatternPicker:
            actionWidget = CanvasPatternPicker(self.rootPanel)
            actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            actionWidget.setInstance(self.rootPanel.api_window, self.rootPanel.managers)
        if actionInfo.special_item_type == ToolshelfDock.SpecialItemType.GradientPicker:
            actionWidget = CanvasGradientPicker(self.rootPanel)
            actionWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            actionWidget.setInstance(self.rootPanel.api_window, self.rootPanel.managers)

        dock.addWidget(actionWidget)
        return dock
    
    def Init_Section(self, section_info: ToolshelfDock):
        sectionWidget: ShelfItem | None = None

        match section_info.section_type:
            case ToolshelfDock.SectionType.Docker:
                sectionWidget = self.Section_Docker(section_info)
            case ToolshelfDock.SectionType.Actions:
                sectionWidget = self.Section_Actions(section_info)
            case ToolshelfDock.SectionType.Special:
                sectionWidget = self.Section_Special(section_info)
            case _:
                sectionWidget = None

        if sectionWidget != None:
            if section_info.min_size_x != 0: sectionWidget.setMinimumWidth(section_info.min_size_x)
            if section_info.min_size_y != 0: sectionWidget.setMinimumHeight(section_info.min_size_y)
            if section_info.max_size_x != 0: sectionWidget.setMaximumWidth(section_info.max_size_x)
            if section_info.max_size_y != 0: sectionWidget.setMaximumHeight(section_info.max_size_y)

        return sectionWidget