from krita import *
from PyQt5.QtWidgets import *
from touchify.src.components.touchify.canvas.NtWidgetPad import NtWidgetPad

from krita import *


from touchify.src.settings import *
from touchify.src.variables import *
from touchify.src.docker_manager import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .Header import Header
    from touchify.src.components.touchify.popups.PopupDialog_Toolshelf import PopupDialog_Toolshelf

class Menu(QMenu):
    def __init__(self, parent: QWidget, cfg: ToolshelfData, registry_index: int):
        super(Menu, self).__init__(parent)
        self.cfg = cfg
        self.registry_index = registry_index
        self.parentNtWidget: NtWidgetPad = None
        self.parentPopup: "PopupDialog_Toolshelf" = None
        self.setupWidgetPad = True
        self.setupPopup = True
        self.setupGlobal = True

        self.editMode: QAction = QAction("Edit Mode", self)
        self.editMode.setCheckable(True)
        self.editMode.setChecked(False)

        self.toggleResizeAct: QAction = QAction("Allow Resizing", self)
        self.toggleResizeAct.changed.connect(self.toggleResize)
        self.toggleResizeAct.setCheckable(True)
        self.toggleResizeAct.setChecked(cfg.header_options.default_to_resize_mode)

        
        if self.registry_index != -1:
            self.current_preset_id = TouchifySettings.instance().getActiveToolshelfId(self.registry_index)
            self.loadPresets()

    def setup(self):
        if self.setupWidgetPad:
            self.parentNtWidget = self.findWidgetPad()
            if self.parentNtWidget != None:
                if self.parentNtWidget.allowResizing:
                    self.parentNtWidget.updateResizingState(self.toggleResizeAct.isChecked())
                    self.addActions([self.toggleResizeAct])
                    self.addSeparator()
            self.setupWidgetPad = False
        if self.setupPopup:
            self.parentPopup = self.findPopup()
            if self.parentPopup != None:
                if self.parentPopup.toolshelf_allow_resizing:
                    self.parentPopup.updateResizingState(self.toggleResizeAct.isChecked())
                    self.addActions([self.toggleResizeAct])
                    self.addSeparator()
            self.setupPopup = False
        if self.setupGlobal:
            self.addAction(self.editMode)
            self.setupGlobal = False
        


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
        
    def toggleResize(self):
        state = self.toggleResizeAct.isChecked()
        if self.parentNtWidget != None:
            self.parentNtWidget.updateResizingState(state)
        elif self.parentPopup != None:
            self.parentPopup.updateResizingState(state)
        

    def loadPresets(self):
        self.clear()

        menus: dict[str, dict[str, QMenu]] = {}
        
        registry = TouchifySettings.instance().getRegistry(ToolshelfData)
        if registry != None:
            for key, preset in registry.items():
                if not key.id in menus:
                    menus[key.id] = self.addMenu(key.name)

                preset: ToolshelfData
                action = QAction(preset.preset_name, self)
                action.setCheckable(True)
                if self.current_preset_id == key.actual_key:
                    action.setChecked(True)
                action.setData(key.actual_key)
                action.triggered.connect(self.changePreset)
                menus[key.id].addAction(action)
        
        self.addSeparator()

    def changePreset(self):
        ac: QAction = self.sender()
        if isinstance(ac, QAction):
            id: str = ac.data()
            if isinstance(id, str):
                TouchifySettings.instance().setActiveToolshelf(self.registry_index, id)