from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import json
import os

from ..ext.KritaSettings import KritaSettings

from ..cfg.CfgHotkeyRegistry import CfgHotkeyRegistry
from ..ext.extensions_json import JsonExtensions
from ..cfg.toolshelf.CfgToolshelf import CfgToolshelf
from ..variables import *

from ..cfg.CfgToolshelfRegistry import CfgToolshelfRegistry
from ..cfg.CfgActionRegistry import CfgActionRegistry
from ..cfg.CfgToolboxRegistry import CfgToolboxRegistry
from ..ext.extensions import *
from ...paths import BASE_DIR
import copy

import json


class TouchifyConfig:
    
    class ConfigFile(object):

        def __init__(self):
            self.__base_dir__ = BASE_DIR            
            self.actions_registry: CfgActionRegistry = CfgActionRegistry()
            self.hotkeys: CfgHotkeyRegistry = CfgHotkeyRegistry()
            self.toolshelf_main: CfgToolshelfRegistry = CfgToolshelfRegistry("main")
            self.toolshelf_alt: CfgToolshelfRegistry = CfgToolshelfRegistry("overview")
            self.toolshelf_docker: CfgToolshelfRegistry = CfgToolshelfRegistry("docker")
            self.toolbox_settings: CfgToolboxRegistry = CfgToolboxRegistry()
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
            
        def load_chunk(self, configName, type):
            try:
                CONFIG_FILE = os.path.join(self.__base_dir__, 'configs', configName + ".json")
                with open(CONFIG_FILE) as f:
                    jsonData = json.load(f)
                    return JsonExtensions.tryGetListAssignment(jsonData, "items", type, [])
            except:
                return type()

        def save_chunk(self, cfg, configName):
            CONFIG_FILE = os.path.join(self.__base_dir__, 'configs', configName + ".json")
            jsonData = { "items": cfg }
            with open(CONFIG_FILE, "w") as f:
                json.dump(jsonData, f, default=lambda o: o.__dict__, indent=4)

        def propertygrid_labels(self):
            labels = {}
            labels["toolshelf_alt"] = "Toolbox Shelf"
            labels["toolshelf_main"] = "Sidebar Shelf"
            labels["toolshelf_docker"] = "Docker Shelf"
            labels["actions_registry"] = "Registry"
            labels["hotkeys"] = "Hotkeys"
            labels["toolbox_settings"] = "Touchify Toolbox"
            return labels
        
        def propertygrid_sisters(self):
            row: dict[str, list[str]] = {}
            row["toolshelfs"] = {"name": "Toolshelf Settings", "items": ["toolshelf_main", "toolshelf_alt", "toolshelf_docker"]}
            return row
        
        def propertygrid_restrictions(self):
            restrictions = {}
            restrictions["hotkeys"] = {"type": "expandable"}
            restrictions["toolshelf_main"] = {"type": "expandable", "text": "Main"}
            restrictions["toolshelf_alt"] = {"type": "expandable", "text": "Preview"}
            restrictions["toolshelf_docker"] = {"type": "expandable", "text": "Docker"}
            restrictions["actions_registry"] = {"type": "expandable"}
            restrictions["toolbox_settings"] = {"type": "expandable"}
            return restrictions
        
        def save(self):
            self.saveClass(self.actions_registry, "actions_registry")
            self.saveClass(self.hotkeys, "hotkeys")
            self.toolshelf_main.save() 
            self.toolshelf_alt.save()
            self.toolshelf_docker.save()
            self.toolbox_settings.save()

        def load(self):
            self.actions_registry = self.loadClass("actions_registry", CfgActionRegistry)
            self.hotkeys = self.loadClass("hotkeys", CfgHotkeyRegistry)
            self.toolshelf_main.load()
            self.toolshelf_alt.load()
            self.toolshelf_docker.load()
            self.toolbox_settings.load()
            
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




