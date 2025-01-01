from krita import *
from PyQt5.QtCore import *


from touchify.src.ext.KritaSettings import *
from touchify.src.components.krita.KisSliderSpinBox import KisSliderSpinBox
from touchify.src.variables import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.window import TouchifyWindow

class BrushSizeSlider(KisSliderSpinBox):

    def __init__(self, parent=None):
        super(BrushSizeSlider, self).__init__(0.01, 1000, False, parent)
        self.view: View = None
        self.appEngine: "TouchifyWindow" = None
        self.setScaling(3)
        self.setAffixes('Size: ', ' px')
        self.connectValueChanged(self.onValueChanged)

    def setInstance(self, window: "TouchifyWindow"):
        self.appEngine = window
        self.appEngine.action_management.viewChanged.connect(self.onViewChanged)
        self.onViewChanged(self.appEngine.action_management.getCurrentView())
        self.appEngine.action_management.brushSizeChanged.connect(self.onSizeChanged)
        self.onSizeChanged(self.appEngine.action_management.getBrushSize())

    def onViewChanged(self, view: View):
        self.view = view

    def onSizeChanged(self, value: float):
        self.setValue(value)

    def onValueChanged(self, value):
        if self.view == None: return
        self.view.setBrushSize(self.value())