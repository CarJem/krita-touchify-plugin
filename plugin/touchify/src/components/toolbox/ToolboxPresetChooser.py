
from krita import *
from ....configs import *
from PyQt5.QtCore import pyqtSignal

class ToolboxPresetChooser(PresetChooser):
    presetChanged = pyqtSignal()

    def __init__(self, parent=None):
        super(ToolboxPresetChooser, self).__init__(parent)
        self.presetSelected.connect(self.brushPresetChanged)
        self.presetClicked.connect(self.brushPresetChanged)

    def brushPresetChanged(self, preset):
        Krita.instance().activeWindow().activeView().activateResource(
            self.currentPreset()
            )
        self.presetChanged.emit()