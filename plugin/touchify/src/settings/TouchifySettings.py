from PyQt5.QtWidgets import *
from PyQt5.QtCore import *



from touchify.src.config.pie_wheel.PieWheelData import PieWheelData
from touchify.src.config.quick_actions.QuickActionsPreset import QuickActionsPreset
from touchify.src.config.resource_pack.ResourcePack import ResourcePack
from touchify.src.config.TouchifyRegistry import TouchifyRegistry
from touchify.src.config.canvas_preset.CanvasPreset import CanvasPreset
from touchify.src.config.docker_group.DockerGroup import DockerGroup
from touchify.src.config.popup.PopupData import PopupData
from touchify.src.config.script.CustomScript import CustomScript
from touchify.src.config.toolbox.ToolboxData import ToolboxData
from touchify.src.config.toolshelf.Toolshelf import Toolshelf
from touchify.src.config.TouchifyPreferences import TouchifyPreferences
from touchify.src.config.context_menu.ContextMenu import ContextMenu
from jemlib.api_touchify.env import *


RegistryItemType = None | ContextMenu | PopupData | DockerGroup | CanvasPreset | Toolshelf | ToolboxData | CustomScript | PieWheelData | QuickActionsPreset

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
            resourcePacks = TouchifySettings.resourcePacks()
            for pack in resourcePacks:
                if pack.INTERNAL_UUID_ID == self.id: return pack
            return None


    def __init__(self) -> None:
        self.notify_hooks = []
        self.cfg = TouchifyRegistry()
        self.cfg.load()

    @staticmethod
    def instance():
        try:
            return TouchifySettings.__instance
        except AttributeError:
            TouchifySettings.__instance = TouchifySettings()
            return TouchifySettings.__instance

    @staticmethod
    def config() -> TouchifyRegistry:
        return TouchifySettings.instance().cfg

    @staticmethod
    def save():
        TouchifySettings.config().save()

    @staticmethod
    def load():
        TouchifySettings.config().load()
        
    @staticmethod
    def preferences() -> TouchifyPreferences:
        return TouchifySettings.config().preferences

    @staticmethod
    def resourcePacks() -> list[ResourcePack]:
        return TouchifySettings.config().resources.presets

    @staticmethod
    def registryItem(item_id: str, type: type) -> RegistryItemType:
        cfg = TouchifySettings.config()
        for pack in cfg.resources.presets:
            pack: ResourcePack

            if type == PopupData:
                for item in pack.popups:
                    item: PopupData
                    id = f"{pack.INTERNAL_UUID_ID}/popup/{item.INTERNAL_UUID_ID}"
                    if item_id == id: return item
            elif type == ContextMenu:
                for item in pack.menus:
                    item: ContextMenu
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
            elif type == QuickActionsPreset:
                for item in pack.quick_actions:
                    item: QuickActionsPreset
                    id = f"{pack.INTERNAL_UUID_ID}/quick_actions/{item.INTERNAL_UUID_ID}"
                    if item_id == id: return item

        return None

    @staticmethod
    def registry(type: type) -> dict[RegistryKey, RegistryItemType]:
        cfg = TouchifySettings.config()
        results: dict = {}
        for pack in cfg.resources.presets:
            pack: ResourcePack

            if type == PopupData:
                for item in pack.popups:
                    item: PopupData
                    id = TouchifySettings.RegistryKey(pack.INTERNAL_UUID_ID, pack.metadata.registry_name, "popup", item.INTERNAL_UUID_ID)
                    results[id] = item
            elif type == ContextMenu:
                for item in pack.menus:
                    item: ContextMenu
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
            elif type == QuickActionsPreset:
                for item in pack.quick_actions:
                    item: QuickActionsPreset
                    id = TouchifySettings.RegistryKey(pack.INTERNAL_UUID_ID, pack.metadata.registry_name, "quick_actions", item.INTERNAL_UUID_ID)
                    results[id] = item

        return results






