from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QSizePolicy, QStackedWidget
from krita import *
from PyQt5.QtWidgets import *

from krita import *

from ....settings.TouchifyConfig import *
from ....variables import *
from ....docker_manager import *
from .... import stylesheet

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfContainer import ToolshelfContainer

class ToolshelfPanelHeader(QWidget):
    def __init__(self, cfg: CfgToolshelf, isRootHeader: bool = True, parent: "ToolshelfContainer" = None):
        super(ToolshelfPanelHeader, self).__init__(parent)

        self.rootContainer = parent

        self._height = cfg.dockerBackHeight
        self._iconSize = self._height - 4
        self.setFixedHeight(self._height)

        self.ourLayout = QHBoxLayout(self)
        self.ourLayout.setSpacing(0)
        self.ourLayout.setContentsMargins(0,0,0,0)
        self.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.setLayout(self.ourLayout)

        self.backButton = None
        self.fillerWidget = None

        if not isRootHeader:
            self.backButton = QPushButton(self)
            self.backButton.setIcon(Krita.instance().action('move_layer_up').icon())
            self.backButton.setIconSize(QSize(self._iconSize, self._iconSize))
            self.backButton.setFixedHeight(self._height)
            self.backButton.clicked.connect(self.goBack)
            self.backButton.setObjectName("back-widget")
            self.ourLayout.addWidget(self.backButton)
        else:
            self.fillerWidget = QWidget(self)
            self.fillerWidget.setObjectName("filler-widget")
            self.ourLayout.addWidget(self.fillerWidget)

        self.pinButton = QPushButton(self)
        self.pinButton.setIcon(Krita.instance().icon('krita_tool_reference_images'))
        self.pinButton.setObjectName("pin-widget")
        self.pinButton.setIconSize(QSize(self._iconSize, self._iconSize))
        self.pinButton.setFixedHeight(self._height)
        self.pinButton.setFixedWidth(self._height)
        self.pinButton.setCheckable(True)
        self.pinButton.clicked.connect(self.pinToolshelf)
        self.ourLayout.addWidget(self.pinButton)

    def setPinState(self, value: bool):
        if self.pinButton:
            self.pinButton.setChecked(True if value else False)

    def goBack(self):
        if self.rootContainer:
            self.rootContainer.goHome()

    def pinToolshelf(self):
        if self.rootContainer:
            self.rootContainer.togglePinned()

    def updateStyleSheet(self):
        self.setStyleSheet(stylesheet.touchify_toolshelf_header)