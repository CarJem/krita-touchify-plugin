import uuid
from krita import *

from .TouchifyActionButton import TouchifyActionButton
from .TouchifyActionMenu import TouchifyActionMenu

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from ....cfg.CfgTouchifyAction import CfgTouchifyAction
from ....cfg.CfgTouchifyActionGroup import CfgTouchifyActionGroup
from ....resources import ResourceManager
from .... import stylesheet
from ....variables import *
from ....settings.TouchifyConfig import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....action_manager import ActionManager


KNOWN_UNCHECKABLES = [
    "show_brush_editor"
]

EXPANDING_SPACERS = [
    "expanding_spacer1",
    "expanding_spacer2"
]

class TouchifyActionPanel(QWidget):
    def __init__(self, cfg: List[CfgTouchifyActionGroup], parent: QWidget=None, actions_manager: "ActionManager" = None, type: str = "default", icon_width: int = -1, icon_height: int = -1, item_width: int = -1, item_height: int = -1, opacity: float = 1.0):
        super(TouchifyActionPanel, self).__init__(parent)

        self.cfg = cfg
        self.type = type
        self.actions_manager = actions_manager
        
        self.icon_width: int = icon_width
        self.icon_height: int = icon_height
        
        self.item_width: int = item_width
        self.item_height: int = item_height
        
        self.opacity: float = opacity

        self._rows: dict[int, QWidget] = {}
        self._buttons: dict[any, TouchifyActionButton] = {}
        
        self.hinted_size: QSize | None = None
        self.registered_actions: list[tuple[QAction, QMetaObject.Connection, bool]] = []
        
        self.createPanel()

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
                       
    
    def __finalizeButton(self, btn: TouchifyActionButton):
        if self.icon_width > 0 and self.icon_height > 0:
            btn.setIconSize(QSize(self.icon_width, self.icon_height))
            
        if self.item_width > 0:
            btn.setFixedWidth(self.item_width)
            
        if self.item_height > 0:
            btn.setFixedHeight(self.item_height)
            
        if self.type == "popup":
            btn.setStyleSheet(stylesheet.touchify_action_btn_popup(self.opacity))
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        elif self.type == "toolbar" or self.type == "toolbar_flat":
            btn.setStyleSheet(stylesheet.touchify_action_btn_toolshelf(self.type == "toolbar_flat"))
            btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
    def __createButton(self, id: any, row: int, onClick: any, toolTip: str, checkable: bool):
        btn = TouchifyActionButton()
        if onClick:
            btn.clicked.connect(onClick) # collect and disconnect all when closing
        btn.setToolTip(toolTip)
        btn.setContentsMargins(0,0,0,0)
        btn.setCheckable(checkable)
        self._buttons[id] = btn

        if row not in self._rows:
            rowWid = QWidget()
            rowWid.setLayout(QHBoxLayout())
            rowWid.layout().setSpacing(1)
            rowWid.layout().setContentsMargins(0, 0, 0, 0)
            rowWid.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
            self._rows[row] = rowWid
            self.layout().addWidget(rowWid)

        self._rows[row].layout().addWidget(btn)
        return btn
   
    def __createButton_Brush(self, act: CfgTouchifyAction, row: int):
        
        def __brushButtonClicked(self, id: Resource):
            Krita.instance().activeWindow().activeView().setCurrentBrushPreset(id)
        
        id = act.brush_name
        brush_presets = ResourceManager.getBrushPresets()
        
        if id in brush_presets:
            preset = brush_presets[id]
            btn = self.__createButton(id, row, lambda: __brushButtonClicked(preset), preset.name(), False)
            if act.brush_override_icon:
                if act.action_use_icon:
                    btn.setIcon(ResourceManager.iconLoader())
                    if act.action_text_and_icon: btn.setText(act.text)
                else:
                    btn.setText(act.text)
            else:
                btn.setIcon(ResourceManager.brushIcon(id))
        self.__finalizeButton(btn)
                   
    def __createButton_Menu(self, act: CfgTouchifyAction, row: int):
        id = str(uuid.uuid4())
        btn = self.__createButton(id, row, None, act.text, False)
        
        if act.action_use_icon:
            btn.setIcon(ResourceManager.iconLoader(act.icon))
            if act.action_text_and_icon: btn.setText(act.text)
        else:
            btn.setText(act.text)
        
        contextMenu = TouchifyActionMenu(act, btn)
        btn.setMenu(contextMenu)
        btn.clicked.connect(btn.showMenu)
        self.__finalizeButton(btn)
        
    def __createButton_Action(self, act: CfgTouchifyAction, row: int):
        action = Krita.instance().action(act.action_id)
        if action:
            checkable = action.isCheckable()
            if act.action_id in KNOWN_UNCHECKABLES:
                checkable = False
                
                
            btn = self.__createButton(act.action_id, row, action.trigger, action.toolTip(), checkable)
            
            if act.action_use_icon:
                if act.action_use_default_icon:
                    btn.setIcon(action.icon())
                    if act.action_text_and_icon: btn.setText(act.text)
                else:
                    btn.setIcon(ResourceManager.iconLoader(act.icon))
                    if act.action_text_and_icon: btn.setText(act.text)
            else:
                btn.setText(act.text)

            if checkable:
                btn.setChecked(action.isChecked())
                self.registerAction(btn, action, act.action_use_default_icon)
            self.__finalizeButton(btn)

    def createPanel(self):
        self.ourLayout = QVBoxLayout()
        self.setLayout(self.ourLayout)
        self.layout().setSpacing(1)
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        actions = self.cfg
        row_index = 0
        
        
        for row in actions:
            row: CfgTouchifyActionGroup
            for entry in row.actions:
                act: CfgTouchifyAction = entry
                if act.variant == CfgTouchifyAction.Variants.Menu:
                    self.__createButton_Menu(act, row_index)
                elif act.variant == CfgTouchifyAction.Variants.Brush:
                    self.__createButton_Brush(act, row_index)
                elif act.variant == CfgTouchifyAction.Variants.Action:
                    self.__createButton_Action(act, row_index)
            row_index += 1
