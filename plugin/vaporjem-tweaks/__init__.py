from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
import os
import json
import sys
import importlib.util
from .src.classes.config import *
from .src.ui.settings import *
from .src.features.custom_styles import *
from .src.features.docker_toggles import *
from .src.features.docker_groups import *
from .src.features.popup_buttons import *
from .src.features.workspace_toggles import *

# For autocomplete
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .src.ext.PyKrita import *
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
        msg = QMessageBox(Krita.instance().activeWindow().qwindow())
        msg.setText("Reloaded Known Workspaces/Dockers. You will need to reload to use them with this extension")
        msg.exec_()

    def openSettings(self):
        SettingsDialog().show()

    def buildMenus(self):
        qwin = Krita.instance().activeWindow().qwindow()
        CustomStyles.applyStyles(qwin)
        root_menu = qwin.menuBar().addMenu("Touchify")
        

        reloadItemsAction = QAction("Reload Known Items...", root_menu)
        reloadItemsAction.triggered.connect(self.reloadKnownItems)
        root_menu.menuAction().menu().addAction(reloadItemsAction)

        openSettingsAction = QAction("Configure Touchify...", root_menu)
        openSettingsAction.triggered.connect(self.openSettings)
        root_menu.menuAction().menu().addAction(openSettingsAction)

        seperator = QAction("", root_menu)
        seperator.setSeparator(True)
        root_menu.addAction(seperator)

        self.basic_dockers.buildMenu(root_menu)  
        self.docker_groups.buildMenu(root_menu)     
        self.workspace_toggles.buildMenu(root_menu)
        self.popup_toggles.buildMenu(root_menu)        
            
    def createActions(self, window):
        ConfigManager.init_instance(os.path.dirname(__file__))

        subItemPath = "VaporJem_Actions"

        for i in range(1, 10):
            hotkeyName = "vjt_action" + str(i)
            hotkeyAction = window.createAction(hotkeyName, "Custom action: " + str(i), subItemPath)
            ConfigManager.instance().addHotkey(i, hotkeyAction)
   
        self.basic_dockers.createActions(window, subItemPath)  
        self.docker_groups.createActions(window, subItemPath)     
        self.workspace_toggles.createActions(window, subItemPath)
        self.popup_toggles.createActions(window, subItemPath)


Krita.instance().addExtension(VaporJem(Krita.instance()))