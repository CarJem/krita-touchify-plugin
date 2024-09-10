

from PyQt5.QtGui import QColor, QIcon, QImage, QPalette, QPixmap
from krita import *


from ....settings.TouchifyConfig import *

from PyQt5.QtWidgets import QSizePolicy, QPushButton, QWidget, QHBoxLayout
from PyQt5.QtCore import QSize, Qt


class ToolshelfPageButton(QPushButton):

    def __init__(self, parent = None):
        super(ToolshelfPageButton, self).__init__(parent)

        self.setFocusPolicy(Qt.NoFocus)
        self.highlightConnection = None
        self._resizing = False

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

class ToolshelfPageButtons(QWidget):
    def __init__(self, parent=None, isHorizontal=False):
        super(ToolshelfPageButtons, self).__init__(parent)
        self._rows: dict[int, QWidget] = {}
        self.isHorizontal = isHorizontal
        if self.isHorizontal:
            self.setLayout(QHBoxLayout(self))
        else:
            self.setLayout(QVBoxLayout(self))
        self.layout().setSpacing(1)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._buttons: dict[any, ToolshelfPageButton] = {}

    def addButton(self, id: any, row: int, onClick: any, toolTip: str, checkable: bool):
        btn = ToolshelfPageButton()
        if onClick:
            btn.clicked.connect(onClick) # collect and disconnect all when closing
        btn.setToolTip(toolTip)
        btn.setContentsMargins(0,0,0,0)
        btn.setCheckable(checkable)
        self._buttons[id] = btn

        if row not in self._rows:
            rowWid = QWidget(self)
            if self.isHorizontal:
                rowWid.setLayout(QVBoxLayout(self))
            else:
                rowWid.setLayout(QHBoxLayout(self))
            rowWid.layout().setSpacing(1)
            rowWid.layout().setContentsMargins(0, 0, 0, 0)
            rowWid.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
            self._rows[row] = rowWid
            self.layout().addWidget(rowWid)

        self._rows[row].layout().addWidget(btn)
        return btn