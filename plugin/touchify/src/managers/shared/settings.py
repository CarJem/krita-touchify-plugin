from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.config.pie_wheel.PieWheelData import PieWheelData
from touchify.src.config.resource_pack.ResourcePack import ResourcePack
from touchify.src.config.TouchifyRegistry import TouchifyRegistry
from touchify.src.config.canvas_preset.CanvasPreset import CanvasPreset
from touchify.src.config.docker_group.DockerGroup import DockerGroup
from touchify.src.config.popup.PopupData import PopupData
from touchify.src.config.script.CustomScript import CustomScript
from touchify.src.config.toolbox.ToolboxData import ToolboxData
from touchify.src.config.toolshelf.Toolshelf import Toolshelf
from touchify.src.config.TouchifyRegistryPreferences import TouchifyRegistryPreferences
from touchify.src.config.menu.TriggerMenu import TriggerMenu
from touchify.src.managers.shared.settings_krita import KritaSettings
from touchify.src.managers.shared.events import GlobalEvents
from touchify.__env__ import *



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
        
        def getResourcePack(self):
            resourcePacks = TouchifySettings.instance().getResourcePacks()
            for pack in resourcePacks:
                if pack.INTERNAL_UUID_ID == self.id: return pack
            return None

    @staticmethod
    def instance():
        try:
            return TouchifySettings.__instance
        except AttributeError:
            TouchifySettings.__instance = TouchifySettings()
            return TouchifySettings.__instance
        
    @staticmethod  
    def reload():
        TouchifySettings.instance().cfg.load()
        GlobalEvents.EMIT_SIGNAL_TOUCHIFY_CONFIG_UPDATED()

    def __init__(self) -> None:
        self.notify_hooks = []
        self.cfg = TouchifyRegistry()
        
    def preferences(self) -> TouchifyRegistryPreferences:
        return self.cfg.preferences

    def getConfig(self) -> TouchifyRegistry:
        return self.cfg
    
    def getResourcePacks(self) -> list[ResourcePack]:
        cfg = self.getConfig()
        return cfg.resources.presets
    
    def getRegistryItem(self, item_id: str, type: type) -> None |\
                                                        TriggerMenu |\
                                                        PopupData |\
                                                        DockerGroup |\
                                                        CanvasPreset |\
                                                        Toolshelf |\
                                                        ToolboxData |\
                                                        CustomScript |\
                                                        PieWheelData:
        cfg = self.getConfig()
        for pack in cfg.resources.presets:
            pack: ResourcePack

            if type == PopupData:
                for item in pack.popups:
                    item: PopupData
                    id = f"{pack.INTERNAL_UUID_ID}/popup/{item.INTERNAL_UUID_ID}"
                    if item_id == id: return item
            elif type == TriggerMenu:
                for item in pack.menus:
                    item: TriggerMenu
                    id = f"{pack.INTERNAL_UUID_ID}/menu/{item.INTERNAL_UUID_ID}"
                    if item_id == id: return item
            elif type == Toolshelf:
                for item in pack.shelves:
                    item: Toolshelf
                    id = f"{pack.INTERNAL_UUID_ID}/shelves/{item.INTERNAL_UUID_ID}"
                    if item_id == id: return item
            elif type == ToolboxData:
                for item in pack.toolboxes:
                    item: ToolboxData
                    id = f"{pack.INTERNAL_UUID_ID}/toolboxes/{item.INTERNAL_UUID_ID}"
                    if item_id == id: return item         
            elif type == DockerGroup:
                for item in pack.docker_groups:
                    item: DockerGroup
                    id = f"{pack.INTERNAL_UUID_ID}/docker_group/{item.INTERNAL_UUID_ID}"
                    if item_id == id: return item
            elif type == CanvasPreset:
                for item in pack.canvas_presets:
                    item: CanvasPreset
                    id = f"{pack.INTERNAL_UUID_ID}/canvas_preset/{item.INTERNAL_UUID_ID}"
                    if item_id == id: return item
            elif type == CustomScript:
                for item in pack.scripts:
                    item: CustomScript
                    id = f"{pack.INTERNAL_UUID_ID}/scripts/{item.INTERNAL_UUID_ID}"
                    if item_id == id: return item
            elif type == PieWheelData:
                for item in pack.pie_wheels:
                    item: PieWheelData
                    id = f"{pack.INTERNAL_UUID_ID}/pie_wheels/{item.INTERNAL_UUID_ID}"
                    if item_id == id: return item

        return None
    
    def getRegistry(self, type: type) -> dict[RegistryKey, any] |\
                                        dict[RegistryKey, TriggerMenu] |\
                                        dict[RegistryKey,PopupData] |\
                                        dict[RegistryKey,DockerGroup] |\
                                        dict[RegistryKey,CanvasPreset] |\
                                        dict[RegistryKey,Toolshelf] |\
                                        dict[RegistryKey,ToolboxData] |\
                                        dict[RegistryKey,CustomScript] |\
                                        dict[RegistryKey,PieWheelData]:
        cfg = self.getConfig()
        results: dict = {}
        for pack in cfg.resources.presets:
            pack: ResourcePack

            if type == PopupData:
                for item in pack.popups:
                    item: PopupData
                    id = TouchifySettings.RegistryKey(pack.INTERNAL_UUID_ID, pack.metadata.registry_name, "popup", item.INTERNAL_UUID_ID)
                    results[id] = item
            elif type == TriggerMenu:
                for item in pack.menus:
                    item: TriggerMenu
                    id = TouchifySettings.RegistryKey(pack.INTERNAL_UUID_ID, pack.metadata.registry_name, "menu", item.INTERNAL_UUID_ID)
                    results[id] = item
            elif type == DockerGroup:
                for item in pack.docker_groups:
                    item: DockerGroup
                    id = TouchifySettings.RegistryKey(pack.INTERNAL_UUID_ID, pack.metadata.registry_name, "docker_group", item.INTERNAL_UUID_ID)
                    results[id] = item
            elif type == CanvasPreset:
                for item in pack.canvas_presets:
                    item: CanvasPreset
                    id = TouchifySettings.RegistryKey(pack.INTERNAL_UUID_ID, pack.metadata.registry_name, "canvas_preset", item.INTERNAL_UUID_ID)
                    results[id] = item
            elif type == Toolshelf:
                for item in pack.shelves:
                    item: Toolshelf
                    id = TouchifySettings.RegistryKey(pack.INTERNAL_UUID_ID, pack.metadata.registry_name, "shelves", item.INTERNAL_UUID_ID)
                    results[id] = item
            elif type == ToolboxData:
                for item in pack.toolboxes:
                    item: ToolboxData
                    id = TouchifySettings.RegistryKey(pack.INTERNAL_UUID_ID, pack.metadata.registry_name, "toolboxes", item.INTERNAL_UUID_ID)
                    results[id] = item
            elif type == CustomScript:
                for item in pack.scripts:
                    item: CustomScript
                    id = TouchifySettings.RegistryKey(pack.INTERNAL_UUID_ID, pack.metadata.registry_name, "scripts", item.INTERNAL_UUID_ID)
                    results[id] = item
            elif type == PieWheelData:
                for item in pack.pie_wheels:
                    item: PieWheelData
                    id = TouchifySettings.RegistryKey(pack.INTERNAL_UUID_ID, pack.metadata.registry_name, "pie_wheels", item.INTERNAL_UUID_ID)
                    results[id] = item

        return results

    #region Toolshelf

    def getActiveShelfId(self, registry_index: int) -> str:
        fallback_val = "none"

        if registry_index >= 0:
            return KritaSettings.readSetting(TOUCHIFY_SETTINGPATH_TOOLSHELF, "SelectedPreset_" + str(registry_index), fallback_val)
        else:
            return fallback_val

    def getActiveShelf(self, registry_index: int) -> Toolshelf:
        registry = self.getRegistry(Toolshelf)
        registry_selection = self.getActiveShelfId(registry_index)

        if registry_selection in registry:
            return registry[registry_selection]    
        else: 
            return Toolshelf()
        
    def getActiveShelfKey(self, registry_index: int) -> RegistryKey:
        registry = self.getRegistry(Toolshelf)
        registry_selection: str = self.getActiveShelfId(registry_index)

        if registry_selection in registry:
            keys = [key for key, val in registry.items() if key.actual_key == registry_selection]
            return keys[0]
        else: 
            return "none"

    def setActiveShelf(self, registry_index: int, id: str) -> str:
        if registry_index >= 0:
            KritaSettings.writeSetting(TOUCHIFY_SETTINGPATH_TOOLSHELF, "SelectedPreset_" + str(registry_index), id, False)

    #region Toolbox 

    def getActiveToolboxId(self) -> str:
        fallback_val = "none"
        return KritaSettings.readSetting(TOUCHIFY_DOCKERID_DOCKER_TOOLBOX, "SelectedPreset", fallback_val)

    def getActiveToolbox(self) -> ToolboxData:
        registry = self.getRegistry(ToolboxData)
        registry_selection = self.getActiveToolboxId()

        if registry_selection in registry:
            return registry[registry_selection]    
        else: 
            return ToolboxData()

    def setActiveToolbox(self, id: str):
        KritaSettings.writeSetting(TOUCHIFY_DOCKERID_DOCKER_TOOLBOX, "SelectedPreset", id, False)
        GlobalEvents.EMIT_SIGNAL_TOUCHIFY_TOOLBOX_PRESET_CHANGED()
    
    #endregion






