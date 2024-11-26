from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QSize

from touchify.src.cfg.toolshelf.CfgToolshelfSection import CfgToolshelfSection
from touchify.src.components.touchify.special.CanvasColorPicker import CanvasColorPicker
from touchify.src.docker_manager import *
from touchify.src.components.touchify.special.BrushBlendingSelector import BrushBlendingSelector
from touchify.src.components.touchify.special.LayerBlendingSelector import LayerBlendingSelector
from touchify.src.components.touchify.special.LayerLabelBox import LayerLabelBox
from touchify.src.components.touchify.special.BrushRotationSlider import BrushRotationSlider
from touchify.src.components.touchify.special.BrushFlowSlider import BrushFlowSlider
from touchify.src.components.touchify.special.BrushOpacitySlider import BrushOpacitySlider
from touchify.src.components.touchify.special.BrushSizeSlider import BrushSizeSlider
from krita import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.action_manager import ActionManager
    


class ToolshelfSpecialSection(QWidget):
  
    def __init__(self, parent: QWidget | None, actionInfo: CfgToolshelfSection, action_manager: "ActionManager"):
        super(ToolshelfSpecialSection, self).__init__(parent)
        self.actionInfo = actionInfo
        self.action_manager = action_manager

        self.size = None
        self.ourWidget: QWidget | None = None

        self.setContentsMargins(0,0,0,0)

        self.ourLayout = QVBoxLayout(self)
        self.ourLayout.setSpacing(0)
        self.ourLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.ourLayout)

        if self.actionInfo.special_item_type == CfgToolshelfSection.SpecialItemType.BrushBlendingMode:
            self.ourWidget = BrushBlendingSelector(self)
        if self.actionInfo.special_item_type == CfgToolshelfSection.SpecialItemType.LayerBlendingMode:
            self.ourWidget = LayerBlendingSelector(self)
        if self.actionInfo.special_item_type == CfgToolshelfSection.SpecialItemType.LayerLabelBox:
            self.ourWidget = LayerLabelBox(self)
        if self.actionInfo.special_item_type == CfgToolshelfSection.SpecialItemType.BrushSizeSlider:
            self.ourWidget = BrushSizeSlider(self)
            self.ourWidget.setSourceWindow(self.action_manager.appEngine.windowSource)
        if self.actionInfo.special_item_type == CfgToolshelfSection.SpecialItemType.BrushOpacitySlider:
            self.ourWidget = BrushOpacitySlider(self)
            self.ourWidget.setSourceWindow(self.action_manager.appEngine.windowSource)
        if self.actionInfo.special_item_type == CfgToolshelfSection.SpecialItemType.BrushFlowSlider:
            self.ourWidget = BrushFlowSlider(self)
            self.ourWidget.setSourceWindow(self.action_manager.appEngine.windowSource)
        if self.actionInfo.special_item_type == CfgToolshelfSection.SpecialItemType.BrushRotationSlider:
            self.ourWidget = BrushRotationSlider(self)
            self.ourWidget.setSourceWindow(self.action_manager.appEngine.windowSource)
        if self.actionInfo.special_item_type == CfgToolshelfSection.SpecialItemType.BackgroundColorBox:
            self.ourWidget = CanvasColorPicker(self, CanvasColorPicker.Mode.Background)
            self.ourWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        if self.actionInfo.special_item_type == CfgToolshelfSection.SpecialItemType.ForegroundColorBox:
            self.ourWidget = CanvasColorPicker(self, CanvasColorPicker.Mode.Foreground)
            self.ourWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        if self.ourWidget != None:
            self.ourLayout.addWidget(self.ourWidget, 1)

    def setMinimumHeight(self, val:int):
        if self.ourWidget: self.ourWidget.setMinimumHeight(val)
        super().setMinimumHeight(val)
        
    def setMaximumHeight(self, val:int):
        if self.ourWidget: self.ourWidget.setMaximumHeight(val)
        super().setMaximumHeight(val)
        
    def setMinimumWidth(self, val:int):
        if self.ourWidget: self.ourWidget.setMinimumWidth(val)
        super().setMinimumWidth(val)
        
    def setMaximumWidth(self, val:int):
        if self.ourWidget: self.ourWidget.setMaximumWidth(val)
        super().setMaximumWidth(val)


    def setSizeHint(self, size):
        self.size = QSize(size[0], size[1])
    
    def sizeHint(self):
        baseSize: QSize = QSize()
        if self.size:
            baseSize = self.size
        else:
            baseSize = super().sizeHint()
            
        return baseSize

