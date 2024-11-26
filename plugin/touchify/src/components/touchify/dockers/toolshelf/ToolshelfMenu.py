from krita import *
from PyQt5.QtWidgets import *
from touchify.src.components.touchify.canvas.NtWidgetPad import NtWidgetPad

from krita import *


from touchify.src.settings import *
from touchify.src.variables import *
from touchify.src.docker_manager import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfHeader import ToolshelfHeader
    from touchify.src.components.touchify.popups.PopupDialog_Toolshelf import PopupDialog_Toolshelf

class ToolshelfMenu(QMenu):
    def __init__(self, parent: QWidget, cfg: CfgToolshelf, registry_index: int):
        super(ToolshelfMenu, self).__init__(parent)
        self.cfg = cfg
        self.registry_index = registry_index
        self.parentNtWidget: NtWidgetPad = None
        self.parentPopup: "PopupDialog_Toolshelf" = None
        self.setupWidgetPad = True
        self.setupPopup = True
        if self.registry_index != -1:
            self.current_preset_index = TouchifyConfig.instance().getActiveToolshelfIndex(self.registry_index)
            self.loadPresets()

    def setup(self):
        if self.setupWidgetPad == True:
            self.parentNtWidget = self.findWidgetPad()
            if self.parentNtWidget != None:
                if self.parentNtWidget.allowResizing:
                    self.addActions([self.parentNtWidget.action_toggleResize])
            self.setupWidgetPad = False
        if self.setupPopup:
            self.parentPopup = self.findPopup()
            if self.parentPopup != None:
                self.addActions([self.parentPopup.action_toggleResize])
            self.setupPopup = False


    def findPopup(self):
        from touchify.src.components.touchify.popups.PopupDialog_Toolshelf import PopupDialog_Toolshelf
        try:
            widget = self.parent()
            while (widget):
                foo = widget
                if isinstance(foo, PopupDialog_Toolshelf):
                    return foo
                widget = widget.parent()
            return None
        except:
            return None

    def findWidgetPad(self):
        try:
            widget = self.parent()
            while (widget):
                foo = widget
                if isinstance(foo, NtWidgetPad):
                    return foo
                widget = widget.parent()
            return None
        except:
            return None

    def loadPresets(self):
        self.clear()
        
        registry = TouchifyConfig.instance().getToolshelfRegistry(self.registry_index)
        if registry != None:
            index = 0
            for preset in registry.presets:
                preset: CfgToolshelf
                action = QAction(preset.preset_name, self)
                action.setCheckable(True)
                if self.current_preset_index == index:
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
                TouchifyConfig.instance().setActiveToolshelf(self.registry_index, index)