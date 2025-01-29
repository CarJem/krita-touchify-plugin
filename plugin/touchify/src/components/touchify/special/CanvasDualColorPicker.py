
from krita import *
from PyQt5.QtCore import *

from touchify.src.components.touchify.special.CanvasColorPicker import CanvasColorPicker
from touchify.src.managers.shared.resources import ResourceManager
from touchify.variables import *


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.window import TouchifyWindow

class CanvasDualColorPicker(QWidget):
    

    def __init__(self, parent: QWidget | None = None):
        super(CanvasDualColorPicker, self).__init__(parent)

        MIN_SIZE = 8

        size_policy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        size_policy.setWidthForHeight(True)

        self.setContentsMargins(0,0,0,0)

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(0,0,0,0)
        self.gridLayout.setSpacing(0)
        self.setLayout(self.gridLayout)

        self.fg_button = CanvasColorPicker(self, CanvasColorPicker.Mode.Foreground)
        self.fg_button.padding = 4
        self.fg_button.setMinimumWidth(MIN_SIZE)
        self.fg_button.setMinimumHeight(MIN_SIZE)
        self.fg_button.setContentsMargins(0,0,0,0)
        self.fg_button.setSizePolicy(size_policy)
        self.gridLayout.addWidget(self.fg_button, 0, 0)

        self.swap_button = QPushButton(self)
        self.swap_button.setMinimumWidth(MIN_SIZE)
        self.swap_button.setMinimumHeight(MIN_SIZE)
        self.swap_button.setIcon(ResourceManager.materialIcon("swap-horizontal"))
        self.swap_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.swap_button.setContentsMargins(0,0,0,0)
        self.swap_button.setSizePolicy(size_policy)
        self.swap_button.clicked.connect(self.toggleColors)
        self.gridLayout.addWidget(self.swap_button, 0, 1)

        self.reset_button = QPushButton(self)
        self.reset_button.setMinimumWidth(MIN_SIZE)
        self.reset_button.setMinimumHeight(MIN_SIZE)
        self.reset_button.setIcon(ResourceManager.kritaIcon("color-to-alpha"))
        self.reset_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.reset_button.clicked.connect(self.resetColors)
        self.reset_button.setSizePolicy(size_policy)
        self.reset_button.setContentsMargins(0,0,0,0)
        self.gridLayout.addWidget(self.reset_button, 1, 0)

        self.bg_button = CanvasColorPicker(self, CanvasColorPicker.Mode.Background)
        self.bg_button.padding = 4
        self.bg_button.setMinimumWidth(MIN_SIZE)
        self.bg_button.setMinimumHeight(MIN_SIZE)
        self.bg_button.setContentsMargins(0,0,0,0)
        self.bg_button.setSizePolicy(size_policy)
        self.gridLayout.addWidget(self.bg_button, 1, 1)

    def toggleColors(self):
        Krita.instance().action("toggle_fg_bg").trigger()

    def resetColors(self):
        Krita.instance().action("reset_fg_bg").trigger()

    def setInstance(self, window: "TouchifyWindow"):
        self.fg_button.setInstance(window)
        self.bg_button.setInstance(window)