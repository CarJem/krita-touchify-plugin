from krita import Krita

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from ....stylesheet import Stylesheet

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .PopupDialog import PopupDialog


class PopupDialog_Titlebar(QFrame):

    def __init__(self, parentDialog: "PopupDialog"):
        super(PopupDialog_Titlebar, self).__init__(parentDialog)
        self.parentDialog = parentDialog
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(1)
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
