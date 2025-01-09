from PyQt5.QtWidgets import QWidget
from krita import *
from PyQt5.QtCore import *
from touchify.src.variables import *

from touchify.src.components.krita.settings import *
from touchify.src.components.krita.ui.KisAngleSelector import KisAngleSelector

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.window import TouchifyWindow


class BrushRotationSlider(KisAngleSelector):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.appEngine: "TouchifyWindow" = None
        self.setContentsMargins(0,0,0,0)
        self.setMinimumWidth(100)
        self.setFixedHeight(30)
        self.setWidgetsHeight(30)

        self.setFlipOptionsMode(KisAngleSelector.FlipOptionsMode.MenuButton)
        self.spinBox.setPrefix('Rotation: ')
        self.spinBox.valueChanged.connect(self.onValueChanged)

    def setInstance(self, window: "TouchifyWindow"):
        self.appEngine = window
        self.appEngine.action_management.viewChanged.connect(self.onViewChanged)
        self.onViewChanged(self.appEngine.action_management.getCurrentView())
        self.appEngine.action_management.brushRotationChanged.connect(self.onRotationChanged)
        self.onRotationChanged(window.action_management.getBrushRotation())

    def onViewChanged(self, view: View):
        self.view = view

    def onRotationChanged(self, value: float):
        self.spinBox.setValue(value)

    def onValueChanged(self, value):
        if self.view == None: return
        self.view.setBrushRotation(self.spinBox.value())