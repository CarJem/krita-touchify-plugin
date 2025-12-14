
from krita import *
from PyQt5.QtCore import *

from touchify.src.api_krita import KritaAPI
from touchify.src.api_krita.wrappers.docker_factory import DockWidgetFactoryAPI
from touchify.src.components.widgets.canvas.CanvasColorPicker import CanvasColorPicker
from touchify.src.managers.GlobalEvents import GlobalEvents
from touchify.src.settings.TouchifySettings import TouchifySettings
from touchify.__env__ import *

from touchify.src.managers.ResourceManager import ResourceManager

DOCKER_TITLE = 'Touchify Addon: Color Options'
DOCKER_ID="Touchify/ColorOptionsDocker"

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.PluginWindow import TouchifyWindow

class ColorSourceToggle(QWidget):
    def __init__(self, parent: QWidget | None = None, cubeSize: int = 25):
        super(ColorSourceToggle, self).__init__(parent)
        self.canvas: Canvas = None
        self.setContentsMargins(0,0,0,0)

        self.app_window: "TouchifyWindow" = None

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
        cubeSize = int(self.cubeSize * TouchifySettings.preferences().Interface_ColorOptionsDockerScale)
        iconSize = int(cubeSize - 8)

        self.toggleBtn.setFixedSize(cubeSize, cubeSize)
        self.toggleBtn.setIconSize(QSize(iconSize, iconSize))

        self.resetBtn.setFixedSize(cubeSize, cubeSize)
        self.resetBtn.setIconSize(QSize(iconSize, iconSize))

        self.setFgBtn.setFixedHeight(cubeSize)
        self.setBgBtn.setFixedHeight(cubeSize)

    def setup(self, app_window: "TouchifyWindow"):
        self.app_window: TouchifyWindow = app_window
        self.setFgBtn.setInstance(self.app_window.api_window)
        self.setBgBtn.setInstance(self.app_window.api_window)

    def toggleColors(self):
        KritaAPI.get_action("toggle_fg_bg").trigger()

    def resetColors(self):
        KritaAPI.get_action("reset_fg_bg").trigger()

    def showEvent(self, event):
        super().showEvent(event)

    def closeEvent(self, event):
        super().closeEvent(event)

    def onCanvasChanged(self, canvas: Canvas):
        pass

class ColorOptionsDocker(DockWidget):

    def __init__(self): 
        super().__init__()
        self.setWindowTitle(DOCKER_TITLE)
        self.colorToggle = ColorSourceToggle(self, 25)
        self.setWidget(self.colorToggle)
        self.colorToggle.onCanvasChanged(self.canvas())
        GlobalEvents().SIGNAL_TOUCHIFY_CONFIG_UPDATED.connect(self.addonUpdateStyle)
        self.addonUpdateStyle()

    def TOUCHIFY_ADDON_SETUP(self, instance: "TouchifyWindow"):
        self.colorToggle.setup(instance)

    def addonUpdateStyle(self):
        widgetHeight = int(50 * TouchifySettings.preferences().Interface_ColorOptionsDockerScale)
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

KritaAPI.add_dock_widget_factory(DOCKER_ID, DockWidgetFactoryAPI.DockPosition.DockRight, ColorOptionsDocker)

