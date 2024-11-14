
from PyQt5.QtWidgets import QWidget
from krita import *
from PyQt5.QtCore import *

from touchify.src.components.touchify.special.BrushFlowSlider import BrushFlowSlider
from touchify.src.components.touchify.special.BrushOpacitySlider import BrushOpacitySlider
from touchify.src.components.touchify.special.BrushRotationSlider import BrushRotationSlider
from touchify.src.components.touchify.special.BrushSizeSlider import BrushSizeSlider
from touchify.src.variables import *

from touchify.src.stylesheet import Stylesheet
from touchify.src.ext.KritaSettings import *
from touchify.src.components.krita.KisSliderSpinBox import KisSliderSpinBox

DOCKER_TITLE = 'Touchify Addon: Brush Options'
DOCKER_ID = "Touchify/BrushOptionsDocker"

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.window import TouchifyWindow

class BrushOptionsDockerCfg:

    def __init__(self):
        self.ShowFlowSlider = KritaSettings.readSettingBool(DOCKER_ID, "ShowFlowSlider", True)
        self.ShowOpacitySlider = KritaSettings.readSettingBool(DOCKER_ID, "ShowOpacitySlider", True)
        self.ShowSizeSlider = KritaSettings.readSettingBool(DOCKER_ID, "ShowSizeSlider", True)
        self.ShowRotationSlider = KritaSettings.readSettingBool(DOCKER_ID, "ShowRotationSlider", True)

    def toggle(self, setting: str):
        if hasattr(self, setting):
            currentValue = getattr(self, setting)
            currentValue = not currentValue
            setattr(self, setting, currentValue)
            self.save()


    def save(self):
        KritaSettings.writeSettingBool(DOCKER_ID, "ShowFlowSlider", self.ShowFlowSlider)
        KritaSettings.writeSettingBool(DOCKER_ID, "ShowOpacitySlider", self.ShowOpacitySlider)
        KritaSettings.writeSettingBool(DOCKER_ID, "ShowSizeSlider", self.ShowSizeSlider)
        KritaSettings.writeSettingBool(DOCKER_ID, "ShowRotationSlider", self.ShowRotationSlider)

class BrushOptionsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super(BrushOptionsWidget, self).__init__(parent)

        self.sourceWindow: Window = None

        self.config = BrushOptionsDockerCfg()
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.gridLayout = QVBoxLayout(self)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setContentsMargins(0,0,0,0)

        self.sizeSlider = BrushSizeSlider(self)
        self.opacitySlider = BrushOpacitySlider(self)
        self.flowSlider = BrushFlowSlider(self)
        self.rotationSlider = BrushRotationSlider(self)

        self.optionsMenu = self.genMenu()
        self.optionsButton = QPushButton(self)
        self.optionsButton.setIcon(Krita.instance().icon("configure"))
        self.optionsButton.setMenu(self.optionsMenu)
        self.optionsButton.setFixedHeight(15)
        self.optionsButton.setStyleSheet(Stylesheet.instance().hide_menu_indicator)
        self.optionsButton.clicked.connect(self.optionsButton.showMenu)
        self.gridLayout.addWidget(self.optionsButton)
        
        self.gridLayout.addWidget(self.sizeSlider)
        self.gridLayout.addWidget(self.opacitySlider)
        self.gridLayout.addWidget(self.flowSlider)
        self.gridLayout.addWidget(self.rotationSlider)
        self.gridLayout.addWidget(self.optionsButton)

        self.updateSliders()

    def setup(self, instance: "TouchifyWindow"):
        self.sourceWindow = instance.windowSource
        
        self.sizeSlider.setSourceWindow(self.sourceWindow)
        self.opacitySlider.setSourceWindow(self.sourceWindow)
        self.flowSlider.setSourceWindow(self.sourceWindow)
        self.rotationSlider.setSourceWindow(self.sourceWindow)

        self.updateSliders()

    def genMenu(self):
        menu = QMenu()
        sect = menu.addSeparator()
        sect.setText("Show:")

        sizeToggle = menu.addAction("Size")
        sizeToggle.setCheckable(True)
        sizeToggle.setChecked(self.config.ShowSizeSlider)
        sizeToggle.toggled.connect(lambda: self.toggleSlider("ShowSizeSlider"))

        opacityToggle = menu.addAction("Opacity")
        opacityToggle.setCheckable(True)
        opacityToggle.setChecked(self.config.ShowOpacitySlider)
        opacityToggle.toggled.connect(lambda: self.toggleSlider("ShowOpacitySlider"))

        flowToggle = menu.addAction("Flow")
        flowToggle.setCheckable(True)
        flowToggle.setChecked(self.config.ShowFlowSlider)
        flowToggle.toggled.connect(lambda: self.toggleSlider("ShowFlowSlider"))

        rotationToggle = menu.addAction("Rotation")
        rotationToggle.setCheckable(True)
        rotationToggle.setChecked(self.config.ShowRotationSlider)
        rotationToggle.toggled.connect(lambda: self.toggleSlider("ShowRotationSlider"))

        return menu

    
    def toggleSlider(self, setting: str):
        self.config.toggle(setting)
        self.updateSliders()

    def updateSliders(self):

        def updateSliderVisibility(option: bool, slider: KisSliderSpinBox):
            if option and slider.isHidden():
                slider.show()
                slider.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
                slider.updateGeometry()
                slider.adjustSize()
            elif option == False and slider.isVisible():
                slider.hide()
                slider.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
                slider.updateGeometry()
                slider.adjustSize()

        updateSliderVisibility(self.config.ShowSizeSlider, self.sizeSlider)
        updateSliderVisibility(self.config.ShowOpacitySlider, self.opacitySlider)
        updateSliderVisibility(self.config.ShowFlowSlider, self.flowSlider)
        updateSliderVisibility(self.config.ShowRotationSlider, self.rotationSlider)
        
    def showEvent(self, event):
        super().showEvent(event)

    def closeEvent(self, event):
        super().closeEvent(event)

    def onCanvasChanged(self, canvas: Canvas):
        self.updateSliders()

class BrushOptionsDocker(DockWidget):

    def __init__(self): 
        super().__init__()
        self.setWindowTitle(DOCKER_TITLE)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.brushOptions = BrushOptionsWidget(self)
        self.setWidget(self.brushOptions)

    def addonSetup(self, instance: "TouchifyWindow"):
        self.brushOptions.setup(instance)

    def showEvent(self, event):
        super().showEvent(event)

    def closeEvent(self, event):
        super().closeEvent(event)
    
    # notifies when views are added or removed
    # 'pass' means do not do anything
    def canvasChanged(self, canvas):
        self.brushOptions.onCanvasChanged(canvas)

Krita.instance().addDockWidgetFactory(DockWidgetFactory(DOCKER_ID, DockWidgetFactoryBase.DockPosition.DockRight, BrushOptionsDocker))
