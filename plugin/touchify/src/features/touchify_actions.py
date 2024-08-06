from functools import partial
from PyQt5 import QtWidgets, QtGui
import os
import json
import sys
import importlib.util
import uuid

from ..variables import *

from ..cfg.CfgTouchifyAction import CfgTouchifyAction
from ..settings.TouchifyConfig import *
from ..resources import *

from krita import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..touchify import TouchifyInstance
    
class TouchifyActions(object):
    
    def __init__(self, instance: "TouchifyInstance"):
        self.appEngine = instance  

    def buildMenu(self, menu: QMenu):
        menu.addMenu(self.root_menu)
        
    def executeAction(self, data: CfgTouchifyAction, action: QAction, overMouse: bool = False):
        self.appEngine.action_management.executeAction(action, data, overMouse)

    def createAction(self, window: Window, data: CfgTouchifyAction, actionPath: str):
        actionIdentifier ='TouchifyAction_{0}'.format(data.id)
        iconName = data.icon
        displayName = data.text

        action = window.createAction(actionIdentifier, displayName, actionPath)    
        icon = ResourceManager.iconLoader(iconName)
        action.setIcon(icon)

        TouchifyConfig.instance().addHotkeyOption(actionIdentifier, displayName, self.executeAction, {'data': data, 'action': action, 'overMouse': True})
        
        action.triggered.connect(lambda: self.executeAction(data, action, False))
        self.root_menu.addAction(action)

    def createActions(self, window: Window, actionPath: str):
        sectionName = TOUCHIFY_ID_ACTIONS_DOCKER
        subItemPath = actionPath + "/" + sectionName
        cfg = TouchifyConfig.instance().getConfig()
        self.root_menu = QtWidgets.QMenu("Registered Actions")

        for action in cfg.actions_registry.actions_registry:
            self.createAction(window, action, subItemPath)
            
