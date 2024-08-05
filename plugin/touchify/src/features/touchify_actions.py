from functools import partial
from PyQt5 import QtWidgets, QtGui
import os
import json
import sys
import importlib.util

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
        
    def windowCreated(self):
        self.qWin = self.appEngine.instanceWindow.qwindow()        
        
    def toggleDocker(self, path):
        dockersList = Krita.instance().dockers()
        for docker in dockersList:
            if (docker.objectName() == path):
                docker.setVisible(not docker.isVisible())
                
    def toggleWorkspace(self, path):
        main_menu = self.qWin.menuBar()
        for root_items in main_menu.actions():
            if root_items.objectName() == 'window':
                for sub_item in root_items.menu().actions():
                    if sub_item.text() == 'Wor&kspace':
                        for workspace in sub_item.menu().actions():
                            if workspace.text() == path:
                                workspace.trigger()
                                break
                break

    def buildMenu(self, menu: QMenu):
        menu.addMenu(self.root_menu)
        
    def executeAction(self, data: CfgTouchifyAction):
        if data.action_type == CfgTouchifyAction.ActionType.Docker:
            self.toggleDocker(data.docker_id)

    def createAction(self, window: Window, data: CfgTouchifyAction, actionPath: str):
        actionIdentifier ='{0}_{1}'.format(TOUCHIFY_ID_ACTION_PREFIX_DOCKER, data.action_id)
        iconName = data.icon
        displayName = data.text

        action = window.createAction(actionIdentifier, displayName, actionPath)    
        icon = ResourceManager.iconLoader(iconName)
        action.setIcon(icon)

        TouchifyConfig.instance().addHotkeyOption(actionIdentifier, displayName, self.executeAction, {'data': data})
        
        action.triggered.connect(lambda: self.executeAction(data))
        self.root_menu.addAction(action)

    def createActions(self, window: Window, actionPath: str):
        sectionName = TOUCHIFY_ID_ACTIONS_DOCKER
        subItemPath = actionPath + "/" + sectionName
        cfg = TouchifyConfig.instance().getConfig()
        self.root_menu = QtWidgets.QMenu("Registered Actions")

        for action in cfg.actions_registry.actions_registry:
            self.createAction(window, action, subItemPath)