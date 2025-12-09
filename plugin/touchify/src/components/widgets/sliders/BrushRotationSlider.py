from PyQt5.QtWidgets import QWidget
from krita import *
from PyQt5.QtCore import *
from touchify.__env__ import *

from touchify.src.api_krita.wrappers.window import WindowAPI
from touchify.src.components.widgets.sliders.Slider import Slider
from touchify.src.managers.shared.settings_krita import *
from touchify.src.components.krita.KisAngleSelector import KisAngleSelector, KisAngleSelectorSpinBox




class BrushRotationSlider(Slider):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(KisAngleSelector(), parent)

        self.api_window: WindowAPI = None

        self.slider().setContentsMargins(0,0,0,0)
        self.slider().setMinimumWidth(100)
        self.slider().setFixedHeight(30)
        self.slider().setWidgetsHeight(30)

        self.slider().setFlipOptionsMode(KisAngleSelector.FlipOptionsMode.MenuButton)
        self.slider().spinBox.setPrefix('Rotation: ')
        self.slider().spinBox.valueChanged.connect(self.onValueChanged)

    def setInstance(self, window: WindowAPI):
        self.api_window = window        
        self.notifier = window.notifier
        self.notifier.viewChanged.connect(self.onViewChanged)
        self.onViewChanged(self.notifier.getCurrentView())
        self.notifier.brushRotationChanged.connect(self.onRotationChanged)
        self.onRotationChanged(self.notifier.getBrushRotation())

    def onViewChanged(self, view: View):
        self.view = view

    def onRotationChanged(self, value: float):
        self.slider().spinBox.setValue(value)

    def onValueChanged(self, value):
        if self.view == None: return
        self.view.setBrushRotation(self.slider().spinBox.value())