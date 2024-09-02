from enum import Enum
from PyQt5.QtWidgets import QWidget, QDockWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt, QSize, QPoint

from ....ext.KritaSettings import KritaSettings

from ....settings.TouchifyConfig import *
from ....ext.extensions_pyqt import PyQtExtensions as Ext
from .NtWidgetPadAlignment import NtWidgetPadAlignment
from ....stylesheet import Stylesheet


from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QSizePolicy, QToolButton


class NtTogglePadButton(QToolButton):
    def __init__(self, parent = None):
        super(NtTogglePadButton, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.setIconSize(QSize(11, 11))
        self.setStyleSheet(Stylesheet.instance().touchify_toggle_button)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.RightButton:
            self.showMenu()
        else:
            return super().mousePressEvent(e)

    def setArrow(self, alignment: NtWidgetPadAlignment):
        if alignment == NtWidgetPadAlignment.Right:
            self.setArrowType(Qt.ArrowType.RightArrow)
        else:
            self.setArrowType(Qt.ArrowType.LeftArrow)