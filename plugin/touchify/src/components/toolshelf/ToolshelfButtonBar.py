

from ...cfg.CfgToolshelf import CfgToolboxAction
from ...resources import ResourceManager
from ...cfg.CfgToolshelf import CfgToolboxAction
from krita import *
from .ToolshelfButton import ToolshelfButton


from ...config import *

from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import QSize, Qt

class ToolshelfButtonBar(QWidget):




    def __init__(self, btnSize, parent=None):
        super(ToolshelfButtonBar, self).__init__(parent)
        self.rows: dict[int, QWidget] = {}
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._buttons = {}
        self.btnSize = btnSize

    def addButton(self, properties: CfgToolboxAction | CfgToolboxPanel, onClick, toolTip="", checkable=False):
        btn = ToolshelfButton(self.btnSize)
        btn.setIcon(ResourceManager.iconLoader(properties.icon))
        btn.clicked.connect(onClick) # collect and disconnect all when closing
        btn.setToolTip(toolTip)
        btn.setCheckable(checkable)
        self._buttons[properties.id] = btn

        if properties.row not in self.rows:
            rowWid = QWidget()
            rowWid.setLayout(QHBoxLayout())
            rowWid.layout().setSpacing(1)
            rowWid.layout().setContentsMargins(0, 0, 0, 0)
            self.rows[properties.row] = rowWid
            self.layout().addWidget(rowWid)

        self.rows[properties.row].layout().addWidget(btn)


    def setButtonSize(self, size):
        self.btnSize = size
        for btn in self._buttons:
            btn.setFixedHeight(size)
            btn.setMinimumWidth(size)


    def count(self):
        return len(self._buttons)


    def button(self, ID):
        return self._buttons[ID]