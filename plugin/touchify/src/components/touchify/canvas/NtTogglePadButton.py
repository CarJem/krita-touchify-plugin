from PyQt5.QtCore import Qt, QSize


from touchify.src.settings import *
from touchify.src.stylesheet import Stylesheet


from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QSizePolicy, QToolButton


class NtTogglePadButton(QToolButton):
    def __init__(self, parent = None):
        super(NtTogglePadButton, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        qApp.paletteChanged.connect(self.updateStyleSheet)
        self.updateStyleSheet()

    def updateStyleSheet(self):
        iconSize: int = int(11 * TouchifyConfig.instance().preferences().Interface_CanvasToggleScale)
        self.setIconSize(QSize(iconSize, iconSize))
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
