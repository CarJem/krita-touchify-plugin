from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
import json
from functools import partial
import sys
import importlib.util

from ...cfg.CfgPopup import CfgPopup
from ...settings.TouchifyConfig import *
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

    def runAction(self, actionName):
        try:
            action = Krita.instance().action(actionName)
            if action:
                action.trigger()
        except:
            pass

    def getActionIcon(self, iconName):
        return ResourceManager.iconLoader(iconName)
            
    def createActionButton(self, layout, text, icon, action, x, y):

        opacityLevel = self.metadata.opacity

        btn = QToolButton()
        btn.setStyleSheet(stylesheet.touchify_popup_action_btn(opacityLevel))
        btn.setText(text)
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        if icon:
            btn.setIcon(self.getActionIcon(icon))
            btn.setIconSize(QSize(self.metadata.actions_icon_width, self.metadata.actions_icon_height))

        btn.setWindowOpacity(opacityLevel)
        btn.setFixedSize(self.metadata.actions_item_width, self.metadata.actions_item_height)
        btn.clicked.connect(lambda: self.runAction(action))
        layout.addWidget(btn, x, y)

    def triggerPopup(self, mode:str, parent: QWidget | None):
        super().triggerPopup(mode, parent)    

    def generateActionsLayout(self):
        layout = QGridLayout()

        current_x = 0
        current_y = 0
        current_index = 0

        padding = self.metadata.actions_grid_padding
        maximum_x = self.metadata.actions_grid_width
        item_count = len(self.metadata.actions_items)

        while current_index < item_count:
            if not current_x < maximum_x:
                current_y += 1
                current_x = 0
            
            btn = self.metadata.actions_items[current_index]
            self.createActionButton(layout, btn.text, btn.icon, btn.action, current_y, current_x)
            current_x += 1
            current_index += 1

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(padding)
        layout.setVerticalSpacing(padding)
        return layout