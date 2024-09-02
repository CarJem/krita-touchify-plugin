from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from ....cfg.CfgTouchifyAction import *
from krita import *

class TouchifyActionMenu(QMenu):
    
    def __init__(self, cfg: CfgTouchifyAction, parent: QWidget | None = None):
        super().__init__(parent)
        self.krita_instance = Krita.instance()
        self.act = cfg
        
        for entry in self.act.context_menu_actions:
            action_cfg: CfgTouchifyAction = entry
            actual_action = self.krita_instance.action(action_cfg.action_id)
            if actual_action:
                self.addAction(actual_action)