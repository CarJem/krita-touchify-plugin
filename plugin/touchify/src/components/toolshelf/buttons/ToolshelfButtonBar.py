

from PyQt5.QtGui import QColor, QIcon, QImage, QPalette, QPixmap
from ....cfg.CfgToolshelf import CfgToolshelfAction
from ....resources import ResourceManager
from ....cfg.CfgToolshelf import CfgToolshelfAction
from krita import *


from ....config import *

from PyQt5.QtWidgets import QSizePolicy, QToolButton, QWidget, QHBoxLayout
from PyQt5.QtCore import QSize, Qt


class ToolshelfButton(QToolButton):

    def __init__(self, parent = None):
        super(ToolshelfButton, self).__init__(parent)

        self.setFocusPolicy(Qt.NoFocus)
        self.highlightConnection = None

    def setIcon(self, icon):
        if isinstance(icon, QIcon):
            super().setIcon(icon)
        elif isinstance(icon, QPixmap):
            super().setIcon(QIcon(icon))
        elif isinstance(icon, QImage):
            super().setIcon(QIcon(QPixmap.fromImage(icon)))
        else:
            raise TypeError(f"Unable to set icon of invalid type {type(icon)}")


    def setColor(self, color): # In case the Krita API opens up for a "color changed" signal, this could be useful...
        if isinstance(color, QColor):
            pxmap = QPixmap(self.iconSize())
            pxmap.fill(color)
            self.setIcon(pxmap)
        else:
            raise TypeError(f"Unable to set color of invalid type {type(color)}")


    def setCheckable(self, checkable):
        if checkable:
            self.highlightConnection = self.toggled.connect(self.highlight)
        else:
            if self.highlightConnection:
                self.disconnect(self.highlightConnection)
                self.highlightConnection = None
        return super().setCheckable(checkable)


    def highlight(self, toggled):
        p = self.window().palette()
        if toggled:
            p.setColor(QPalette.Button, p.color(QPalette.Highlight))
        self.setPalette(p)

class ToolshelfButtonBar(QWidget):
    def __init__(self, parent=None):
        super(ToolshelfButtonBar, self).__init__(parent)
        self.rows: dict[int, QWidget] = {}
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(1)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._buttons: dict[any, ToolshelfButton] = {}

    def addButton(self, id: any, displayData: str, row: int, onClick: any, toolTip: str, checkable: bool, hasIcon: bool):
        btn = ToolshelfButton()
        
        if hasIcon:
            btn.setIcon(ResourceManager.iconLoader(displayData))
        else: 
            btn.setText(displayData)
        btn.clicked.connect(onClick) # collect and disconnect all when closing
        btn.setToolTip(toolTip)
        btn.setCheckable(checkable)
        self._buttons[id] = btn

        if row not in self.rows:
            rowWid = QWidget()
            rowWid.setLayout(QHBoxLayout())
            rowWid.layout().setSpacing(1)
            rowWid.layout().setContentsMargins(0, 0, 0, 0)
            rowWid.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
            self.rows[row] = rowWid
            self.layout().addWidget(rowWid)

        self.rows[row].layout().addWidget(btn)

    def addTextButton(self, id: any, text: str, onClick: any, toolTip: str="", row: int = 0):
        self.addButton(id, text, row, onClick, toolTip, False, False)

    def addCfgButton(self, properties: CfgToolshelfAction | CfgToolshelfPanel, onClick, toolTip="", checkable=False):
        self.addButton(properties.id, properties.icon, properties.row, onClick, toolTip, checkable, True)

    def count(self):
        return len(self._buttons)

    def button(self, ID):
        return self._buttons[ID]