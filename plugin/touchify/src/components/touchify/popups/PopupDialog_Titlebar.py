from krita import Krita

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from ....stylesheet import Stylesheet

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .PopupDialog import PopupDialog


class PopupDialog_Titlebar(QWidget):

    def __init__(self, parentDialog: "PopupDialog"):
        super(PopupDialog_Titlebar, self).__init__(parentDialog)
        self.parentDialog = parentDialog
        self.setObjectName("popupFrameTitlebar")
        self.setStyleSheet(Stylesheet.instance().touchify_popup_titlebar(self.parentDialog.allowOpacity, self.parentDialog.metadata.opacity))

        buttonSize = 16
        iconSize = 13
        textSize = 10

        self.isMoving = False
        
        self.ourLayout = QHBoxLayout(self)
        self.ourLayout.setContentsMargins(3, 3, 3, 4)
        self.setLayout(self.ourLayout)

        self.titlebarText = QLabel(self)
        self.titlebarText.setFont(self.getTitleFont(textSize))
        self.titlebarText.setText(self.parentDialog.metadata.display_name)
        self.ourLayout.addWidget(self.titlebarText)

        self.minimizeBtn = QPushButton(self)
        self.minimizeBtn.setIcon(Krita.instance().icon('arrow-down'))
        self.minimizeBtn.setFixedSize(buttonSize,buttonSize)
        self.minimizeBtn.setIconSize(QSize(iconSize, iconSize))
        self.minimizeBtn.clicked.connect(self.toggleMinimized)
        self.minimizeBtn.setStyleSheet(Stylesheet.instance().touchify_toggle_button)
        self.ourLayout.addWidget(self.minimizeBtn)

        self.closeButton = QPushButton(self)
        self.closeButton.setIcon(Krita.instance().icon('docker_close'))
        self.closeButton.setFixedSize(buttonSize,buttonSize)
        self.closeButton.setIconSize(QSize(iconSize, iconSize))
        self.closeButton.clicked.connect(self.parentDialog.close)
        self.closeButton.setStyleSheet(Stylesheet.instance().touchify_toggle_button)
        self.ourLayout.addWidget(self.closeButton)

    def getTitleFont(self, textSize: int):
        result = QFont()
        result.setPixelSize(textSize)
        return result

    def toggleMinimized(self):
        self.parentDialog.toggleMinimized()

    def mousePressEvent(self, event: QMouseEvent):
        if not self.parentDialog.isResizing:
            self.start = self.mapToGlobal(event.pos())
            self.isMoving = True
        elif event.button() == Qt.MouseButton.LeftButton and self.parentDialog.isResizing:
            self.parentDialog.resizeWindow(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.isMoving:
            self.end = self.mapToGlobal(event.pos())
            self.movement = self.end-self.start
            self.parentDialog.setGeometry(self.mapToGlobal(self.movement).x(),
                                self.mapToGlobal(self.movement).y(),
                                self.parentDialog.width(),
                                self.parentDialog.height())
            self.start = self.end

    def mouseReleaseEvent(self, event):
        self.isMoving = False
