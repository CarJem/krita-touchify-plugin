from krita import *
from PyQt5.QtCore import *


from touchify.src.api_krita.wrappers.window import WindowAPI
from touchify.src.managers.shared.settings_krita import *
from touchify.src.components.krita.KisSliderSpinBox import KisSliderSpinBox
from touchify.__env__ import *

class BrushSizeSlider(KisSliderSpinBox):

    def __init__(self, parent=None):
        super(BrushSizeSlider, self).__init__(0.01, 1000, False, parent)
        self.view: View = None
        self.api_window: WindowAPI = None
        self.setScaling(3)
        self.setAffixes('Size: ', ' px')
        self.connectValueChanged(self.onValueChanged)

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
        self.setValue(value)

    def onValueChanged(self, value):
        if self.view == None: return
        self.view.setBrushSize(self.value())