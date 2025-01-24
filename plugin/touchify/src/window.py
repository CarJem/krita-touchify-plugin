from typing import TYPE_CHECKING
from PyQt5 import *
from PyQt5.QtWidgets import *
from krita import *

from touchify.src.features.canvas_manager import CanvasManager
from touchify.src.features.touchify_dev import TouchifyDev
from touchify.src.features.touchify_shortcut_composer import TouchifyShortcutComposer
from touchify.src.helpers import TouchifyHelpers
from touchify.src.local_events import LocalEvents
from touchify.src.variables import *
from touchify.src.features.docker_manager import DockerManager
from touchify.src.features.action_manager import ActionManager

from touchify.src.components.touchify.util.settings_dialog import SettingsDialog

from touchify.src.features.touchify_shortcuts import TouchifyShortcuts
from touchify.src.features.touchify_tweaks import TouchifyTweaks
from touchify.src.features.touchify_registered_actions import TouchifyRegisteredActions

from touchify.src.components.pyqt.extensions import PyQtExtensions

from touchify.src.components.touchify.dockers.toolshelf.ToolshelfDockWidget import ToolshelfDockWidget
from touchify.src.components.touchify.dockers.toolbox.ToolboxDocker import ToolboxDocker

WINDOW_ID: int = 0
if TYPE_CHECKING:
    from .extension import TouchifyExtension

class TouchifyWindow(QObject):
    
    def __init__(self, parent: QObject):
        super().__init__(parent)
        self.Variables_Init()

    #region Init Functions
    def Variables_Init(self):
        global WINDOW_ID
        self.windowUUID = WINDOW_ID
        WINDOW_ID += 1

        self.event_handler = LocalEvents(self)
        self.mgr_registry = TouchifyRegisteredActions(self)
        self.mgr_tweaker = TouchifyTweaks(self)
        self.mgr_shortcuts = TouchifyShortcuts(self)
        self.mgr_canvas = CanvasManager(self)
        self.mgr_dev = TouchifyDev(self)
        self.mgr_sc = TouchifyShortcutComposer(self)
        self.mgr_actions = ActionManager(self)
        self.settings_dlg: SettingsDialog | None = None

    def Actions_Init(self, window: Window):
        self.__main_menu_bar = QMenu(TOUCHIFY_ID_ACTION_ROOT, window.qwindow())

        openSettingsAction = window.createAction(TOUCHIFY_ID_ACTION_CONFIGURE, "Configure Touchify...", "settings")
        openSettingsAction.triggered.connect(self.Trigger_OpenSettings)

        menuAction = window.createAction("touchify", TOUCHIFY_ID_ACTION_ROOT, "tools")
        menuAction.setMenu(self.__main_menu_bar)

        self.mgr_shortcuts.Actions_Init(window, TOUCHIFY_ID_ACTION_ROOT)
        self.mgr_registry.Actions_Init(window, TOUCHIFY_ID_ACTION_ROOT)  
        self.mgr_dev.Actions_Init(window, TOUCHIFY_ID_ACTION_ROOT)
        self.mgr_tweaker.Actions_Init(window, TOUCHIFY_ID_ACTION_ROOT)
        self.mgr_canvas.Actions_Init(window)
        self.mgr_sc.Actions_Init(window, self.__main_menu_bar)
    #endregion

    #region Post-Init Functions

    def Variables_Post(self, window: Window):
        self.krita_window = window    
        self.setParent(window.qwindow())

        self.mgr_dockers = DockerManager(self)

        self.mgr_actions.Window_Load()
        self.mgr_shortcuts.Window_Load()
        self.mgr_tweaker.Window_Load()
        self.mgr_canvas.Window_Load()

    def Actions_Post(self):
        instance_seperator = QAction("", self.__main_menu_bar)
        instance_seperator.setText(f"Instance: #{self.windowUUID}")
        instance_seperator.setEnabled(False)
        instance_seperator.setSeparator(True)
        self.__main_menu_bar.addAction(instance_seperator)

        self.mgr_shortcuts.Actions_Post()
        self.mgr_tweaker.Actions_Post()
        self.mgr_canvas.Actions_Post()
        self.mgr_registry.Actions_Post(self.__main_menu_bar)
        self.mgr_sc.Actions_Post(self.__main_menu_bar)
        self.mgr_dev.Actions_Post(self.__main_menu_bar)
    
    def Addons_Post(self):
        dockers = self.krita_window.dockers()
        dockers_menu_action = TouchifyHelpers.getDockerMenu(self.krita_window)
        if dockers_menu_action == None: return

        touchify_title_prefix = "Touchify Core: "
        addon_title_prefix = "Touchify Addon: "

        addon_id_prefix = "Touchify/"
        addon_setup_method = "TOUCHIFY_ADDON_SETUP"
        
        for docker in dockers:
            window_title = docker.windowTitle()
            docker_id = docker.objectName()

            if window_title.startswith(addon_title_prefix):
                docker.setWindowTitle(window_title.strip(addon_title_prefix))
            elif window_title.startswith(touchify_title_prefix):
                docker.setWindowTitle(window_title.strip(addon_title_prefix))

            if docker_id == TOUCHIFY_ID_DOCKER_TOOLSHELFDOCKER:
                toolshelfDocker: ToolshelfDockWidget = docker
                toolshelfDocker.setup(self)
            elif docker_id == TOUCHIFY_ID_DOCKER_TOOLBOX:
                toolboxDocker: ToolboxDocker = docker
                toolboxDocker.setup(self)
            else:
                if not docker_id.startswith(addon_id_prefix): pass
                elif not hasattr(docker, addon_setup_method): pass
                elif not callable(getattr(docker, addon_setup_method, False)): pass
                else: getattr(docker, addon_setup_method)(self)


        addons_list: list[QAction] = []
        normal_list: list[QAction] = []

        for docker_action in dockers_menu_action.menu().actions():
            docker_text = docker_action.text()

            if docker_text.startswith(addon_title_prefix): 
                docker_action.setText(docker_text.strip(touchify_title_prefix))
                normal_list.append(docker_action)

            elif docker_text.startswith(touchify_title_prefix):
                docker_action.setText(docker_text.strip(addon_title_prefix))
                addons_list.append(docker_action)
                
        dockers_menu_action.menu().addSection("Touchify")
        for docker in normal_list: dockers_menu_action.menu().addAction(docker)

        dockers_menu_action.menu().addSection("Touchify Addons")
        for docker in addons_list: dockers_menu_action.menu().addAction(docker)
        
    #endregion

    #region Window Functions

    def Window_Unload(self):
        pass

    def Window_Load(self, window: Window):
        self.Variables_Post(window)
        self.Actions_Post()
        self.Addons_Post()

    #endregion

    #region Trigger Functions

    def Trigger_OpenSettings(self):
        if self.settings_dlg != None:
            if PyQtExtensions.isDeleted(self.settings_dlg) == False:
                return
          
        self.settings_dlg = SettingsDialog(self.krita_window)
        self.settings_dlg.show()

    #endregion
