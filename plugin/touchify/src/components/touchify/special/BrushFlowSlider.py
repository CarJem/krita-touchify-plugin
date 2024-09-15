from math import e
from PyQt5.QtWidgets import QWidget
from krita import *
from PyQt5.QtCore import *

from ....stylesheet import Stylesheet
from ....ext.KritaSettings import *
from ...krita.KisSliderSpinBox import KisSliderSpinBox


class BrushFlowSlider(KisSliderSpinBox):
    def __init__(self, parent=None, window: Window = None):
        super(BrushFlowSlider, self).__init__(parent=parent, isInt=True)
        self.view: View = None
        self.sourceWindow: Window = window
        self.setAffixes('Flow: ', '%')
        self.connectValueChanged(self.valueChanged)

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
        self.view.setPaintingFlow(self.value()/100)

    def synchronizeView(self):
        active_window = self.sourceWindow
        if active_window == None: return

        active_view = active_window.activeView()
        if active_view == None: return

        self.view = active_view
        self.synchronize()

    def synchronize(self):
        if self.view == None: return
        self.setValue(self.view.paintingFlow()*100)