from krita import Krita, Extension
from PyQt5 import QtWidgets, QtGui
import os
import json
import sys
import importlib.util
from .src.classes.config import *
from .src.components.docker_toggles import *
from .src.components.docker_groups import *
from .src.components.popup_buttons import *
from .src.components.workspace_toggles import *
#from .src.components.hotkey_bar import *



class VaporJem(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def reloadKnownItems(self):
        self.basic_dockers.reloadDockers()
        self.workspace_toggles.reloadWorkspaces()
            
    def createActions(self, window):
        ConfigManager.init(os.path.dirname(__file__))

        subItemPath = "tools/VaporJem"
        
        root = window.createAction("VaporJem", "VaporJem", subItemPath)
        root_menu = QtWidgets.QMenu("VaporJem", window.qwindow())
        root.setMenu(root_menu)


        cacheDockerNamesAction = window.createAction("VaporJem_ReloadKnownItems", "VaporJem: Reload Known Items", subItemPath)
        cacheDockerNamesAction.triggered.connect(lambda: self.reloadKnownItems())
        root_menu.addAction(cacheDockerNamesAction)

        seperator = window.createAction("", "", subItemPath)
        seperator.setSeparator(True)
        root_menu.addAction(seperator)

        self.basic_dockers = DockerToggles()
        self.basic_dockers.createActions(window, subItemPath)

        self.docker_groups = DockerGroups()
        self.docker_groups.createActions(window, subItemPath)

        self.workspace_toggles = WorkspaceToggles()
        self.workspace_toggles.createActions(window, subItemPath)

        self.popup_toggles = PopupButtons()
        self.popup_toggles.createActions(window, subItemPath)


Krita.instance().addExtension(VaporJem(Krita.instance()))