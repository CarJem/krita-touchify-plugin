from krita import *
from PyQt5.QtCore import *

from ....ext.KritaSettings import *
from ...krita.KisSliderSpinBox import KisSliderSpinBox
from ....variables import *

class BrushSizeSlider(KisSliderSpinBox):

    def __init__(self, parent=None, window: Window = None):
        super(BrushSizeSlider, self).__init__(0.01, 1000, False, parent)
        self.view: View = None
        self.sourceWindow: Window = window
        self.setScaling(3)
        self.setAffixes('Size: ', ' px')
        self.connectValueChanged(self.valueChanged)

        self.timer_pulse = QTimer(self)
        self.timer_pulse.timeout.connect(self.synchronizeView)
        self.timer_pulse.start(TOUCHIFY_TIMER_BRUSH_SLIDER_INTERVAL)

    def showEvent(self, event):
        self.timer_pulse.start()
        super().showEvent(event)

    def hideEvent(self, event):
        self.timer_pulse.stop()
        super().hideEvent(event)

    def closeEvent(self, event):
        self.timer_pulse.stop()
        super().closeEvent(event)

    def setSourceWindow(self, window: Window):
        self.sourceWindow = window
        self.synchronizeView()

    def valueChanged(self, value):
        if self.view == None: return
        self.view.setBrushSize(value)

    def synchronizeView(self):
        if self.isVisible() == False:
            return
        
        active_window = self.sourceWindow
        if active_window == None: return

        active_view = active_window.activeView()
        if active_view == None: return

        self.view = active_view
        self.synchronize()

    def synchronize(self):
        if self.view == None: return
        self.setValue(self.view.brushSize())