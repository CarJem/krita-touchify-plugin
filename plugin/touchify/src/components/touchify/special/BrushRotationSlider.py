from math import e
from PyQt5.QtWidgets import QWidget
from krita import *
from PyQt5.QtCore import *

from ....stylesheet import Stylesheet
from ....ext.KritaSettings import *
from ...krita.KisAngleSelector import KisAngleSelector


class BrushRotationSlider(KisAngleSelector):
    def __init__(self, parent: QWidget | None = None, window: Window = None) -> None:
        super().__init__(parent)
        self.view: View = None
        self.sourceWindow: Window = window
        self.setContentsMargins(0,0,0,0)
        self.setMinimumWidth(100)
        self.setFixedHeight(30)
        self.setWidgetsHeight(30)

        self.setFlipOptionsMode(KisAngleSelector.FlipOptionsMode.MenuButton)
        self.spinBox.setPrefix('Rotation: ')
        self.spinBox.valueChanged.connect(self.valueChanged)

        self.timer_pulse = QTimer(self)
        self.timer_pulse.timeout.connect(self.synchronizeView)
        self.timer_pulse.start(100)

    def showEvent(self, event):
        self.timer_pulse.start()
        super().showEvent(event)
    def closeEvent(self, event):
        self.timer_pulse.stop()
        super().closeEvent(event)

    def setSourceWindow(self, window: Window):
        self.sourceWindow = window
        self.synchronizeView()

    def valueChanged(self, value):
        if self.view == None: return
        self.view.setBrushRotation(self.spinBox.value())

    def synchronizeView(self):
        active_window = self.sourceWindow
        if active_window == None: return

        active_view = active_window.activeView()
        if active_view == None: return

        self.view = active_view
        self.synchronize()

    def synchronize(self):
        if self.view == None: return
        self.setAngle(self.view.brushRotation())