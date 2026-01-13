from krita import *
from PyQt5.QtCore import *
from jemlib.api_touchify.env import *

from jemlib.api_krita.wrappers.window import WindowAPI
from jemlib.alib_kis.widgets.KisSliderSpinBox import KisSliderSpinBox
from jemlib.alib_kis.widgets.KisSliderSpinBoxContainer import KisSliderSpinBoxContainer
from jemlib.managers.KritaSettings import *



class BrushOpacitySlider(KisSliderSpinBoxContainer):

    def __init__(self, parent=None):
        super(BrushOpacitySlider, self).__init__(KisSliderSpinBox(parent=None, isInt=True), parent)
        self.view: View = None
        self.api_window: WindowAPI = None
        self.__lastValue: float = 0
        
        self.slider().setAffixes('Opacity: ', '%')
        self.slider().connectValueChanged(self.onValueChanged)
    
    def setInstance(self, window: WindowAPI):
        self.api_window = window
        self.notifier = window.notifier
        self.notifier.viewChanged.connect(self.onViewChanged)
        self.onViewChanged(self.notifier.getCurrentView())
        self.notifier.brushOpacityChanged.connect(self.onOpacityChanged)
        self.onOpacityChanged(self.notifier.getBrushOpacity())

    def onViewChanged(self, view: View):
        self.view = view

    def onOpacityChanged(self, value: float):
        if self.__lastValue == value: return
        self.__lastValue = value
        self.slider().setValue(value*100, suppress_signals=True)

    def onValueChanged(self, value):
        if self.view == None: return
        self.view.setPaintingOpacity(self.slider().value()/100)

