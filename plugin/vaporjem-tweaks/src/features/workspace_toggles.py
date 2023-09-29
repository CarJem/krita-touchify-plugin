from PyQt5 import QtWidgets, QtGui
import os
import json
import sys
import importlib.util
from ..classes.config import *
from ..classes.resources import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..ext.PyKrita import *
else:
    from krita import *


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

        actionName = 'WorkspaceToggles_{0}'.format(workspace.id)
        id = workspace.id
        text = '{0}'.format(workspace.display_name)


        action = window.createAction(actionName, "Workspace: " + text, actionPath)    
        icon = ResourceManager.iconLoader(id, 'workspaces', True)
        action.setIcon(icon)

        if not workspace.hotkeyNumber == 0:
            ConfigManager.instance().getHotkeyAction(workspace.hotkeyNumber).triggered.connect(lambda: self.toggleWorkspace(id))

        pending_actions.append(action)
        action.triggered.connect(lambda: self.toggleWorkspace(id))

    def createActions(self, window, actionPath):
        sectionName = "VaporJem_Workspaces"
        subItemPath = actionPath + "/" + sectionName

        cfg = ConfigManager.instance().getJSON()
        for workspace in cfg.workspaces:
            self.createAction(window, workspace, subItemPath)