from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.cfg.resource_pack.ResourcePack import ResourcePack
from touchify.src.cfg.TouchifyRegistry import TouchifyRegistry
from touchify.src.cfg.canvas_preset.CanvasPreset import CanvasPreset
from touchify.src.cfg.docker_group.DockerGroup import DockerGroup
from touchify.src.cfg.popup.PopupData import PopupData
from touchify.src.cfg.toolbox.ToolboxData import ToolboxData
from touchify.src.cfg.toolshelf.ToolshelfData import ToolshelfData
from touchify.src.cfg.TouchifyRegistryPreferences import TouchifyRegistryPreferences
from touchify.src.cfg.widget_layout.WidgetLayout import WidgetLayout
from touchify.src.ext.KritaSettings import KritaSettings
from touchify.src.variables import *

from touchify.src.ext.Extensions import *



class TouchifySettings:

    class RegistryKey:
        def __init__(self, id: str, name: str, item_type: str, item_id: str):
            self.id = id
            self.name = name
            self.item_type = item_type
            self.item_id = item_id

            self.actual_key = f"{self.id}/{self.item_type}/{self.item_id}"

        def __eq__(self, another):
            if isinstance(another, str):
                return self.actual_key == another
            else:
                return hasattr(another, 'actual_key') and self.actual_key == another.actual_key
        
        def __hash__(self):
            return hash(self.actual_key)

    def instance():
        try:
            return TouchifySettings.__instance
        except AttributeError:
            TouchifySettings.__instance = TouchifySettings()
            return TouchifySettings.__instance

    def __init__(self) -> None:
        self.notify_hooks = []
        self.hotkey_options_storage = {}
        self.cfg = TouchifyRegistry()
        
    def preferences(self) -> TouchifyRegistryPreferences:
        return self.cfg.preferences

    def getConfig(self) -> TouchifyRegistry:
        return self.cfg
    
    def getRegistryItem(self, item_id: str, type: type) -> None |\
                                                        PopupData |\
                                                        DockerGroup |\
                                                        CanvasPreset:
        cfg = self.getConfig()
        for pack in cfg.resources.presets:
            pack: ResourcePack

            if type == PopupData:
                for item in pack.popups:
                    item: PopupData
                    id = f"{pack.INTERNAL_FILENAME_ID}/popup/{item.INTERNAL_FILENAME_ID}"
                    if item_id == id: return item
            elif type == DockerGroup:
                for item in pack.docker_groups:
                    item: DockerGroup
                    id = f"{pack.INTERNAL_FILENAME_ID}/docker_group/{item.INTERNAL_FILENAME_ID}"
                    if item_id == id: return item
            elif type == CanvasPreset:
                for item in pack.canvas_presets:
                    item: CanvasPreset
                    id = f"{pack.INTERNAL_FILENAME_ID}/canvas_preset/{item.INTERNAL_FILENAME_ID}"
                    if item_id == id: return item

        return None
    
    def getRegistry(self, type: type) -> dict[RegistryKey, any] |\
                                        dict[RegistryKey,PopupData] |\
                                        dict[RegistryKey,DockerGroup] |\
                                        dict[RegistryKey,CanvasPreset] |\
                                        dict[RegistryKey,ToolshelfData] |\
                                        dict[RegistryKey,ToolboxData] |\
                                        dict[RegistryKey,WidgetLayout]:
        cfg = self.getConfig()
        results: dict = {}
        for pack in cfg.resources.presets:
            pack: ResourcePack

            if type == PopupData:
                for item in pack.popups:
                    item: PopupData
                    id = TouchifySettings.RegistryKey(pack.INTERNAL_FILENAME_ID, pack.metadata.registry_name, "popup", item.INTERNAL_FILENAME_ID)
                    results[id] = item
            elif type == DockerGroup:
                for item in pack.docker_groups:
                    item: DockerGroup
                    id = TouchifySettings.RegistryKey(pack.INTERNAL_FILENAME_ID, pack.metadata.registry_name, "docker_group", item.INTERNAL_FILENAME_ID)
                    results[id] = item
            elif type == CanvasPreset:
                for item in pack.canvas_presets:
                    item: CanvasPreset
                    id = TouchifySettings.RegistryKey(pack.INTERNAL_FILENAME_ID, pack.metadata.registry_name, "canvas_preset", item.INTERNAL_FILENAME_ID)
                    results[id] = item
            elif type == ToolshelfData:
                for item in pack.toolshelves:
                    item: ToolshelfData
                    id = TouchifySettings.RegistryKey(pack.INTERNAL_FILENAME_ID, pack.metadata.registry_name, "toolshelves", item.INTERNAL_FILENAME_ID)
                    results[id] = item
            elif type == ToolboxData:
                for item in pack.toolboxes:
                    item: ToolboxData
                    id = TouchifySettings.RegistryKey(pack.INTERNAL_FILENAME_ID, pack.metadata.registry_name, "toolboxes", item.INTERNAL_FILENAME_ID)
                    results[id] = item
            elif type == WidgetLayout:
                for item in pack.widget_layouts:
                    item: WidgetLayout
                    id = TouchifySettings.RegistryKey(pack.INTERNAL_FILENAME_ID, pack.metadata.registry_name, "widget_layout", item.INTERNAL_FILENAME_ID)
                    results[id] = item

        return results

    #region Toolshelf 

    def getActiveToolshelfId(self, registry_index: int) -> str:
        fallback_val = "none"
        if registry_index == 0:
            return KritaSettings.readSetting(TOUCHIFY_ID_SETTINGS_TOOLSHELF, "SelectedPreset_Main", fallback_val)
        elif registry_index == 1:
            return KritaSettings.readSetting(TOUCHIFY_ID_SETTINGS_TOOLSHELF, "SelectedPreset_Alt", fallback_val)
        elif registry_index == 2:
            return KritaSettings.readSetting(TOUCHIFY_ID_SETTINGS_TOOLSHELF, "SelectedPreset_Docker", fallback_val)
        else:
            return fallback_val

    def getActiveToolshelf(self, registry_index: int) -> ToolshelfData:
        registry = self.getRegistry(ToolshelfData)
        registry_selection = self.getActiveToolshelfId(registry_index)

        if registry_selection in registry:
            return registry[registry_selection]    
        else: 
            return ToolshelfData()

    def setActiveToolshelf(self, registry_index: int, id: str):
        if registry_index == 0:
            KritaSettings.writeSetting(TOUCHIFY_ID_SETTINGS_TOOLSHELF, "SelectedPreset_Main", id, False)
        elif registry_index == 1:
            KritaSettings.writeSetting(TOUCHIFY_ID_SETTINGS_TOOLSHELF, "SelectedPreset_Alt", id, False)
        elif registry_index == 2:
            KritaSettings.writeSetting(TOUCHIFY_ID_SETTINGS_TOOLSHELF, "SelectedPreset_Docker", id, False)

        self.notifyUpdate()
    
    #endregion

    #region Toolbox 

    def getActiveToolboxId(self) -> str:
        fallback_val = "none"
        return KritaSettings.readSetting(TOUCHIFY_ID_DOCKER_TOOLBOX, "SelectedPreset", fallback_val)

    def getActiveToolbox(self) -> ToolboxData:
        registry = self.getRegistry(ToolboxData)
        registry_selection = self.getActiveToolboxId()

        if registry_selection in registry:
            return registry[registry_selection]    
        else: 
            return ToolboxData()

    def setActiveToolbox(self, id: str):
        KritaSettings.writeSetting(TOUCHIFY_ID_DOCKER_TOOLBOX, "SelectedPreset", id, False)
        self.notifyUpdate()
    
    #endregion

    #region Widget Layouts 

    def getActiveWidgetLayoutId(self) -> str:
        fallback_val = "none"
        return KritaSettings.readSetting(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "SelectedPreset", fallback_val)

    def getActiveWidgetLayout(self) -> WidgetLayout:
        registry = self.getRegistry(WidgetLayout)
        registry_selection = self.getActiveWidgetLayoutId()

        if registry_selection in registry:
            return registry[registry_selection]    
        else: 
            return WidgetLayout()

    def setActiveWidgetLayout(self, id: str):
        KritaSettings.writeSetting(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "SelectedPreset", id, False)
        self.notifyUpdate()
    
    #endregion

    def addHotkeyOption(self, actionName, displayName, action, parameters):
        self.hotkey_options_storage[actionName] = {
            "displayName": displayName,
            "action": action,
            "params": parameters
        }
    
    def runHotkeyOption(self, actionName: str):
        if actionName == "none":
            return
        
        if actionName not in TouchifySettings.instance().hotkey_options_storage:
            return
        
        actionObj = TouchifySettings.instance().hotkey_options_storage[actionName]
        params = actionObj["params"]
        action = actionObj["action"]
        
        action(**params)

    def notifyConnect(self, event):
        self.notify_hooks.append(event)

    def notifyUpdate(self):
        self.cfg.load()

        for hook in self.notify_hooks:
            hook()




