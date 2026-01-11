from typing import TYPE_CHECKING
from PyQt5 import *
from PyQt5.QtWidgets import *
from jemlib.alib_propertygrid.dialogs.PropertyGrid_Window import PropertyGrid_Window
from krita import *

from touchify.src.PluginManagers import TouchifyManagers
from jemlib.api_krita.wrappers.window import WindowAPI
from jemlib.api_touchify.env import *

from touchify.src.PluginOptions import PluginOptions
from touchify.src.config.TouchifyRegistry import TouchifyRegistry
from touchify.src.managers.ApplicationManager import ApplicationManager
from touchify.src.settings.TouchifySettings import TouchifySettings




WINDOW_ID: int = 0
if TYPE_CHECKING:
    from .Plugin import TouchifyPlugin




class TouchifyWindow(QObject):
    
    sigWindowMoved = pyqtSignal()
    sigWindowResized = pyqtSignal()

    def __init__(self, parent: QObject):
        super().__init__(parent)

        global WINDOW_ID; self.INSTANCE_ID = WINDOW_ID; WINDOW_ID += 1
        self.managers = TouchifyManagers(self)
        self.dlg: PropertyGrid_Window | None = None

    def Load(self, window: WindowAPI):
        self.api_window = window
        self.setParent(self.api_window.qwindow)
        self.managers.Load(self)
        ApplicationManager.instance().onWindowLoaded(window.qwindow)

        self.api_window.qwindow.installEventFilter(self)
        
        self.api_window.themeChanged.connect(self.ReloadTheme)

        self.action_plugin_instance = QAction(f"Instance: #{self.INSTANCE_ID}", self.action_plugin_tools_menu)
        self.action_plugin_instance.setEnabled(False)
        self.action_plugin_instance.setSeparator(True)
        self.action_plugin_tools_menu.addAction(self.action_plugin_instance)
        self.managers.ActionWidgets(self)

        self.managers.Addons(self)

    def LoadActions(self, window: WindowAPI):
        self.action_plugin_settings = window.create_action(TouchifyEnv.ActionID.CONFIGURE, "Configure Touchify...", "settings")
        self.action_plugin_settings.triggered.connect(self.OpenSettings)

        self.action_plugin_tools_menu = QMenu(None, window.qwindow)
        self.action_plugin_tools = window.create_action("touchify", "Touchify", "tools")
        self.action_plugin_tools.setMenu(self.action_plugin_tools_menu)

        self.managers.Actions(window)
 
    def Unload(self):
        pass

    def ReloadTheme(self):
        self.managers.ReloadTheme()

    def ReloadSettings(self):
        TouchifySettings.load()
        self.managers.Reload()


    def eventFilter(self, a0: QObject, a1: QEvent):
        try:
            if isinstance(a0, QMainWindow) and a1.type() == QEvent.Type.Resize:
                self.sigWindowResized.emit()
            elif isinstance(a0, QMainWindow) and a1.type() == QEvent.Type.Move:
                self.sigWindowMoved.emit()
        except Exception:
            # Catch-all for any unexpected errors to prevent crashes
            pass
        return super().eventFilter(a0, a1)

    def OpenSettings(self):
        self.dlg = PluginOptions.Setup(self.dlg, self.api_window.qwindow.window(), TouchifySettings.config(), [
            QDialogButtonBox.StandardButton.Save,
            QDialogButtonBox.StandardButton.Apply,
            QDialogButtonBox.StandardButton.Close
        ])
        self.dlg.onObjectSave = self.onSettingsSaved
        self.dlg.onWindowDeleted = self.onSettingsClosed
        self.dlg.show()

    def onSettingsClosed(self):
        self.dlg.deleteLater()
        self.dlg = None

    def onSettingsSaved(self, result: "TouchifyRegistry"):
        result.save()
        self.ReloadSettings()