


from ....cfg.CfgToolshelf import CfgToolshelfAction
from ....variables import *
from ....cfg.CfgToolshelf import CfgToolshelfAction
from krita import *

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import QMargins
from ....config import *
from .ToolshelfButtonBar import ToolshelfButton, ToolshelfButtonBar
from .... import stylesheet

KNOWN_UNCHECKABLES = [
    "show_brush_editor"
]

class ToolshelfQuickActions(QWidget):
    def __init__(self, cfg: List[CfgToolshelfAction], parent: QWidget=None,):
        super(ToolshelfQuickActions, self).__init__(parent)

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
            action = Krita.instance().action(act.id)

            checkable = action.isCheckable()
            if act.id in KNOWN_UNCHECKABLES:
                checkable = False
                

            if action:
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