from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from jemlib.api_touchify.env import *
from jemlib.api_krita import KritaAPI
from jemlib.alib_widgets.labels.ElidedLabel import ElidedLabel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from touchify_toolshelves.src.components.PopupWidget import PopupWidget

class PopupTitlebar(QWidget):
    def __init__(self, parent_popup: "PopupWidget"):
        super().__init__(parent_popup)
        self.parent_popup = parent_popup
        self.setObjectName("touchify_popup_titlebar")
        self.setFixedHeight(17)
        self.ourLayout = QHBoxLayout(self)
        self.ourLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.ourLayout)


        self.titlebarText = ElidedLabel(self)
        self.ourLayout.addWidget(self.titlebarText)

        self.minimizeBtn = QPushButton(self)
        self.minimizeBtn.setIcon(KritaAPI.get_icon('docker_collapse_a'))
        self.minimizeBtn.setFixedSize(18,18)
        self.minimizeBtn.clicked.connect(self.parent_popup.toggleShade)
        self.minimizeBtn.setFlat(True)
        self.ourLayout.addWidget(self.minimizeBtn)

        self.closeButton = QPushButton(self)
        self.closeButton.setIcon(KritaAPI.get_icon('docker_close'))
        self.closeButton.setFixedSize(18,18)
        self.closeButton.setFlat(True)
        self.closeButton.clicked.connect(self.parent_popup.closePopup)
        self.ourLayout.addWidget(self.closeButton)

    def setTitleBarText(self, text: str):
        self.titlebarText.setText(text)

    def updateCollapseState(self, is_collapsed: bool):
        if is_collapsed:
            self.minimizeBtn.setIcon(KritaAPI.get_icon('docker_collapse_a'))
        else:
            self.minimizeBtn.setIcon(KritaAPI.get_icon('docker_collapse_b'))
            

    def setFloatingVisibility(self, value: bool):
        self.minimizeBtn.setVisible(value)