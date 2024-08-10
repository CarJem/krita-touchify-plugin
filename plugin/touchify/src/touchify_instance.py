from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMessageBox

from .docker_manager import DockerManager

from .components.touchify.dockers import TouchifyToolshelfDocker

from .action_manager import ActionManager

from .ext.extensions_pyqt import PyQtExtensions

from .features.touchify_looks import TouchifyLooks
from .variables import *


from .ui.SettingsDialog import *
from .features.touchify_tweaks import *
from .features.touchify_canvas import *
from .features.touchify_hotkeys import *
from .features.canvas_presets import *
from .features.touchify_actions import *



from krita import *

class TouchifyInstance(object):
    def __init__(self):
        self.touchify_actions = TouchifyActions(self)
        self.touchify_looks = TouchifyLooks(self)
        self.touchify_canvas = TouchifyCanvas(self)
        self.touchify_hotkeys = TouchifyHotkeys(self)
        self.touchify_tweaks = TouchifyTweaks(self)
        self.canvas_presets = CanvasPresets(self)
        
        self.action_management = ActionManager()
        
        self.settings_dlg: SettingsDialog | None = None

    def onKritaConfigUpdated(self):
        toolshelf_docker = self.getDockerToolshelf()
        if toolshelf_docker: toolshelf_docker.onKritaConfigUpdate()
        
        self.touchify_canvas.onKritaConfigUpdated()

    def onConfigUpdated(self):     
        toolshelf_docker = self.getDockerToolshelf()
        if toolshelf_docker: toolshelf_docker.onConfigUpdated()
        
        self.touchify_canvas.onConfigUpdated()    

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
        
        canvasDecorationsPopup = window.createAction(TOUCHIFY_ID_ACTION_CANVAS_DECORATION_PRESETS, "Canvas Presets...", TOUCHIFY_ID_MENU_ROOT)
        canvasDecorationsPopup.triggered.connect(self.openCanvasDecoPopup)
        self.mainMenuBar.addAction(canvasDecorationsPopup)

        self.mainMenuBar.addSection("Actions")

        reloadItemsAction = QAction("Refresh Known Items", self.mainMenuBar)
        reloadItemsAction.triggered.connect(self.reloadKnownItems)
        self.mainMenuBar.addAction(reloadItemsAction)
    
    
    def getDockerToolshelf(self):
        for docker in Krita.instance().dockers():
            if docker.objectName() == "TouchifyToolshelfDocker":
                toolshelfDocker: TouchifyToolshelfDocker = docker
                return toolshelfDocker
        return None
        
    def setupDockers(self, window: Window):
        for docker in Krita.instance().dockers():
            if docker.objectName() == "TouchifyToolshelfDocker":
                toolshelfDocker: TouchifyToolshelfDocker = docker
                toolshelfDocker.setup(self)

    def onWindowCreated(self, window: Window):
        self.instanceWindow = window
        self.docker_management = DockerManager(self.instanceWindow)
        self.action_management.windowCreated(self.instanceWindow, self.docker_management)
        
        self.setupDockers(window)

        seperator = QAction("", self.mainMenuBar)
        seperator.setSeparator(True)
        self.mainMenuBar.addAction(seperator)
        
        self.touchify_hotkeys.windowCreated()
        self.touchify_tweaks.windowCreated()
        self.touchify_looks.windowCreated()
        self.touchify_canvas.windowCreated()

        self.touchify_hotkeys.buildMenu(self.mainMenuBar)
        self.touchify_actions.buildMenu(self.mainMenuBar)


    def reloadKnownItems(self):
        msg = QMessageBox(self.instanceWindow.qwindow())
        msg.setText("Reloaded Known Workspaces/Dockers. You will need to reload to use them with this extension")
        msg.exec_()
        
    def openCanvasDecoPopup(self):
        self.canvas_presets.show()

    def openSettings(self):
        if self.settings_dlg != None:
            if PyQtExtensions.isDeleted(self.settings_dlg) == False:
                return
        
        
        self.settings_dlg = SettingsDialog(self.instanceWindow)
        self.settings_dlg.show()