from typing import Callable
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QFrame
from PyQt5.QtCore import QSize, QEvent
from .....cfg.toolshelf.CfgToolshelfSection import CfgToolshelfSection
from .....docker_manager import *
from ...special.BrushBlendingSelector import BrushBlendingSelector
from ...special.LayerBlendingSelector import LayerBlendingSelector
from ...special.LayerLabelBox import LayerLabelBox
from krita import *
    


class ToolshelfSpecialWidget(QWidget):
  
    def __init__(self, parent: QWidget | None, actionInfo: CfgToolshelfSection):
        super(ToolshelfSpecialWidget, self).__init__(parent)
        self.actionInfo = actionInfo

        self.size = None
        self.ourWidget = None

        self.ourLayout = QVBoxLayout(self)
        self.setContentsMargins(0,0,0,0)
        self.ourLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.ourLayout)

        if self.actionInfo.special_item_type == CfgToolshelfSection.SpecialItemType.BrushBlendingMode:
            self.ourWidget = BrushBlendingSelector(self)
            self.ourLayout.addWidget(self.ourWidget)
        if self.actionInfo.special_item_type == CfgToolshelfSection.SpecialItemType.LayerBlendingMode:
            self.ourWidget = LayerBlendingSelector(self)
            self.ourLayout.addWidget(self.ourWidget)
        if self.actionInfo.special_item_type == CfgToolshelfSection.SpecialItemType.LayerLabelBox:
            self.ourWidget = LayerLabelBox(self)
            self.ourLayout.addWidget(self.ourWidget)


    def setSizeHint(self, size):
        self.size = QSize(size[0], size[1])

    def minimumSize(self) -> QSize:
        baseSize: QSize = QSize()
        if self.ourWidget:
            baseSize = self.ourWidget.minimumSize()
        else:
            baseSize = super().minimumSize()
        return baseSize
    
    def sizeHint(self):
        baseSize: QSize = QSize()
        if self.size:
            baseSize = self.size
        elif self.ourWidget:
            baseSize = self.ourWidget.sizeHint()
        else:
            baseSize = super().sizeHint()
            
        return baseSize

