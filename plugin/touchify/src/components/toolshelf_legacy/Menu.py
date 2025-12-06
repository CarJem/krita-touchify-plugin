from krita import *
from PyQt5.QtWidgets import *
from touchify.src.components.canvas.NtWidgetPad import NtWidgetPad

from krita import *


from touchify.src.managers.shared.settings import *
from touchify.__env__ import *
from touchify.src.managers.normal.dockers import *
from touchify.src.components.toolshelf_legacy.Helpers import Helpers

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .Header import Header
    from touchify.src.components.special.TouchifyPopup import TouchifyPopup

class Menu(QMenu):
    SIGNAL_RESIZE_STATE_CHANGED = pyqtSignal(bool)

    def __init__(self, parent: QWidget, cfg: ToolshelfData, registry_index: int):
        super(Menu, self).__init__(parent)
        self.cfg = cfg
        self.registry_index = registry_index
        self.parentNtWidget: NtWidgetPad = None
        self.parentPopup: "TouchifyPopup" = None
        self.setupWidgetPad = True
        self.setupPopup = True
        self.setupGlobal = True

        self.editModeAction: QAction = QAction("Edit Mode", self)
        self.editModeAction.setCheckable(True)
        self.editModeAction.setChecked(False)

        self.toggleResizeAct: QAction = QAction("Allow Resizing", self)
        self.toggleResizeAct.setCheckable(True)
        self.toggleResizeAct.setChecked(cfg.header_options.default_to_resize_mode)
        self.toggleResizeAct.changed.connect(self.toggleResize)

        
        if self.registry_index != -3:
            self.current_preset_id = TouchifySettings.instance().getActiveToolshelfId(self.registry_index)
            self.loadPresets()

    def setup(self):
        if self.setupWidgetPad:
            self.parentNtWidget = Helpers.findWidgetPad(self)
            if self.parentNtWidget != None:
                if self.parentNtWidget.option_allow_resizing:
                    self.parentNtWidget.setResizable(self.toggleResizeAct.isChecked())
                    self.addActions([self.toggleResizeAct])
                    self.addSeparator()
            self.setupWidgetPad = False
        if self.setupPopup:
            self.parentPopup = Helpers.findPopup(self)
            if self.parentPopup != None:
                if self.parentPopup.State_resizingAllowed:
                    self.parentPopup.Action_SetResizable(self.toggleResizeAct.isChecked())
                    self.addActions([self.toggleResizeAct])
                    self.addSeparator()
            self.setupPopup = False
        if self.setupGlobal:
            self.addAction(self.editModeAction)
            self.setupGlobal = False
        
    def toggleResize(self):
        state = self.toggleResizeAct.isChecked()
        if self.parentNtWidget != None:
            self.parentNtWidget.setResizable(state)
        elif self.parentPopup != None:
            self.parentPopup.Action_SetResizable(state)

        self.SIGNAL_RESIZE_STATE_CHANGED.emit(state)
        

    def loadPresets(self):
        self.clear()

        menus: dict[str, QMenu] = {}
        sub_menus: dict[str, dict[str, QMenu]] = {}
        
        registry = TouchifySettings.instance().getRegistry(ToolshelfData)
        if registry != None:
            for key, preset in registry.items():
                if not key.id in menus:
                    menus[key.id] = self.addMenu(key.name)
                    sub_menus[key.id] = {}

                preset: ToolshelfData
                action = QAction(preset.preset_name, self)
                action.setCheckable(True)
                if self.current_preset_id == key.actual_key:
                    action.setChecked(True)
                action.setData(key.actual_key)
                action.triggered.connect(self.changePreset)

                if preset.preset_group == "":
                    menus[key.id].addAction(action)
                else:
                    if not preset.preset_group in sub_menus[key.id]:
                        sub_menus[key.id][preset.preset_group] = menus[key.id].addMenu(preset.preset_group)
                    sub_menus[key.id][preset.preset_group].addAction(action)
        
        self.addSeparator()

    def changePreset(self):
        ac: QAction = self.sender()
        if isinstance(ac, QAction):
            id: str = ac.data()
            if isinstance(id, str):
                TouchifySettings.instance().setActiveToolshelf(self.registry_index, id)