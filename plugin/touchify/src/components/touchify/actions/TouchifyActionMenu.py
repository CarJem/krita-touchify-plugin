from typing import TYPE_CHECKING
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from touchify.src.cfg.action.CfgTouchifyAction import *
from krita import *

if TYPE_CHECKING:
    from touchify.src.action_manager import ActionManager

class TouchifyActionMenu(QMenu):
    
    def __init__(self, cfg: CfgTouchifyAction, parent: QWidget, action_mgr: "ActionManager"):
        super().__init__(parent)
        self.krita_instance = Krita.instance()
        self.act = cfg
        
        for entry in self.act.context_menu_actions:
            action_cfg: CfgTouchifyAction = entry
            action_mgr.createMenuItem(self, action_cfg)