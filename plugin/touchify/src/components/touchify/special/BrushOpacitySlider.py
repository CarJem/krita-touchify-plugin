from krita import *
from PyQt5.QtCore import *
from touchify.src.variables import *

from touchify.src.ext.KritaSettings import *
from touchify.src.components.krita.KisSliderSpinBox import KisSliderSpinBox

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.window import TouchifyWindow

class BrushOpacitySlider(KisSliderSpinBox):

    def __init__(self, parent=None):
        super(BrushOpacitySlider, self).__init__(parent=parent, isInt=True)
        self.view: View = None
        self.appEngine: "TouchifyWindow" = None
        self.setAffixes('Opacity: ', '%')
        self.connectValueChanged(self.onValueChanged)
    
    def setInstance(self, window: "TouchifyWindow"):
        self.appEngine = window
        self.appEngine.action_management.viewChanged.connect(self.onViewChanged)
        self.appEngine.action_management.brushOpacityChanged.connect(self.onOpacityChanged)
        self.onOpacityChanged(window.action_management.getBrushProperty("opacity"))

    def onViewChanged(self, view: View):
        self.view = view

    def onOpacityChanged(self, value: float):
        self.setValue(value*100)

    def onValueChanged(self, value):
        if self.view == None: return
        self.view.setPaintingOpacity(self.value()/100)

