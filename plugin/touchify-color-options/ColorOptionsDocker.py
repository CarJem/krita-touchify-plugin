
from krita import *
from PyQt5.QtCore import *

from touchify.src.components.touchify.special.CanvasColorPicker import CanvasColorPicker
from touchify.src.settings import TouchifySettings
from touchify.src.variables import *

from touchify.src.resources import ResourceManager
from touchify.src.helpers import TouchifyHelpers

DOCKER_TITLE = 'Touchify Addon: Color Options'
DOCKER_ID="Touchify/ColorOptionsDocker"

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.window import TouchifyWindow

class ColorSourceToggle(QWidget):
    def __init__(self, parent: QWidget | None = None, cubeSize: int = 25):
        super(ColorSourceToggle, self).__init__(parent)
        self.canvas: Canvas = None
        self.setContentsMargins(0,0,0,0)

        self.instance: TouchifyWindow = None
        self.sourceWindow: Window = None

        self.cubeSize = cubeSize

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.gridLayout = QHBoxLayout(self)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setContentsMargins(0,0,0,0)

        self.setFgBtn = CanvasColorPicker(self, CanvasColorPicker.Mode.Foreground)
        self.setFgBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.gridLayout.addWidget(self.setFgBtn)

        self.toggleBtn = QPushButton(self)
        self.toggleBtn.setIcon(ResourceManager.materialIcon("swap-horizontal"))
        self.toggleBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.toggleBtn.clicked.connect(self.toggleColors)
        self.gridLayout.addWidget(self.toggleBtn)

        self.setBgBtn = CanvasColorPicker(self, CanvasColorPicker.Mode.Background)
        self.setBgBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.gridLayout.addWidget(self.setBgBtn)

        self.resetBtn = QPushButton(self)
        self.resetBtn.setIcon(ResourceManager.kritaIcon("color-to-alpha"))
        self.resetBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.resetBtn.clicked.connect(self.resetColors)
        
        self.gridLayout.addWidget(self.resetBtn)

        self.updateStyle()

    def updateStyle(self):
        cubeSize = int(self.cubeSize * TouchifySettings.instance().preferences().Interface_ColorOptionsDockerScale)
        iconSize = int(cubeSize - 8)

        self.toggleBtn.setFixedSize(cubeSize, cubeSize)
        self.toggleBtn.setIconSize(QSize(iconSize, iconSize))

        self.resetBtn.setFixedSize(cubeSize, cubeSize)
        self.resetBtn.setIconSize(QSize(iconSize, iconSize))

        self.setFgBtn.setFixedHeight(cubeSize)
        self.setBgBtn.setFixedHeight(cubeSize)

    def setup(self, instance: "TouchifyWindow"):
        self.sourceWindow: Window = instance.windowSource
        parentExtension = TouchifyHelpers.getExtension()
        if parentExtension:
            parentExtension.intervalTimerTicked.connect(self.intervalTimerTicked)

    def toggleColors(self):
        Krita.instance().action("toggle_fg_bg").trigger()
        self.setFgBtn.updateColors()
        self.setBgBtn.updateColors()

    def resetColors(self):
        Krita.instance().action("reset_fg_bg").trigger()
        self.setFgBtn.updateColors()
        self.setBgBtn.updateColors()

    def showEvent(self, event):
        super().showEvent(event)

    def closeEvent(self, event):
        super().closeEvent(event)

    def intervalTimerTicked(self):
        pass

    def onCanvasChanged(self, canvas: Canvas):
        self.setFgBtn.updateColors()
        self.setBgBtn.updateColors()

class ColorOptionsDocker(DockWidget):

    def __init__(self): 
        super().__init__()
        self.setWindowTitle(DOCKER_TITLE)
        self.colorToggle = ColorSourceToggle(self, 25)
        self.setWidget(self.colorToggle)
        self.colorToggle.onCanvasChanged(self.canvas())
        self.addonUpdateStyle()

    def addonSetup(self, instance: "TouchifyWindow"):
        self.colorToggle.setup(instance)
        instance.connectNotify

    def addonUpdateStyle(self):
        widgetHeight = int(50 * TouchifySettings.instance().preferences().Interface_ColorOptionsDockerScale)
        self.setFixedHeight(widgetHeight)
        self.colorToggle.updateStyle()

    def showEvent(self, event):
        super().showEvent(event)

    def closeEvent(self, event):
        super().closeEvent(event)

    # notifies when views are added or removed
    # 'pass' means do not do anything
    def canvasChanged(self, canvas):
        self.colorToggle.onCanvasChanged(canvas)

Krita.instance().addDockWidgetFactory(DockWidgetFactory(DOCKER_ID, DockWidgetFactoryBase.DockPosition.DockRight, ColorOptionsDocker))
