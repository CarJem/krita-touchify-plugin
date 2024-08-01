from PyQt5 import QtWidgets, QtGui
import os
import json
import sys
import importlib.util

from ..cfg.CfgWorkspace import CfgWorkspace
from ..settings.TouchifyConfig import *
from ..resources import *

from krita import *

from ..variables import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..touchify import TouchifyInstance



class WorkspaceToggles(object):

    def __init__(self, instance: "TouchifyInstance"):
        self.appEngine = instance

    def windowCreated(self):
        self.qWin = self.appEngine.instanceWindow.qwindow()

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

    def reloadWorkspaces(self):
        cfg = TouchifyConfig.instance().getConfig()

        Workspaces = []
        main_menu = self.qWin.menuBar()

        for root_items in main_menu.actions():
            if root_items.objectName() == 'window':
                for sub_item in root_items.menu().actions():
                    if sub_item.text() == 'Wor&kspace':
                        for workspace in sub_item.menu().actions():
                            if workspace.isSeparator():
                                break
                            else:
                                action = CfgWorkspace()
                                action.display_name = workspace.text()
                                action.id = workspace.text()
                                Workspaces.append(action)
                break
        
        cfg.workspaces = Workspaces
        cfg.save()


    def buildMenu(self, menu: QMenu):
        menu.addMenu(self.root_menu)
   
    def createAction(self, window: Window, workspace: CfgWorkspace, actionPath):

        actionName = '{0}_{1}'.format(TOUCHIFY_ID_ACTION_PREFIX_WORKSPACE, workspace.id)
        id = workspace.id
        text = '{0} [Workspace]'.format(workspace.display_name)
        iconName = 'custom:' + workspace.id


        action = window.createAction(actionName, text, actionPath)    
        icon = ResourceManager.iconLoader(iconName)
        action.setIcon(icon)

        TouchifyConfig.instance().addHotkeyOption(actionName, text, self.toggleWorkspace, {'path': id})
        
        self.root_menu.addAction(action)
        action.triggered.connect(lambda: self.toggleWorkspace(id))

    def createActions(self, window, actionPath):
        self.root_menu = QtWidgets.QMenu("Workspace Triggers")

        sectionName = TOUCHIFY_ID_ACTIONS_WORKSPACE
        subItemPath = actionPath + "/" + sectionName

        cfg = TouchifyConfig.instance().getConfig()
        for workspace in cfg.workspaces:
            self.createAction(window, workspace, subItemPath)