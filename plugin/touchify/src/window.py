from typing import Callable
from PyQt5 import *
from PyQt5.QtWidgets import *
from krita import *

from touchify.src.variables import *
from touchify.src.docker_manager import DockerManager
from touchify.src.action_manager import ActionManager

from touchify.src.components.touchify.util.settings_dialog import SettingsDialog

from touchify.src.features.touchify_canvas import TouchifyCanvas
from touchify.src.features.touchify_hotkeys import TouchifyHotkeys
from touchify.src.features.touchify_looks import TouchifyLooks
from touchify.src.features.touchify_actions import TouchifyActions

from touchify.src.ext.PyQtExtensions import PyQtExtensions

from touchify.src.components.touchify.dockers.toolshelf.ToolshelfDocker import ToolshelfDocker
from touchify.src.components.touchify.dockers.toolbox.ToolboxDocker import ToolboxDocker

WINDOW_ID: int = 0

class TouchifyWindow(QObject):
    
    def __init__(self, parent: QObject):
        super().__init__(parent)
        global WINDOW_ID
        self.windowUUID = WINDOW_ID
        WINDOW_ID += 1


        self.update_style_calls: list[Callable] = []

        self.touchify_actions = TouchifyActions(self)
        self.touchify_looks = TouchifyLooks(self)
        self.touchify_canvas = TouchifyCanvas(self)
        self.touchify_hotkeys = TouchifyHotkeys(self)
        
        self.action_management = ActionManager(self)
        
        self.settings_dlg: SettingsDialog | None = None

    def openSettings(self):
        if self.settings_dlg != None:
            if PyQtExtensions.isDeleted(self.settings_dlg) == False:
                return
          
        self.settings_dlg = SettingsDialog(self.windowSource)
        self.settings_dlg.show()

    def unload(self):
        pass

    #region Signal Callbacks

    def onWindowCreated(self, window: Window):
        self.setParent(window.qwindow())
        self.windowSource = window
        self.docker_management = DockerManager(self)
        self.setupAddons(window)
        self.setupWindow()
        self.setupSoftActions()
        
    def onKritaConfigUpdated(self):
        toolshelf_docker = self.getToolshelfDocker()
        if toolshelf_docker: toolshelf_docker.onKritaConfigUpdate()
        
        self.touchify_canvas.onKritaConfigUpdated()

        for call in self.update_style_calls:
            call()

    def onTimerTick(self):
        self.action_management.onTimerTick()
        self.docker_management.onTimerTick()

    def onTouchifyConfigUpdated(self):
        toolshelf_docker = self.getToolshelfDocker()
        if toolshelf_docker: toolshelf_docker.onConfigUpdated()
        
        toolbox_docker = self.getToolboxDocker()
        if toolbox_docker: toolbox_docker.onConfigUpdated()
        
        self.touchify_canvas.onConfigUpdated()    

        self.action_management.onConfigUpdated()

        for call in self.update_style_calls:
            call()

    #endregion

    #region Event Handlers

    def event_findContextMenus(self):
        actions = self.windowSource.qwindow().findChildren(QAction)
        for act in actions:
            if act.text().find("Selection") != -1:
                print("Found IT!!!")

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if (event.type() == QEvent.Type.ContextMenu):
            print("Context Test")
            QTimer.singleShot(1000, self.event_findContextMenus)

        return super().eventFilter(source, event)

    #endregion

    #region Setup Functions

    def setupWindow(self):
        window = self.windowSource.qwindow()
        window.installEventFilter(self)

    def setupActions(self, window: Window):
        self.mainMenuBar = window.qwindow().menuBar().addMenu(TOUCHIFY_ID_MENU_ROOT)

        subItemPath = TOUCHIFY_ID_MENU_ROOT

        self.touchify_hotkeys.createActions(window, subItemPath)
        self.touchify_actions.createActions(window, subItemPath)  


        self.mainMenuBar.addSection("Touchify")
        
        openSettingsAction = window.createAction(TOUCHIFY_ID_ACTION_CONFIGURE, "Configure Touchify...", TOUCHIFY_ID_MENU_ROOT)
        openSettingsAction.triggered.connect(self.openSettings)
        self.mainMenuBar.addAction(openSettingsAction)
        
        self.touchify_looks.createActions(window, self.mainMenuBar)
        self.touchify_canvas.createActions(window, self.mainMenuBar)

    def setupSoftActions(self):
        seperator = QAction("", self.mainMenuBar)
        seperator.setText(f"Instance: #{self.windowUUID}")
        seperator.setEnabled(False)
        seperator.setSeparator(True)
        self.mainMenuBar.addAction(seperator)


        self.action_management.onWindowCreated()
        
        self.touchify_hotkeys.windowCreated()
        self.touchify_looks.windowCreated()
        self.touchify_canvas.windowCreated()

        self.touchify_hotkeys.buildMenu(self.mainMenuBar)
        self.touchify_actions.buildMenu(self.mainMenuBar)
            
    def setupAddons(self, window: Window):   

        def setupDockers():
            for docker in self.windowSource.dockers():
                if docker.objectName() == TOUCHIFY_ID_DOCKER_TOOLSHELFDOCKER:
                    toolshelfDocker: ToolshelfDocker = docker
                    toolshelfDocker.setup(self)
                elif docker.objectName() == TOUCHIFY_ID_DOCKER_TOOLBOX:
                    toolboxDocker: ToolboxDocker = docker
                    toolboxDocker.setup(self)
                elif docker.objectName().startswith("Touchify/"):
                    addonSetupFn = getattr(docker, "addonSetup", None)
                    addonUpdateStyleFn = getattr(docker, "addonUpdateStyle", None)
                    if callable(addonSetupFn):
                        addonSetupFn(self)
                    if callable(addonUpdateStyleFn):
                        self.update_style_calls.append(addonUpdateStyleFn)

        def setupDockerMenu():
            dockerMenu = None
            for m in window.qwindow().actions():
                if m.objectName() == "settings_dockers_menu":
                    dockerMenu = m

            if dockerMenu == None: return

            addonPrefix = 'Touchify Addon:'
            normalPrefix = 'Touchify'

            addon_dockers: list[QAction] = []
            normal_dockers: list[QAction] = []

            for a in dockerMenu.menu().actions():
                if a.text().startswith(normalPrefix) and not a.text().startswith(addonPrefix):
                    normal_dockers.append(a)
                elif a.text().startswith(addonPrefix):
                    a.setText(a.text().strip(addonPrefix))
                    addon_dockers.append(a)

            normalSection = dockerMenu.menu().addSection("Touchify")
            for docker in normal_dockers:
                dockerMenu.menu().addAction(docker)

            addonSection = dockerMenu.menu().addSection("Touchify Addons")
            for docker in addon_dockers:
                dockerMenu.menu().addAction(docker)

        def setupDockerTitles():
            docker_title_prefix = "Touchify Addon: "

            for docker in Krita.instance().dockers():
                if docker.windowTitle().startswith(docker_title_prefix):
                    docker.setWindowTitle(docker.windowTitle().strip(docker_title_prefix))

        setupDockers()
        setupDockerMenu()
        setupDockerTitles()

    #endregion

    #region Helper Functions

    def getToolshelfDocker(self):
        for docker in self.windowSource.dockers():
            if docker.objectName() == TOUCHIFY_ID_DOCKER_TOOLSHELFDOCKER:
                toolshelfDocker: ToolshelfDocker = docker
                return toolshelfDocker
        return None
    
    def getToolboxDocker(self):
        for docker in self.windowSource.dockers():
            if docker.objectName() == TOUCHIFY_ID_DOCKER_TOOLBOX:
                result: ToolboxDocker = docker
                return result
        return None
    
    #endregion