from krita import *
from PyQt5.QtCore import *

from touchify.__env__ import *

from touchify.src.managers.shared.settings_krita import *
from touchify.src.components.krita.KisSliderSpinBox import KisSliderSpinBox

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.PluginWindow import TouchifyWindow


class BrushFlowSlider(KisSliderSpinBox):
    def __init__(self, parent=None):
        super(BrushFlowSlider, self).__init__(parent=parent, isInt=True)
        self.appEngine: "TouchifyWindow" = None
        self.setAffixes('Flow: ', '%')
        self.connectValueChanged(self.onValueChanged)
        self.view: View = None

    def setInstance(self, window: "TouchifyWindow"):
        self.appEngine = window
        self.notifier = window.api_window.notifier()
        self.notifier.viewChanged.connect(self.onViewChanged)
        self.onViewChanged(self.notifier.getCurrentView())
        self.notifier.brushFlowChanged.connect(self.onFlowChanged)
        self.onFlowChanged(self.notifier.getBrushFlow())

    def onViewChanged(self, view: View):
        self.view = view

    def onFlowChanged(self, value: float):
        self.setValue(value*100)

    def onValueChanged(self, value):
        if self.view == None: return
        self.view.setPaintingFlow(self.value()/100)