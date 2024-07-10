from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import json
import os

from touchify.src.ext.KritaSettings import KritaSettings

from .ext.extensions_json import JsonExtensions

from .cfg.CfgToolshelf import CfgToolshelf

from .variables import *

from .ext.extensions_json import JsonExtensions
from .cfg.CfgDocker import CfgDocker
from .cfg.CfgDockerGroup import CfgDockerGroup
from .cfg.CfgToolshelf import CfgToolshelfPanel
from .cfg.CfgPopup import CfgPopup
from .cfg.CfgWorkspace import CfgWorkspace
from .cfg.CfgToolshelf import CfgToolshelfAction
from .ext.extensions import *
from ..paths import BASE_DIR
import copy
from configparser import ConfigParser

import json

class ConfigFile(object):

    def __init__(self):
        self.dockers: TypedList[CfgDocker] = []
        self.docker_groups: TypedList[CfgDockerGroup] = []
        self.popups: TypedList[CfgPopup] = []
        self.workspaces: TypedList[CfgWorkspace] = []

        self.toolshelf_main: CfgToolshelf = CfgToolshelf()
        self.toolshelf_alt: CfgToolshelf = CfgToolshelf()

    def loadClass(self, configName, type):
        CONFIG_FILE = os.path.join(self.__base_dir__, 'configs', configName + ".json")
        with open(CONFIG_FILE) as f:
            return type(**json.load(f))

    def saveClass(self, cfg, configName):
        CONFIG_FILE = os.path.join(self.__base_dir__, 'configs', configName + ".json")
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, default=lambda o: o.__dict__, indent=4)
        
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
        labels["toolshelf_main"] = "Tool Options Shelf"
        labels["toolshelf_alt"] = "Toolbox Shelf"
        return labels

    def propertygrid_groups(self):
        groups = {}
        groups["dockers"] = {"name": "Dockers", "items": ["dockers"]}
        groups["docker_groups"] = {"name": "Docker Groups", "items": ["docker_groups"]}
        groups["popups"] = {"name": "Popups", "items": ["popups"]}
        groups["workspaces"] = {"name": "Workspaces", "items": ["workspaces"]}
        groups["toolshelfs"] = {"name": "Toolshelfs", "items": ["toolshelf_alt", "toolshelf_main"]}
        return groups
    
    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["toolshelf_main"] = {"type": "expandable"}
        restrictions["toolshelf_alt"] = {"type": "expandable"}
        return restrictions
    
    def save(self):
        self.save_chunk(self.dockers, "dockers")
        self.save_chunk(self.docker_groups, "docker_groups")
        self.save_chunk(self.popups, "popups")
        self.save_chunk(self.workspaces, "workspaces")
        self.saveClass(self.toolshelf_main, "toolshelf_main")
        self.saveClass(self.toolshelf_alt, "toolshelf_alt")

    def load(self):
        self.dockers = self.load_chunk("dockers", CfgDocker)
        self.docker_groups = self.load_chunk("docker_groups", CfgDockerGroup)
        self.popups = self.load_chunk("popups", CfgPopup)
        self.workspaces = self.load_chunk("workspaces", CfgWorkspace)
        self.toolshelf_main = self.loadClass("toolshelf_main", CfgToolshelf)
        self.toolshelf_alt = self.loadClass("toolshelf_alt", CfgToolshelf)
        

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

        self.base_dir = path
        self.cfg = ConfigFile(self.base_dir)

    def getEditableCfg(self):
        return copy.copy(self.cfg)

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

