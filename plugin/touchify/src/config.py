from typing import List
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import json
import os

from .ext.extensions import JsonExtensions
from .cfg.CfgDocker import CfgDocker
from .cfg.CfgDockerGroup import CfgDockerGroup
from .cfg.CfgToolboxDocker import CfgToolboxDocker
from .cfg.CfgPopup import CfgPopup
from .cfg.CfgWorkspace import CfgWorkspace
from .cfg.CfgToolboxAction import CfgToolboxAction
from .ext.extensions import *
from ..paths import BASE_DIR
    
from configparser import ConfigParser

import json

class ConfigFile:
    dockers: TypedList[CfgDocker] = []
    docker_groups: TypedList[CfgDockerGroup] = []
    popups: TypedList[CfgPopup] = []
    workspaces: TypedList[CfgWorkspace] = []

    kb_dockers: TypedList[CfgToolboxDocker] = []
    kb_actions: TypedList[CfgToolboxAction] = []
    kb_titleButtonHeight: int = 10
    kb_dockerButtonHeight: int = 32
    kb_dockerBackHeight: int = 16
    kb_sliderHeight: int = 16
    kb_actionHeight: int = 16

    def load_kb(self):
        CONFIG_FILE = os.path.join(self.__base_dir__, 'configs', "toolbar_buddy.json")
        with open(CONFIG_FILE) as f:
            jsonData = json.load(f)
            self.kb_dockers = Extensions.list_assignment(jsonData["kb_dockers"], CfgToolboxDocker)
            self.kb_actions = Extensions.list_assignment(jsonData["kb_actions"], CfgToolboxAction)
            self.kb_titleButtonHeight = JsonExtensions.tryGetEntry(jsonData, "kb_titleButtonHeight", int, 10)
            self.kb_dockerButtonHeight = JsonExtensions.tryGetEntry(jsonData, "kb_dockerButtonHeight", int, 32)
            self.kb_dockerBackHeight = JsonExtensions.tryGetEntry(jsonData, "kb_dockerBackHeight", int, 16)
            self.kb_sliderHeight = JsonExtensions.tryGetEntry(jsonData, "kb_sliderHeight", int, 16)
            self.kb_actionHeight = JsonExtensions.tryGetEntry(jsonData, "kb_actionHeight", int, 16)


    def save_kb(self):
        CONFIG_FILE = os.path.join(self.__base_dir__, 'configs', "toolbar_buddy.json")
        jsonData = { 
            "kb_dockers": self.kb_dockers,
            "kb_actions": self.kb_actions,
            "kb_titleButtonHeight": self.kb_titleButtonHeight,
            "kb_dockerButtonHeight": self.kb_dockerButtonHeight,
            "kb_dockerBackHeight": self.kb_dockerBackHeight,
            "kb_sliderHeight": self.kb_sliderHeight,
            "kb_actionHeight": self.kb_actionHeight
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(jsonData, f, default=lambda o: o.__dict__, indent=4)
        
    def load_chunk(self, configName):
        CONFIG_FILE = os.path.join(self.__base_dir__, 'configs', configName + ".json")
        with open(CONFIG_FILE) as f:
            jsonData = json.load(f)
            return jsonData["items"]

    def save_chunk(self, cfg, configName):
        CONFIG_FILE = os.path.join(self.__base_dir__, 'configs', configName + ".json")
        jsonData = { "items": cfg }
        with open(CONFIG_FILE, "w") as f:
            json.dump(jsonData, f, default=lambda o: o.__dict__, indent=4)


    def propertygrid_groups(self):
        groups = {}
        groups["dockers"] = {"name": "Dockers", "items": ["dockers"]}
        groups["docker_groups"] = {"name": "Docker Groups", "items": ["docker_groups"]}
        groups["popups"] = {"name": "Popups", "items": ["popups"]}
        groups["workspaces"] = {"name": "Workspaces", "items": ["workspaces"]}
        groups["toolbar_buddy"] = {"name": "Toolbar Buddy", "items": [
            "kb_dockers",
            "kb_actions",
            "kb_titleButtonHeight",
            "kb_dockerButtonHeight",
            "kb_dockerBackHeight",
            "kb_sliderHeight",
            "kb_actionHeight"
        ]}
        return groups
    
    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions
    
    def save(self):
        self.save_chunk(self.dockers, "dockers")
        self.save_chunk(self.docker_groups, "docker_groups")
        self.save_chunk(self.popups, "popups")
        self.save_chunk(self.workspaces, "workspaces")
        self.save_kb()
        self.load()

    def load(self):
        self.dockers = Extensions.list_assignment(self.load_chunk("dockers"), CfgDocker)
        self.docker_groups = Extensions.list_assignment(self.load_chunk("docker_groups"), CfgDockerGroup)
        self.popups = Extensions.list_assignment(self.load_chunk("popups"), CfgPopup)
        self.workspaces = Extensions.list_assignment(self.load_chunk("workspaces"), CfgWorkspace)
        self.load_kb()
        

    def __init__(self, base_dir):
        self.__base_dir__ = base_dir
        self.load()

class ConfigManager:
    

    def instance():
        return ConfigManager.root

    def __init__(self, path) -> None:

        self.notify_hooks = []

        self.hotkeys_storage = {}
        self.base_dir = path
        self.cfg = ConfigFile(self.base_dir)

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

    def getHotkeyAction(self, index):
        return self.hotkeys_storage[index]

    def addHotkey(self, index, action):
        self.hotkeys_storage[index] = action

    def getJSON(self) -> ConfigFile:
        return self.cfg

class KritaSettings:
    def readSetting(group:str, name:str, defaultValue:str):
        return Krita.instance().readSetting(group, name, defaultValue)
    
    def writeSetting(group:str, name:str, value:str):
        return Krita.instance().writeSetting(group, name, value)

ConfigManager.root = ConfigManager(BASE_DIR)