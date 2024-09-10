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
from .components.touchify.dockers.toolshelf.ToolshelfDocker import ToolshelfDocker
from .components.touchify.dockers.reference_tabs.ReferenceTabsDocker import ReferenceTabsDocker
from .components.touchify.dockers.touchify_toolbox.ToolboxDocker import ToolboxDocker

WINDOW_ID: int = 0

class Touchify(Extension):

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
            self.canvas_presets = CanvasPresets(self)
            
            self.timer: QTimer = None
            
            self.action_management = ActionManager(self)
            
            self.settings_dlg: SettingsDialog | None = None

        def openSettings(self):
            if self.settings_dlg != None:
                if PyQtExtensions.isDeleted(self.settings_dlg) == False:
                    return
            
            
            self.settings_dlg = SettingsDialog(self.windowSource)
            self.settings_dlg.show()

        def openCanvasDecoPopup(self):
            self.canvas_presets.show()

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
                    
        def startTimer(self, window: Window):
            self.timer = QTimer(window.qwindow())
            self.timer.setInterval(500)
            self.timer.start()

        def onWindowCreated(self, window: Window):
            self.setParent(window.qwindow())
            self.windowSource = window
            self.docker_management = DockerManager(self)     
            self.setupDockers()

            self.startTimer(self.windowSource)

            seperator = QAction("", self.mainMenuBar)
            seperator.setText(f"Instance: #{self.windowUUID}")
            seperator.setEnabled(False)
            seperator.setSeparator(True)
            self.mainMenuBar.addAction(seperator)
            
            self.touchify_hotkeys.windowCreated()
            self.touchify_looks.windowCreated()
            self.touchify_canvas.windowCreated()

            self.touchify_hotkeys.buildMenu(self.mainMenuBar)
            self.touchify_actions.buildMenu(self.mainMenuBar)

        def unload(self):
            pass

    instances: dict[str, TouchifyWindow] = {}
    instance_generate: bool = False
    instance_generated: TouchifyWindow = None

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        Krita.instance().notifier().windowCreated.connect(self.onWindowCreated)
        TouchifyConfig.instance().notifyConnect(self.onConfigUpdated)
        KritaSettings.notifyConnect(self.onKritaConfigUpdated)

    def onKritaConfigUpdated(self):
        for id in self.instances:
            self.instances[id].onKritaConfigUpdated()

    def onConfigUpdated(self):
        for id in self.instances:
            self.instances[id].onConfigUpdated()

    def getNewWindow(self):
        window = Krita.instance().activeWindow()
        window_hash = str(window.qwindow().windowHandle().__hash__())
        if window_hash not in self.instances:
            return window
    
    def onWindowDestroyed(self, windowId: str):
        item: Touchify.TouchifyWindow = self.instances[windowId]
        item.unload()
        item.deleteLater()
        del self.instances[windowId]

    def onWindowCreated(self):
        if self.instance_generate:
            new_window = self.getNewWindow()
            new_window_id = str(new_window.qwindow().windowHandle().__hash__())
            new_window.windowClosed.connect(lambda: self.onWindowDestroyed(new_window_id))
            self.instances[new_window_id] = self.instance_generated
            self.instances[new_window_id].onWindowCreated(new_window)
            self.instance_generate = False


    def createActions(self, window: Window):
        self.instance_generate = True
        self.instance_generated = Touchify.TouchifyWindow(self)
        self.instance_generated.createActions(window)


Krita.instance().addExtension(Touchify(Krita.instance()))
Krita.instance().addDockWidgetFactory(DockWidgetFactory(TOUCHIFY_ID_DOCKER_COLOROPTIONSDOCKER, DockWidgetFactoryBase.DockPosition.DockRight, ColorOptionsDocker))
Krita.instance().addDockWidgetFactory(DockWidgetFactory(TOUCHIFY_ID_DOCKER_BRUSHOPTIONSDOCKER, DockWidgetFactoryBase.DockPosition.DockRight, BrushOptionsDocker))
Krita.instance().addDockWidgetFactory(DockWidgetFactory(TOUCHIFY_ID_DOCKER_TOOLSHELFDOCKER, DockWidgetFactoryBase.DockPosition.DockRight, ToolshelfDocker))
Krita.instance().addDockWidgetFactory(DockWidgetFactory(TOUCHIFY_ID_DOCKER_REFERENCETABSDOCKER, DockWidgetFactoryBase.DockPosition.DockRight, ReferenceTabsDocker))
Krita.instance().addDockWidgetFactory(DockWidgetFactory(TOUCHIFY_ID_DOCKER_TOOLBOX, DockWidgetFactoryBase.DockPosition.DockRight, ToolboxDocker))
