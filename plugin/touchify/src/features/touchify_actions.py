from functools import partial
from PyQt5 import QtWidgets, QtGui
import os
import json
import sys
import importlib.util
import uuid
from ..ext.extensions_krita import *

from ..variables import *

from ..cfg.CfgTouchifyAction import CfgTouchifyAction
from ..settings.TouchifyConfig import *
from ..resources import *

from krita import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..touchify import Touchify
    
class TouchifyActions(object):
    
    def __init__(self, instance: "Touchify"):
        self.appEngine = instance  

    def buildMenu(self, menu: QMenu):
        menu.addMenu(self.root_menu)
        
    def createAction(self, data: CfgTouchifyAction, window: Window, actionPath: str):
        action = self.appEngine.action_management.createAction(data, window, actionPath)
        self.root_menu.addAction(action)

    def createActions(self, window: Window, actionPath: str):
        sectionName = TOUCHIFY_ID_ACTIONS_DOCKER
        subItemPath = actionPath + "/" + sectionName
        cfg = TouchifyConfig.instance().getConfig()
        self.root_menu = QtWidgets.QMenu("Registered Actions")

        for action in cfg.actions_registry.actions_registry:
            self.createAction(action, window, subItemPath)

            
