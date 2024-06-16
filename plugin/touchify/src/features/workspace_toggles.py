from PyQt5 import QtWidgets, QtGui
import os
import json
import sys
import importlib.util

from ..cfg.CfgWorkspace import Workspace
from ..config import *
from ..resources import *

from krita import *

from ..variables import *


pending_actions = []

class WorkspaceToggles:

    def toggleWorkspace(self, path):
        main_menu = Krita.instance().activeWindow().qwindow().menuBar()
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
        cfg = ConfigManager.instance().getJSON()

        Workspaces = []
        main_menu = Krita.instance().activeWindow().qwindow().menuBar()

        for root_items in main_menu.actions():
            if root_items.objectName() == 'window':
                for sub_item in root_items.menu().actions():
                    if sub_item.text() == 'Wor&kspace':
                        for workspace in sub_item.menu().actions():
                            if workspace.isSeparator():
                                break
                            else:
                                action = Workspace()
                                action.display_name = workspace.text()
                                action.id = workspace.text()
                                Workspaces.append(action)
                break
        
        cfg.workspaces = Workspaces
        cfg.save()


    def buildMenu(self, menu: QMenu):
        root_menu = QtWidgets.QMenu("Workspaces", menu)
        menu.addMenu(root_menu)

        for action in pending_actions:
            root_menu.addAction(action)
   
    def createAction(self, window, workspace: Workspace, actionPath):

        actionName = '{0}_{1}'.format(TOUCHIFY_AID_ACTIONS_WORKSPACE, workspace.id)
        id = workspace.id
        text = '{0}'.format(workspace.display_name)
        iconName = 'custom:' + workspace.id


        action = window.createAction(actionName, "Workspace: " + text, actionPath)    
        icon = ResourceManager.iconLoader(iconName)
        action.setIcon(icon)

        if not workspace.hotkeyNumber == 0:
            ConfigManager.instance().getHotkeyAction(workspace.hotkeyNumber).triggered.connect(lambda: self.toggleWorkspace(id))

        pending_actions.append(action)
        action.triggered.connect(lambda: self.toggleWorkspace(id))

    def createActions(self, window, actionPath):
        sectionName = TOUCHIFY_ID_ACTIONS_WORKSPACE
        subItemPath = actionPath + "/" + sectionName

        cfg = ConfigManager.instance().getJSON()
        for workspace in cfg.workspaces:
            self.createAction(window, workspace, subItemPath)