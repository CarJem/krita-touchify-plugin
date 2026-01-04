from typing import TYPE_CHECKING
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from touchify.src.config.context_menu.ContextMenu import ContextMenu
from touchify.src.config.triggers.Trigger import *
from krita import *

if TYPE_CHECKING:
    from touchify.src.managers.ActionManager import ActionManager

class TriggerMenuWidget(QMenu):
    
    def __init__(self, cfg: Trigger | ContextMenu, parent: QWidget, action_mgr: "ActionManager"):
        super().__init__(parent)

        if isinstance(cfg, ContextMenu):
            action_list = cfg.context_menu_actions
        elif isinstance(cfg, Trigger):
            action_list = cfg.menu_data
        else:
            action_list = []

        for entry in action_list:    
            action_cfg: Trigger = entry
            action_mgr.Create_MenuItem(self, action_cfg)
        
            
            