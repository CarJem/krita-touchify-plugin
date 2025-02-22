from typing import TYPE_CHECKING
from PyQt5 import *
from PyQt5.QtWidgets import *
from krita import *

from touchify.src.api_krita.wrappers.window import WindowAPI
from touchify.src.extensions.krita_extensions import KritaExtensions
from touchify.src.managers.normal.canvas import CanvasManager
from touchify.src.managers.normal.developer import DeveloperManager
from touchify.__env__ import *
from touchify.src.managers.normal.dockers import DockerManager
from touchify.src.managers.normal.action_manager import ActionManager

from touchify.src.PluginOptions import PluginOptions

from touchify.src.managers.normal.shortcuts import ShortcutsManager
from touchify.src.managers.normal.tweaks import TweakManager

import touchify.src.extensions.pyqt_extensions as PyQtExtensions

from touchify.src.components.toolshelf.ToolshelfDockWidget import ToolshelfDockWidget
from touchify.src.components.toolbox.ToolboxDocker import ToolboxDocker

WINDOW_ID: int = 0
if TYPE_CHECKING:
    from .Plugin import TouchifyPlugin

class TouchifyWindow(QObject):

    class WorkerTasks(QObject):
        @staticmethod
        def Addons_Post(self: "TouchifyWindow"):
            # Thread
            self.worker_thread = QThread()
            # Worker
            self.worker_instance = TouchifyWindow.WorkerTasks()
            self.worker_instance.moveToThread( self.worker_thread )
            # Thread
            self.worker_thread.started.connect( lambda : self.worker_instance.Addons_Post_Async( self ) )
            self.worker_thread.start()

        def Addons_Post_Async(a, self: "TouchifyWindow"):
            dockers_menu_action = KritaExtensions.getDockerMenu(self.krita_window)
            if dockers_menu_action == None: return

            touchify_title_prefix = "Touchify Core: "
            addon_title_prefix = "Touchify Addon: "

            addon_id_prefix = "Touchify/"
            addon_setup_method = "TOUCHIFY_ADDON_SETUP"
            
            addons_list: list[QAction] = []
            core_list: list[QAction] = []

            for docker_action in dockers_menu_action.menu().actions():
                docker_text = docker_action.text()

                if docker_text.startswith(addon_title_prefix): 
                    docker_action.setText(docker_text.removeprefix(addon_title_prefix))
                    addons_list.append(docker_action)
                    
                if docker_text.startswith(touchify_title_prefix):
                    docker_action.setText(docker_text.removeprefix(touchify_title_prefix))
                    core_list.append(docker_action)
                    
            dockers_menu_action.menu().addSection("Touchify Core")
            for act in core_list: dockers_menu_action.menu().addAction(act)

            dockers_menu_action.menu().addSection("Touchify Addons")
            for act in addons_list: dockers_menu_action.menu().addAction(act)

            for docker in self.krita_window.dockers():
                window_title = docker.windowTitle()
                docker_id = docker.objectName()

                if window_title.startswith(addon_title_prefix):
                    docker.setWindowTitle(window_title.removeprefix(addon_title_prefix))

                if window_title.startswith(touchify_title_prefix):
                    docker.setWindowTitle(window_title.removeprefix(touchify_title_prefix))

                if docker_id == TOUCHIFY_DOCKERID_TOOLSHELFDOCKER:
                    toolshelfDocker: ToolshelfDockWidget = docker
                    toolshelfDocker.setup(self)
                elif docker_id == TOUCHIFY_DOCKERID_DOCKER_TOOLBOX:
                    toolboxDocker: ToolboxDocker = docker
                    toolboxDocker.setup(self)
                else:
                    if not docker_id.startswith(addon_id_prefix): pass
                    elif not hasattr(docker, addon_setup_method): pass
                    elif not callable(getattr(docker, addon_setup_method, False)): pass
                    else: getattr(docker, addon_setup_method)(self)
    
    def __init__(self, parent: QObject):
        super().__init__(parent)
        self.Variables_Init()

    #region Init Functions
    def Variables_Init(self):
        global WINDOW_ID; self.__UUID = WINDOW_ID; WINDOW_ID += 1
        
        self.mgr_tweaker = TweakManager(self)
        self.mgr_shortcuts = ShortcutsManager(self)
        self.mgr_canvas = CanvasManager(self)
        self.mgr_dev = DeveloperManager(self)
        self.mgr_actions = ActionManager(self)
        self.settings_dlg: PluginOptions | None = None

    def Actions_Init(self, window: WindowAPI):
        self.__main_menu_bar = QMenu(None, window.qwindow())

        openSettingsAction = window.createAction(TOUCHIFY_ACTIONID_CONFIGURE, "Configure Touchify...", "settings")
        openSettingsAction.triggered.connect(self.Trigger_OpenSettings)

        menuAction = window.createAction("touchify", "Touchify", "tools")
        menuAction.setMenu(self.__main_menu_bar)

        self.mgr_shortcuts.Actions_Init(window, "tools/touchify", "settings")
        self.mgr_actions.Actions_Init(window, "tools/touchify")  
        self.mgr_dev.Actions_Init(window, "settings")
        self.mgr_tweaker.Actions_Init(window, "settings")
        self.mgr_canvas.Actions_Init(window, "settings")
    #endregion

    #region Post-Init Functions

    def Variables_Post(self, window: WindowAPI):
        self.api_window = window
        self.krita_window = window.native()    
        self.setParent(window.qwindow())

        self.mgr_dockers = DockerManager(self)

        self.mgr_actions.Window_Load()
        self.mgr_shortcuts.Window_Load()
        self.mgr_tweaker.Window_Load()
        self.mgr_canvas.Window_Load()

    def Actions_Post(self):
        instance_seperator = QAction("", self.__main_menu_bar)
        instance_seperator.setText(f"Instance: #{self.__UUID}")
        instance_seperator.setEnabled(False)
        instance_seperator.setSeparator(True)
        self.__main_menu_bar.addAction(instance_seperator)
        self.mgr_shortcuts.Actions_Post()
        self.mgr_tweaker.Actions_Post()
        self.mgr_canvas.Actions_Post()
        self.mgr_actions.Actions_Post(self.__main_menu_bar)
        self.mgr_dev.Actions_Post(self.__main_menu_bar)


        
    #endregion

    #region Window Functions

    def Window_UUID(self):
        return self.__UUID

    def Window_Unload(self):
        pass

    def Window_Load(self, window: WindowAPI):
        self.Variables_Post(window)
        self.Actions_Post()
        TouchifyWindow.WorkerTasks.Addons_Post(self)

    #endregion

    #region Trigger Functions

    def Trigger_OpenSettings(self):
        if self.settings_dlg != None:
            if PyQtExtensions.CommonHelpers.isDeleted(self.settings_dlg) == False:
                return
          
        self.settings_dlg = PluginOptions(self.krita_window)
        self.settings_dlg.show()

    #endregion
