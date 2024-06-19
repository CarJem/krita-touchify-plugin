from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import json
import os

from .variables import *

from .ext.extensions import JsonExtensions
from .cfg.CfgDocker import CfgDocker
from .cfg.CfgDockerGroup import CfgDockerGroup
from .cfg.CfgToolboxPanel import CfgToolboxPanel
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

    kb_dockers: TypedList[CfgToolboxPanel] = []
    kb_actions: TypedList[CfgToolboxAction] = []

    kb_toolbox_dockers: TypedList[CfgToolboxPanel] = []
    kb_toolbox_actions: TypedList[CfgToolboxAction] = []
    
    kb_titleButtonHeight: int = 10
    kb_dockerButtonHeight: int = 32
    kb_dockerBackHeight: int = 16
    kb_sliderHeight: int = 16
    kb_actionHeight: int = 16

    def load_kb(self):
        CONFIG_FILE = os.path.join(self.__base_dir__, 'configs', "toolbar_buddy.json")
        with open(CONFIG_FILE) as f:
            jsonData = json.load(f)
            self.kb_dockers = JsonExtensions.tryGetListAssignment(jsonData, "kb_dockers", CfgToolboxPanel, [])
            self.kb_actions = JsonExtensions.tryGetListAssignment(jsonData, "kb_actions", CfgToolboxAction, [])
            self.kb_toolbox_dockers = JsonExtensions.tryGetListAssignment(jsonData, "kb_toolbox_dockers", CfgToolboxPanel, [])
            self.kb_toolbox_actions = JsonExtensions.tryGetListAssignment(jsonData, "kb_toolbox_actions", CfgToolboxAction, [])
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
            "kb_toolbox_dockers": self.kb_toolbox_dockers,
            "kb_toolbox_actions": self.kb_toolbox_actions,
            "kb_titleButtonHeight": self.kb_titleButtonHeight,
            "kb_dockerButtonHeight": self.kb_dockerButtonHeight,
            "kb_dockerBackHeight": self.kb_dockerBackHeight,
            "kb_sliderHeight": self.kb_sliderHeight,
            "kb_actionHeight": self.kb_actionHeight
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(jsonData, f, default=lambda o: o.__dict__, indent=4)
        
    def load_chunk(self, configName, type):
        CONFIG_FILE = os.path.join(self.__base_dir__, 'configs', configName + ".json")
        with open(CONFIG_FILE) as f:
            jsonData = json.load(f)
            return JsonExtensions.tryGetListAssignment(jsonData, "items", type, [])

    def save_chunk(self, cfg, configName):
        CONFIG_FILE = os.path.join(self.__base_dir__, 'configs', configName + ".json")
        jsonData = { "items": cfg }
        with open(CONFIG_FILE, "w") as f:
            json.dump(jsonData, f, default=lambda o: o.__dict__, indent=4)


    def propertygrid_labels(self):
        labels = {}
        labels["dockers"] = None
        labels["docker_groups"] = None
        labels["popups"] = None
        labels["workspaces"] = None
        labels["kb_dockers"] = "Tool Options Dockers"
        labels["kb_actions"] = "Tool Options Actions"
        labels["kb_toolbox_dockers"] = "Toolbox Dockers"
        labels["kb_toolbox_actions"] = "Toolbox Actions"
        labels["kb_titleButtonHeight"] = "Title Button Height"
        labels["kb_dockerButtonHeight"] = "Docker Button Height"
        labels["kb_dockerBackHeight"] = "Back Button Height"
        labels["kb_sliderHeight"] = "Slider Height"
        labels["kb_actionHeight"] = "Action Button Height"
        return labels

    def propertygrid_groups(self):
        groups = {}
        groups["dockers"] = {"name": "Dockers", "items": ["dockers"]}
        groups["docker_groups"] = {"name": "Docker Groups", "items": ["docker_groups"]}
        groups["popups"] = {"name": "Popups", "items": ["popups"]}
        groups["workspaces"] = {"name": "Workspaces", "items": ["workspaces"]}
        groups["touchify_toolbox"] = {"name": "Touchify Toolbox", "items": [
            "kb_dockers",
            "kb_actions",
            "kb_toolbox_dockers",
            "kb_toolbox_actions",
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
        self.dockers = self.load_chunk("dockers", CfgDocker)
        self.docker_groups = self.load_chunk("docker_groups", CfgDockerGroup)
        self.popups = self.load_chunk("popups", CfgPopup)
        self.workspaces = self.load_chunk("workspaces", CfgWorkspace)
        self.load_kb()
        

    def __init__(self, base_dir):
        self.__base_dir__ = base_dir
        self.load()

class ConfigManager:
    

    def instance():
        try:
            return ConfigManager.__instance
        except AttributeError:
            ConfigManager.__instance = ConfigManager(BASE_DIR)
            return ConfigManager.__instance

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

    def init():
        KritaSettings.notify_hooks = []

    def notifyConnect(event):
        KritaSettings.notify_hooks.append(event)

    def notifyUpdate():
        for hook in KritaSettings.notify_hooks:
            hook()

    def readSetting(group:str, name:str, defaultValue:str):
        return Krita.instance().readSetting(group, name, defaultValue)
    
    def readSettingBool(group:str, name:str, defaultValue:bool):
        defaultVal = "true" if defaultValue == True else "false"

        result = KritaSettings.readSetting(group, name, defaultVal)
        if result == "true": return True
        elif result == "false": return False
        else: return None
    
    def writeSettingBool(group:str, name:str, value:bool):
        defaultVal = "true" if value == True else "false"
        return KritaSettings.writeSetting(group, name, defaultVal)

    def writeSetting(group:str, name:str, value:str):
        result = Krita.instance().writeSetting(group, name, value)
        KritaSettings.notifyUpdate()
        return result
    
class InternalConfig:

    def instance():
        try:
            return InternalConfig.__instance
        except AttributeError:
            InternalConfig.__instance = InternalConfig()
            return InternalConfig.__instance

    def __init__(self) -> None:
        self.__has_preloaded = False

        self.usesFlatTheme = False
        self.usesBorderlessToolbar = False
        self.usesThinDocumentTabs = False
        self.usesNuToolbox = False
        self.usesNuToolOptions = False
        self.ntToolbox = None
        self.ntToolOptions = None
        self.nuOptions_ToolboxOnRight = False
        self.nuOptions_SharedToolDocker = False
        self.nuOptions_AlternativeToolboxPosition = False

        self.loadSettings()

    def private_readSettingsBool(self, name: str, defaultValue: bool) -> bool:
        return KritaSettings.readSettingBool(TOUCHIFY_ID_OPTIONSROOT_MAIN, name, defaultValue)
    
    def private_writeSettingsBool(self, name: str, value: bool, defaultValue: bool) -> bool:
        if self.private_readSettingsBool(name, defaultValue) != value:
            KritaSettings.writeSettingBool(TOUCHIFY_ID_OPTIONSROOT_MAIN, name, value)
    
    def loadSettings(self):
        self.usesFlatTheme = False

        self.usesBorderlessToolbar = self.private_readSettingsBool(TOUCHIFY_ID_OPTIONS_BORDERLESS_TOOLBAR, False)
        self.usesThinDocumentTabs = self.private_readSettingsBool(TOUCHIFY_ID_OPTIONS_THIN_DOC_TABS, False)
        self.usesNuToolbox = self.private_readSettingsBool(TOUCHIFY_ID_OPTIONS_NU_TOOLBOX, False)
        self.usesNuToolOptions = self.private_readSettingsBool(TOUCHIFY_ID_OPTIONS_NU_TOOL_OPTIONS, False)

        self.nuOptions_ToolboxOnRight = self.private_readSettingsBool(TOUCHIFY_ID_OPTIONS_NU_OPTIONS_RIGHT_HAND_TOOLBOX, False)
        self.nuOptions_SharedToolDocker = self.private_readSettingsBool(TOUCHIFY_ID_OPTIONS_NU_OPTIONS_SHAREDTOOLDOCKER, False)
        self.nuOptions_AlternativeToolboxPosition = self.private_readSettingsBool(TOUCHIFY_ID_OPTIONS_NU_OPTIONS_ALTERNATIVE_TOOLBOX_POSITION, False)

    def saveSettings(self):
        self.private_writeSettingsBool(TOUCHIFY_ID_OPTIONS_BORDERLESS_TOOLBAR, self.usesBorderlessToolbar, False)
        self.private_writeSettingsBool(TOUCHIFY_ID_OPTIONS_THIN_DOC_TABS, self.usesThinDocumentTabs, False)
        self.private_writeSettingsBool(TOUCHIFY_ID_OPTIONS_NU_TOOLBOX, self.usesNuToolbox, False)
        self.private_writeSettingsBool(TOUCHIFY_ID_OPTIONS_NU_TOOL_OPTIONS, self.usesNuToolOptions, False)

        self.private_writeSettingsBool(TOUCHIFY_ID_OPTIONS_NU_OPTIONS_RIGHT_HAND_TOOLBOX, self.nuOptions_ToolboxOnRight, False)
        self.private_writeSettingsBool(TOUCHIFY_ID_OPTIONS_NU_OPTIONS_SHAREDTOOLDOCKER, self.nuOptions_SharedToolDocker, False)
        self.private_writeSettingsBool(TOUCHIFY_ID_OPTIONS_NU_OPTIONS_ALTERNATIVE_TOOLBOX_POSITION, self.nuOptions_AlternativeToolboxPosition, False)

KritaSettings.init()