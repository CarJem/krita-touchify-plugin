from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import json
import os

from ..cfg.CfgHotkeys import CfgHotkeys
from ..ext.extensions_json import JsonExtensions
from ..cfg.CfgToolshelf import CfgToolshelf
from ..variables import *
from ..cfg.CfgTouchifyRegistry import CfgTouchifyRegistry
from ..ext.extensions import *
from ...paths import BASE_DIR
import copy

import json


class TouchifyConfig:
    
    class ConfigFile(object):

        def __init__(self):
            self.__base_dir__ = BASE_DIR            
            self.actions_registry: CfgTouchifyRegistry = CfgTouchifyRegistry()
            self.hotkeys: CfgHotkeys = CfgHotkeys()
            self.toolshelf_main: CfgToolshelf = CfgToolshelf()
            self.toolshelf_alt: CfgToolshelf = CfgToolshelf()
            self.toolshelf_docker: CfgToolshelf = CfgToolshelf()
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
            return labels

        def propertygrid_groups(self):
            groups = {}
            #groups["canvas"] = {"name": "Toolshelf Widgets", "items": ["toolshelf_alt", "toolshelf_main", "toolshelf_docker"]}
            #groups["miscellaneous"] = {"name": "Miscellaneous", "items": ["hotkeys"]}
            return groups
        
        def propertygrid_restrictions(self):
            restrictions = {}
            restrictions["hotkeys"] = {"type": "expandable"}
            restrictions["toolshelf_main"] = {"type": "expandable"}
            restrictions["toolshelf_alt"] = {"type": "expandable"}
            restrictions["toolshelf_docker"] = {"type": "expandable"}
            restrictions["actions_registry"] = {"type": "expandable"}
            return restrictions
        
        def save(self):
            self.saveClass(self.actions_registry, "actions_registry")
            self.saveClass(self.hotkeys, "hotkeys")
            self.saveClass(self.toolshelf_main, "toolshelf_main")
            self.saveClass(self.toolshelf_alt, "toolshelf_alt")
            self.saveClass(self.toolshelf_docker, "toolshelf_docker")

        def load(self):
            self.actions_registry = self.loadClass("actions_registry", CfgTouchifyRegistry)
            self.hotkeys = self.loadClass("hotkeys", CfgHotkeys)
            self.toolshelf_main = self.loadClass("toolshelf_main", CfgToolshelf)
            self.toolshelf_alt = self.loadClass("toolshelf_alt", CfgToolshelf)
            self.toolshelf_docker = self.loadClass("toolshelf_docker", CfgToolshelf)
            
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

    def copyConfig(self):
        return copy.copy(self.cfg)

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




