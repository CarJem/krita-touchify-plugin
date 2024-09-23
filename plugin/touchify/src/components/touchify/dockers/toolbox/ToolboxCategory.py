from PyQt5.QtWidgets import QToolButton
from PyQt5.QtGui import QPalette, QColor
from .ToolboxButton import ToolboxButton

from .....stylesheet import Stylesheet

from krita import *

class ToolboxCategory(QFrame):

    def __init__(self, parent: QWidget | None, name):
        super().__init__(parent)

        self.name = name
        self.buttons: list[ToolboxButton] = [] # Each ToolCategory has a dictionary of ToolButton.name : ToolButton items
        self.setObjectName("toolbox_frame")
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.gridLayout)

    def updatePalette(self):
        for btn in self.buttons:
            btn.updatePalette()

    def addTool(self, btn: ToolboxButton, x: int, y: int, alignment: Qt.Alignment | Qt.AlignmentFlag):
        self.buttons.append(btn)
        self.gridLayout.addWidget(btn, x, y, alignment)

    def removeTool(self, btn: ToolboxButton):
        self.gridLayout.removeWidget(btn)
        self.buttons.remove(btn)