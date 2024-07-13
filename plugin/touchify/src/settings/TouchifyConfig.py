from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import json
import os

from ..cfg.CfgHotkeys import CfgHotkeys
from ..ext.extensions_json import JsonExtensions
from ..cfg.CfgToolshelf import CfgToolshelf
from ..variables import *
from ..cfg.CfgDocker import CfgDocker
from ..cfg.CfgDockerGroup import CfgDockerGroup
from ..cfg.CfgPopup import CfgPopup
from ..cfg.CfgWorkspace import CfgWorkspace
from ..ext.extensions import *
from ...paths import BASE_DIR
import copy

import json


class TouchifyConfig:
    
    class ConfigFile(object):

        def __init__(self):
            self.dockers: TypedList[CfgDocker] = []
            self.docker_groups: TypedList[CfgDockerGroup] = []
            self.popups: TypedList[CfgPopup] = []
            self.workspaces: TypedList[CfgWorkspace] = []
            
            self.hotkeys: CfgHotkeys = CfgHotkeys()
            self.toolshelf_main: CfgToolshelf = CfgToolshelf()
            self.toolshelf_alt: CfgToolshelf = CfgToolshelf()

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
            labels["dockers"] = "Dockers"
            labels["docker_groups"] = "Docker Groups"
            labels["popups"] = "Popups"
            labels["workspaces"] = "Workspaces"
            labels["toolshelf_main"] = "Tool Options Shelf"
            labels["toolshelf_alt"] = "Toolbox Shelf"
            labels["hotkeys"] = "Hotkeys"
            return labels

        def propertygrid_groups(self):
            groups = {}
            groups["core"] = {"name": "Core Features", "items": ["dockers", "docker_groups", "popups", "workspaces"]}
            groups["canvas"] = {"name": "Canvas Widgets", "items": ["toolshelf_alt", "toolshelf_main"]}
            groups["miscellaneous"] = {"name": "Miscellaneous", "items": ["hotkeys"]}
            return groups
        
        def propertygrid_restrictions(self):
            restrictions = {}
            restrictions["hotkeys"] = {"type": "expandable"}
            restrictions["toolshelf_main"] = {"type": "expandable"}
            restrictions["toolshelf_alt"] = {"type": "expandable"}
            return restrictions
        
        def save(self):
            self.save_chunk(self.dockers, "dockers")
            self.save_chunk(self.docker_groups, "docker_groups")
            self.save_chunk(self.popups, "popups")
            self.save_chunk(self.workspaces, "workspaces")
            self.saveClass(self.hotkeys, "hotkeys")
            self.saveClass(self.toolshelf_main, "toolshelf_main")
            self.saveClass(self.toolshelf_alt, "toolshelf_alt")

        def load(self):
            self.dockers = self.load_chunk("dockers", CfgDocker)
            self.docker_groups = self.load_chunk("docker_groups", CfgDockerGroup)
            self.popups = self.load_chunk("popups", CfgPopup)
            self.workspaces = self.load_chunk("workspaces", CfgWorkspace)
            self.hotkeys = self.loadClass("hotkeys", CfgHotkeys)
            self.toolshelf_main = self.loadClass("toolshelf_main", CfgToolshelf)
            self.toolshelf_alt = self.loadClass("toolshelf_alt", CfgToolshelf)
            
        def __init__(self, base_dir):
            self.__base_dir__ = base_dir
            self.load()

    def instance():
        try:
            return TouchifyConfig.__instance
        except AttributeError:
            TouchifyConfig.__instance = TouchifyConfig(BASE_DIR)
            return TouchifyConfig.__instance

    def __init__(self, path) -> None:

        self.notify_hooks = []
        self.hotkey_options_storage = {}
        
        self.base_dir = path
        self.cfg = TouchifyConfig.ConfigFile(self.base_dir)

    def getEditableCfg(self):
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

    def getBaseDirectory(self):
        return self.base_dir

    def getResourceFolder(self):
        return os.path.join(self.base_dir, "resources")

    def getJSON(self) -> ConfigFile:
        return self.cfg

