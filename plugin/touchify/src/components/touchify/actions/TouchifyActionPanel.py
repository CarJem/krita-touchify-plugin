import uuid
from krita import *

from .TouchifyActionPushButton import *
from .TouchifyActionToolButton import *
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
        self._buttons: dict[any, TouchifyActionPushButton | TouchifyActionToolButton] = {}
        
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
        
    def updateButton(self, btn: TouchifyActionPushButton | TouchifyActionToolButton, action: QAction, useIcon: bool):
        btn.setChecked(action.isChecked())
        if useIcon:
            btn.setIcon(action.icon())
    
    def registerAction(self, btn: TouchifyActionPushButton | TouchifyActionToolButton, action: QAction, useIcon: bool):
        connection = action.changed.connect(lambda: self.updateButton(btn, action, useIcon))
        self.registered_actions.append((action, connection, useIcon))
    
    def unregisterActions(self):
        for action in self.registered_actions:
            try:
                action[0].changed.disconnect(action[1])
            except TypeError:
                pass
                       
    def appendButton(self, data: CfgTouchifyAction, btn: TouchifyActionPushButton | TouchifyActionToolButton, row: int):
        def action_id():
            result = None
            while result in self._buttons or result == None:
                result = str(uuid.uuid4())
            return result
        
        id = action_id()
        self._buttons[id] = btn
        
        if data.variant == CfgTouchifyAction.Variants.Action:
            action = Krita.instance().action(data.action_id)
            if action:
                if action.isCheckable():
                    self.registerAction(btn, action, data.action_use_icon)

        if row not in self._rows:
            rowWid = QWidget()
            rowWid.setLayout(QHBoxLayout())
            rowWid.layout().setSpacing(1)
            rowWid.layout().setContentsMargins(0, 0, 0, 0)
            rowWid.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
            self._rows[row] = rowWid
            self.layout().addWidget(rowWid)

        self._rows[row].layout().addWidget(btn)
        
    def stylizeButton(self, btn: TouchifyActionPushButton | TouchifyActionToolButton):   
        if self.icon_width > 0 and self.icon_height > 0:
            btn.setIconSize(QSize(self.icon_width, self.icon_height))
            
        if self.item_width > 0:
            btn.setFixedWidth(self.item_width)
            
        if self.item_height > 0:
            btn.setFixedHeight(self.item_height)
            
        if self.type == "popup":
            btn.setStyleSheet(stylesheet.touchify_action_btn_popup(self.opacity))
            if isinstance(btn, TouchifyActionToolButton): btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        elif self.type == "toolbar" or self.type == "toolbar_flat":
            btn.setStyleSheet(stylesheet.touchify_action_btn_toolshelf())
            if isinstance(btn, TouchifyActionPushButton) and self.type == "toolbar_flat": btn.setFlat(True)
            btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

    def createPanel(self):
        self.ourLayout = QVBoxLayout()
        self.setLayout(self.ourLayout)
        self.layout().setSpacing(1)
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        actions = self.cfg
        row_index = 0
        isTool = False
        
        if self.type == "popup":
            isTool = True
        
        
        for row in actions:
            row: CfgTouchifyActionGroup
            for entry in row.actions:
                act: CfgTouchifyAction = entry
                btn = self.actions_manager.createButton(act, isTool)
                if btn:
                    self.stylizeButton(btn)
                    self.appendButton(act, btn, row_index)

            row_index += 1
