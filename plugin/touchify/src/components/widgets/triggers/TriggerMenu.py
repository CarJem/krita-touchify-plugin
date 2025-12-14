from typing import TYPE_CHECKING
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from touchify.src.config.menu.TriggerMenu import TriggerMenu
from touchify.src.config.menu.TriggerMenuItem import TriggerMenuItem
from touchify.src.config.triggers.Trigger import *
from krita import *

if TYPE_CHECKING:
    from touchify.src.managers.ActionManager import ActionManager

class TriggerMenuWidget(QMenu):
    
    def __init__(self, cfg: TriggerMenuItem | TriggerMenu, parent: QWidget, action_mgr: "ActionManager"):
        super().__init__(parent)
        self.act = cfg
        
        for entry in self.act.context_menu_actions:
            action_cfg: TriggerMenuItem = entry
            action_mgr.Create_MenuItem(self, action_cfg)