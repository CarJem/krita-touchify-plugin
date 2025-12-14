from krita import *
from PyQt5.QtCore import *


from touchify.src.api_krita.wrappers.window import WindowAPI
from touchify.src.alib_kis.widgets.KisSliderSpinBox import KisSliderSpinBox
from touchify.src.alib_kis.widgets.KisSliderSpinBoxContainer import KisSliderSpinBoxContainer
from touchify.src.settings.KritaSettings import *
from touchify.__env__ import *

class BrushSizeSlider(KisSliderSpinBoxContainer):

    def __init__(self, parent=None):
        super(BrushSizeSlider, self).__init__(KisSliderSpinBox(0.01, 1000, False, None), parent)
        self.view: View = None
        self.api_window: WindowAPI = None
        self.slider().setScaling(3)
        self.slider().setAffixes('Size: ', ' px')
        self.slider().connectValueChanged(self.onValueChanged)

    def setInstance(self, window: WindowAPI):
        self.api_window = window
        self.notifier = window.notifier
        self.notifier.viewChanged.connect(self.onViewChanged)
        self.onViewChanged(self.notifier.getCurrentView())
        self.notifier.brushSizeChanged.connect(self.onSizeChanged)
        self.onSizeChanged(self.notifier.getBrushSize())

    def onViewChanged(self, view: View):
        self.view = view

    def onSizeChanged(self, value: float):
        self.slider().setValue(value)

    def onValueChanged(self, value):
        if self.view == None: return
        self.view.setBrushSize(self.slider().value())