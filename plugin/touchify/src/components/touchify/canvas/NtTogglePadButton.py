from enum import Enum
from PyQt5.QtWidgets import QWidget, QDockWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt, QSize, QPoint

from ....ext.KritaSettings import KritaSettings

from ....settings.TouchifyConfig import *
from ....ext.PyQtExtensions import PyQtExtensions as Ext
from ....stylesheet import Stylesheet


from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QSizePolicy, QToolButton


class NtTogglePadButton(QToolButton):
    def __init__(self, parent = None):
        super(NtTogglePadButton, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.setIconSize(QSize(11, 11))

        qApp.paletteChanged.connect(self.updateStyleSheet)
        self.updateStyleSheet()

    def updateStyleSheet(self):
        self.setStyleSheet(Stylesheet.instance().touchify_toggle_button)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.RightButton:
            self.showMenu()
        else:
            return super().mousePressEvent(e)

    def setArrow(self, alignment_x: Qt.AlignmentFlag, alignment_y: Qt.AlignmentFlag, enabled: bool = True):
        if alignment_x == Qt.AlignmentFlag.AlignLeft:
            self.setArrowType(Qt.ArrowType.RightArrow if not enabled else Qt.ArrowType.LeftArrow)
        elif alignment_x == Qt.AlignmentFlag.AlignRight:
            self.setArrowType(Qt.ArrowType.LeftArrow if not enabled else Qt.ArrowType.RightArrow)
        elif alignment_x == Qt.AlignmentFlag.AlignHCenter:
            if alignment_y == Qt.AlignmentFlag.AlignTop:
                self.setArrowType(Qt.ArrowType.DownArrow if not enabled else Qt.ArrowType.UpArrow)
            elif alignment_y == Qt.AlignmentFlag.AlignBottom:
                self.setArrowType(Qt.ArrowType.UpArrow if not enabled else Qt.ArrowType.DownArrow)
            else:
                self.setArrowType(Qt.ArrowType.DownArrow if not enabled else Qt.ArrowType.UpArrow)
        else:
            self.setArrowType(Qt.ArrowType.RightArrow if not enabled else Qt.ArrowType.LeftArrow)
