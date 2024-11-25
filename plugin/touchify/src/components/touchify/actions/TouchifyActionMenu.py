from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from touchify.src.enums.common_actions import CommonActions
from touchify.src.cfg.action.CfgTouchifyAction import *
from krita import *

class TouchifyActionMenu(QMenu):
    
    def __init__(self, cfg: CfgTouchifyAction, parent: QWidget | None = None):
        super().__init__(parent)
        self.krita_instance = Krita.instance()
        self.act = cfg
        
        for entry in self.act.context_menu_actions:
            action_cfg: CfgTouchifyAction = entry
            if action_cfg.variant == CfgTouchifyAction.Variants.Menu:
                actual_menu = TouchifyActionMenu(action_cfg, self)
                actual_menu.setTitle(action_cfg.text)
                self.addMenu(actual_menu)
            elif action_cfg.variant == CfgTouchifyAction.Variants.Action:
                if action_cfg.action_id in CommonActions.EXPANDING_SPACERS:
                    actual_action = QAction(self)
                    actual_action.setSeparator(True)
                else:
                    actual_action = self.krita_instance.action(action_cfg.action_id)

                if actual_action:
                    self.addAction(actual_action)