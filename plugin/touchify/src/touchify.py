from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from .components.nu_tools.NtToolbox import NtToolbox
from .components.nu_tools.NtToolOptions import NtToolOptions
from . import stylesheet
from PyQt5.QtWidgets import QMessageBox
from .variables import *


from .ui.settings import *
from .features.touchify_tweaks import *
from .features.docker_toggles import *
from .features.docker_groups import *
from .features.popup_buttons import *
from .features.workspace_toggles import *
from .features.redesign_components import *
from .features.touchify_hotkeys import *



from krita import *

class Touchify(Extension):
    mainMenuBar: QMenuBar = None

    basic_dockers: DockerToggles = None
    docker_groups: DockerGroups = None
    workspace_toggles: WorkspaceToggles = None
    popup_toggles: PopupButtons = None
    redesign_components: RedesignComponents = None
    touchify_hotkeys: TouchifyHotkeys = None
    touchify_tweaks: TouchifyTweaks = None

    def __init__(self, parent):
        super().__init__(parent)
        self.basic_dockers = DockerToggles()
        self.docker_groups = DockerGroups()
        self.workspace_toggles = WorkspaceToggles()
        self.popup_toggles = PopupButtons()
        self.redesign_components = RedesignComponents()
        self.touchify_hotkeys = TouchifyHotkeys()
        self.touchify_tweaks = TouchifyTweaks()

    def setup(self):
        appNotifier  = Krita.instance().notifier()
        appNotifier.windowCreated.connect(self.windowCreated)
        appNotifier.windowCreated.connect(self.finishActions)
        self.redesign_components.setup()


    def createActions(self, window):
        self.mainMenuBar = window.qwindow().menuBar().addMenu("Touchify")

        subItemPath = TOUCHIFY_ID_ACTIONS_ROOT

        self.touchify_hotkeys.createActions(window, subItemPath)
        self.basic_dockers.createActions(window, subItemPath)  
        self.docker_groups.createActions(window, subItemPath)     
        self.workspace_toggles.createActions(window, subItemPath)
        self.popup_toggles.createActions(window, subItemPath)

        reloadItemsAction = QAction("Reload Known Items...", self.mainMenuBar)
        reloadItemsAction.triggered.connect(self.reloadKnownItems)
        self.mainMenuBar.addAction(reloadItemsAction)

        openSettingsAction = QAction("Configure Touchify...", self.mainMenuBar)
        openSettingsAction.triggered.connect(self.openSettings)
        self.mainMenuBar.addAction(openSettingsAction)

        self.redesign_components.createActions(window, self.mainMenuBar)

    def finishActions(self):
        seperator = QAction("", self.mainMenuBar)
        seperator.setSeparator(True)
        self.mainMenuBar.addAction(seperator)

        self.basic_dockers.buildMenu(self.mainMenuBar)  
        self.docker_groups.buildMenu(self.mainMenuBar)     
        self.workspace_toggles.buildMenu(self.mainMenuBar)
        self.popup_toggles.buildMenu(self.mainMenuBar)

    def windowCreated(self):
        window = Krita.instance().activeWindow().qwindow()
        self.touchify_tweaks.load(window)

    def reloadKnownItems(self):
        self.basic_dockers.reloadDockers()
        self.workspace_toggles.reloadWorkspaces()
        msg = QMessageBox(Krita.instance().activeWindow().qwindow())
        msg.setText("Reloaded Known Workspaces/Dockers. You will need to reload to use them with this extension")
        msg.exec_()

    def openSettings(self):
        SettingsDialog().show()

Krita.instance().addExtension(Touchify(Krita.instance()))