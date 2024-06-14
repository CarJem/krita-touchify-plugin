from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
import json
from functools import partial
import sys
import importlib.util

from ...cfg.Popup import Popup
from ...config import *
from ...resources import *
from .PopupDialog import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...ext.PyKrita import *
else:
    from krita import *


class PopupDialog_Actions(PopupDialog):

    def __init__(self, parent: QMainWindow, args: Popup):     
        super().__init__(parent, args)
        self.grid = self.generateActionsLayout()
        self.allowOpacity = True
        self.initLayout()


    def generateSize(self):
        padding = self.metadata.grid_padding
        grid_width = self.metadata.grid_width
    
        item_width = self.metadata.item_width + padding * 2
        item_height = self.metadata.item_height + padding * 2

        item_count = len(self.metadata.items)


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
        btn_stylesheet = f"""
            QToolButton {{
                border-radius: 0px; 
                background-color: rgba(0,0,0,{opacityLevel}); 
                padding: 5px 5px;
                border: 0px solid transparent; 
                font-size: 12px
            }}
            
            QToolButton:hover {{
                background-color: rgba(155,155,155,{opacityLevel}); 
            }}
                          
            QToolButton:pressed {{
                background-color: rgba(128,128,128,{opacityLevel}); 
            }}
        """

        btn = QToolButton()
        btn.setStyleSheet(btn_stylesheet)
        btn.setText(text)
        btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        if icon:
            btn.setIcon(self.getActionIcon(icon))
            btn.setIconSize(QSize(self.metadata.icon_width, self.metadata.icon_height))

        btn.setWindowOpacity(opacityLevel)
        btn.setFixedSize(self.metadata.item_width, self.metadata.item_height)
        btn.clicked.connect(lambda: self.runAction(action))
        layout.addWidget(btn, x, y)
    

    def generateActionsLayout(self):
        layout = QGridLayout()

        current_x = 0
        current_y = 0
        current_index = 0

        padding = self.metadata.grid_padding
        maximum_x = self.metadata.grid_width
        item_count = len(self.metadata.items)

        while current_index < item_count:
            if not current_x < maximum_x:
                current_y += 1
                current_x = 0
            
            btn = self.metadata.items[current_index]
            self.createActionButton(layout, btn.text, btn.icon, btn.action, current_y, current_x)
            current_x += 1
            current_index += 1

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(padding)
        layout.setVerticalSpacing(padding)
        return layout