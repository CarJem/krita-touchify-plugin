from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QSize
from touchify.src.cfg.toolshelf.CfgToolshelfSection import CfgToolshelfSection
from touchify.src.docker_manager import *
from touchify.src.components.touchify.special.BrushBlendingSelector import BrushBlendingSelector
from touchify.src.components.touchify.special.LayerBlendingSelector import LayerBlendingSelector
from touchify.src.components.touchify.special.LayerLabelBox import LayerLabelBox
from krita import *
    


class ToolshelfSpecialSection(QWidget):
  
    def __init__(self, parent: QWidget | None, actionInfo: CfgToolshelfSection):
        super(ToolshelfSpecialSection, self).__init__(parent)
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

