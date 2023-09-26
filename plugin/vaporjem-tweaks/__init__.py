from krita import Krita, Extension
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
import os
import json
import sys
import importlib.util
from .src.classes.config import *
from .src.ui.settings import *
from .src.components.docker_toggles import *
from .src.components.docker_groups import *
from .src.components.popup_buttons import *
from .src.components.workspace_toggles import *
#from .src.components.hotkey_bar import *

# For autocomplete
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .PyKrita import *
else:
    from krita import *

class VaporJem(Extension):
    def __init__(self, parent):
        super().__init__(parent)
        self.basic_dockers = DockerToggles()
        self.docker_groups = DockerGroups()
        self.workspace_toggles = WorkspaceToggles()
        self.popup_toggles = PopupButtons()

    def setup(self):
        appNotifier  = Krita.instance().notifier()
        appNotifier.windowCreated.connect(self.buildMenus)

    def reloadKnownItems(self):
        self.basic_dockers.reloadDockers()
        self.workspace_toggles.reloadWorkspaces()

    def openSettings(self):
        SettingsDialog().show()

    def buildMenus(self):
        qwin = Krita.instance().activeWindow().qwindow()
        main_menu: QMenuBar = qwin.menuBar()
        tools_section: QMenu = None

        for action in main_menu.actions():
            if action.objectName() == "tools":
                tools_section = action.menu()

        if not tools_section:
            return
        
        root_menu = QMenu("VaporJem", main_menu)
        tools_section.addMenu(root_menu)

        reloadItemsAction = QAction("Reload Known Items...", root_menu)
        reloadItemsAction.triggered.connect(self.reloadKnownItems)
        root_menu.menuAction().menu().addAction(reloadItemsAction)

        seperator = QAction("", root_menu)
        seperator.setSeparator(True)
        root_menu.addAction(seperator)

        self.basic_dockers.buildMenu(root_menu)  
        self.docker_groups.buildMenu(root_menu)     
        self.workspace_toggles.buildMenu(root_menu)
        self.popup_toggles.buildMenu(root_menu)        
            
    def createActions(self, window):
        ConfigManager.init(os.path.dirname(__file__))

        subItemPath = "VaporJem"

        for i in range(1, 10):
            hotkeyName = "vjt_action" + str(i)
            hotkeyAction = window.createAction(hotkeyName, "Custom action: " + str(i), subItemPath + "/Hotkeys")
            hotkeyAction.setVisible(False)
            ConfigManager.addHotkey(i, hotkeyAction)
   
        self.basic_dockers.createActions(window, subItemPath)  
        self.docker_groups.createActions(window, subItemPath)     
        self.workspace_toggles.createActions(window, subItemPath)
        self.popup_toggles.createActions(window, subItemPath)


Krita.instance().addExtension(VaporJem(Krita.instance()))