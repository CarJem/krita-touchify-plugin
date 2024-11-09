from krita import *
from PyQt5.QtCore import *
from ....variables import *

from ....ext.KritaSettings import *
from ...krita.KisSliderSpinBox import KisSliderSpinBox
from ....helpers import TouchifyHelpers


class BrushFlowSlider(KisSliderSpinBox):
    def __init__(self, parent=None, window: Window = None):
        super(BrushFlowSlider, self).__init__(parent=parent, isInt=True)
        self.view: View = None
        self.sourceWindow: Window = window
        self.setAffixes('Flow: ', '%')
        self.connectValueChanged(self.valueChanged)
        self.timerActive = False
        self.setupTimer()

    def setupTimer(self):
        parentExtension = TouchifyHelpers.getExtension()
        if parentExtension:
            parentExtension.intervalTimerTicked.connect(self.onTimerTick)
            self.timerActive = True

    def onTimerTick(self):
        if self.timerActive:
            self.synchronizeView()

    def showEvent(self, event):
        self.timerActive = True
        super().showEvent(event)

    def hideEvent(self, event):
        self.timerActive = False
        super().hideEvent(event)

    def closeEvent(self, event):
        self.timerActive = False
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