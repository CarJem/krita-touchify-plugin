from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
import json
from functools import partial
import sys
import importlib.util

from ...cfg.CfgPopup import CfgPopup, CfgPopupActionItem
from ...settings.TouchifyConfig import *
from ..touchify.actions.TouchifyActionPanel import *
from ...resources import *
from .PopupDialog import *

from krita import *


class PopupDialog_Actions(PopupDialog):

    def __init__(self, parent: QMainWindow, args: CfgPopup):     
        super().__init__(parent, args)
        self.grid = self.generateActionsLayout()
        self.allowOpacity = True
        if self.isSizeGripEnabled():
            self.setSizeGripEnabled(False)
        self.initLayout()


    def generateSize(self):
        padding = self.metadata.actions_grid_padding
        grid_width = self.metadata.actions_grid_width
    
        item_width = self.metadata.actions_item_width + padding * 2
        item_height = self.metadata.actions_item_height + padding * 2

        item_count = len(self.metadata.actions_items)


        item_count_x = grid_width
        item_count_y = item_count / grid_width


        dialog_width = (item_count_x * item_width)
        dialog_height = (item_count_y * item_height)
        return [int(dialog_width), int(dialog_height)]

    def triggerPopup(self, mode:str, parent: QWidget | None):
        super().triggerPopup(mode, parent)    

    def generateActionsLayout(self):   
        layout = QVBoxLayout()
        
        converted_actions: list[CfgTouchifyAction] = []
            
        current_x = 0
        current_y = 0
        current_index = 0
        
        padding = self.metadata.actions_grid_padding
        maximum_x = self.metadata.actions_grid_width
        
        actionItem: CfgPopupActionItem
        for actionItem in self.metadata.actions_items:
            if not current_x < maximum_x:
                current_y += 1
                current_x = 0
            
            newAction = CfgTouchifyAction()
            newAction.action_id = actionItem.action
            newAction.text = actionItem.text
            newAction.icon = actionItem.icon
            newAction.text_and_icon = True
            newAction.row = current_y
            converted_actions.append(newAction)
            
            current_x += 1
            current_index += 1
        
        icon_width = self.metadata.actions_icon_width
        icon_height = self.metadata.actions_icon_height
        
        item_width = self.metadata.actions_item_width
        item_height = self.metadata.actions_item_height
        
        self.actionPanel = TouchifyActionPanel(converted_actions, None, "popup", icon_width, icon_height, item_width, item_height)
        layout.addWidget(self.actionPanel)
        
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(padding)
        
        return layout