from typing import TYPE_CHECKING
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from jemlib.alib_kis.tools.ToolOptionsPages import ToolOptionPage, ToolOptionPages
from jemlib.alib_vaporjem import Logger
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from jemlib.api_krita.enums.tool import Tool
from jemlib.api_krita.wrappers.window import WindowAPI
from jemlib.api_touchify.env import TouchifyEnv
from jemlib.managers.KritaSettings import KritaSettings
from krita import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from touchify.src.settings.TouchifySettings import TouchifySettings

if TYPE_CHECKING:
    from ..PluginManagers import TouchifyManagers
    from ..PluginWindow import TouchifyWindow

class ToolOptionsManager(QObject):

    class RuntimeCache:
        def __init__(self, **args) -> None:
            self.single_brush_memory: dict[str, dict[str, any]] = {}
            self.multi_brush_memory: dict[str, dict[str, any]] = {}
            JsonExtensions.dictToObject(self, args)

        @staticmethod
        def load_cache():
            return JsonExtensions.loadClass(KritaSettings.readSetting(TouchifyEnv.SettingsPath.CACHE, "brush_manager", ""), ToolOptionsManager.RuntimeCache)

        @staticmethod
        def save_cache(input: any):
            jsonData = JsonExtensions.saveClass(input)
            KritaSettings.writeSetting(TouchifyEnv.SettingsPath.CACHE, "brush_manager", jsonData, False)

    def __init__(self, parent: QObject, managers: "TouchifyManagers"):
        super().__init__(parent)
        self.managers = managers

        self.window: "TouchifyWindow | None" = None
        self.api_window: WindowAPI | None = None
        self.notifier = None
        self.options_page: ToolOptionPage = None

        self.__lastToolboxTool = ""

        self._runtime_cache = ToolOptionsManager.RuntimeCache()

    def Window_Load(self, window: "TouchifyWindow"):
        self.window = window
        self.api_window = self.window.api_window
        self.notifier = self.api_window.notifier

        self._runtime_cache = ToolOptionsManager.RuntimeCache.load_cache()

        self.__lastToolboxTool = self.notifier.getCurrentTool()
        self.__lastBrushId = self.notifier.getCurrentBrushName()

        self.notifier.toolChanged.connect(self.Notifier_ToolChanged)
        self.notifier.brushChanged.connect(self.Notifier_BrushChanged)

    def Notifier_ToolChanged(self, new_tool_id: str):
        self.syncBrushState(self.__lastBrushId, new_tool_id)

    def Notifier_BrushChanged(self, resource: Resource):
        if resource: self.syncBrushState(resource.name(), self.__lastToolboxTool)

    def restoreBrushState(self, brush_id: str, cache_list: dict, options_page: ToolOptionPage):
        if brush_id in cache_list: options_page.set_settings(cache_list[brush_id])

    def saveBrushState(self, brush_id: str, cache_list: dict, cfg: dict):
        cache_list[brush_id] = cfg
        ToolOptionsManager.RuntimeCache.save_cache(self._runtime_cache)

    def syncBrushState(self, new_brush_id: str, new_tool_id: str):
        if self.options_page: self.options_page.blockSignals(True)

        old_brush_id = str(self.__lastBrushId)
        old_tool_id = str(self.__lastToolboxTool)

        self.__lastToolboxTool = new_tool_id
        self.__lastBrushId = new_brush_id

        if self.options_page and new_tool_id != old_tool_id:
            self.options_page.close()
            self.options_page = None

        
        if not TouchifySettings.preferences().Brushes_OptionsPerBrush: return
        if not new_brush_id: return
        if not self.__lastBrushId: return

        if new_tool_id == Tool.FREEHAND_BRUSH.value: 
            self.options_page = ToolOptionPages.FreehandBrush(self.api_window)
        elif new_tool_id == Tool.MULTI_BRUSH.value: 
            self.options_page = ToolOptionPages.MultiBrush(self.api_window)
        else:
            self.options_page = None

        if not self.options_page: return
        self.options_page.optionsChanged.connect(self.onBrushStateChanged)

        if old_tool_id != new_tool_id:
            QTimer.singleShot(1, lambda: self.setBrushState(new_tool_id, old_tool_id, new_brush_id, old_brush_id))
        else:
            self.setBrushState(new_tool_id, old_tool_id, new_brush_id, old_brush_id)

    def onBrushStateChanged(self):
        current_settings = self.options_page.get_settings()
        if not current_settings: return

        brush_id = self.__lastBrushId
        tool_id = self.__lastToolboxTool

        is_freehand_brush = tool_id == Tool.FREEHAND_BRUSH.value
        is_multi_brush = tool_id == Tool.MULTI_BRUSH.value

        if is_freehand_brush:
            Logger.logDebug("Touchify", "BrushManager", "onBrushStateChanged", "Saving: Freehand Brush")
            self.saveBrushState(brush_id, self._runtime_cache.single_brush_memory, current_settings)
        elif is_multi_brush:
            Logger.logDebug("Touchify", "BrushManager", "onBrushStateChanged", "Saving: Multibrush Brush")
            self.saveBrushState(brush_id, self._runtime_cache.multi_brush_memory, current_settings)

    def setBrushState(self, new_tool_id: str, old_tool_id: str, new_brush_id: str, old_brush_id: str):
        # State invalidated by a newer sync event; ignore the request
        if self.__lastToolboxTool != new_tool_id and self.__lastBrushId != new_brush_id: 
            return

        current_settings = self.options_page.get_settings()
        if not current_settings: return

        has_tool_changed = old_tool_id != new_tool_id
        has_brush_changed = old_brush_id != new_brush_id

        is_freehand_brush = new_tool_id == Tool.FREEHAND_BRUSH.value
        is_multi_brush = new_tool_id == Tool.MULTI_BRUSH.value

        if has_tool_changed:
            if is_freehand_brush: 
                Logger.logDebug("Touchify", "BrushManager", "setBrushState", "Restoring: Freehand Brush")
                self.restoreBrushState(new_brush_id, self._runtime_cache.single_brush_memory, self.options_page)
            elif is_multi_brush: 
                Logger.logDebug("Touchify", "BrushManager", "setBrushState", "Restoring: Multibrush Brush")
                self.restoreBrushState(new_brush_id, self._runtime_cache.multi_brush_memory, self.options_page)

        elif has_brush_changed:
            if is_freehand_brush:
                Logger.logDebug("Touchify", "BrushManager", "setBrushState", "Loading: Freehand Brush")
                self.saveBrushState(old_brush_id, self._runtime_cache.single_brush_memory, current_settings)
                self.restoreBrushState(new_brush_id, self._runtime_cache.single_brush_memory, self.options_page)
            elif is_multi_brush:
                Logger.logDebug("Touchify", "BrushManager", "setBrushState", "Loading: Multibrush Brush")
                self.saveBrushState(old_brush_id, self._runtime_cache.multi_brush_memory, current_settings)
                self.restoreBrushState(new_brush_id, self._runtime_cache.multi_brush_memory, self.options_page)
            

        
            


