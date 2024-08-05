import uuid

from .TouchifyActionBar import TouchifyActionBar
from .TouchifyActionButton import TouchifyActionButton
from .TouchifyActionMenu import TouchifyActionMenu

from ....cfg.CfgTouchifyAction import CfgTouchifyAction

from ....resources import ResourceManager
from ....variables import *
from ....cfg.CfgTouchifyAction import CfgTouchifyAction
from krita import *

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from ....settings.TouchifyConfig import *


KNOWN_UNCHECKABLES = [
    "show_brush_editor"
]

EXPANDING_SPACERS = [
    "expanding_spacer1",
    "expanding_spacer2"
]

class TouchifyActionPanel(QWidget):
    def __init__(self, cfg: List[CfgTouchifyAction], parent: QWidget=None,):
        super(TouchifyActionPanel, self).__init__(parent)

        self.cfg = cfg

        self.hinted_size: QSize | None = None
        self.registered_actions: list[tuple[QAction, QMetaObject.Connection, bool]] = []

        self.ourLayout = QVBoxLayout()
        self.ourLayout.setSpacing(0)
        self.ourLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.ourLayout)

        self.bar = TouchifyActionBar(self)
        self.initQuickActions()
        self.ourLayout.addWidget(self.bar)

    def setSizeHint(self, hint: QSize):
        self.hinted_size = hint

    def sizeHint(self):
        if self.hinted_size:
            return self.hinted_size
        else:
            return self.minimumSize()
        
    def updateButton(self, btn: TouchifyActionButton, action: QAction, useIcon: bool):
        btn.setChecked(action.isChecked())
        if useIcon:
            btn.setIcon(action.icon())
    
    def registerAction(self, btn: TouchifyActionButton, action: QAction, useIcon: bool):
        connection = action.changed.connect(lambda: self.updateButton(btn, action, useIcon))
        self.registered_actions.append((action, connection, useIcon))
    
    def unregisterActions(self):
        for action in self.registered_actions:
            try:
                action[0].changed.disconnect(action[1])
            except TypeError:
                pass
                       
    def __brushButtonClicked(self, id: Resource):
        Krita.instance().activeWindow().activeView().setCurrentBrushPreset(id)
            
    def __createBrushButton(self, act: CfgTouchifyAction):
        id = act.brush_name
        brush_presets = ResourceManager.getBrushPresets()
        
        if id in brush_presets:
            preset = brush_presets[id]
            btn = self.bar.addButton(id, act.row, lambda: self.__brushButtonClicked(preset), preset.name(), False)
            if act.brush_override_icon:
                if act.use_icon:
                    btn.setIcon(ResourceManager.iconLoader())
                else:
                    btn.setText(act.text)
            else:
                btn.setIcon(ResourceManager.brushIcon(id))
                   
    def __createMenuButton(self, act: CfgTouchifyAction):
        id = str(uuid.uuid4())
        btn = self.bar.addButton(id, act.row, None, act.context_menu_name, False)
        
        if act.use_icon:
            btn.setIcon(ResourceManager.iconLoader(act.icon))
        else:
            btn.setText(act.text)
        
        contextMenu = TouchifyActionMenu(act, btn)
        btn.setMenu(contextMenu)
        btn.clicked.connect(btn.showMenu)
        
    def __createActionButton(self, act: CfgTouchifyAction):
        action = Krita.instance().action(act.action_id)
        if action:
            checkable = action.isCheckable()
            if act.action_id in KNOWN_UNCHECKABLES:
                checkable = False
                
                
            btn = self.bar.addButton(act.action_id, act.row, action.trigger, action.toolTip(), checkable)
            
            if act.use_icon:
                if act.action_use_default_icon:
                    btn.setIcon(action.icon())
                else:
                    btn.setIcon(ResourceManager.iconLoader(act.icon))
            else:
                btn.setText(act.text)

            if checkable:
                btn.setChecked(action.isChecked())
                self.registerAction(btn, action, act.action_use_default_icon)

    def initQuickActions(self):
        actions = self.cfg
        for entry in actions:
            act: CfgTouchifyAction = entry
            if act.action_type == "menu":
                self.__createMenuButton(act)
            elif act.action_type == "brush":
                self.__createBrushButton(act)
            else:
                self.__createActionButton(act)
