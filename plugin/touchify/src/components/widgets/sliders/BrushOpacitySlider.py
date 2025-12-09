from krita import *
from PyQt5.QtCore import *
from touchify.__env__ import *

from touchify.src.api_krita.wrappers.window import WindowAPI
from touchify.src.components.krita.KisSliderSpinBox import KisSliderSpinBox
from touchify.src.components.widgets.sliders.Slider import Slider
from touchify.src.managers.shared.settings_krita import *



class BrushOpacitySlider(Slider):

    def __init__(self, parent=None):
        super(BrushOpacitySlider, self).__init__(KisSliderSpinBox(parent=None, isInt=True), parent)
        self.view: View = None
        self.api_window: WindowAPI = None
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
        self.slider().setValue(value*100)

    def onValueChanged(self, value):
        if self.view == None: return
        self.view.setPaintingOpacity(self.slider().value()/100)

