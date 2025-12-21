from krita import *
from PyQt5.QtCore import *

from jemlib.api_touchify.env import *

from jemlib.api_krita.wrappers.window import WindowAPI
from jemlib.alib_kis.widgets.KisSliderSpinBox import KisSliderSpinBox
from jemlib.alib_kis.widgets.KisSliderSpinBoxContainer import KisSliderSpinBoxContainer
from jemlib.managers.KritaSettings import *


class BrushFlowSlider(KisSliderSpinBoxContainer):
    def __init__(self, parent=None):
        super(BrushFlowSlider, self).__init__(KisSliderSpinBox(parent=None, isInt=True), parent)
        self.api_window: WindowAPI = None
        self.slider().setAffixes('Flow: ', '%')
        self.slider().connectValueChanged(self.onValueChanged)
        self.view: View = None

    def setInstance(self, window: WindowAPI):
        self.api_window = window
        self.notifier = window.notifier
        self.notifier.viewChanged.connect(self.onViewChanged)
        self.onViewChanged(self.notifier.getCurrentView())
        self.notifier.brushFlowChanged.connect(self.onFlowChanged)
        self.onFlowChanged(self.notifier.getBrushFlow())

    def onViewChanged(self, view: View):
        self.view = view

    def onFlowChanged(self, value: float):
        self.slider().setValue(value*100)

    def onValueChanged(self, value):
        if self.view == None: return
        self.view.setPaintingFlow(self.slider().value()/100)