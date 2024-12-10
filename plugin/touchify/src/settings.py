from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import json
import os


from touchify.src.cfg.CfgHotkeyRegistry import CfgHotkeyRegistry
from touchify.src.cfg.ResourcePackRegistry import ResourcePackRegistry
from touchify.src.cfg.toolshelf.CfgToolshelf import CfgToolshelf
from touchify.src.cfg.CfgPreferences import CfgPreferences
from touchify.src.variables import *

from touchify.src.cfg.CfgToolshelfRegistry import CfgToolshelfRegistry
from touchify.src.cfg.CfgActionRegistry import CfgActionRegistry
from touchify.src.cfg.CfgToolboxRegistry import CfgToolboxRegistry
from touchify.src.cfg.CfgWidgetPadRegistry import CfgWidgetPadRegistry

from touchify.src.ext.Extensions import *
from touchify.paths import BASE_DIR

import json


class TouchifyConfig:
    
    class ConfigFile(object):

        def __init__(self):
            self.__base_dir__ = BASE_DIR            
            self.actions_registry: CfgActionRegistry = CfgActionRegistry()
            self.resources: ResourcePackRegistry = ResourcePackRegistry()
            self.hotkeys: CfgHotkeyRegistry = CfgHotkeyRegistry()
            self.toolshelf_main: CfgToolshelfRegistry = CfgToolshelfRegistry("main")
            self.toolshelf_alt: CfgToolshelfRegistry = CfgToolshelfRegistry("overview")
            self.toolshelf_docker: CfgToolshelfRegistry = CfgToolshelfRegistry("docker")
            self.toolbox_settings: CfgToolboxRegistry = CfgToolboxRegistry()
            self.widget_pads: CfgWidgetPadRegistry = CfgWidgetPadRegistry()
            self.preferences: CfgPreferences = CfgPreferences()
            self.load()

        def loadClass(self, configName, type):
            try:
                CONFIG_FILE = os.path.join(self.__base_dir__, 'configs', configName + ".json")
                with open(CONFIG_FILE) as f:
                    return type(**json.load(f))
            except:
                return type()
                
        def saveClass(self, cfg, configName):
            CONFIG_FILE = os.path.join(self.__base_dir__, 'configs', configName + ".json")
            with open(CONFIG_FILE, "w") as f:
                json.dump(cfg, f, default=lambda o: o.__dict__, indent=4)

        def propertygrid_labels(self):
            labels = {}
            labels["registries"] = "Registries"
            labels["resources"] = "Resource Packs"
            labels["actions_registry"] = "Legacy Registry"

            labels["toolshelfs"] = "Toolshelf Presets"
            labels["toolshelf_main"] = "Main Toolshelves"
            labels["toolshelf_alt"] = "Preview Toolshelves "
            labels["toolshelf_docker"] = "Docker Toolshelves"

            labels["other_presets"] = "Touchify Presets"
            labels["toolbox_settings"] = "Touchify Toolbox"
            labels["widget_pads"] = "Widget Pads"

            labels["options"] = "Options"
            labels["hotkeys"] = "Hotkeys"
            labels["preferences"] = "Preferences"
            return labels
        
        def propertygrid_sisters(self):
            row: dict[str, list[str]] = {}
            row["toolshelfs"] = {"items": ["toolshelf_main", "toolshelf_alt", "toolshelf_docker"], "use_labels": True, "flip_labels": True}
            row["registries"] = {"items": ["resources", "actions_registry"], "use_labels": True, "flip_labels": True}
            row["options"] = {"items": ["hotkeys", "preferences"], "use_labels": True, "flip_labels": True}
            row["other_presets"] = {"items": ["toolbox_settings", "widget_pads"], "use_labels": True, "flip_labels": True}
            return row
        
        def propertygrid_restrictions(self):
            restrictions = {}
            restrictions["resources"] = {"type": "expandable"}
            restrictions["actions_registry"] = {"type": "expandable"}
            restrictions["hotkeys"] = {"type": "expandable"}
            restrictions["toolshelf_main"] = {"type": "expandable"}
            restrictions["toolshelf_alt"] = {"type": "expandable"}
            restrictions["toolshelf_docker"] = {"type": "expandable"}
            restrictions["toolbox_settings"] = {"type": "expandable"}
            restrictions["widget_pads"] = {"type": "expandable"}
            restrictions["preferences"] = {"type": "expandable"}
            return restrictions
        
        def save(self):
            self.saveClass(self.actions_registry, "actions_registry")
            self.saveClass(self.hotkeys, "hotkeys")
            self.resources.save()
            self.toolshelf_main.save() 
            self.toolshelf_alt.save()
            self.toolshelf_docker.save()
            self.toolbox_settings.save()
            self.widget_pads.save()
            self.preferences.save()

        def load(self):
            self.actions_registry = self.loadClass("actions_registry", CfgActionRegistry)
            self.hotkeys = self.loadClass("hotkeys", CfgHotkeyRegistry)
            self.resources.load()
            self.toolshelf_main.load()
            self.toolshelf_alt.load()
            self.toolshelf_docker.load()
            self.toolbox_settings.load()
            self.widget_pads.load()
            self.preferences.load()
            
    def instance():
        try:
            return TouchifyConfig.__instance
        except AttributeError:
            TouchifyConfig.__instance = TouchifyConfig()
            return TouchifyConfig.__instance

    def __init__(self) -> None:
        self.notify_hooks = []
        self.hotkey_options_storage = {}
        self.cfg = TouchifyConfig.ConfigFile()
        
    def preferences(self) -> CfgPreferences:
        return self.cfg.preferences

    def getConfig(self) -> ConfigFile:
        return self.cfg
    
    def getToolshelfRegistry(self, registry_index: int) -> CfgToolshelfRegistry | None:
        cfg = self.getConfig()
        if registry_index == 0: return cfg.toolshelf_main
        elif registry_index == 1: return cfg.toolshelf_alt
        elif registry_index == 2: return cfg.toolshelf_docker
        else: return None

    def getActiveToolshelfIndex(self, registry_index: int) -> int:
        cfg = self.getConfig()
        if registry_index == 0: return cfg.toolshelf_main.getActiveIndex()
        elif registry_index == 1: return cfg.toolshelf_alt.getActiveIndex()
        elif registry_index == 2: return cfg.toolshelf_docker.getActiveIndex()
        else: return 0

    def getActiveToolshelf(self, registry_index: int) -> CfgToolshelf | None:
        cfg = self.getConfig()
        if registry_index == 0: return cfg.toolshelf_main.getActive()
        elif registry_index == 1: return cfg.toolshelf_alt.getActive()
        elif registry_index == 2: return cfg.toolshelf_docker.getActive()
        else: return None

    def setActiveToolshelf(self, registry_index: int, index: int):
        cfg = self.getConfig()
        if registry_index == 0: cfg.toolshelf_main.setActive(index)
        elif registry_index == 1: cfg.toolshelf_alt.setActive(index)
        elif registry_index == 2: cfg.toolshelf_docker.setActive(index)

        self.notifyUpdate()

    def addHotkeyOption(self, actionName, displayName, action, parameters):
        self.hotkey_options_storage[actionName] = {
            "displayName": displayName,
            "action": action,
            "params": parameters
        }
    
    def runHotkeyOption(self, actionName: str):
        if actionName == "none":
            return
        
        if actionName not in TouchifyConfig.instance().hotkey_options_storage:
            return
        
        actionObj = TouchifyConfig.instance().hotkey_options_storage[actionName]
        params = actionObj["params"]
        action = actionObj["action"]
        
        action(**params)

    def notifyConnect(self, event):
        self.notify_hooks.append(event)

    def notifyUpdate(self):
        self.cfg.load()

        for hook in self.notify_hooks:
            hook()




