from krita import *
from PyQt5.QtCore import *


from touchify.src.managers.shared.settings_krita import *
from touchify.src.components.krita.KisSliderSpinBox import KisSliderSpinBox
from touchify.__env__ import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.PluginWindow import TouchifyWindow

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
        self.appEngine.mgr_actions.viewChanged.connect(self.onViewChanged)
        self.onViewChanged(self.appEngine.mgr_actions.getCurrentView())
        self.appEngine.mgr_actions.brushSizeChanged.connect(self.onSizeChanged)
        self.onSizeChanged(self.appEngine.mgr_actions.getBrushSize())

    def onViewChanged(self, view: View):
        self.view = view

    def onSizeChanged(self, value: float):
        self.setValue(value)

    def onValueChanged(self, value):
        if self.view == None: return
        self.view.setBrushSize(self.value())