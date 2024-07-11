from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMessageBox

from .features.touchify_looks import TouchifyLooks
from .variables import *


from .ui.SettingsDialog import *
from .features.touchify_tweaks import *
from .features.docker_toggles import *
from .features.docker_groups import *
from .features.popup_buttons import *
from .features.workspace_toggles import *
from .features.touchify_canvas import *
from .features.touchify_hotkeys import *



from krita import *

class TouchifyInstance(object):
    def __init__(self):
        self.basic_dockers = DockerToggles(self)
        self.docker_groups = DockerGroups(self)
        self.workspace_toggles = WorkspaceToggles(self)
        self.popup_toggles = PopupButtons(self)
        self.touchify_looks = TouchifyLooks(self)
        self.touchify_canvas = TouchifyCanvas(self)
        self.touchify_hotkeys = TouchifyHotkeys(self)
        self.touchify_tweaks = TouchifyTweaks(self)

    def onKritaConfigUpdated(self):
        self.touchify_canvas.onKritaConfigUpdated()

    def onConfigUpdated(self):
        self.touchify_canvas.onConfigUpdated()
        self.popup_toggles.onConfigUpdated()
        self.docker_groups.onConfigUpdated()        

    def createActions(self, window: Window):
        self.mainMenuBar = window.qwindow().menuBar().addMenu(TOUCHIFY_ID_MENU_ROOT)

        subItemPath = TOUCHIFY_ID_MENU_ROOT

        self.touchify_hotkeys.createActions(window, subItemPath)
        self.basic_dockers.createActions(window, subItemPath)  
        self.docker_groups.createActions(window, subItemPath)     
        self.workspace_toggles.createActions(window, subItemPath)
        self.popup_toggles.createActions(window, subItemPath)

        openSettingsAction = QAction("Configure Touchify...", self.mainMenuBar)
        openSettingsAction.triggered.connect(self.openSettings)
        self.mainMenuBar.addAction(openSettingsAction)

        self.touchify_looks.createActions(window, self.mainMenuBar)
        self.touchify_canvas.createActions(window, self.mainMenuBar)

        seperator = QAction("Actions", self.mainMenuBar)
        seperator.setSeparator(True)
        self.mainMenuBar.addAction(seperator)

        reloadItemsAction = QAction("Refresh Known Items...", self.mainMenuBar)
        reloadItemsAction.triggered.connect(self.reloadKnownItems)
        self.mainMenuBar.addAction(reloadItemsAction)

    def onWindowCreated(self, window: Window):
        self.instanceWindow = window
        self.docker_management = DockerManager(self.instanceWindow)

        seperator = QAction("", self.mainMenuBar)
        seperator.setSeparator(True)
        self.mainMenuBar.addAction(seperator)
        
        self.touchify_hotkeys.windowCreated()
        self.touchify_tweaks.windowCreated()
        self.touchify_looks.windowCreated()
        self.touchify_canvas.windowCreated()
        self.workspace_toggles.windowCreated()

        self.touchify_hotkeys.buildMenu(self.mainMenuBar)
        self.basic_dockers.buildMenu(self.mainMenuBar)  
        self.docker_groups.buildMenu(self.mainMenuBar)     
        self.popup_toggles.buildMenu(self.mainMenuBar)
        self.workspace_toggles.buildMenu(self.mainMenuBar)

    def reloadKnownItems(self):
        self.basic_dockers.reloadDockers()
        self.workspace_toggles.reloadWorkspaces()
        msg = QMessageBox(self.instanceWindow.qwindow())
        msg.setText("Reloaded Known Workspaces/Dockers. You will need to reload to use them with this extension")
        msg.exec_()

    def openSettings(self):
        dlg = SettingsDialog(self.instanceWindow)
        dlg.show()