from PyQt5.QtWidgets import QWidget
from krita import *
from PyQt5.QtCore import *
from jemlib.api_touchify.env import *

from jemlib.api_krita.wrappers.window import WindowAPI
from jemlib.managers.KritaSettings import *
from jemlib.alib_kis.widgets.KisAngleSelector import KisAngleSelector




class BrushAngleSelector(KisAngleSelector):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.api_window: WindowAPI = None

        self.setContentsMargins(0,0,0,0)
        self.setMinimumWidth(100)
        self.setFixedHeight(30)
        self.setWidgetsHeight(30)

        self.setFlipOptionsMode(KisAngleSelector.FlipOptionsMode.MenuButton)
        self.spinBox.setPrefix('Rotation: ')
        self.spinBox.valueChanged.connect(self.onValueChanged)

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
        self.spinBox.setValue(value)

    def onValueChanged(self, value):
        if self.view == None: return
        self.view.setBrushRotation(self.spinBox.value())