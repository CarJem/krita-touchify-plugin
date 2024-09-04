from PyQt5 import *
from PyQt5.QtWidgets import *
from krita import *

from .variables import *
from .docker_manager import DockerManager
from .action_manager import ActionManager

from .ui.SettingsDialog import *

from .features.touchify_canvas import *
from .features.touchify_hotkeys import *
from .features.touchify_looks import *
from .features.canvas_presets import *
from .features.touchify_actions import *

from .ext.KritaSettings import KritaSettings
from .ext.extensions_pyqt import PyQtExtensions

from .components.touchify.dockers.color_options.ColorOptionsDocker import ColorOptionsDocker
from .components.touchify.dockers.brush_options.BrushOptionsDocker import BrushOptionsDocker
from .components.touchify.dockers.toolshelf.ToolshelfDocker import TouchifyToolshelfDocker
from .components.touchify.dockers.reference_tabs.ReferenceTabsDocker import ReferenceTabsDocker
from .components.touchify.dockers.touchify_toolbox.TouchifyToolboxDocker import TouchifyToolboxDocker


class Touchify(Extension):
    
    HAS_LOADED = False

    def __init__(self, parent):
        super().__init__(parent)


        TOUCHIFY_ID_ACTION_CANVAS_DECORATION_PRESETS

        self.touchify_actions = TouchifyActions(self)
        self.touchify_looks = TouchifyLooks(self)
        self.touchify_canvas = TouchifyCanvas(self)
        self.touchify_hotkeys = TouchifyHotkeys(self)
        self.canvas_presets = CanvasPresets(self)
        
        self.timer: QTimer = None
        
        self.action_management = ActionManager(self)
        
        self.settings_dlg: SettingsDialog | None = None

        Touchify.HAS_LOADED = True

    def krita(self) -> Krita:
        return self.parent()

    def setup(self):
        self.krita().notifier().windowCreated.connect(self.onWindowCreated)
        TouchifyConfig.instance().notifyConnect(self.onConfigUpdated)
        KritaSettings.notifyConnect(self.onKritaConfigUpdated)

    def onKritaConfigUpdated(self):
        toolshelf_docker = self.getDockerToolshelf()
        if toolshelf_docker: toolshelf_docker.onKritaConfigUpdate()
        
        self.touchify_canvas.onKritaConfigUpdated()

    def openCanvasDecoPopup(self):
        self.canvas_presets.show()

    def openSettings(self):
        if self.settings_dlg != None:
            if PyQtExtensions.isDeleted(self.settings_dlg) == False:
                return
        
        
        self.settings_dlg = SettingsDialog(self.instanceWindow)
        self.settings_dlg.show()

    def onConfigUpdated(self):
        toolshelf_docker = self.getDockerToolshelf()
        if toolshelf_docker: toolshelf_docker.onConfigUpdated()
        
        self.touchify_canvas.onConfigUpdated()    

    def getDockerToolshelf(self):
        for docker in Krita.instance().dockers():
            if docker.objectName() == "TouchifyToolshelfDocker":
                toolshelfDocker: TouchifyToolshelfDocker = docker
                return toolshelfDocker
        return None
        
    def setupDockers(self):
        for docker in Krita.instance().dockers():
            if docker.objectName() == "TouchifyToolshelfDocker":
                toolshelfDocker: TouchifyToolshelfDocker = docker
                toolshelfDocker.setup(self)
                
    def startTimer(self, window: Window):
        self.timer = QTimer(window.qwindow())
        self.timer.setInterval(500)
        self.timer.start()

    def onWindowCreated(self):
        #self.krita().notifier().windowCreated.disconnect(self.onWindowCreated)
        window = Krita.instance().activeWindow()
        self.instanceWindow = window
        self.docker_management = DockerManager(self)     
        self.setupDockers()

        self.startTimer(window)

        seperator = QAction("", self.mainMenuBar)
        seperator.setSeparator(True)
        self.mainMenuBar.addAction(seperator)
        
        self.touchify_hotkeys.windowCreated()
        self.touchify_looks.windowCreated()
        self.touchify_canvas.windowCreated()

        self.touchify_hotkeys.buildMenu(self.mainMenuBar)
        self.touchify_actions.buildMenu(self.mainMenuBar)

    def reloadKnownItems(self):
        msg = QMessageBox(self.instanceWindow.qwindow())
        msg.setText("Reloaded Known Workspaces/Dockers. You will need to reload to use them with this extension")
        msg.exec_()

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


if Touchify.HAS_LOADED == False:
    instance = Krita.instance()
    extension = Touchify(instance)

    instance.addExtension(extension)
    instance.addDockWidgetFactory(DockWidgetFactory(TOUCHIFY_ID_DOCKER_COLOROPTIONSDOCKER, DockWidgetFactoryBase.DockPosition.DockRight, ColorOptionsDocker))
    instance.addDockWidgetFactory(DockWidgetFactory(TOUCHIFY_ID_DOCKER_BRUSHOPTIONSDOCKER, DockWidgetFactoryBase.DockPosition.DockRight, BrushOptionsDocker))
    instance.addDockWidgetFactory(DockWidgetFactory(TOUCHIFY_ID_DOCKER_TOOLSHELFDOCKER, DockWidgetFactoryBase.DockPosition.DockRight, TouchifyToolshelfDocker))
    instance.addDockWidgetFactory(DockWidgetFactory(TOUCHIFY_ID_DOCKER_REFERENCETABSDOCKER, DockWidgetFactoryBase.DockPosition.DockRight, ReferenceTabsDocker))
    instance.addDockWidgetFactory(DockWidgetFactory(TOUCHIFY_ID_DOCKER_TOOLBOX, DockWidgetFactoryBase.DockPosition.DockRight, TouchifyToolboxDocker))
