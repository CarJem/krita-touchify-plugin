from krita import *
from PyQt5.QtCore import *
from touchify.__env__ import *

from touchify.src.managers.shared.settings_krita import *
from touchify.src.components.krita.KisSliderSpinBox import KisSliderSpinBox

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.PluginWindow import TouchifyWindow

class BrushOpacitySlider(KisSliderSpinBox):

    def __init__(self, parent=None):
        super(BrushOpacitySlider, self).__init__(parent=parent, isInt=True)
        self.view: View = None
        self.appEngine: "TouchifyWindow" = None
        self.setAffixes('Opacity: ', '%')
        self.connectValueChanged(self.onValueChanged)
    
    def setInstance(self, window: "TouchifyWindow"):
        self.appEngine = window
        self.notifier = window.api_window.notifier()
        self.notifier.viewChanged.connect(self.onViewChanged)
        self.onViewChanged(self.notifier.getCurrentView())
        self.notifier.brushOpacityChanged.connect(self.onOpacityChanged)
        self.onOpacityChanged(self.notifier.getBrushOpacity())

    def onViewChanged(self, view: View):
        self.view = view

    def onOpacityChanged(self, value: float):
        self.setValue(value*100)

    def onValueChanged(self, value):
        if self.view == None: return
        self.view.setPaintingOpacity(self.value()/100)

