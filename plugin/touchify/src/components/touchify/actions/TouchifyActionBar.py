import uuid
from .TouchifyActionButton import TouchifyActionButton
from ....variables import *
from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from ....settings.TouchifyConfig import *


class TouchifyActionBar(QWidget):
    def __init__(self, parent=None):
        super(TouchifyActionBar, self).__init__(parent)
        self._rows: dict[int, QWidget] = {}
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(1)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._buttons: dict[any, TouchifyActionButton] = {}

    def addButton(self, id: any, row: int, onClick: any, toolTip: str, checkable: bool):
        btn = TouchifyActionButton()
        if onClick:
            btn.clicked.connect(onClick) # collect and disconnect all when closing
        btn.setToolTip(toolTip)
        btn.setContentsMargins(0,0,0,0)
        btn.setCheckable(checkable)
        self._buttons[id] = btn

        if row not in self._rows:
            rowWid = QWidget()
            rowWid.setLayout(QHBoxLayout())
            rowWid.layout().setSpacing(1)
            rowWid.layout().setContentsMargins(0, 0, 0, 0)
            rowWid.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
            self._rows[row] = rowWid
            self.layout().addWidget(rowWid)

        self._rows[row].layout().addWidget(btn)
        return btn