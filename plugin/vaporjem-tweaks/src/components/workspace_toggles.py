from krita import Krita, Extension
from PyQt5 import QtWidgets, QtGui
import os
import json
import sys
import importlib.util
from ..classes.config import *
from ..classes.resources import *

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

    def addWorkspace(self, window, menu, actionName, id, text, actionPath):
        action = window.createAction(actionName, text, actionPath)    
        icon = ResourceManager.customIcon('dockers', id)
        action.setIcon(icon)

        menu.addAction(action)
        action.triggered.connect(lambda: self.toggleWorkspace(id))

    def reloadWorkspaces(self):
        cfg = ConfigManager.getJSON()

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
                                action_text = workspace.text()
                                Workspaces.append(Config_Workspace(action_text, action_text))
                break
        
        cfg.workspaces = Workspaces
        ConfigManager.saveJSON(cfg)

    def createActions(self, window, actionPath):

        sectionName = "VaporJem_Workspaces"
        root = window.createAction(sectionName, "Workspaces", actionPath)
        root_menu = QtWidgets.QMenu(sectionName, window.qwindow())
        root.setMenu(root_menu)

        subItemPath = actionPath + "/" + sectionName

        refreshWorkspacesAction = window.createAction("Refresh Known Workspaces", "Refresh Known Workspaces", subItemPath)
        refreshWorkspacesAction.triggered.connect(lambda: self.reloadWorkspaces())
        root_menu.addAction(refreshWorkspacesAction)

        seperator = window.createAction("WorkspaceTogglesSeperator", "", subItemPath)
        seperator.setSeparator(True)
        root_menu.addAction(seperator)

        cfg = ConfigManager.getJSON()
        for workspace in cfg.workspaces:
            self.addWorkspace(window, root_menu, 'WorkspaceToggles_{0}'.format(workspace["id"]), workspace["id"], '{0}'.format(workspace["display_name"]), subItemPath)