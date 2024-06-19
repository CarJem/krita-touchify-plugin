

from ...resources import ResourceManager
from ...cfg.CfgToolboxAction import CfgToolboxAction
from krita import *
from .ToolshelfButton import ToolshelfButton


from ...config import *

from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import QSize, Qt

class ToolshelfButtonBar(QWidget):

    def __init__(self, btnSize, parent=None):
        super(ToolshelfButtonBar, self).__init__(parent)
        self.setLayout(QHBoxLayout())
        self.layout().setSpacing(1)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._buttons = {}
        self.btnSize = btnSize


    def addButton(self, properties: CfgToolboxAction, onClick, toolTip="", checkable=False):
        btn = ToolshelfButton(self.btnSize)
        btn.setIcon(ResourceManager.iconLoader(properties.icon))
        btn.clicked.connect(onClick) # collect and disconnect all when closing
        btn.setToolTip(toolTip)
        btn.setCheckable(checkable)

        self._buttons[properties.id] = btn
        self.layout().addWidget(btn)


    def setButtonSize(self, size):
        self.btnSize = size
        for btn in self._buttons:
            btn.setFixedSize(QSize(size, size))


    def count(self):
        return len(self._buttons)


    def button(self, ID):
        return self._buttons[ID]