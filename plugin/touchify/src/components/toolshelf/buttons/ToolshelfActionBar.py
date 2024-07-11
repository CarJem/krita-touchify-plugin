


from multiprocessing import context
import uuid
from ....cfg.CfgToolshelf import CfgToolshelfAction, CfgToolshelfActionSubItem
from ....variables import *
from ....cfg.CfgToolshelf import CfgToolshelfAction
from krita import *

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import QMargins
from ....settings.TouchifyConfig import *
from .ToolshelfButtonBar import ToolshelfButton, ToolshelfButtonBar
from .... import stylesheet

KNOWN_UNCHECKABLES = [
    "show_brush_editor"
]

EXPANDING_SPACERS = [
    "expanding_spacer1",
    "expanding_spacer2"
]

class ToolshelfActionBar(QWidget):
    def __init__(self, cfg: List[CfgToolshelfAction], parent: QWidget=None,):
        super(ToolshelfActionBar, self).__init__(parent)

        self.cfg = cfg

        self.hinted_size: QSize | None = None
        self.registered_actions: list[tuple[QAction, QMetaObject.Connection, bool]] = []

        self.ourLayout = QVBoxLayout()
        self.ourLayout.setSpacing(0)
        self.ourLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.ourLayout)

        self.bar = ToolshelfButtonBar(self)
        self.initQuickActions()
        self.ourLayout.addWidget(self.bar)

    def setSizeHint(self, hint: QSize):
        self.hinted_size = hint

    def sizeHint(self):
        if self.hinted_size:
            return self.hinted_size
        else:
            return self.minimumSize()
        
    def updateButton(self, btn: ToolshelfButton, action: QAction, useIcon: bool):
        btn.setChecked(action.isChecked())
        if useIcon:
            btn.setIcon(action.icon())
    
    def registerAction(self, btn: ToolshelfButton, action: QAction, useIcon: bool):
        connection = action.changed.connect(lambda: self.updateButton(btn, action, useIcon))
        self.registered_actions.append((action, connection, useIcon))
    
    def unregisterActions(self):
        for action in self.registered_actions:
            try:
                action[0].changed.disconnect(action[1])
            except TypeError:
                pass

    def initQuickActions(self):
        actions = self.cfg
        for entry in actions:
            act: CfgToolshelfAction = entry
            if act.has_context_menu:
                id = str(uuid.uuid4())
                self.bar.addButton(id, act.icon, act.row, None, act.context_menu_name, False, True)
                btn = self.bar.button(id)

                contextMenu = QMenu(btn)
                
                for entry in act.context_menu_actions:
                    action_cfg: CfgToolshelfActionSubItem = entry
                    actual_action = Krita.instance().action(action_cfg.id)
                    if actual_action:
                        contextMenu.addAction(actual_action)


                btn.setMenu(contextMenu)
                btn.clicked.connect(btn.showMenu)

            else:
                action = Krita.instance().action(act.id)
                if action:
                    checkable = action.isCheckable()
                    if act.id in KNOWN_UNCHECKABLES:
                        checkable = False

                    self.bar.addCfgButton(
                        act,
                        action.trigger,
                        action.toolTip(),
                        checkable
                        )
                    
                    if act.useActionIcon:
                        btn = self.bar.button(act.id)
                        btn.setIcon(action.icon())

                    if checkable:
                        btn = self.bar.button(act.id)
                        btn.setChecked(action.isChecked())
                        self.registerAction(btn, action, act.useActionIcon)