class InternalConfig:

    def instance():
        try:
            return InternalConfig.__instance
        except AttributeError:
            InternalConfig.__instance = InternalConfig()
            return InternalConfig.__instance

    def __init__(self) -> None:
        self.__has_preloaded = False

        self.Styles_FlatTheme = False
        self.Styles_BorderlessToolbar = False
        self.Styles_ThinDocumentTabs = False

        self.CanvasWidgets_EnableToolbox = False
        self.CanvasWidgets_EnableToolshelf = False
        self.CanvasWidgets_EnableAltToolshelf = False
        self.CanvasWidgets_ToolboxOnRight = False
        self.CanvasWidgets_AlternativeToolboxPosition = False

        self.DockerUtils_HiddenDockersLeft: str = ""
        self.DockerUtils_HiddenDockersRight: str = ""
        self.DockerUtils_HiddenDockersUp: str = ""
        self.DockerUtils_HiddenDockersDown: str = ""

        self.loadSettings()

    def private_readSetting(self, name: str, defaultValue: str) -> str:
        return KritaSettings.readSetting("Touchify", name, defaultValue)
    
    def private_writeSetting(self, name: str, value: str, defaultValue: str) -> None:
        if self.private_readSetting(name, defaultValue) != value:
            KritaSettings.writeSetting("Touchify", name, value)

    def private_readSettingBool(self, name: str, defaultValue: bool) -> bool:
        return KritaSettings.readSettingBool("Touchify", name, defaultValue)
    
    def private_writeSettingBool(self, name: str, value: bool, defaultValue: bool) -> None:
        if self.private_readSettingBool(name, defaultValue) != value:
            KritaSettings.writeSettingBool("Touchify", name, value)
    
    def loadSettings(self):
        self.Styles_FlatTheme = False

        self.Styles_BorderlessToolbar = self.private_readSettingBool("usesBorderlessToolbar", False)
        self.Styles_ThinDocumentTabs = self.private_readSettingBool("usesThinDocumentTabs", False)
        self.CanvasWidgets_EnableToolbox = self.private_readSettingBool("usesNuToolbox", False)
        self.CanvasWidgets_EnableToolshelf = self.private_readSettingBool("usesNuToolOptions", False)
        self.CanvasWidgets_EnableAltToolshelf = self.private_readSettingBool("usesNuToolOptionsAlt", False)
        
        self.CanvasWidgets_ToolboxOnRight = self.private_readSettingBool("nuOptions_ToolboxOnRight", False)
        self.CanvasWidgets_AlternativeToolboxPosition = self.private_readSettingBool("nuOptions_alternativeToolboxPosition", False)

        self.DockerUtils_HiddenDockersLeft = self.private_readSetting("DockerUtils_HiddenLeft", "")
        self.DockerUtils_HiddenDockersRight = self.private_readSetting("DockerUtils_HiddenRight", "")
        self.DockerUtils_HiddenDockersUp = self.private_readSetting("DockerUtils_HiddenUp", "")
        self.DockerUtils_HiddenDockersDown = self.private_readSetting("DockerUtils_HiddenDown", "")

    def saveSettings(self):
        self.private_writeSettingBool("usesBorderlessToolbar", self.Styles_BorderlessToolbar, False)
        self.private_writeSettingBool("usesThinDocumentTabs", self.Styles_ThinDocumentTabs, False)
        self.private_writeSettingBool("usesNuToolbox", self.CanvasWidgets_EnableToolbox, False)
        self.private_writeSettingBool("usesNuToolOptions", self.CanvasWidgets_EnableToolshelf, False)
        self.private_writeSettingBool("usesNuToolOptionsAlt", self.CanvasWidgets_EnableAltToolshelf, False)

        self.private_writeSettingBool("nuOptions_ToolboxOnRight", self.CanvasWidgets_ToolboxOnRight, False)
        self.private_writeSettingBool("nuOptions_alternativeToolboxPosition", self.CanvasWidgets_AlternativeToolboxPosition, False)

        self.private_writeSetting("DockerUtils_HiddenLeft", self.DockerUtils_HiddenDockersLeft, "")
        self.private_writeSetting("DockerUtils_HiddenRight", self.DockerUtils_HiddenDockersRight, "")
        self.private_writeSetting("DockerUtils_HiddenUp", self.DockerUtils_HiddenDockersUp, "")
        self.private_writeSetting("DockerUtils_HiddenDown", self.DockerUtils_HiddenDockersDown, "")

