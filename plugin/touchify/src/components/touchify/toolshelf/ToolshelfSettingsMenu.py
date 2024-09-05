from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QSizePolicy, QStackedWidget
from krita import *
from PyQt5.QtWidgets import *
from ..canvas.NtWidgetPad import NtWidgetPad

from krita import *

from ....settings.TouchifyConfig import *
from ....variables import *
from ....docker_manager import *
from ....stylesheet import Stylesheet
from ....ext.extensions_krita import KritaExtensions

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfPanelHeader import ToolshelfPanelHeader

class ToolshelfSettingsMenu(QMenu):
    def __init__(self, parent: QWidget, cfg: CfgToolshelf, panelIndex: int):
        super(ToolshelfSettingsMenu, self).__init__(parent)
        self.cfg = cfg
        self.panelIndex = panelIndex
        self.selectedPresetIndex = TouchifyConfig.instance().getActiveToolshelfIndex(self.panelIndex)
        self.parentNtWidget: NtWidgetPad = None
        self.setupWidgetPad = True
        self.loadPresets()

    def setup(self):
        if self.setupWidgetPad == True:
            self.parentNtWidget = self.findWidgetPad()
            if self.parentNtWidget != None:
                if self.parentNtWidget.allowResizing:
                    self.addActions([self.parentNtWidget.resizingToggleAction])
            self.setupWidgetPad = False

    def findWidgetPad(self):
        widget = self.parent()
        while (widget):
            foo = widget
            if isinstance(foo, NtWidgetPad):
                return foo
            widget = widget.parent()
        return None

    def loadPresets(self):
        self.clear()
        
        registry = TouchifyConfig.instance().getToolshelfRegistry(self.panelIndex)
        if registry != None:
            index = 0
            for preset in registry.presets:
                preset: CfgToolshelf
                action = QAction(preset.presetName, self)
                action.setCheckable(True)
                if self.selectedPresetIndex == index:
                    action.setChecked(True)
                action.setData(index)
                action.triggered.connect(self.changePreset)
                index += 1
                self.addAction(action)
        
        self.addSeparator()

    def changePreset(self):
        ac: QAction = self.sender()
        if isinstance(ac, QAction):
            index: int = ac.data()
            if isinstance(index, int):
                TouchifyConfig.instance().setActiveToolshelf(self.panelIndex, index)