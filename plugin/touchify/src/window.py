from PyQt5 import *
from PyQt5.QtWidgets import *
from krita import *

from .variables import *
from .docker_manager import DockerManager
from .action_manager import ActionManager

from .settings_dialog import SettingsDialog

from .features.touchify_canvas import TouchifyCanvas
from .features.touchify_hotkeys import TouchifyHotkeys
from .features.touchify_looks import TouchifyLooks
from .features.touchify_actions import TouchifyActions

from .ext.PyQtExtensions import PyQtExtensions

from .components.touchify.dockers.color_options.ColorOptionsDocker import ColorOptionsDocker
from .components.touchify.dockers.brush_options.BrushOptionsDocker import BrushOptionsDocker
from .components.touchify.dockers.toolshelf.ToolshelfDocker import ToolshelfDocker
from .components.touchify.dockers.toolbox.ToolboxDocker import ToolboxDocker

WINDOW_ID: int = 0

class TouchifyWindow(QObject):
    
    def __init__(self, parent: QObject):
        super().__init__(parent)
        global WINDOW_ID
        self.windowUUID = WINDOW_ID
        WINDOW_ID += 1

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

    def createActions(self, window: Window):
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

    def onActionTick(self):
        self.action_management.onTimerTick()

    def onKritaConfigUpdated(self):
        toolshelf_docker = self.getToolshelfDocker()
        if toolshelf_docker: toolshelf_docker.onKritaConfigUpdate()
        
        self.touchify_canvas.onKritaConfigUpdated()

    def onConfigUpdated(self):
        toolshelf_docker = self.getToolshelfDocker()
        if toolshelf_docker: toolshelf_docker.onConfigUpdated()
        
        toolbox_docker = self.getToolboxDocker()
        if toolbox_docker: toolbox_docker.onConfigUpdated()
        
        self.touchify_canvas.onConfigUpdated()    

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
        
    def setupDockers(self):
        for docker in self.windowSource.dockers():
            if docker.objectName() == TOUCHIFY_ID_DOCKER_TOOLSHELFDOCKER:
                toolshelfDocker: ToolshelfDocker = docker
                toolshelfDocker.setup(self)
            elif docker.objectName() == TOUCHIFY_ID_DOCKER_BRUSHOPTIONSDOCKER:
                brushDocker: BrushOptionsDocker = docker
                brushDocker.setup(self)
            elif docker.objectName() == TOUCHIFY_ID_DOCKER_COLOROPTIONSDOCKER:
                colorDocker: ColorOptionsDocker = docker
                colorDocker.setup(self)
            elif docker.objectName() == TOUCHIFY_ID_DOCKER_TOOLBOX:
                toolboxDocker: ToolboxDocker = docker
                toolboxDocker.setup(self)
            

    def onWindowCreated(self, window: Window):
        self.setParent(window.qwindow())
        self.windowSource = window
        self.docker_management = DockerManager(self)     
        self.setupDockers()

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

    def unload(self):
        pass
